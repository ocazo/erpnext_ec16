import frappe


def execute(filters=None):
	columns = [
		{
			"label": "Establecimiento",
			"fieldname": "sri_establishment",
			"fieldtype": "Link",
			"options": "Sri Establishment",
			"width": 180,
		},
		{"label": "Punto de Emisión", "fieldname": "record_name", "fieldtype": "Data", "width": 120},
		{"label": "Descripción", "fieldname": "description", "fieldtype": "Data", "width": 220},
		{
			"label": "Ambiente",
			"fieldname": "sri_environment_lnk",
			"fieldtype": "Link",
			"options": "Sri Environment",
			"width": 120,
		},
		{"label": "Sec. Factura", "fieldname": "sec_factura", "fieldtype": "Int", "width": 110},
		{"label": "Sec. Nota Crédito", "fieldname": "sec_notacredito", "fieldtype": "Int", "width": 130},
		{"label": "Sec. Nota Débito", "fieldname": "sec_notadebito", "fieldtype": "Int", "width": 130},
		{
			"label": "Sec. Retención",
			"fieldname": "sec_comprobanteretencion",
			"fieldtype": "Int",
			"width": 130,
		},
		{
			"label": "Sec. Liquidación",
			"fieldname": "sec_liquidacioncompra",
			"fieldtype": "Int",
			"width": 130,
		},
		{"label": "Sec. Guía", "fieldname": "sec_guiaremision", "fieldtype": "Int", "width": 110},
	]

	data = frappe.db.sql(
		"""
		SELECT sri_establishment, record_name, description, sri_environment_lnk,
			sec_factura, sec_notacredito, sec_notadebito,
			sec_comprobanteretencion, sec_liquidacioncompra, sec_guiaremision
		FROM `tabSri Ptoemi`
		ORDER BY sri_establishment, record_name
		""",
		as_dict=True,
	)

	return columns, data
