from __future__ import unicode_literals

import json
import os

import frappe

REOPEN_SEQ_DOCTYPES = {
	"FAC": "Sales Invoice",
	"GRS": "Delivery Note",
	"CRE": "Purchase Withholding Sri Ec",
}


def get_last_sequencial_found(company_id, sri_type_doc_lnk, establishment, ptoemi):
	# Frappe v16 no longer allows raw SQL functions in get_list fields.
	doctype = REOPEN_SEQ_DOCTYPES.get(sri_type_doc_lnk)
	if not doctype:
		return 0

	result = frappe.db.sql(
		f"SELECT MAX(secuencial) FROM `tab{doctype}` "
		"WHERE company = %s AND estab = %s AND ptoemi = %s",
		(company_id, establishment, ptoemi),
	)
	return result[0][0] if result and result[0][0] is not None else 0


def _upsert_ptoemi(establishment_name, company, record_name, child):
	child = dict(child)
	child.pop("naming_series", None)
	child["doctype"] = "Sri Ptoemi"
	child["sri_establishment"] = establishment_name
	child["record_name"] = record_name
	child["sec_factura"] = get_last_sequencial_found(
		company, "FAC", establishment_name, record_name
	)
	child["sec_guiaremision"] = get_last_sequencial_found(
		company, "GRS", establishment_name, record_name
	)
	child["sec_comprobanteretencion"] = get_last_sequencial_found(
		company, "CRE", establishment_name, record_name
	)

	existing = frappe.get_all(
		"Sri Ptoemi",
		filters={"sri_establishment": establishment_name, "record_name": record_name},
		fields=["name"],
	)
	if existing:
		ptoemi = frappe.get_doc("Sri Ptoemi", existing[0].name)
		ptoemi.update(child)
		ptoemi.save(ignore_permissions=True)
	else:
		frappe.get_doc(child).insert(ignore_permissions=True)


def insert_update(DocTypeName, JsonPath):
	print("insert_update_data")
	with open(JsonPath) as file:
		data = json.loads(file.read())

	default_company = frappe.defaults.get_user_default("Company")
	print("Company:", default_company)

	for record in data:
		record["company_link"] = default_company
		record["name"] = record.get("name", "").replace("*", "")
		ptoemi_detail = record.pop("sri_ptoemi_detail", [])

		print("Procesando:", record["name"])

		try:
			existing = frappe.get_all(
				DocTypeName,
				filters={"record_name": record["record_name"]},
				fields=["name"],
			)

			if existing:
				document_object = frappe.get_doc(DocTypeName, existing[0].name)
				for key, value in record.items():
					if key != "name":
						setattr(document_object, key, value)
				document_object.save(ignore_permissions=True)
			else:
				document_object = frappe.get_doc(record)
				document_object.insert(ignore_permissions=True)

			for child in ptoemi_detail:
				_upsert_ptoemi(
					document_object.name,
					record["company_link"],
					child["record_name"],
					child,
				)

			frappe.db.commit()

		except Exception as e:
			print("Error en registro:", record.get("name"), "-", str(e))
			frappe.db.rollback()

	print("Proceso terminado insert_update.")


def execute():
	dir_path = os.path.dirname(os.path.realpath(__file__))

	source_list = [
		{
			"doctype": "Sri Establishment",
			"json_file": "sri_establishment.json",
			"action": "update",
		},
	]

	for source_item in source_list:
		print(source_item)
		filepathfull = os.path.join(
			dir_path, "../../fixtures/specials", source_item["json_file"]
		)

		try:
			if source_item["action"] == "update":
				insert_update(source_item["doctype"], filepathfull)
		except Exception as e:
			return {"message": "Failed import.", "error": str(e)}
