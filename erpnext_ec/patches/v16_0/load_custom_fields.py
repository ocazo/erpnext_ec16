"""Load the custom fields defined in ``fixtures/*.json``.

The fixtures shipped with this app are plain lists of ``Custom Field`` records
(exported from the Customize Form grid), grouped by target DocType.  There was
no automatic loader for them in the legacy code, so they are applied here in an
idempotent way using ``create_custom_fields``.
"""

import glob
import json
import os

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

FIXTURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "fixtures"))

# Keys that belong to the Customize Form child grid / audit metadata and must
# not be copied into the Custom Field document.
IGNORED_KEYS = {
	"name",
	"parent",
	"parentfield",
	"parenttype",
	"idx",
	"docstatus",
	"owner",
	"creation",
	"modified",
	"modified_by",
	"_user_tags",
	"_comments",
	"_assign",
	"_liked_by",
	"is_custom_field",
}


def execute():
	custom_fields = {}

	for path in sorted(glob.glob(os.path.join(FIXTURES_DIR, "*.json"))):
		with open(path) as fixture:
			try:
				records = json.load(fixture)
			except json.JSONDecodeError:
				frappe.log_error(title="erpnext_ec: invalid fixture", message=path)
				continue

		if not isinstance(records, list):
			continue

		for record in records:
			if not isinstance(record, dict) or record.get("doctype") != "Custom Field":
				continue

			doctype = record.get("dt")
			fieldname = record.get("fieldname")
			if not doctype or not fieldname:
				continue

			df = {key: value for key, value in record.items() if key not in IGNORED_KEYS}
			# Frappe stores Custom Field names in lower case; align to avoid
			# "create when it already exists" crashes in create_custom_fields.
			df["fieldname"] = fieldname.lower()
			custom_fields.setdefault(doctype, []).append(df)

	if custom_fields:
		create_custom_fields(custom_fields, ignore_validate=True)
		frappe.db.commit()
