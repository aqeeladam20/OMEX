"""
AI Help System for Frappe/ERPNext
Provides local AI-powered help instead of external documentation links
"""

import frappe
import json
import os
from frappe import _

# This will store our local documentation data
DOCUMENTATION_CACHE = {}

@frappe.whitelist()
def get_help(topic, context=None, module='general'):
	"""
	Get AI help for a specific topic
	"""
	try:
		# Load documentation if not already cached
		if not DOCUMENTATION_CACHE:
			load_documentation()
		
		# Generate help content based on topic and context
		help_content = generate_help_content(topic, context, module)
		
		return help_content
	except Exception as e:
		frappe.log_error(f"AI Help Error: {str(e)}")
		return _("I apologize, but I'm having trouble accessing the help information right now. Please try again later.")

@frappe.whitelist()
def answer_question(question, topic=None, context=None, module='general'):
	"""
	Answer a specific user question about the system
	"""
	try:
		# Load documentation if not already cached
		if not DOCUMENTATION_CACHE:
			load_documentation()
		
		# Generate answer based on question and context
		answer = generate_answer(question, topic, context, module)
		
		return answer
	except Exception as e:
		frappe.log_error(f"AI Help Answer Error: {str(e)}")
		return _("I apologize, but I couldn't process your question. Please try rephrasing it.")

def load_documentation():
	"""
	Load local documentation data into cache
	"""
	global DOCUMENTATION_CACHE
	
	# Define documentation structure
	DOCUMENTATION_CACHE = {
		"User Management": {
			"description": "User management involves creating, modifying, and managing user accounts in the system.",
			"topics": {
				"Adding Users": "To add a new user, go to Setup > Users and Permissions > User. Click 'New' and fill in the required details including email, first name, and roles.",
				"User Roles": "Roles define what a user can access. Common roles include System Manager, Sales User, Purchase User, etc.",
				"User Permissions": "User permissions restrict access to specific documents or data based on user-defined rules."
			}
		},
		"Customer Management": {
			"description": "Customer management helps you track and manage your customer relationships and transactions.",
			"topics": {
				"Creating Customers": "Go to CRM > Customer to create a new customer. Fill in customer details, contact information, and billing preferences.",
				"Customer Groups": "Organize customers into groups for better management and reporting.",
				"Credit Limits": "Set credit limits to control customer outstanding amounts and prevent over-selling."
			}
		},
		"Sales Order": {
			"description": "Sales Orders are confirmations of sales from customers and serve as the basis for delivery and invoicing.",
			"topics": {
				"Creating Sales Orders": "Go to Selling > Sales Order. Select customer, add items, set quantities and rates.",
				"Sales Order Status": "Track order status from Draft to Submitted to Delivered to Closed.",
				"Recurring Orders": "Set up automatic recurring sales orders for regular customers."
			}
		},
		"Purchase Order": {
			"description": "Purchase Orders are sent to suppliers to request goods or services.",
			"topics": {
				"Creating Purchase Orders": "Go to Buying > Purchase Order. Select supplier, add items with quantities and rates.",
				"Purchase Approval": "Set up approval workflows for purchase orders above certain amounts.",
				"Receiving Goods": "Create Purchase Receipts against Purchase Orders when goods are received."
			}
		},
		"Item Management": {
			"description": "Item management involves creating and maintaining your product/service catalog.",
			"topics": {
				"Creating Items": "Go to Stock > Item to create new items. Set item code, name, and basic details.",
				"Item Variants": "Create variants for items with different attributes like size, color, etc.",
				"Item Pricing": "Set up item prices for different price lists and customer groups.",
				"Stock Management": "Track item stock levels, set reorder levels, and manage warehouses."
			}
		},
		"Sales Invoice": {
			"description": "Sales Invoices are bills sent to customers for goods delivered or services provided.",
			"topics": {
				"Creating Invoices": "Create invoices from Sales Orders or directly. Add items, taxes, and payment terms.",
				"Payment Collection": "Track payments against invoices and manage outstanding amounts.",
				"Invoice Templates": "Customize invoice formats and print templates."
			}
		},
		"Data Import": {
			"description": "Data Import tool helps you bulk import data from spreadsheets into the system.",
			"topics": {
				"Import Process": "Go to Setup > Data Import. Download template, fill data, and upload the file.",
				"Data Validation": "The system validates data before import and shows errors if any.",
				"Update Records": "Use import to update existing records by including the ID column."
			}
		},
		"System Settings": {
			"description": "System Settings control global system behavior and preferences.",
			"topics": {
				"Basic Settings": "Configure date format, time zone, currency, and language preferences.",
				"Email Settings": "Set up outgoing email server and email templates.",
				"Backup Settings": "Configure automatic database backups and retention policies."
			}
		},
		"Role Based Permissions": {
			"description": "Role-based permissions control what users can see and do in the system.",
			"topics": {
				"Creating Roles": "Define custom roles with specific permissions for different user types.",
				"Permission Levels": "Set read, write, create, delete, and submit permissions for each role.",
				"Document Permissions": "Control access to specific document types based on roles."
			}
		}
	}

def generate_help_content(topic, context, module):
	"""
	Generate help content for a specific topic
	"""
	if topic in DOCUMENTATION_CACHE:
		doc = DOCUMENTATION_CACHE[topic]
		
		content = f"<h4>{topic}</h4>"
		content += f"<p>{doc['description']}</p>"
		
		if 'topics' in doc:
			content += "<h5>Key Topics:</h5><ul>"
			for subtopic, description in doc['topics'].items():
				content += f"<li><strong>{subtopic}:</strong> {description}</li>"
			content += "</ul>"
		
		content += f"<p><em>Need more specific help? Click 'Ask Follow-up Question' to get detailed assistance.</em></p>"
		
		return content
	else:
		# Generic help based on topic name
		return generate_generic_help(topic, context, module)

def generate_generic_help(topic, context, module):
	"""
	Generate generic help when specific documentation is not available
	"""
	content = f"<h4>Help: {topic}</h4>"
	
	if context:
		content += f"<p>{context}</p>"
	
	# Add module-specific guidance
	if module == 'Selling':
		content += "<p>This is part of the Sales module. Common tasks include managing customers, creating quotations and sales orders, and generating invoices.</p>"
	elif module == 'Buying':
		content += "<p>This is part of the Purchase module. Common tasks include managing suppliers, creating purchase orders, and receiving goods.</p>"
	elif module == 'Stock':
		content += "<p>This is part of the Inventory module. Common tasks include managing items, tracking stock levels, and handling stock movements.</p>"
	elif module == 'Accounts':
		content += "<p>This is part of the Accounting module. Common tasks include managing invoices, payments, and financial reports.</p>"
	else:
		content += "<p>For detailed guidance on this topic, please use the 'Ask Follow-up Question' feature to get specific help.</p>"
	
	return content

def generate_answer(question, topic, context, module):
	"""
	Generate an answer to a specific user question
	"""
	question_lower = question.lower()
	
	# Simple keyword-based responses (can be enhanced with actual AI/ML)
	if any(word in question_lower for word in ['create', 'add', 'new']):
		if 'user' in question_lower:
			return "To create a new user, go to Setup > Users and Permissions > User. Click 'New' and fill in the email, name, and assign appropriate roles."
		elif 'customer' in question_lower:
			return "To create a new customer, go to CRM > Customer. Click 'New' and fill in the customer name, contact details, and other relevant information."
		elif 'item' in question_lower:
			return "To create a new item, go to Stock > Item. Click 'New' and fill in the item code, name, and configure the item settings."
		elif 'invoice' in question_lower:
			return "To create an invoice, go to Accounts > Sales Invoice. Select the customer, add items, and save the invoice."
	
	elif any(word in question_lower for word in ['how', 'what', 'where']):
		if 'permission' in question_lower:
			return "Permissions are managed through Setup > Users and Permissions > Role Permissions Manager. You can set read, write, create, and delete permissions for each role."
		elif 'report' in question_lower:
			return "Reports can be found in each module. Go to the relevant module and look for the 'Reports' section, or use the global search to find specific reports."
		elif 'backup' in question_lower:
			return "Backups can be configured in Setup > System Settings. You can set up automatic backups and download manual backups from Setup > Download Backups."
	
	elif 'error' in question_lower or 'problem' in question_lower:
		return "If you're experiencing an error, please check the Error Log in Setup > System Console > Error Log. This will show detailed error information that can help diagnose the issue."
	
	# Default response
	return f"I understand you're asking about '{question}'. While I don't have a specific answer for this question, I recommend checking the relevant module documentation or contacting your system administrator for detailed guidance."

def get_module_help_topics(module):
	"""
	Get help topics specific to a module
	"""
	module_topics = {
		'Selling': ['Customer Management', 'Sales Order', 'Sales Invoice', 'Quotation'],
		'Buying': ['Supplier Management', 'Purchase Order', 'Purchase Invoice'],
		'Stock': ['Item Management', 'Stock Entry', 'Warehouse Management'],
		'Accounts': ['Sales Invoice', 'Purchase Invoice', 'Payment Entry', 'Journal Entry'],
		'Setup': ['User Management', 'System Settings', 'Role Based Permissions', 'Data Import']
	}
	
	return module_topics.get(module, [])

@frappe.whitelist()
def get_module_topics(module):
	"""
	Get available help topics for a specific module
	"""
	return get_module_help_topics(module) 