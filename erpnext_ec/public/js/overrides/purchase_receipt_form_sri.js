var doctype_customized = "Purchase Receipt";

frappe.ui.form.on(doctype_customized, {
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
        
        SetFormSriButtons(frm, doctype_customized);      
        //console.log(frm);
        //console.log(frm.doctype_customized);
    },
    estab: function(frm)
	{
        //frm.set_value('ptoemi',  '');
        //frm.refresh_field('ptoemi');
	},
})
