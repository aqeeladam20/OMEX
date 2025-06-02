import frappe
from frappe.model.document import Document

class AIChatLog(Document):
    def before_insert(self):
        if not self.timestamp:
            self.timestamp = frappe.utils.now()
        if not self.user:
            self.user = frappe.session.user 