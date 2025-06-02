frappe.provide("frappe.help.help_links");

// Import the AI help functions from the main help_links.js
// These functions will be available globally

frappe.help.help_links["data-import-tool"] = [
	{
		label: "Data Import Help",
		action: () => showAIHelp("Data Import", "Importing and exporting data")
	},
];

frappe.help.help_links["modules/Setup"] = [
	{
		label: "Setup Module Help",
		action: () => showAIHelp("Setup Module", "Users, permissions, system settings, and configuration")
	},
];

frappe.help.help_links["List/User"] = [
	{
		label: "User Management Help",
		action: () => showAIHelp("User Management", "Adding and managing users")
	},
];

frappe.help.help_links["permission-manager"] = [
	{
		label: "Role Permissions Help",
		action: () => showAIHelp("Role Permissions Manager", "Managing role-based permissions")
	},
];

frappe.help.help_links["user-permissions"] = [
	{
		label: "User Permissions Help",
		action: () => showAIHelp("User Permissions", "Setting up user-specific permissions")
	},
];

frappe.help.help_links["Form/System Settings"] = [
	{
		label: "System Settings Help",
		action: () => showAIHelp("System Settings", "Configuring system-wide settings")
	},
];

frappe.help.help_links["List/Email Account"] = [
	{
		label: "Email Account Help",
		action: () => showAIHelp("Email Account", "Setting up and managing email accounts")
	},
];

frappe.help.help_links["List/Notification"] = [
	{
		label: "Notification Help",
		action: () => showAIHelp("Notifications", "Setting up automated notifications")
	},
];

frappe.help.help_links["Form/Print Settings"] = [
	{
		label: "Print Settings Help",
		action: () => showAIHelp("Print Settings", "Configuring print and PDF settings")
	},
];

frappe.help.help_links["print-format-builder"] = [
	{
		label: "Print Format Help",
		action: () => showAIHelp("Print Format Builder", "Creating custom print formats")
	},
];
