var doctype_customized = "Sales Invoice";

frappe.ui.form.on(doctype_customized, {
	onload(frm) {
		// El valor por defecto de "Emitir al SRI" y el ambiente se toman de la Compañía
		if (frm.doc.company) {
			frappe.db
				.get_value("Company", frm.doc.company, [
					"facturacion_electronica",
					"sri_active_environment",
				])
				.then((r) => {
					const data = (r && r.message) || {};
					frm.__sri_environment = data.sri_active_environment;
					if (frm.is_new() && cint(data.facturacion_electronica)) {
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

	estab(frm) {
		// El punto de emisión depende del establecimiento
		if (frm.doc.sri_ptoemi) {
			frappe.db
				.get_value("Sri Ptoemi", frm.doc.sri_ptoemi, "sri_establishment")
				.then((r) => {
					if (r && r.message && r.message.sri_establishment !== frm.doc.estab) {
						frm.set_value("sri_ptoemi", "");
					}
				});
		}
	},

	refresh(frm) {
		frm.set_query("sri_ptoemi", function () {
			const filters = { sri_establishment: frm.doc.estab };
			if (frm.__sri_environment) {
				filters.sri_environment_lnk = frm.__sri_environment;
			}
			return { filters };
		});

		// Factura no electrónica: no se exige ni se muestra nada del SRI
		if (!cint(frm.doc.emitir_sri)) {
			return;
		}

		if (frm.doc.status == "Draft") {
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
		if (frm.doc.estab && frm.doc.sri_ptoemi) {
			return;
		}

		// Se resuelve en el servidor (devuelve establecimiento, punto de emisión
		// y el código de 3 dígitos).
		const r = await frappe.call({
			method: "erpnext_ec.utilities.tools.get_sri_default_establishment",
		});
		const data = r.message || {};

		if (!frm.doc.estab && data.estab) {
			await frm.set_value("estab", data.estab);
		}
		if (!frm.doc.sri_ptoemi && data.sri_ptoemi) {
			await frm.set_value("sri_ptoemi", data.sri_ptoemi);
		}
		if (!frm.doc.ptoemi && data.ptoemi) {
			await frm.set_value("ptoemi", data.ptoemi);
		}
	} catch (e) {
		// Sin configuración SRI: no bloquear la factura
		console.warn(e);
	}
}
