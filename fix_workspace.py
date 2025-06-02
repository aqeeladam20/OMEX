import frappe

def update_workspace_labels():
    # Update Selling workspace to Sales
    selling = frappe.get_doc('Workspace', 'Selling')
    selling.label = 'Sales'
    selling.title = 'Sales'
    selling.save()
    
    # Update Buying workspace to Procurement  
    buying = frappe.get_doc('Workspace', 'Buying')
    buying.label = 'Procurement'
    buying.title = 'Procurement'
    buying.save()
    
    frappe.db.commit()
    print('Updated workspace labels successfully')

update_workspace_labels() 