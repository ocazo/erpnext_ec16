var doctype_customized = "Purchase Invoice";

frappe.ui.form.on(doctype_customized, {
    onload: function(frm) {        
        if (frappe.session.default_is_purchase_settlement == 1) {
            var default_is_purchase_settlement = frappe.session.default_is_purchase_settlement;
            frm.set_value('is_purchase_settlement', default_is_purchase_settlement);
            frappe.session.default_is_purchase_settlement = null;
        }

        if (frm.doc.is_purchase_settlement)
        {
            //frm.dashboard.clear_headline();
            //frm.dashboard.set_headline('MODO LIQUIDACIÓN DE COMPRA')
        }
    },
	refresh(frm)
    {
        if (frm.doc.status == 'Draft')
        {
            // Punto de emisión del establecimiento y ambiente activo de la compañía
            frappe.db.get_value("Company", frm.doc.company, "sri_active_environment").then((r) => {
                const environment = r && r.message && r.message.sri_active_environment;
                frm.set_query('sri_ptoemi', function() {
                    const filters = { 'sri_establishment': frm.doc.estab };
                    if (environment) {
                        filters['sri_environment_lnk'] = environment;
                    }
                    return { filters: filters };
                });
            });
        }

        if (frm.doc.status == 'Cancelled' || frm.doc.status == 'Draft')
        {
            return false;
        }        
        
        //SetFormSriButtons(frm, doctype_customized);      
        //console.log(frm);
        //console.log(frm.doctype_customized);
    },
    estab: function(frm)
	{
        //frm.set_value('ptoemi',  '');
        //frm.refresh_field('ptoemi');
	},
    is_purchase_settlement: function(frm)
    {
        if (frm.doc.is_purchase_settlement) {
            frm.set_value('is_return', 0);
        }
        update_headline(frm);
    },
    is_return: function(frm)
    {
        if (frm.doc.is_return) {
            frm.set_value('is_purchase_settlement', 0);
        }
        update_headline(frm);
    }
})


function update_headline(frm) {
    frm.dashboard.clear_headline()
    if (frm.doc.is_purchase_settlement) {
        frm.dashboard.set_headline("LIQUIDACIÓN DE COMPRA");
    } else if (frm.doc.is_return) {
        frm.dashboard.set_headline("NOTA DE DÉBITO");
    } else {
        frm.dashboard.set_headline("FACTURA DE COMPRA");
    }
}