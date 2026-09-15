var doctype_customized = "Sales Invoice";

frappe.ui.form.on(doctype_customized, {
	onload(frm) {
		// El valor por defecto de "Emitir al SRI" se toma de la Compañía
		if (frm.is_new() && frm.doc.company) {
			frappe.db
				.get_value("Company", frm.doc.company, "facturacion_electronica")
				.then((r) => {
					if (r && r.message && cint(r.message.facturacion_electronica)) {
						frm.set_value("emitir_sri", 1);
					}
				});
		}
	},

	emitir_sri(frm) {
		if (frm.doc.emitir_sri) {
			set_default_sri_establishment(frm);
		}
	},

	refresh(frm) {
		// Factura no electrónica: no se exige ni se muestra nada del SRI
		if (!cint(frm.doc.emitir_sri)) {
			return;
		}

		if (frm.doc.status == "Draft") {
			frm.set_query("ptoemi", function () {
				return {
					filters: {
						//'sri_establishment_lnk': frm.doc.estab
					},
				};
			});

			set_default_sri_establishment(frm);
		}

		if (frm.doc.status == "Cancelled" || frm.doc.status == "Draft") {
			return false;
		}

		SetFormSriButtons(frm, doctype_customized);
	},
});

async function set_default_sri_establishment(frm) {
	try {
		if (frm.doc.estab && frm.doc.ptoemi) {
			return;
		}

		// v16 no permite filtrar la tabla hija Sri Ptoemi por "parent" desde el
		// cliente (PermissionError). Se resuelve en el servidor.
		const r = await frappe.call({
			method: "erpnext_ec.utilities.tools.get_sri_default_establishment",
		});
		const data = r.message || {};

		if (!frm.doc.estab && data.estab) {
			await frm.set_value("estab", data.estab);
		}
		if (!frm.doc.ptoemi && data.ptoemi) {
			await frm.set_value("ptoemi", data.ptoemi);
		}
	} catch (e) {
		// Sin configuración SRI: no bloquear la factura
		console.warn(e);
	}
}
