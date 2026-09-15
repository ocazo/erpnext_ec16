"""Grant read access to the SRI catalogue DocTypes.

Sales Invoices link to ``Sri Establishment`` and ``Sri Ptoemi``; without read
permission on those DocTypes other roles cannot use the Link fields or list
pages. Sensitive configuration (signature) is restricted to accounting roles.
"""

import frappe
from frappe.permissions import add_permission

# Reference / catalogue DocTypes: read for every user.
READ_FOR_ALL = [
	"Sri Environment",
	"Sri Establishment",
	"Sri Ptoemi",
	"Sri Sequence",
	"Sri Type Doc",
	"Sri Type Id",
	"Sri External Establishment",
	"Sri Establishment Link",
	"Regional Settings Ec",
	"Xml Responses",
]

# Sensitive DocTypes: read only for accounting/administration roles.
READ_FOR_ACCOUNTING = {
	"Sri Signature": ["Accounts Manager"],
}


def execute():
	for doctype in READ_FOR_ALL:
		if frappe.db.exists("DocType", doctype):
			add_permission(doctype, "All", 0, "read")

	for doctype, roles in READ_FOR_ACCOUNTING.items():
		if not frappe.db.exists("DocType", doctype):
			continue
		for role in roles:
			add_permission(doctype, role, 0, "read")

	frappe.db.commit()
	frappe.clear_cache()
