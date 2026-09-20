"""Load SRI catalogues, Mode of Payment and the default establishment/points.

Idempotent (upsert by name). Runs on every migrate through ``after_migrate`` so
that a ``git pull`` + ``bench migrate`` is enough to configure a site.
"""

import json
import os

import frappe

FIXTURES_DIR = os.path.abspath(
	os.path.join(os.path.dirname(__file__), "..", "..", "fixtures", "seed")
)

CATALOG_FILES = {
	"sri_environment.json": "Sri Environment",
	"sri_type_doc.json": "Sri Type Doc",
	"sri_type_id.json": "Sri Type Id",
	"sri_external_establishment.json": "Sri External Establishment",
	"mode_of_payment.json": "Mode of Payment",
}

DEFAULT_ESTABLISHMENT = "001"
DEFAULT_PTOEMI = "001"
DEFAULT_ENVIRONMENTS = ["DES", "PRO"]


def _columns(doctype):
	return {df.fieldname for df in frappe.get_meta(doctype).fields}


def _upsert(doctype, record):
	name = record.get("name")
	if not name:
		return

	if frappe.db.exists(doctype, name):
		columns = _columns(doctype)
		doc = frappe.get_doc(doctype, name)
		for key, value in record.items():
			if key in columns:
				doc.set(key, value)
		doc.save(ignore_permissions=True)
	else:
		doc = frappe.get_doc(record)
		doc.flags.name_set = True
		doc.insert(ignore_permissions=True)


def _default_company():
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	if not company:
		companies = frappe.get_all("Company", pluck="name", limit=1)
		company = companies[0] if companies else None
	return company


def _ensure_default_points(company):
	if not company:
		return

	if not frappe.db.exists("Sri Establishment", DEFAULT_ESTABLISHMENT):
		frappe.get_doc(
			{
				"doctype": "Sri Establishment",
				"record_name": DEFAULT_ESTABLISHMENT,
				"company_link": company,
				"description": "Matriz",
			}
		).insert(ignore_permissions=True)

	for environment in DEFAULT_ENVIRONMENTS:
		exists = frappe.db.exists(
			"Sri Ptoemi",
			{
				"sri_establishment": DEFAULT_ESTABLISHMENT,
				"record_name": DEFAULT_PTOEMI,
				"sri_environment_lnk": environment,
			},
		)
		if not exists:
			frappe.get_doc(
				{
					"doctype": "Sri Ptoemi",
					"sri_establishment": DEFAULT_ESTABLISHMENT,
					"record_name": DEFAULT_PTOEMI,
					"description": "Matriz",
					"sri_environment_lnk": environment,
				}
			).insert(ignore_permissions=True)


def execute():
	for filename, doctype in CATALOG_FILES.items():
		path = os.path.join(FIXTURES_DIR, filename)
		if not os.path.exists(path):
			continue

		with open(path) as fixture:
			try:
				records = json.load(fixture)
			except json.JSONDecodeError:
				frappe.log_error(title="erpnext_ec: invalid fixture", message=path)
				continue

		if not isinstance(records, list):
			continue

		for record in records:
			if isinstance(record, dict) and record.get("doctype") == doctype:
				_upsert(doctype, record)

	_ensure_default_points(_default_company())

	frappe.db.commit()
