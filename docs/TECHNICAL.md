# Documentación técnica — ERPNext Ec

Localización de Ecuador para ERPNext v16 / Frappe v16 (Python 3.14).
Este documento describe la arquitectura, los cambios de migración y las
decisiones técnicas.

## 1. Estructura de la app

```
erpnext_ec/                  # paquete de la app (hooks, patches, public, utilities)
  erpnext_ec/                # módulo "Erpnext Ec" (DocTypes propios)
  erpnext_sri/               # módulo "Erpnext Sri" (catálogos SRI, workspace, page)
  patches/v16_0/             # parches de migración
  fixtures/seed/*.json       # Custom Fields (subcarpeta no autoimportada por v16)
  utilities/                 # XML builders, firma, WS del SRI, utilidades
  public/js/                 # overrides de formularios/listas y UI SRI
  tests/                     # pruebas unitarias
```

## 2. Puntos de enganche con ERPNext

`hooks.py`:

- `doctype_js` / `doctype_list_js`: overrides para Sales Invoice, Delivery Note,
  Purchase Invoice, Company, Print Format, Account, Sri Establishment.
- `app_include_js` / `app_include_css`: UI SRI global (botones, validación).
- `jinja.methods`: builders de XML usados por los formatos de impresión (RIDE).
- `doc_events` (**Xml Responses**): `validate`, `on_update`, `after_insert`.
- `on_session_creation`: `erpnext_ec.utilities.tools.on_login_auto` (aviso de
  configuración incompleta).
- `before_install` / `after_install`.
- **Sin** `override_doctype_class` ni `override_whitelisted_methods`.

Los **Custom Fields** se inyectan por el parche
`patches/v16_0/load_custom_fields.py`, que lee `fixtures/seed/*.json`. En v16
`sync_fixtures` importa automáticamente todos los `.json` de `fixtures/`, por lo
que los seeds viven en la subcarpeta `seed/` (no autoimportada) para no chocar
con el loader.

## 3. Cambios de migración a v16

### 3.1 Metadata y assets
- `pyproject.toml`: `requires-python >=3.14`, `frappe >=16.0.0,<17.0.0`.
- `requirements.txt`: se retiraron `xmlsig`, `xades` y `web3` (no usados; el
  firmador activo es `xades_tool_v4` con `lxml` + `cryptography`).
- `hooks.py`: eliminados hooks de v13 (`jenv`, `jenv_customizations`,
  `get_translated_dict`) y verificaciones de versión. Assets vía
  `app_include_js`/`app_include_css` (v16 no usa `bundles.json`).
- Eliminado `config/desktop.py` (mecanismo `get_data()` obsoleto).
- Parches movidos `patches/v15_0` → `patches/v16_0`.
- Código muerto eliminado: backups JS/Jinja, firmadores v1/v2/v3, `XadesToolV2`,
  `.py` generados por generateDS (usaban `basestring`), DocTypes duplicados/de
  prueba.

### 3.2 Cambios de comportamiento de v16
- **Item Wise Tax Detail**: v16 quitó el campo JSON `item_wise_tax_detail` de
  `Sales Taxes and Charges` y lo reemplazó por la tabla hija `Item Wise Tax
  Detail`. `get_full_items`, `get_full_items_purchase_receipt` y
  `get_full_items_purchase_invoice` leen ahora esa tabla.
- **Agregados SQL**: `settings_tools.get_last_sequencial_found` usaba
  `fields=["MAX(secuencial) as max_secuencial"]`, rechazado por v16; ahora usa
  `frappe.db.sql`.
- **`create_custom_fields`**: los `fieldname` se guardan en minúsculas; el
  cargador normaliza el nombre antes de crear/actualizar.

### 3.3 Generación de XML
- **Resolución de XSD**: los XSD de retención/NC/ND/liquidación importan el
  esquema `xmldsig` por URL remota (lxml no puede resolverla). Se agregó un
  `Resolver` local hacia `utilities/xsd/xmldsig-core-schema.xsd`.
- **Orden de validación**: se omiten valores `None`, se eliminan elementos
  vacíos **antes** de validar, y `validate_xml` devuelve booleano.

### 3.4 Firma electrónica (`xades_tool_v4`)
- El bloque XAdES insertado dejaba un `tail` de espacios; al aplicar la
  transformación *enveloped-signature* el digest del documento cambiaba y la
  firma era inválida. Se aplica `.strip()` al bloque antes de insertarlo.
- Se verifica localmente `SignatureValue` (RSA‑SHA1) y el digest de
  `#comprobante`.
- `XadesSignerCmd` requiere .NET 6 (no instalado); el sitio se configura con
  `Regional Settings Ec.signature_tool = "Python Native (With Fails)"`.

### 3.5 Alineación con la Ficha Técnica SRI v2.34
- **Factura normal vs SRI**: `Company.facturacion_electronica` (interruptor
  maestro) y `Sales Invoice.emitir_sri` (por documento). `estab`/`ptoemi` son
  obligatorios solo cuando `emitir_sri` está marcado; se quitó el default
  inválido `ptoemi="002"`.
- **Retención**: `<codigo>` toma el código de impuesto del SRI (campo
  `codigo`), no el índice de fila.
- **Nota de Débito**: `codDoc=05` y estructura según la Ficha
  (`impuestos`, `valorTotal`, `pagos`, `motivos/motivo/razon/valor`).
- **RIMPE**: `contribuyenteRimpe` condicional, según
  `Company.tipo_contribuyente` (incluye `CONTRIBUYENTE NEGOCIO POPULAR - RÉGIMEN
  RIMPE`, 45 caracteres).
- **Liquidación**: totales de reembolso solo cuando `codDocReembolso = 41`.
- **Formato**: importes y cantidades con 2 decimales.
- **Secuencias**: `estab`/`ptoemi` se normalizan de Link (`name`) a
  `record_name` antes de `setSecuencial`; el XML usa `001`/`002`.
- **Campos adicionales**: `direccionComprador`, `guiaRemision`, `placa`,
  `dirEstablecimiento`, `rise`, `contribuyenteEspecial`, y en `infoAdicional`
  "Gran Contribuyente" y "RUC Proveedor".

## 4. Modelo de datos

### Company (Custom Fields opcionales)
`facturacion_electronica`, `tipo_contribuyente`
(Régimen General / RIMPE Emprendedor / RIMPE Negocio Popular / Gran
Contribuyente), `resolucion_gran_contribuyente`, `regimen_microempresas`,
`ruc_proveedor_sistemas`, `agenteretencion`, `contribuyenteespecial`,
`obligadocontabilidad`, `nombrecomercial`, `sri_active_environment`,
`sri_signature`, `use_simulation_mode`, `regional_settings_ec`, formatos RIDE y
plantillas de email.

### Sales Invoice (Custom Fields)
`emitir_sri`, `estab`, `ptoemi`, `secuencial`, `datos_sri`,
`numeroautorizacion`, `fechaautorizacion`, `coddocmodificado`, `docidsri`,
`fechaemisiondocsustento`, `numdocsustento`, `motivo`, `sri_estado`,
`sri_response`, `placa`. Los campos SRI tienen
`depends_on: eval:doc.emitir_sri`.

### DocTypes propios
`Sri Environment`, `Sri Establishment`, `Sri Ptoemi`, `Sri Sequence`,
`Sri Signature`, `Sri Type Doc`, `Sri Type Id`, `Sri External Establishment`,
`Sri Establishment Link`, `Regional Settings Ec`, `Xml Responses`,
`Purchase Withholding Sri Ec`, `Purchase Taxes and Charges Ec`,
`Campo Adicional`, `Detalle Impuestos`, `Reembolso Detalle`.

## 5. Flujo de emisión (Factura)

1. El usuario marca `emitir_sri`.
2. `build_doc_fac` arma los datos (compañía, cliente, ítems, impuestos, pagos).
3. `build_doc_fac_sri` transforma al formato del SRI.
4. `XMLGenerator` genera el XML y valida contra `factura_V1/1/0.xsd`.
5. `xades_tool_v4.sign_xml` firma (XAdES‑BES, RSA‑SHA1).
6. `sri_ws` envía al SRI (o simula con `use_simulation_mode`).

## 6. Pruebas

```bash
bench --site <sitio> set-config allow_tests true
bench --site <sitio> run-tests --app erpnext_ec --skip-before-tests
```

- `test_sri_xml.py`: valida FAC/GRS/CRE/NCR/LIQ contra los XSD, la alineación
  con la Ficha v2.34 y la creación de facturas no‑SRI.
- `test_sri_signing.py`: firma con certificado autofirmado y verifica
  `SignatureValue` y el digest enveloped.

## 7. Desarrollo

```bash
bench get-app https://github.com/ocazo/erpnext_ec16
bench --site <sitio> install-app erpnext_ec
bench build --app erpnext_ec
```

Tras cambiar fixtures, volver a aplicar los Custom Fields:

```bash
bench --site <sitio> execute erpnext_ec.patches.v16_0.load_custom_fields.execute
```
