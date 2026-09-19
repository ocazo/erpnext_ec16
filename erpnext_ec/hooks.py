app_name = "erpnext_ec"
app_title = "ERPNext Ec"
app_publisher = "BeebTech"
app_description = "ERPNext Ecuador"
app_email = "ronald.chonillo@gmail.com"
app_license = "mit"

# Required Apps
required_apps = ["erpnext"]

# Includes in <head>
# ------------------

app_include_js = [
	"/assets/erpnext_ec/js/sri_custom.js",
	"/assets/erpnext_ec/js/sales_invoice_tools.js",
	"/assets/erpnext_ec/js/delivery_note_tools.js",
	"/assets/erpnext_ec/js/withholding_tools.js",
	"/assets/erpnext_ec/js/frappe_sri_ui_tools.js",
	"/assets/erpnext_ec/js/purchase_receipt_tools.js",
	"/assets/erpnext_ec/js/libs/jsonTree/jsonTree.js",
	"/assets/erpnext_ec/js/libs/monthpicker/jquery.ui.monthpicker.min.js",
	"/assets/erpnext_ec/js/utils/desk.custom.js",
]

app_include_css = [
	"/assets/erpnext_ec/js/libs/jsonTree/jsonTree.css",
	"/assets/erpnext_ec/js/libs/monthpicker/qunit.min.css",
	"/assets/erpnext_ec/js/libs/monthpicker/jquery-ui.css",
]

# Include js in doctype views
doctype_js = {
	"Sales Invoice": "public/js/overrides/sales_invoice_form_sri.js",
	"Delivery Note": "public/js/overrides/delivery_note_form_sri.js",
	"Purchase Invoice": "public/js/overrides/purchase_invoice_form_sri.js",
	"Company": "public/js/overrides/company_form_sri.js",
}

doctype_list_js = {
	"Sales Invoice": "public/js/overrides/sales_invoice_list_sri.js",
	"Purchase Invoice": "public/js/overrides/purchase_invoice_list_sri.js",
	"Delivery Note": "public/js/overrides/delivery_note_list_sri.js",
	"Print Format": "public/js/overrides/print_format_list_sri.js",
	"Account": "public/js/overrides/account_list_sri.js",
	"Sri Establishment": "public/js/overrides/sri_establishment_list.js",
}

# Jinja
# ----------

jinja = {
	"methods": [
		"erpnext_ec.utilities.doc_builder_fac.build_doc_fac_with_images",
		"erpnext_ec.utilities.doc_builder_cre.build_doc_cre_with_images",
		"erpnext_ec.utilities.doc_builder_grs.build_doc_grs_with_images",
		"erpnext_ec.utilities.doc_builder_ncr.build_doc_ncr_with_images",
		"erpnext_ec.utilities.doc_builder_liq.build_doc_liq_with_images",
		"erpnext_ec.utilities.tools.get_full_url",
	]
}

# Document Events
# ---------------
doc_events = {
	"Xml Responses": {
		"validate": "erpnext_ec.erpnext_ec.doctype.xml_responses.events.validate",
		"on_update": "erpnext_ec.erpnext_ec.doctype.xml_responses.events.on_update",
		"after_insert": "erpnext_ec.erpnext_ec.doctype.xml_responses.events.after_insert",
	}
}

on_session_creation = [
	"erpnext_ec.utilities.tools.on_login_auto",
]

# Installation
# ------------

before_install = "erpnext_ec.install.before_install"
after_install = ["erpnext_ec.install.after_install"]

# Keep Custom Fields in sync on every migrate (idempotent loader).
after_migrate = [
	"erpnext_ec.patches.v16_0.load_custom_fields.execute",
]
