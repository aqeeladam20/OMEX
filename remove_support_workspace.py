#!/usr/bin/env python3

import frappe

def remove_support_workspace():
    """Remove the Support workspace and related content from ERPNext"""
    
    # Initialize frappe
    frappe.init(site="localhost")
    frappe.connect()
    
    try:
        print("🗑️  Removing Support workspace and related content...")
        
        # Remove the Support workspace document if it exists
        if frappe.db.exists("Workspace", "Support"):
            print("📄 Deleting Support workspace document...")
            frappe.delete_doc("Workspace", "Support", force=True, ignore_permissions=True)
            print("✅ Support workspace document deleted")
        else:
            print("ℹ️  Support workspace document not found")
        
        # Remove any workspace settings references
        try:
            workspace_settings = frappe.get_single("Workspace Settings")
            if workspace_settings.workspace_visibility_json:
                import json
                visibility_data = json.loads(workspace_settings.workspace_visibility_json)
                if "Support" in visibility_data:
                    del visibility_data["Support"]
                    workspace_settings.workspace_visibility_json = json.dumps(visibility_data)
                    workspace_settings.save(ignore_permissions=True)
                    print("✅ Updated Workspace Settings")
        except Exception as e:
            print(f"ℹ️  Workspace Settings update: {e}")
        
        # Remove Module Def for Support if it exists
        if frappe.db.exists("Module Def", "Support"):
            print("📄 Deleting Support module definition...")
            frappe.delete_doc("Module Def", "Support", force=True, ignore_permissions=True)
            print("✅ Support module definition deleted")
        else:
            print("ℹ️  Support module definition not found")
        
        # Remove any desktop icons related to Support
        support_icons = frappe.db.get_all(
            "Desktop Icon", 
            filters={"module_name": "Support"}, 
            fields=["name"]
        )
        
        for icon in support_icons:
            frappe.delete_doc("Desktop Icon", icon.name, force=True, ignore_permissions=True)
            print(f"✅ Deleted desktop icon: {icon.name}")
        
        # Commit all changes
        frappe.db.commit()
        print("🎉 Successfully removed Support workspace and related content!")
        
        # Clear cache to refresh the sidebar
        frappe.clear_cache()
        print("🔄 Cache cleared")
        
    except Exception as e:
        print(f"❌ Error removing Support workspace: {str(e)}")
        frappe.db.rollback()
        raise
    
    finally:
        frappe.destroy()

if __name__ == "__main__":
    remove_support_workspace() 