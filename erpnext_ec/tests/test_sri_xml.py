"""Basic tests for SRI structured XML generation.

These tests build synthetic document objects and validate the generated XML
against the XSDs bundled with the app, without requiring real ERPNext
transactions.
"""

import contextlib
import datetime
import io
import os

import frappe
from frappe.tests.utils import FrappeTestCase
from lxml import etree

from erpnext_ec.utilities.xml_builder import XMLGenerator, build_xml_data

XSD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utilities", "xsd")

XSD_BY_TYPE = {
	"FAC": os.path.join(XSD_DIR, "factura_V1", "1", "0.xsd"),
	"GRS": os.path.join(XSD_DIR, "guiaRemision_V1", "0", "0.xsd"),
	"CRE": os.path.join(XSD_DIR, "comprobanteRetencion_V1", "0", "0.xsd"),
	"NCR": os.path.join(XSD_DIR, "notaCredito_V1", "0", "0.xsd"),
	"LIQ": os.path.join(XSD_DIR, "liquidacionCompra_V1", "0", "0.xsd"),
}

CLAVE = "1309202601099337126500120010020000000011234567818"


def _d(**kwargs):
	return frappe._dict(kwargs)


def _taxes():
	return [_d(sricode="2", codigoPorcentaje="4", baseImponible=100.0, rate=15.0, tax_amount=15.0)]


def _items():
	return [
		_d(
			item_code="PROD001",
			description="Producto de prueba",
			qty=1,
			precioUnitario=100.0,
			discount_amount=0.0,
			precioTotalSinImpuesto=100.0,
			impuestos=[
				{
					"codigo": "2",
					"codigoPorcentaje": "4",
					"tarifa": 15.0,
					"baseImponible": 100.0,
					"valor": 15.0,
				}
			],
		)
	]


def _pagos():
	return [{"formaPago": "01", "total": 115.0, "plazo": 0, "unidadTiempo": "dias"}]


def _common():
	return dict(
		ambiente="1",
		razonSocial="Empresa de Prueba SA",
		nombreComercial="Empresa Prueba",
		tax_id="0993371265001",
		claveAcceso=CLAVE,
		estab="001",
		ptoemi="001",
		secuencial=1,
		DireccionMatriz="Guayaquil, Ecuador",
		contribuyenteEspecial="123",
		obligadoContabilidad=1,
		contribuyenteRimpe=0,
		agenteRetencion=None,
		infoAdicional=[{"nombre": "Email", "valor": "test@test.com"}],
	)


def _fac():
	return _d(
		**_common(),
		posting_date=datetime.date(2026, 9, 13),
		dirEstablecimiento="Guayaquil, Ecuador",
		tipoIdentificacionComprador="04",
		customer_name="Cliente de Prueba",
		customer_tax_id="0912345678",
		base_total=100.0,
		totalDescuento=0.0,
		grand_total=115.0,
		taxes=_taxes(),
		items=_items(),
		pagos=_pagos(),
	)


def _grs():
	return _d(
		**_common(),
		razonSocialTransportista=None,
		tipoIdentificacionTransportista=None,
		rucTransportista=None,
		dirEstablecimiento="Guayaquil, Ecuador",
		fechaInicioTransporte=datetime.date(2026, 9, 13),
		placa_vehiculo="ABC1234",
		destinatarios=[
			{
				"identificacionDestinatario": "0912345678",
				"razonSocialDestinatario": "Cliente de Prueba",
				"dirDestinatario": "Guayaquil, Ecuador",
				"motivoTraslado": "Venta",
				"docAduaneroUnico": "",
				"codEstabDestino": "",
				"ruta": "",
				"codDocSustento": "01",
				"numDocSustento": "001-001-000000001",
				"numAutDocSustento": "",
				"fechaEmisionDocSustento": "13/09/2026",
				"detalles": {
					"detalle": [
						{
							"codigoInterno": "PROD001",
							"descripcion": "Producto de prueba",
							"cantidad": "1.00",
						}
					]
				},
			}
		],
	)


def _cre():
	return _d(
		**_common(),
		fechaEmision=datetime.date(2026, 9, 13),
		tipoIdentificacionSujetoRetenido="04",
		razonSocialSujetoRetenido="Proveedor de Prueba",
		identificacionSujetoRetenido="0912345678",
		periodoFiscal="09/2026",
		impuestos=[
			_d(
				idx=1,
				codigoRetencionId="1",
				baseImponible=100.0,
				porcentajeRetener=1.0,
				valorRetenido=1.0,
				codDocSustento="01",
				numDocSustento="001-001-000000001",
				fechaEmisionDocSustento=datetime.date(2026, 9, 13),
			)
		],
	)


def _ncr():
	return _d(
		**_common(),
		posting_date=datetime.date(2026, 9, 13),
		dirEstablecimiento="Guayaquil, Ecuador",
		tipoIdentificacionComprador="04",
		customer_name="Cliente de Prueba",
		customer_tax_id="0912345678",
		codDocModificado="01",
		numDocModificado="001-001-000000001",
		fechaEmisionDocSustento=datetime.date(2026, 9, 13),
		base_total=100.0,
		valorModificacion=115.0,
		motivo="Devolucion",
		taxes=_taxes(),
		items=_items(),
	)


def _liq():
	return _d(
		**_common(),
		posting_date=datetime.date(2026, 9, 13),
		dirEstablecimiento="Guayaquil, Ecuador",
		tipoIdentificacionProveedor="04",
		razonSocialProveedor="Proveedor de Prueba",
		identificacionProveedor="0912345678",
		direccionProveedor="Guayaquil, Ecuador",
		base_total=100.0,
		discount_amount=0.0,
		grand_total=115.0,
		taxes=_taxes(),
		items=_items(),
		pagos=_pagos(),
	)


BUILDERS = {
	"FAC": _fac,
	"GRS": _grs,
	"CRE": _cre,
	"NCR": _ncr,
	"LIQ": _liq,
}


class TestSriXmlGeneration(FrappeTestCase):
	def _build_and_validate(self, type_code):
		with contextlib.redirect_stdout(io.StringIO()):
			xml = build_xml_data(
				BUILDERS[type_code](), f"TST-{type_code}-0001", type_code, frappe.local.site
			)

		self.assertIn("<", xml)
		root = etree.fromstring(xml.encode("utf-8"))
		schema = XMLGenerator(XSD_BY_TYPE[type_code]).schema
		valid = schema.validate(root)
		if not valid:
			self.fail(f"{type_code} XML invalido: {schema.error_log}")

	def test_factura(self):
		self._build_and_validate("FAC")

	def test_guia_remision(self):
		self._build_and_validate("GRS")

	def test_comprobante_retencion(self):
		self._build_and_validate("CRE")

	def test_nota_credito(self):
		self._build_and_validate("NCR")

	def test_liquidacion_compra(self):
		self._build_and_validate("LIQ")
