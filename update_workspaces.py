#!/usr/bin/env python3

import frappe
from frappe import _

def update_workspaces():
    """Update workspace labels and create parent-child relationships"""
    
    # Connect to the database
    frappe.connect()
    
    # Update Selling workspace to Sales
    try:
        selling_workspace = frappe.get_doc("Workspace", "Selling")
        selling_workspace.label = "Sales"
        selling_workspace.title = "Sales"
        selling_workspace.save()
        print("Updated Selling workspace to Sales")
    except Exception as e:
        print(f"Error updating Selling workspace: {e}")
    
    # Update Buying workspace to Procurement
    try:
        buying_workspace = frappe.get_doc("Workspace", "Buying")
        buying_workspace.label = "Procurement"
        buying_workspace.title = "Procurement"
        buying_workspace.save()
        print("Updated Buying workspace to Procurement")
    except Exception as e:
        print(f"Error updating Buying workspace: {e}")
    
    # Create child workspaces for Sales
    sales_children = [
        {"name": "Customer", "title": "Customer", "link_to": "Customer", "link_type": "DocType"},
        {"name": "Quotation", "title": "Quotation", "link_to": "Quotation", "link_type": "DocType"},
        {"name": "Sales Order", "title": "Sales Order", "link_to": "Sales Order", "link_type": "DocType"},
        {"name": "Sales Invoice", "title": "Sales Invoice", "link_to": "Sales Invoice", "link_type": "DocType"},
        {"name": "Sales Partner", "title": "Sales Partner", "link_to": "Sales Partner", "link_type": "DocType"},
        {"name": "Blanket Order", "title": "Blanket Order", "link_to": "Blanket Order", "link_type": "DocType"},
        {"name": "Sales Person", "title": "Sales Person", "link_to": "Sales Person", "link_type": "DocType"},
    ]
    
    for child in sales_children:
        try:
            if not frappe.db.exists("Workspace", child["name"]):
                workspace = frappe.new_doc("Workspace")
                workspace.name = child["name"]
                workspace.title = child["title"]
                workspace.label = child["title"]
                workspace.parent_page = "Selling"
                workspace.module = "Selling"
                workspace.app = "erpnext"
                workspace.public = 1
                workspace.type = "Link"
                workspace.link_type = child["link_type"]
                workspace.link_to = child["link_to"]
                workspace.sequence_id = 7.0 + len([c for c in sales_children if c["name"] <= child["name"]])
                workspace.insert()
                print(f"Created {child['title']} workspace")
            else:
                workspace = frappe.get_doc("Workspace", child["name"])
                workspace.parent_page = "Selling"
                workspace.save()
                print(f"Updated {child['title']} workspace parent")
        except Exception as e:
            print(f"Error with {child['title']} workspace: {e}")
    
    # Create child workspaces for Procurement
    procurement_children = [
        {"name": "Material Request", "title": "Material Request", "link_to": "Material Request", "link_type": "DocType"},
        {"name": "Purchase Order", "title": "Purchase Order", "link_to": "Purchase Order", "link_type": "DocType"},
        {"name": "Purchase Invoice", "title": "Purchase Invoice", "link_to": "Purchase Invoice", "link_type": "DocType"},
        {"name": "Request for Quotation", "title": "Request for Quotation", "link_to": "Request for Quotation", "link_type": "DocType"},
        {"name": "Supplier Quotation", "title": "Supplier Quotation", "link_to": "Supplier Quotation", "link_type": "DocType"},
    ]
    
    for child in procurement_children:
        try:
            if not frappe.db.exists("Workspace", child["name"]):
                workspace = frappe.new_doc("Workspace")
                workspace.name = child["name"]
                workspace.title = child["title"]
                workspace.label = child["title"]
                workspace.parent_page = "Buying"
                workspace.module = "Buying"
                workspace.app = "erpnext"
                workspace.public = 1
                workspace.type = "Link"
                workspace.link_type = child["link_type"]
                workspace.link_to = child["link_to"]
                workspace.sequence_id = 14.0 + len([c for c in procurement_children if c["name"] <= child["name"]])
                workspace.insert()
                print(f"Created {child['title']} workspace")
            else:
                workspace = frappe.get_doc("Workspace", child["name"])
                workspace.parent_page = "Buying"
                workspace.save()
                print(f"Updated {child['title']} workspace parent")
        except Exception as e:
            print(f"Error with {child['title']} workspace: {e}")
    
    # Commit changes
    frappe.db.commit()
    print("All workspace updates completed!")

if __name__ == "__main__":
    update_workspaces() 