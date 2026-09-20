"""Rename existing ``Sri Ptoemi`` records to include the environment.

The name is now ``{establishment}-{record_name}-{environment}`` so that the same
point code (e.g. 001) can exist in DES and PRO without collision.
"""

import frappe


def execute():
	if not frappe.db.exists("DocType", "Sri Ptoemi"):
		return

	rows = frappe.get_all(
		"Sri Ptoemi",
		fields=["name", "sri_establishment", "record_name", "sri_environment_lnk"],
	)

	for row in rows:
		environment = row.sri_environment_lnk or "DES"
		target = f"{row.sri_establishment}-{row.record_name}-{environment}"

		if row.name == target or frappe.db.exists("Sri Ptoemi", target):
			continue

		try:
			frappe.rename_doc("Sri Ptoemi", row.name, target, force=True, show_alert=False)
		except Exception:
			frappe.log_error(
				title="erpnext_ec: could not rename Sri Ptoemi",
				message=f"{row.name} -> {target}\n{frappe.get_traceback()}",
			)

	frappe.db.commit()
