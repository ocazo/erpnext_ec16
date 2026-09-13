// Configuración SRI - revisión permanente de la configuración de facturación electrónica
frappe.provide("frappe.sri_validation");

frappe.pages["sri-validation"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Configuración SRI"),
		single_column: true,
	});

	$(page.body).append(`
		<div class="text-muted" style="margin-bottom: 16px;">
			${__("Verificación de la configuración necesaria para emitir documentos electrónicos del SRI.")}
		</div>
		<div class="sri-quick-links" style="margin-bottom: 20px;"></div>
		<div class="sri-validation-results"></div>
	`);

	render_quick_links(page);

	page.set_primary_action(__("Revalidar"), function () {
		frappe.sri_validation.load(page);
	});

	frappe.sri_validation.load(page);
};

function render_quick_links(page) {
	var links = [
		{ label: __("Firmas Electrónicas"), route: ["List", "Sri Signature"] },
		{ label: __("Establecimientos"), route: ["List", "Sri Establishment"] },
		{ label: __("Puntos de Emisión"), route: ["List", "Sri Ptoemi"] },
		{ label: __("Secuencias"), route: ["List", "Sri Sequence"] },
		{ label: __("Retenciones"), route: ["List", "Purchase Withholding Sri Ec"] },
		{ label: __("Configuración Regional"), route: ["List", "Regional Settings Ec"] },
	];

	var $links = $(page.body).find(".sri-quick-links");

	links.forEach(function (link) {
		$(
			`<button class="btn btn-default btn-sm" style="margin: 0 6px 6px 0;">${link.label}</button>`
		)
			.on("click", function () {
				frappe.set_route.apply(null, link.route);
			})
			.appendTo($links);
	});
}

frappe.sri_validation.status_pill = function (ready) {
	if (ready) {
		return `<span class="indicator-pill green filterable no-indicator-dot ellipsis"><span class="ellipsis">${__("Ready")}</span></span>`;
	}
	return `<span class="indicator-pill red filterable no-indicator-dot ellipsis"><span class="ellipsis">${__("Fail")}</span></span>`;
};

frappe.sri_validation.html = function (groups) {
	var html = "";

	(groups || []).forEach(function (group) {
		var ready = group.SettingsAreReady;

		html += `<div class="frappe-card" style="padding: 16px; margin-bottom: 16px;">`;
		html += `<h5 style="margin-top: 0; margin-bottom: 12px;">
			${frappe.utils.escape_html(group.description || "")}
			${frappe.sri_validation.status_pill(ready)}
		</h5>`;

		html += `<table class="table table-bordered" style="margin-bottom: 10px;"><tbody>`;
		(group.header || []).forEach(function (item) {
			// item.value may contain trusted server-rendered HTML (status pill)
			html += `<tr>
				<td style="width: 45%;"><b>${frappe.utils.escape_html(item.description || "")}</b></td>
				<td>${item.value == null ? "" : item.value}</td>
			</tr>`;
		});
		html += `</tbody></table>`;

		(group.alerts || []).forEach(function (alert) {
			var help = alert.help
				? ` <span class="text-muted">${frappe.utils.escape_html(alert.help)}</span>`
				: "";
			html += `<div class="alert alert-danger" style="margin-bottom: 6px;">
				${frappe.utils.escape_html(alert.description || "")}${help}
			</div>`;
		});

		html += `</div>`;
	});

	return html;
};

frappe.sri_validation.load = function (page) {
	var $results = $(page.body).find(".sri-validation-results");
	$results.html(`<div class="text-muted">${__("Verificando configuración...")}</div>`);

	frappe.call({
		method: "erpnext_ec.utilities.tools.validate_sri_settings",
		callback: function (r) {
			if (!r.message || !r.message.groups) {
				$results.html(
					`<div class="text-muted">${__("No hay datos de configuración.")}</div>`
				);
				return;
			}

			var groups = r.message.groups;
			var ready = groups.every(function (group) {
				return group.SettingsAreReady;
			});

			var banner = ready
				? `<div class="alert alert-success">
						<b>${__("Configuración compatible con el SRI")}</b>
					</div>`
				: `<div class="alert alert-danger">
						<b>${__("Configuración incompatible con el SRI")}</b><br>
						${__("Revise y corrija los puntos marcados antes de generar documentos electrónicos.")}
					</div>`;

			$results.html(banner + frappe.sri_validation.html(groups));
		},
		error: function () {
			$results.html(
				`<div class="text-danger">${__("No se pudo validar la configuración del SRI.")}</div>`
			);
		},
	});
};
