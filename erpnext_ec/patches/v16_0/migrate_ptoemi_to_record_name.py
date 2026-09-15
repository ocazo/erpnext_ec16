"""Convert existing ``ptoemi`` values from the child document name to record_name.

``ptoemi`` used to be a Link to the child DocType ``Sri Ptoemi`` (value = child
name like ``PTO-00001``). It is now a Data field holding the SRI emission point
code (``record_name``, e.g. ``002``).
"""

import frappe

DOCTYPE_LIST = [
	"Sales Invoice",
	"Delivery Note",
	"Purchase Invoice",
	"Purchase Receipt",
	"Purchase Withholding Sri Ec",
]


def execute():
	for doctype in DOCTYPE_LIST:
		if not frappe.db.has_column(doctype, "ptoemi"):
			continue

		rows = frappe.db.sql(
			f"SELECT name, ptoemi FROM `tab{doctype}` WHERE IFNULL(ptoemi, '') != ''",
			as_dict=True,
		)

		for row in rows:
			record_name = frappe.db.get_value("Sri Ptoemi", row.ptoemi, "record_name")
			if record_name and record_name != row.ptoemi:
				frappe.db.set_value(
					doctype, row.name, "ptoemi", record_name, update_modified=False
				)

	frappe.db.commit()
