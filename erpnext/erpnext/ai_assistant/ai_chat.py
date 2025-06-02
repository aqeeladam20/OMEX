import frappe
import openai
import json
import re
from datetime import datetime, timedelta
from frappe import _
from frappe.utils import nowdate, add_days, getdate


class AIAssistant:
    def __init__(self):
        # Get OpenAI API key from site config or environment
        self.api_key = frappe.conf.get("openai_api_key") or "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"
        openai.api_key = self.api_key
        
    def get_context_prompt(self):
        """Generate context about the current OMEX instance"""
        company = frappe.defaults.get_user_default("Company") or "OMEX ERP"
        user = frappe.session.user
        
        context = f"""
        You are an AI assistant for {company} using OMEX ERP (formerly OMEX).
        Current user: {user}
        Current date: {nowdate()}
        
        You can help with:
        1. Querying data (sales, purchases, inventory, etc.)
        2. Creating documents (tasks, events, invoices, etc.)
        3. Generating reports and insights
        4. Workflow automation
        
        When suggesting actions, be specific about what you can do and ask for confirmation.
        Always format data in a clear, readable way.
        """
        return context
    
    def handle_data_queries(self, user_message):
        """Handle database queries using AI to interpret and generate queries"""
        try:
            # Use AI to understand the query and generate appropriate database query
            query_analysis = self.analyze_query_with_ai(user_message)
            
            if query_analysis and query_analysis.get('is_data_query'):
                return self.execute_dynamic_query(query_analysis)
            
            return None
        except Exception as e:
            frappe.log_error(f"Data Query Error: {str(e)}")
            return None
    
    def analyze_query_with_ai(self, user_message):
        """Use AI to analyze the user query and determine what data to fetch"""
        try:
            analysis_prompt = f"""
            Analyze this user query and determine if it's asking for data from an ERP system: "{user_message}"
            
            Available OMEX DocTypes and common fields:
            - Item: name, item_name, item_group, stock_uom, creation
            - Customer: name, customer_name, customer_group, territory, creation
            - Sales Invoice: name, customer, posting_date, grand_total, status, docstatus
            - Sales Order: name, customer, transaction_date, grand_total, status, docstatus
            - Purchase Invoice: name, supplier, posting_date, grand_total, status, docstatus
            - Task: name, subject, status, priority, assigned_to, exp_end_date
            - Lead: name, lead_name, status, source, creation
            - Supplier: name, supplier_name, supplier_group, creation
            
            Respond with a JSON object containing:
            {{
                "is_data_query": true/false,
                "doctype": "DocType name",
                "query_type": "count/list/latest/sum/specific",
                "filters": {{"field": "value"}},
                "fields": ["field1", "field2"],
                "limit": number,
                "order_by": "field_name desc/asc",
                "description": "What the user is asking for"
            }}
            
            Examples:
            - "do i have any items" -> {{"is_data_query": true, "doctype": "Item", "query_type": "count"}}
            - "show my customers" -> {{"is_data_query": true, "doctype": "Customer", "query_type": "list", "limit": 10}}
            - "what is my latest sale" -> {{"is_data_query": true, "doctype": "Sales Invoice", "query_type": "latest", "limit": 1, "order_by": "creation desc"}}
            - "total sales this month" -> {{"is_data_query": true, "doctype": "Sales Invoice", "query_type": "sum", "filters": {{"posting_date": "this_month"}}}}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a database query analyzer. Respond only with valid JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            import json
            try:
                return json.loads(ai_response)
            except:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return None
                
        except Exception as e:
            frappe.log_error(f"Query Analysis Error: {str(e)}")
            return None
    
    def execute_dynamic_query(self, query_analysis):
        """Execute the database query based on AI analysis"""
        try:
            doctype = query_analysis.get('doctype')
            query_type = query_analysis.get('query_type')
            filters = query_analysis.get('filters', {})
            fields = query_analysis.get('fields', ['name'])
            limit = query_analysis.get('limit', 10)
            order_by = query_analysis.get('order_by', 'creation desc')
            description = query_analysis.get('description', 'data')
            
            # Process special filters
            processed_filters = self.process_filters(filters)
            
            if query_type == 'count':
                count = frappe.db.count(doctype, filters=processed_filters)
                if count == 0:
                    response = f"You don't have any {doctype.lower()}s in the system."
                elif count == 1:
                    response = f"You have 1 {doctype.lower()} in the system."
                else:
                    response = f"You have {count} {doctype.lower()}s in the system."
                    
            elif query_type == 'list':
                data = frappe.db.get_list(doctype, 
                    filters=processed_filters,
                    fields=fields,
                    limit=limit,
                    order_by=order_by
                )
                
                if not data:
                    response = f"No {doctype.lower()}s found."
                else:
                    response = f"Your {doctype}s:\n\n"
                    for item in data:
                        response += f"• {item.get('name', 'N/A')}"
                        if len(fields) > 1:
                            details = []
                            for field in fields[1:]:
                                if item.get(field):
                                    details.append(f"{field}: {item.get(field)}")
                            if details:
                                response += f" ({', '.join(details)})"
                        response += "\n"
                        
            elif query_type == 'latest':
                data = frappe.db.get_list(doctype,
                    filters=processed_filters,
                    fields=['*'],
                    limit=1,
                    order_by=order_by
                )
                
                if not data:
                    response = f"No {doctype.lower()}s found."
                else:
                    item = data[0]
                    response = f"Your latest {doctype.lower()}:\n\n"
                    response += f"• ID: {item.get('name')}\n"
                    
                    # Add relevant fields based on doctype
                    if doctype == 'Sales Invoice':
                        response += f"• Customer: {item.get('customer', 'N/A')}\n"
                        response += f"• Date: {item.get('posting_date', 'N/A')}\n"
                        response += f"• Amount: ₹{item.get('grand_total', 0):,.2f}\n"
                        response += f"• Status: {item.get('status', 'N/A')}\n"
                    elif doctype == 'Customer':
                        response += f"• Name: {item.get('customer_name', 'N/A')}\n"
                        response += f"• Group: {item.get('customer_group', 'N/A')}\n"
                    elif doctype == 'Item':
                        response += f"• Name: {item.get('item_name', 'N/A')}\n"
                        response += f"• Group: {item.get('item_group', 'N/A')}\n"
                    
            elif query_type == 'sum':
                if doctype == 'Sales Invoice':
                    result = frappe.db.sql("""
                        SELECT COUNT(*) as count, SUM(grand_total) as total
                        FROM `tabSales Invoice`
                        WHERE docstatus = 1
                    """, as_dict=True)
                    
                    if result and result[0]:
                        count = result[0].count or 0
                        total = result[0].total or 0
                        response = f"Sales Summary:\n• {count} invoices\n• ₹{total:,.2f} total revenue"
                    else:
                        response = "No sales data found."
                else:
                    response = f"Sum operation not supported for {doctype}."
            elif query_type == 'specific':
                # Handle specific queries - for now, treat as list with filters
                data = frappe.db.get_list(doctype, 
                    filters=processed_filters,
                    fields=fields,
                    limit=limit,
                    order_by=order_by
                )
                
                if not data:
                    response = f"No {doctype.lower()}s found matching your criteria."
                else:
                    response = f"Found {len(data)} {doctype.lower()}(s):\n\n"
                    for item in data:
                        response += f"• {item.get('name', 'N/A')}"
                        if len(fields) > 1:
                            details = []
                            for field in fields[1:]:
                                if item.get(field):
                                    details.append(f"{field}: {item.get(field)}")
                            if details:
                                response += f" ({', '.join(details)})"
                        response += "\n"
            else:
                response = f"Query type '{query_type}' not supported yet."
            
            return {
                "response": response,
                "actions": [],
                "success": True
            }
            
        except Exception as e:
            return {
                "response": f"Error executing query: {str(e)}",
                "actions": [],
                "success": False
            }
    
    def process_filters(self, filters):
        """Process special filter values like 'this_month', 'today', etc."""
        processed = {}
        
        for field, value in filters.items():
            if value == 'today':
                processed[field] = nowdate()
            elif value == 'this_month':
                from frappe.utils import get_first_day, get_last_day
                today = getdate()
                processed[field] = ['between', [get_first_day(today), get_last_day(today)]]
            else:
                processed[field] = value
                
        return processed
    

        
    def process_query(self, user_message):
        """Process user query and return AI response"""
        try:
            # Check for direct item creation pattern first (SUZ-008, AI Testing item, no description, 600, 700)
            item_creation_pattern = r'([A-Z0-9-]+),\s*([^,]+),\s*([^,]*),\s*(\d+),\s*(\d+)'
            # Also check for create item commands
            create_item_pattern = r'create.*item.*([A-Z0-9-]+),\s*([^,]+),\s*([^,]*),\s*(\d+),\s*(\d+)'
            
            if re.search(item_creation_pattern, user_message) or re.search(create_item_pattern, user_message):
                # Directly create the item
                result = create_item_from_text(user_message)
                if result.get("success"):
                    return {
                        "response": result.get("message"),
                        "actions": [],
                        "success": True
                    }
                else:
                    return {
                        "response": f"Error creating item: {result.get('message')}",
                        "actions": [],
                        "success": False
                    }
            
            # Check if this is a data query
            data_response = self.handle_data_queries(user_message)
            if data_response:
                return data_response
            
            # Prepare the prompt with context
            context = self.get_context_prompt()
            
            # Enhanced prompt for better ERP understanding
            system_prompt = f"""
            {context}
            
            Available OMEX DocTypes you can work with:
            - Sales Order, Sales Invoice, Customer, Item
            - Purchase Order, Purchase Invoice, Supplier
            - Task, Project, Timesheet
            - Lead, Opportunity, Quotation
            - Stock Entry, Material Request
            - Employee, Attendance, Leave Application
            - Journal Entry, Payment Entry
            
            I can directly query the database for you. When users ask about data (items, customers, sales, etc.), 
            I will check the actual database and provide real information.
            When they want to create something, explain the process and ask for confirmation.
            Be helpful and specific to OMEX/OMEX ERP functionality.
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Check if the response contains actionable items
            actions = self.extract_actions(ai_response, user_message)
            
            return {
                "response": ai_response,
                "actions": actions,
                "success": True
            }
            
        except Exception as e:
            frappe.log_error(f"AI Assistant Error: {str(e)}")
            return {
                "response": "I'm sorry, I encountered an error processing your request. Please try again.",
                "actions": [],
                "success": False,
                "error": str(e)
            }
    
    def extract_actions(self, ai_response, user_message):
        """Extract actionable items from AI response"""
        actions = []
        
        # Look for common action patterns
        action_patterns = {
            "create_task": r"create.*task|new.*task|add.*task",
            "create_event": r"schedule.*meeting|create.*event|calendar.*event",
            "create_todo": r"create.*todo|add.*todo|reminder",
            "create_item": r"create.*item|new.*item|add.*item|create.*product",
            "create_customer": r"create.*customer|new.*customer|add.*customer",
            "create_supplier": r"create.*supplier|new.*supplier|add.*supplier",
            "send_email": r"send.*email|email.*reminder",
            "generate_report": r"generate.*report|create.*report|show.*report"
        }
        
        combined_text = (ai_response + " " + user_message).lower()
        
        # Check for item creation with comma-separated values (SUZ-008, AI Testing item, etc.)
        item_creation_pattern = r'([A-Z0-9-]+),\s*([^,]+),\s*([^,]*),\s*(\d+),\s*(\d+)'
        if re.search(item_creation_pattern, user_message):
            actions.append({
                "type": "create_item_from_text",
                "description": "Create the item with the details you provided?",
                "requires_confirmation": True,
                "data": user_message
            })
        
        for action_type, pattern in action_patterns.items():
            if re.search(pattern, combined_text):
                actions.append({
                    "type": action_type,
                    "description": f"Would you like me to {action_type.replace('_', ' ')}?",
                    "requires_confirmation": True
                })
        
        return actions
    
    def execute_action(self, action_type, parameters):
        """Execute confirmed actions"""
        try:
            if action_type == "create_task":
                return self.create_task(parameters)
            elif action_type == "create_event":
                return self.create_event(parameters)
            elif action_type == "create_todo":
                return self.create_todo(parameters)
            elif action_type == "create_item":
                return self.create_item(parameters)
            elif action_type == "create_item_from_text":
                # Handle item creation from text format
                item_data = parameters.get("data", "")
                return create_item_from_text(item_data)
            elif action_type == "create_customer":
                return self.create_customer(parameters)
            elif action_type == "create_supplier":
                return self.create_supplier(parameters)
            elif action_type == "send_email":
                return self.send_email(parameters)
            elif action_type == "generate_report":
                return self.generate_report(parameters)
            else:
                return {"success": False, "message": "Unknown action type"}
                
        except Exception as e:
            frappe.log_error(f"Action Execution Error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def create_task(self, parameters):
        """Create a new task"""
        task = frappe.get_doc({
            "doctype": "Task",
            "subject": parameters.get("subject", "AI Generated Task"),
            "description": parameters.get("description", ""),
            "priority": parameters.get("priority", "Medium"),
            "status": "Open"
        })
        task.insert()
        return {"success": True, "message": f"Task '{task.subject}' created successfully", "doc_name": task.name}
    
    def create_event(self, parameters):
        """Create a calendar event"""
        event = frappe.get_doc({
            "doctype": "Event",
            "subject": parameters.get("subject", "AI Generated Event"),
            "description": parameters.get("description", ""),
            "starts_on": parameters.get("starts_on", nowdate()),
            "event_type": "Private"
        })
        event.insert()
        return {"success": True, "message": f"Event '{event.subject}' created successfully", "doc_name": event.name}
    
    def create_todo(self, parameters):
        """Create a todo item"""
        todo = frappe.get_doc({
            "doctype": "ToDo",
            "description": parameters.get("description", "AI Generated Todo"),
            "priority": parameters.get("priority", "Medium"),
            "status": "Open"
        })
        todo.insert()
        return {"success": True, "message": f"Todo created successfully", "doc_name": todo.name}
    
    def create_item(self, parameters):
        """Create a new item"""
        try:
            item_code = parameters.get("item_code")
            item_name = parameters.get("item_name") or item_code
            
            # Check if item already exists
            if frappe.db.exists("Item", item_code):
                return {"success": False, "message": f"Item with code '{item_code}' already exists"}
            
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": item_code,
                "item_name": item_name,
                "description": parameters.get("description", ""),
                "item_group": parameters.get("item_group", "All Item Groups"),
                "stock_uom": parameters.get("stock_uom", "Nos"),
                "is_sales_item": 1,
                "is_purchase_item": 1,
                "is_stock_item": 1,
                "include_item_in_manufacturing": 0,
                "opening_stock": 0,
                "valuation_rate": parameters.get("valuation_rate", 0),
                "standard_rate": parameters.get("standard_rate", 0)
            })
            
            # Add item pricing if provided
            if parameters.get("selling_price"):
                item.append("item_defaults", {
                    "company": frappe.defaults.get_user_default("Company"),
                    "default_price_list": "Standard Selling",
                    "price_list_rate": parameters.get("selling_price")
                })
            
            if parameters.get("buying_price"):
                item.append("item_defaults", {
                    "company": frappe.defaults.get_user_default("Company"), 
                    "default_price_list": "Standard Buying",
                    "price_list_rate": parameters.get("buying_price")
                })
            
            item.insert()
            
            # Create item prices if specified
            if parameters.get("selling_price"):
                self.create_item_price(item_code, "Standard Selling", parameters.get("selling_price"))
            
            if parameters.get("buying_price"):
                self.create_item_price(item_code, "Standard Buying", parameters.get("buying_price"))
            
            return {
                "success": True, 
                "message": f"Item '{item_code}' created successfully",
                "doc_name": item.name,
                "item_code": item_code,
                "item_name": item_name
            }
            
        except Exception as e:
            frappe.log_error(f"Item Creation Error: {str(e)}")
            return {"success": False, "message": f"Error creating item: {str(e)}"}
    
    def create_item_price(self, item_code, price_list, rate):
        """Create item price for a specific price list"""
        try:
            if not frappe.db.exists("Item Price", {"item_code": item_code, "price_list": price_list}):
                item_price = frappe.get_doc({
                    "doctype": "Item Price",
                    "item_code": item_code,
                    "price_list": price_list,
                    "price_list_rate": rate
                })
                item_price.insert()
        except Exception as e:
            frappe.log_error(f"Item Price Creation Error: {str(e)}")
    
    def create_customer(self, parameters):
        """Create a new customer"""
        try:
            customer_name = parameters.get("customer_name")
            
            if frappe.db.exists("Customer", customer_name):
                return {"success": False, "message": f"Customer '{customer_name}' already exists"}
            
            customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": customer_name,
                "customer_type": parameters.get("customer_type", "Individual"),
                "customer_group": parameters.get("customer_group", "Individual"),
                "territory": parameters.get("territory", "All Territories")
            })
            customer.insert()
            
            return {
                "success": True,
                "message": f"Customer '{customer_name}' created successfully",
                "doc_name": customer.name
            }
            
        except Exception as e:
            frappe.log_error(f"Customer Creation Error: {str(e)}")
            return {"success": False, "message": f"Error creating customer: {str(e)}"}
    
    def create_supplier(self, parameters):
        """Create a new supplier"""
        try:
            supplier_name = parameters.get("supplier_name")
            
            if frappe.db.exists("Supplier", supplier_name):
                return {"success": False, "message": f"Supplier '{supplier_name}' already exists"}
            
            supplier = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": supplier_name,
                "supplier_type": parameters.get("supplier_type", "Individual"),
                "supplier_group": parameters.get("supplier_group", "All Supplier Groups")
            })
            supplier.insert()
            
            return {
                "success": True,
                "message": f"Supplier '{supplier_name}' created successfully", 
                "doc_name": supplier.name
            }
            
        except Exception as e:
            frappe.log_error(f"Supplier Creation Error: {str(e)}")
            return {"success": False, "message": f"Error creating supplier: {str(e)}"}
    
    def send_email(self, parameters):
        """Send email (placeholder for now)"""
        return {"success": True, "message": "Email functionality will be implemented based on your requirements"}
    
    def generate_report(self, parameters):
        """Generate reports (placeholder for now)"""
        return {"success": True, "message": "Report generation functionality will be implemented based on your requirements"}


@frappe.whitelist()
def chat_with_ai(message, chat_id=None):
    """API endpoint for chat functionality"""
    if not message:
        return {"error": "Message is required"}
    
    # Generate a new chat_id if not provided
    if not chat_id:
        import uuid
        chat_id = str(uuid.uuid4())
    
    assistant = AIAssistant()
    response = assistant.process_query(message)
    
    # Log the conversation with chat_id
    frappe.get_doc({
        "doctype": "AI Chat Log",
        "user": frappe.session.user,
        "chat_id": chat_id,
        "message": message,
        "response": response.get("response", ""),
        "timestamp": datetime.now()
    }).insert(ignore_permissions=True)
    
    # Return response with chat_id
    response["chat_id"] = chat_id
    return response


@frappe.whitelist()
def execute_ai_action(action_type, parameters):
    """API endpoint for executing AI suggested actions"""
    assistant = AIAssistant()
    result = assistant.execute_action(action_type, json.loads(parameters))
    return result


@frappe.whitelist()
def get_chat_history(limit=20, offset=0, chat_id=None):
    """Get recent chat history for the current user"""
    filters = {"user": frappe.session.user}
    
    # Filter by specific chat session if provided
    if chat_id:
        filters["chat_id"] = chat_id
    
    return frappe.get_all(
        "AI Chat Log",
        filters=filters,
        fields=["message", "response", "timestamp", "chat_id"],
        order_by="timestamp desc",
        limit=limit,
        start=offset
    )

@frappe.whitelist()
def create_item_from_text(item_data):
    """Create an item from text input like 'SUZ-008, AI Testing item, no description, 600, 700'"""
    try:
        # Parse the input - expect format: code, name, description, selling_price, buying_price
        parts = [part.strip() for part in item_data.split(',')]
        
        if len(parts) < 2:
            return {"success": False, "message": "Please provide at least item code and name. Format: 'CODE, Name, Description, Selling Price, Buying Price'"}
        
        parameters = {
            "item_code": parts[0],
            "item_name": parts[1] if len(parts) > 1 else parts[0],
            "description": parts[2] if len(parts) > 2 and parts[2].lower() not in ['no description', 'none', ''] else "",
            "selling_price": float(parts[3]) if len(parts) > 3 and parts[3].replace('.', '').isdigit() else 0,
            "buying_price": float(parts[4]) if len(parts) > 4 and parts[4].replace('.', '').isdigit() else 0
        }
        
        assistant = AIAssistant()
        result = assistant.create_item(parameters)
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Item Creation from Text Error: {str(e)}")
        return {"success": False, "message": f"Error creating item: {str(e)}"}

@frappe.whitelist()
def get_recent_chat_session():
    """Get the most recent chat session ID for the current user"""
    recent_chat = frappe.get_all(
        "AI Chat Log",
        filters={"user": frappe.session.user},
        fields=["chat_id"],
        order_by="timestamp desc",
        limit=1
    )
    
    if recent_chat:
        return {"chat_id": recent_chat[0].chat_id}
    else:
        return {"chat_id": None} 