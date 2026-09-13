// Revisión de configuración SRI.
// El detalle permanente vive en la página "Configuración SRI" (workspace Sri).
// Aquí solo se muestra el aviso al iniciar sesión.

function getCookie(cname) {
	let name = cname + "=";
	let ca = document.cookie.split(";");
	for (let i = 0; i < ca.length; i++) {
		let c = ca[i];
		while (c.charAt(0) == " ") {
			c = c.substring(1);
		}
		if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
		}
	}
	return "";
}

function buildSriSettingsHtml(groups) {
	var SettingsAreReady = true;
	var body = "";

	(groups || []).forEach(function (group) {
		if (group.SettingsAreReady === false) {
			SettingsAreReady = false;
		}

		body += '<table class="table table-bordered" style="margin-bottom: 8px;"><tbody>';
		(group.header || []).forEach(function (item) {
			body +=
				"<tr><td style='width:45%;'><b>" +
				item.description +
				"</b></td><td>" +
				(item.value == null ? "" : item.value) +
				"</td></tr>";
		});
		(group.alerts || []).forEach(function (alert) {
			var help = alert.help ? ' <span class="text-muted">' + alert.help + "</span>" : "";
			body +=
				'<tr><td colspan="2" class="text-danger">' +
				alert.description +
				help +
				"</td></tr>";
		});
		body += '</tbody></table><div class="dropdown-divider"></div>';
	});

	return { ready: SettingsAreReady, html: body };
}

function showEvalSriSettings(changeStatus) {
	frappe.call({
		method: "erpnext_ec.utilities.tools.validate_sri_settings",
		callback: function (r) {
			if (!r || !r.message || !r.message.groups) {
				return;
			}

			var result = buildSriSettingsHtml(r.message.groups);

			if (!result.ready) {
				frappe.msgprint({
					title: __("Configuración incompatible con el SRI"),
					indicator: "red",
					message:
						"<p>Se requiere revisión</p>" +
						result.html +
						'<div class="text-muted">Por favor, corrija su configuración antes de generar documentos electrónicos.</div>',
				});
			}

			if (changeStatus) {
				frappe.call({
					method: "erpnext_ec.utilities.tools.set_cookie",
					args: {
						cookie_name: "login_boot",
						cookie_value: "not",
					},
				});
			}
		},
		error: function (r) {
			console.log(r);
		},
	});
}

function evalSriSettings() {
	if (getCookie("login_boot") == "yes") {
		showEvalSriSettings(true);
	}
}

setTimeout(function () {
	evalSriSettings();
}, 2000);
