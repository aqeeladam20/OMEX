frappe.provide("frappe.help.help_links");

// Local AI Help System - replaces external documentation links
function showAIHelp(topic, context = null) {
	// This will trigger the local AI help system
	frappe.call({
		method: "frappe.utils.ai_help.get_help",
		args: {
			topic: topic,
			context: context,
			module: frappe.get_route()[0] || 'general'
		},
		callback: function(r) {
			if (r.message) {
				// Show AI help in a modal
				let d = new frappe.ui.Dialog({
					title: __('AI Help: {0}', [topic]),
					fields: [
						{
							fieldtype: 'HTML',
							fieldname: 'help_content',
							options: `<div class="ai-help-content">${r.message}</div>`
						}
					],
					primary_action_label: __('Ask Follow-up Question'),
					primary_action: function() {
						// Allow users to ask follow-up questions
						showAIChat(topic, context);
					}
				});
				d.show();
			}
		}
	});
}

function showAIChat(initialTopic, context = null) {
	// Interactive AI chat for follow-up questions
	let d = new frappe.ui.Dialog({
		title: __('AI Help Chat'),
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'chat_area',
				options: '<div id="ai-chat-area" style="height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 10px;"></div>'
			},
			{
				fieldtype: 'Data',
				fieldname: 'user_question',
				label: __('Ask a question'),
				placeholder: __('Type your question here...')
			}
		],
		primary_action_label: __('Send'),
		primary_action: function() {
			let question = d.get_value('user_question');
			if (question) {
				sendAIQuestion(question, initialTopic, context, d);
				d.set_value('user_question', '');
			}
		}
	});
	d.show();
	
	// Add initial context
	if (initialTopic) {
		$('#ai-chat-area').append(`<div class="ai-message"><strong>AI:</strong> I can help you with ${initialTopic}. What would you like to know?</div>`);
	}
}

function sendAIQuestion(question, topic, context, dialog) {
	// Add user message to chat
	$('#ai-chat-area').append(`<div class="user-message" style="text-align: right; margin: 5px 0;"><strong>You:</strong> ${question}</div>`);
	
	// Show typing indicator
	$('#ai-chat-area').append('<div id="typing-indicator" style="color: #888;"><em>AI is typing...</em></div>');
	$('#ai-chat-area').scrollTop($('#ai-chat-area')[0].scrollHeight);
	
	frappe.call({
		method: "frappe.utils.ai_help.answer_question",
		args: {
			question: question,
			topic: topic,
			context: context,
			module: frappe.get_route()[0] || 'general'
		},
		callback: function(r) {
			$('#typing-indicator').remove();
			if (r.message) {
				$('#ai-chat-area').append(`<div class="ai-message" style="margin: 5px 0;"><strong>AI:</strong> ${r.message}</div>`);
			} else {
				$('#ai-chat-area').append('<div class="ai-message" style="margin: 5px 0;"><strong>AI:</strong> I apologize, but I couldn\'t find information about that. Please try rephrasing your question.</div>');
			}
			$('#ai-chat-area').scrollTop($('#ai-chat-area')[0].scrollHeight);
		}
	});
}

// Replace all external documentation links with AI help calls
frappe.help.help_links["Form/Rename Tool"] = [
	{
		label: "Bulk Rename Help",
		action: () => showAIHelp("Bulk Rename", "How to rename multiple documents at once")
	},
];

//Setup
frappe.help.help_links["List/User"] = [
	{
		label: "User Management Help",
		action: () => showAIHelp("User Management", "Adding and managing users in the system")
	},
];

frappe.help.help_links["permission-manager"] = [
	{
		label: "Permissions Help",
		action: () => showAIHelp("Role Based Permissions", "Understanding and managing user permissions and roles")
	},
];

frappe.help.help_links["Form/System Settings"] = [
	{
		label: "System Settings Help",
		action: () => showAIHelp("System Settings", "Configuring system-wide settings")
	},
];

frappe.help.help_links["Form/Data Import"] = [
	{
		label: "Data Import Help",
		action: () => showAIHelp("Data Import", "Importing and exporting data")
	},
];

frappe.help.help_links["List/Data Import"] = [
	{
		label: "Data Import Help",
		action: () => showAIHelp("Data Import", "Importing and exporting data")
	},
];

frappe.help.help_links["module_setup"] = [
	{
		label: "Role Permissions Manager Help",
		action: () => showAIHelp("Role Based Permissions", "Understanding role-based permissions")
	},
];

frappe.help.help_links["Form/Document Naming Settings"] = [
	{
		label: "Naming Series Help",
		action: () => showAIHelp("Document Naming", "Setting up document naming series")
	},
];

frappe.help.help_links["Form/Global Defaults"] = [
	{
		label: "Global Settings Help",
		action: () => showAIHelp("Global Defaults", "Configuring global default settings")
	},
];

frappe.help.help_links["List/Print Heading"] = [
	{
		label: "Print Heading Help",
		action: () => showAIHelp("Print Heading", "Managing print headings")
	},
];

frappe.help.help_links["Form/Print Heading"] = [
	{
		label: "Print Heading Help",
		action: () => showAIHelp("Print Heading", "Managing print headings")
	},
];

frappe.help.help_links["List/Letter Head"] = [
	{
		label: "Letter Head Help",
		action: () => showAIHelp("Letter Head", "Setting up letter heads")
	},
];

frappe.help.help_links["List/Address Template"] = [
	{
		label: "Address Template Help",
		action: () => showAIHelp("Address Template", "Managing address templates")
	},
];

frappe.help.help_links["List/Terms and Conditions"] = [
	{
		label: "Terms and Conditions Help",
		action: () => showAIHelp("Terms and Conditions", "Managing terms and conditions")
	},
];

frappe.help.help_links["List/Cheque Print Template"] = [
	{
		label: "Cheque Print Template Help",
		action: () => showAIHelp("Cheque Print Template", "Setting up cheque print templates")
	},
];

frappe.help.help_links["List/Email Account"] = [
	{
		label: "Email Account Help",
		action: () => showAIHelp("Email Account", "Configuring email accounts")
	},
];

frappe.help.help_links["List/Notification"] = [
	{
		label: "Notification Help",
		action: () => showAIHelp("Notifications", "Setting up notifications")
	},
];

frappe.help.help_links["Form/Notification"] = [
	{
		label: "Notification Help",
		action: () => showAIHelp("Notifications", "Setting up notifications")
	},
];

frappe.help.help_links["Form/Email Digest"] = [
	{
		label: "Email Digest Help",
		action: () => showAIHelp("Email Digest", "Configuring email digests")
	},
];

frappe.help.help_links["List/Auto Email Report"] = [
	{
		label: "Auto Email Reports Help",
		action: () => showAIHelp("Auto Email Reports", "Setting up automatic email reports")
	},
];

frappe.help.help_links["Form/Print Settings"] = [
	{
		label: "Print Settings Help",
		action: () => showAIHelp("Print Settings", "Configuring print settings")
	},
];

frappe.help.help_links["print-format-builder"] = [
	{
		label: "Print Format Builder Help",
		action: () => showAIHelp("Print Format Builder", "Building custom print formats")
	},
];

//setup-integrations
frappe.help.help_links["Form/PayPal Settings"] = [
	{
		label: "PayPal Settings Help",
		action: () => showAIHelp("PayPal Integration", "Setting up PayPal integration")
	},
];

frappe.help.help_links["Form/Razorpay Settings"] = [
	{
		label: "Razorpay Settings Help",
		action: () => showAIHelp("Razorpay Integration", "Setting up Razorpay integration")
	},
];

frappe.help.help_links["Form/Dropbox Settings"] = [
	{
		label: "Dropbox Settings Help",
		action: () => showAIHelp("Dropbox Backup", "Setting up Dropbox backup")
	},
];

frappe.help.help_links["Form/LDAP Settings"] = [
	{
		label: "LDAP Settings Help",
		action: () => showAIHelp("LDAP Integration", "Setting up LDAP integration")
	},
];

frappe.help.help_links["Form/Stripe Settings"] = [
	{
		label: "Stripe Settings Help",
		action: () => showAIHelp("Stripe Integration", "Setting up Stripe integration")
	},
];

//Sales
frappe.help.help_links["Form/Quotation"] = [
	{
		label: "Quotation Help",
		action: () => showAIHelp("Quotation", "Creating and managing quotations")
	},
];

frappe.help.help_links["List/Customer"] = [
	{
		label: "Customer Help",
		action: () => showAIHelp("Customer Management", "Managing customers and credit limits")
	},
];

frappe.help.help_links["Form/Customer"] = [
	{
		label: "Customer Help",
		action: () => showAIHelp("Customer Management", "Managing customers and credit limits")
	},
];

frappe.help.help_links["List/Sales Taxes and Charges Template"] = [
	{
		label: "Setting Up Taxes Help",
		action: () => showAIHelp("Tax Setup", "Setting up taxes and charges")
	},
];

frappe.help.help_links["Form/Sales Taxes and Charges Template"] = [
	{
		label: "Setting Up Taxes Help",
		action: () => showAIHelp("Tax Setup", "Setting up taxes and charges")
	},
];

frappe.help.help_links["List/Sales Order"] = [
	{
		label: "Sales Order Help",
		action: () => showAIHelp("Sales Order", "Creating and managing sales orders")
	},
];

frappe.help.help_links["Form/Sales Order"] = [
	{
		label: "Sales Order Help",
		action: () => showAIHelp("Sales Order", "Creating and managing sales orders, recurring orders, discounts, and margins")
	},
];

frappe.help.help_links["Form/Product Bundle"] = [
	{
		label: "Product Bundle Help",
		action: () => showAIHelp("Product Bundle", "Creating and managing product bundles")
	},
];

frappe.help.help_links["Form/Selling Settings"] = [
	{
		label: "Selling Settings Help",
		action: () => showAIHelp("Selling Settings", "Configuring selling settings")
	},
];

//Buying
frappe.help.help_links["List/Supplier"] = [
	{
		label: "Supplier Help",
		action: () => showAIHelp("Supplier Management", "Managing suppliers and vendor relationships")
	},
];

frappe.help.help_links["Form/Supplier"] = [
	{
		label: "Supplier Help",
		action: () => showAIHelp("Supplier Management", "Managing suppliers and vendor relationships")
	},
];

frappe.help.help_links["Form/Request for Quotation"] = [
	{
		label: "Request for Quotation Help",
		action: () => showAIHelp("Request for Quotation", "Creating and managing RFQs")
	},
];

frappe.help.help_links["Form/Supplier Quotation"] = [
	{
		label: "Supplier Quotation Help",
		action: () => showAIHelp("Supplier Quotation", "Managing supplier quotations")
	},
];

frappe.help.help_links["Form/Buying Settings"] = [
	{
		label: "Buying Settings Help",
		action: () => showAIHelp("Buying Settings", "Configuring buying settings")
	},
];

frappe.help.help_links["List/Purchase Order"] = [
	{
		label: "Purchase Order Help",
		action: () => showAIHelp("Purchase Order", "Creating and managing purchase orders")
	},
];

frappe.help.help_links["Form/Purchase Order"] = [
	{
		label: "Purchase Order Help",
		action: () => showAIHelp("Purchase Order", "Creating and managing purchase orders, UoM, supplier codes, and subcontracting")
	},
];

frappe.help.help_links["List/Purchase Taxes and Charges Template"] = [
	{
		label: "Setting Up Taxes Help",
		action: () => showAIHelp("Tax Setup", "Setting up purchase taxes and charges")
	},
];

frappe.help.help_links["List/Price List"] = [
	{
		label: "Price List Help",
		action: () => showAIHelp("Price List", "Managing price lists")
	},
];

frappe.help.help_links["List/Authorization Rule"] = [
	{
		label: "Authorization Rule Help",
		action: () => showAIHelp("Authorization Rule", "Setting up authorization rules")
	},
];

frappe.help.help_links["Form/SMS Settings"] = [
	{
		label: "SMS Settings Help",
		action: () => showAIHelp("SMS Settings", "Configuring SMS settings")
	},
];

frappe.help.help_links["List/Stock Reconciliation"] = [
	{
		label: "Stock Reconciliation Help",
		action: () => showAIHelp("Stock Reconciliation", "Performing stock reconciliation")
	},
];

frappe.help.help_links["Tree/Territory"] = [
	{
		label: "Territory Help",
		action: () => showAIHelp("Territory", "Managing territories")
	},
];

frappe.help.help_links["List/Workflow"] = [
	{
		label: "Workflow Help",
		action: () => showAIHelp("Workflow", "Setting up workflows")
	},
];

frappe.help.help_links["List/Company"] = [
	{
		label: "Company Help",
		action: () => showAIHelp("Company Setup", "Setting up and managing companies")
	},
];

//Accounts
frappe.help.help_links["Tree/Account"] = [
	{
		label: "Chart of Accounts Help",
		action: () => showAIHelp("Chart of Accounts", "Managing chart of accounts and tree structures")
	},
];

frappe.help.help_links["Form/Sales Invoice"] = [
	{
		label: "Sales Invoice Help",
		action: () => showAIHelp("Sales Invoice", "Creating and managing sales invoices")
	},
];

frappe.help.help_links["List/Sales Invoice"] = [
	{
		label: "Sales Invoice Help",
		action: () => showAIHelp("Sales Invoice", "Creating sales invoices, opening balances, returns, and recurring invoices")
	},
];

frappe.help.help_links["point-of-sale"] = [
	{
		label: "Point of Sale Help",
		action: () => showAIHelp("Point of Sale", "Using point of sale features")
	},
];

frappe.help.help_links["List/POS Profile"] = [
	{
		label: "Point of Sale Profile Help",
		action: () => showAIHelp("POS Profile", "Setting up POS profiles")
	},
];

frappe.help.help_links["Form/POS Profile"] = [
	{
		label: "POS Profile Help",
		action: () => showAIHelp("POS Profile", "Setting up POS profiles")
	},
];

frappe.help.help_links["List/Purchase Invoice"] = [
	{
		label: "Purchase Invoice Help",
		action: () => showAIHelp("Purchase Invoice", "Creating and managing purchase invoices")
	},
];

frappe.help.help_links["List/Journal Entry"] = [
	{
		label: "Journal Entry Help",
		action: () => showAIHelp("Journal Entry", "Creating journal entries and advance payments")
	},
];

frappe.help.help_links["List/Payment Entry"] = [
	{
		label: "Payment Entry Help",
		action: () => showAIHelp("Payment Entry", "Managing payment entries")
	},
];

frappe.help.help_links["List/Payment Request"] = [
	{
		label: "Payment Request Help",
		action: () => showAIHelp("Payment Request", "Creating payment requests")
	},
];

frappe.help.help_links["List/Asset"] = [
	{
		label: "Managing Fixed Assets Help",
		action: () => showAIHelp("Asset Management", "Managing fixed assets")
	},
];

frappe.help.help_links["List/Asset Category"] = [
	{
		label: "Asset Category Help",
		action: () => showAIHelp("Asset Category", "Managing asset categories")
	},
];

frappe.help.help_links["Tree/Cost Center"] = [
	{
		label: "Budgeting Help",
		action: () => showAIHelp("Budgeting", "Managing budgets and cost centers")
	},
];

//Stock
frappe.help.help_links["List/Item"] = [
	{
		label: "Item Management Help",
		action: () => showAIHelp("Item Management", "Managing items, pricing, and inventory")
	},
];

frappe.help.help_links["Form/Item"] = [
	{
		label: "Item Management Help",
		action: () => showAIHelp("Item Management", "Managing items, pricing, and inventory")
	},
];

frappe.help.help_links["List/Purchase Receipt"] = [
	{
		label: "Purchase Receipt Help",
		action: () => showAIHelp("Purchase Receipt", "Managing purchase receipts and barcodes")
	},
];

frappe.help.help_links["List/Delivery Note"] = [
	{
		label: "Delivery Note Help",
		action: () => showAIHelp("Delivery Note", "Managing delivery notes, barcodes, and returns")
	},
];

frappe.help.help_links["Form/Delivery Note"] = [
	{
		label: "Delivery Note Help",
		action: () => showAIHelp("Delivery Note", "Managing delivery notes, barcodes, and returns")
	},
];

frappe.help.help_links["List/Installation Note"] = [
	{
		label: "Installation Note Help",
		action: () => showAIHelp("Installation Note", "Managing installation notes")
	},
];

frappe.help.help_links["List/Budget"] = [
	{
		label: "Budgeting Help",
		action: () => showAIHelp("Budgeting", "Managing budgets")
	},
];

frappe.help.help_links["List/Material Request"] = [
	{
		label: "Material Request Help",
		action: () => showAIHelp("Material Request", "Creating and managing material requests")
	},
];

frappe.help.help_links["Form/Material Request"] = [
	{
		label: "Material Request Help",
		action: () => showAIHelp("Material Request", "Creating and managing material requests")
	},
];

frappe.help.help_links["Form/Stock Entry"] = [
	{
		label: "Stock Entry Help",
		action: () => showAIHelp("Stock Entry", "Managing stock entries, types, repack, opening stock, and subcontracting")
	},
];

frappe.help.help_links["List/Stock Entry"] = [
	{
		label: "Stock Entry Help",
		action: () => showAIHelp("Stock Entry", "Managing stock entries")
	},
];

frappe.help.help_links["Tree/Warehouse"] = [
	{
		label: "Warehouse Help",
		action: () => showAIHelp("Warehouse", "Managing warehouses")
	},
];

frappe.help.help_links["List/Serial No"] = [
	{
		label: "Serial No Help",
		action: () => showAIHelp("Serial No", "Managing serial numbers")
	},
];

frappe.help.help_links["Form/Serial No"] = [
	{
		label: "Serial No Help",
		action: () => showAIHelp("Serial No", "Managing serial numbers")
	},
];

frappe.help.help_links["List/Batch"] = [
	{
		label: "Batch Help",
		action: () => showAIHelp("Batch", "Managing batches")
	},
];

frappe.help.help_links["Form/Batch"] = [
	{
		label: "Batch Help",
		action: () => showAIHelp("Batch", "Managing batches")
	},
];

frappe.help.help_links["Form/Packing Slip"] = [
	{
		label: "Packing Slip Help",
		action: () => showAIHelp("Packing Slip", "Managing packing slips")
	},
];

frappe.help.help_links["Form/Quality Inspection"] = [
	{
		label: "Quality Inspection Help",
		action: () => showAIHelp("Quality Inspection", "Managing quality inspections")
	},
];

frappe.help.help_links["Form/Landed Cost Voucher"] = [
	{
		label: "Landed Cost Voucher Help",
		action: () => showAIHelp("Landed Cost Voucher", "Managing landed cost vouchers")
	},
];

frappe.help.help_links["Tree/Item Group"] = [
	{
		label: "Item Group Help",
		action: () => showAIHelp("Item Group", "Managing item groups")
	},
];

frappe.help.help_links["Form/Item Attribute"] = [
	{
		label: "Item Attribute Help",
		action: () => showAIHelp("Item Attribute", "Managing item attributes")
	},
];

frappe.help.help_links["Form/UOM"] = [
	{
		label: "UOM Help",
		action: () => showAIHelp("UOM", "Managing units of measure and fractions")
	},
];

frappe.help.help_links["Form/Stock Reconciliation"] = [
	{
		label: "Opening Stock Entry Help",
		action: () => showAIHelp("Stock Reconciliation", "Managing opening stock and reconciliation")
	},
];

//CRM
frappe.help.help_links["Form/Lead"] = [
	{
		label: "Lead Management Help",
		action: () => showAIHelp("Lead Management", "Managing leads and prospects")
	},
];

frappe.help.help_links["Form/Opportunity"] = [
	{
		label: "Opportunity Help",
		action: () => showAIHelp("Opportunity Management", "Managing sales opportunities")
	},
];

frappe.help.help_links["Form/Address"] = [
	{
		label: "Address Help",
		action: () => showAIHelp("Address", "Managing addresses")
	},
];

frappe.help.help_links["Form/Contact"] = [
	{
		label: "Contact Help",
		action: () => showAIHelp("Contact", "Managing contacts")
	},
];

frappe.help.help_links["Form/Newsletter"] = [
	{
		label: "Newsletter Help",
		action: () => showAIHelp("Newsletter", "Managing newsletters")
	},
];

frappe.help.help_links["Form/Campaign"] = [
	{
		label: "Campaign Help",
		action: () => showAIHelp("Campaign", "Managing campaigns")
	},
];

frappe.help.help_links["Tree/Sales Person"] = [
	{
		label: "Sales Person Help",
		action: () => showAIHelp("Sales Person", "Managing sales persons")
	},
];

frappe.help.help_links["Form/Sales Person"] = [
	{
		label: "Sales Person Help",
		action: () => showAIHelp("Sales Person", "Managing sales person targets and transactions")
	},
];

//Manufacturing
frappe.help.help_links["Form/BOM"] = [
	{
		label: "Bill of Materials Help",
		action: () => showAIHelp("Bill of Materials", "Creating and managing BOMs")
	},
];

frappe.help.help_links["Form/Work Order"] = [
	{
		label: "Work Order Help",
		action: () => showAIHelp("Work Order", "Managing manufacturing work orders")
	},
];

frappe.help.help_links["Form/Workstation"] = [
	{
		label: "Workstation Help",
		action: () => showAIHelp("Workstation", "Managing workstations")
	},
];

frappe.help.help_links["Form/Operation"] = [
	{
		label: "Operation Help",
		action: () => showAIHelp("Operation", "Managing operations")
	},
];

frappe.help.help_links["Form/BOM Update Tool"] = [
	{
		label: "BOM Update Tool Help",
		action: () => showAIHelp("BOM Update Tool", "Using the BOM update tool")
	},
];

//Customize
frappe.help.help_links["Form/Customize Form"] = [
	{
		label: "Custom Field Help",
		action: () => showAIHelp("Custom Field", "Creating custom fields and customizing forms")
	},
];

frappe.help.help_links["List/Custom Field"] = [
	{
		label: "Custom Field Help",
		action: () => showAIHelp("Custom Field", "Creating and managing custom fields")
	},
];

frappe.help.help_links["Form/Custom Field"] = [
	{
		label: "Custom Field Help",
		action: () => showAIHelp("Custom Field", "Creating and managing custom fields")
	},
];

// Add a general help function for any module
frappe.help.show_module_help = function(module_name) {
	showAIHelp(`${module_name} Module`, `General help for the ${module_name} module`);
};
