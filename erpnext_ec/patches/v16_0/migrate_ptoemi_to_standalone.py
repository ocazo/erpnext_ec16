"""Migrate ``Sri Ptoemi`` from a child table to a standalone DocType.

- populate ``sri_establishment`` from the old ``parent``
- rename each record to ``{establishment}-{record_name}``
- link existing transactions (``sri_ptoemi``) by (estab, ptoemi code)
"""

import frappe

TRANSACTION_DOCTYPES = [
	"Sales Invoice",
	"Delivery Note",
	"Purchase Invoice",
	"Purchase Receipt",
	"Purchase Withholding Sri Ec",
]


def _set(doctype, name, fieldname, value):
	frappe.db.set_value(doctype, name, fieldname, value, update_modified=False)


def execute():
	if not frappe.db.exists("DocType", "Sri Ptoemi"):
		return

	# 1) populate establishment + rename to composite name
	rows = frappe.get_all(
		"Sri Ptoemi",
		fields=["name", "record_name", "sri_establishment", "parent"],
	)
	renames = {}

	for row in rows:
		establishment = row.sri_establishment or row.get("parent")
		if not establishment:
			continue

		if not row.sri_establishment:
			_set("Sri Ptoemi", row.name, "sri_establishment", establishment)

		target = f"{establishment}-{row.record_name}"
		if row.name != target:
			renames[row.name] = target

	for old_name, new_name in renames.items():
		if frappe.db.exists("Sri Ptoemi", new_name):
			continue
		try:
			frappe.rename_doc(
				"Sri Ptoemi",
				old_name,
				new_name,
				force=True,
				show_alert=False,
			)
		except Exception:
			frappe.log_error(
				title="erpnext_ec: could not rename Sri Ptoemi",
				message=f"{old_name} -> {new_name}\n{frappe.get_traceback()}",
			)

	# 2) link transactions to the standalone emission point
	for doctype in TRANSACTION_DOCTYPES:
		if not frappe.db.has_column(doctype, "sri_ptoemi"):
			continue

		transactions = frappe.db.sql(
			f"SELECT name, estab, ptoemi, sri_ptoemi FROM `tab{doctype}` "
			"WHERE IFNULL(ptoemi, '') != ''",
			as_dict=True,
		)

		for txn in transactions:
			if txn.sri_ptoemi:
				continue
			record = frappe.db.get_value(
				"Sri Ptoemi",
				{"sri_establishment": txn.estab, "record_name": txn.ptoemi},
				"name",
			)
			if record:
				_set(doctype, txn.name, "sri_ptoemi", record)

	frappe.db.commit()
	frappe.clear_cache()
