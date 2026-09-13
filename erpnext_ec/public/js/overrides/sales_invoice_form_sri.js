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
		let estab = frm.doc.estab;
		if (!estab) {
			const estabs = await frappe.db.get_list("Sri Establishment", {
				fields: ["name"],
				limit: 1,
			});
			if (estabs.length) {
				estab = estabs[0].name;
				await frm.set_value("estab", estab);
			}
		}

		if (estab && !frm.doc.ptoemi) {
			const ptoemis = await frappe.db.get_list("Sri Ptoemi", {
				fields: ["name"],
				filters: { parent: estab },
				limit: 1,
			});
			if (ptoemis.length) {
				await frm.set_value("ptoemi", ptoemis[0].name);
			}
		}
	} catch (e) {
		// Sin configuración SRI: no bloquear la factura
		console.warn(e);
	}
}
