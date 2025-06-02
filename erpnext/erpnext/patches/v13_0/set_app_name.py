import frappe


def execute():
	frappe.reload_doctype("System Settings")
	settings = frappe.get_doc("System Settings")
	# Keep the app name as erpnext for API compatibility
	# The display name can be OMEX ERP but the app name should remain erpnext
	settings.db_set("app_name", "erpnext", commit=True)
