"""Ensure ``read`` **and** ``select`` permission on the SRI catalogue DocTypes.

Link fields perform link validation through
``frappe.client.validate_link_and_fetch`` which uses the query builder's
select-permission check. Granting only ``read`` is not enough, so users get
"Insufficient Permission for Sri Ptoemi" when a Sales Invoice sets
``estab``/``ptoemi``.
"""

import frappe
from frappe.permissions import add_permission

READ_SELECT_ALL = [
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

# Sensitive DocTypes: only accounting/administration roles.
READ_SELECT_ACCOUNTING = {
	"Sri Signature": ["Accounts Manager", "System Manager"],
}


def _grant(doctype, role):
	perm_name = frappe.db.get_value(
		"Custom DocPerm",
		{"parent": doctype, "role": role, "permlevel": 0, "if_owner": 0},
		"name",
	)
	if not perm_name:
		add_permission(doctype, role, 0, "read")
		perm_name = frappe.db.get_value(
			"Custom DocPerm",
			{"parent": doctype, "role": role, "permlevel": 0, "if_owner": 0},
			"name",
		)

	if perm_name:
		perm = frappe.get_doc("Custom DocPerm", perm_name)
		perm.read = 1
		perm.select = 1
		perm.save(ignore_permissions=True)

	frappe.clear_cache(doctype=doctype)


def execute():
	for doctype in READ_SELECT_ALL:
		if frappe.db.exists("DocType", doctype):
			_grant(doctype, "All")

	for doctype, roles in READ_SELECT_ACCOUNTING.items():
		if not frappe.db.exists("DocType", doctype):
			continue
		for role in roles:
			_grant(doctype, role)

	frappe.db.commit()
	frappe.clear_cache()
