# Changelog

## [migrate-v16] - ERPNext v16 / Python 3.14

### Changed
- `pyproject.toml`: `requires-python` bumped to `>=3.14`; `frappe` dependency
  range changed to `>=16.0.0,<17.0.0`.
- `requirements.txt`: dropped unused `xmlsig`, `xades` and `web3`. The active
  signer is `utilities/xades_tool_v4.py` (lxml + cryptography) and the external
  `utilities/apps/XadesSignerCmd`, so those packages were only pulled into the
  login/XML import path without being used.
- `hooks.py`: `app_license` kept as `mit` (matches `license.txt`; the original
  README's GPLv3 text was unedited ERPNext boilerplate).
- Removed legacy hooks not supported in v16 (`jenv`, `jenv_customizations`,
  `get_translated_dict`) and version checks (`is_frappe_above_v12/v13/v14`).
- Assets keep using `app_include_js` / `app_include_css` (the v16 mechanism);
  the `bundles.json` mechanism is not used by Frappe v16.
- Removed `config/desktop.py` and `config/erpnext_ec.py`, which relied on the
  v13 `get_data()` desktop mechanism that no longer exists.
- Patches moved from `patches/v15_0` to `patches/v16_0`; `patches.txt`,
  `install.py`, `settings_tools.py` and `run_*.sh` updated accordingly.
- Removed the obsolete `client_scripts` patch (the app now injects JS through
  `doctype_js` / `doctype_list_js`).
- Removed dead code: `public/js/backup`, `public/jinja/backup`,
  `utilities/backup`, `utilities/test.py`, legacy signers
  (`xades_tool_v1/v2/v3`, `XadesToolV2`), the generateDS Python files under
  `utilities/xsd` (py2 `basestring`), duplicate `purchase_invoice/` and unused
  `sales_invoice/` doctype folders, and test/backup doctypes/fixtures.

### Fixed (ERPNext v16 behaviour changes)
- **Item-wise taxes**: ERPNext v16 removed the `item_wise_tax_detail` JSON field
  from `Sales Taxes and Charges` and introduced the `Item Wise Tax Detail` child
  table on the transaction. `get_full_items`,
  `get_full_items_purchase_receipt` and `get_full_items_purchase_invoice` were
  updated to read the new child table. This is required for the SRI
  per-item `<impuestos>` block to be emitted.
- **XSD loading**: several bundled SRI XSDs import the xmldsig core schema
  through a remote URL that lxml cannot fetch, which made
  `comprobanteRetencion`, `notaCredito`, `notaDebito` and `liquidacionCompra`
  schemas fail to load. A local resolver now maps those imports to the bundled
  `utilities/xsd/xmldsig-core-schema.xsd`.
- **XML generation**: `None` values are skipped and empty elements are removed
  before XSD validation (previously the literal string `None` was serialized
  and validation ran before pruning). `validate_xml` now returns a boolean.
- Custom fields defined in `fixtures/seed/*.json` (Sales Invoice, Purchase
  Invoice, Company, Customer, Item, etc.) had typos (`inser_after`,
  `is_custom_field`) and had no loader under v16. A `load_custom_fields` patch
  now applies them idempotently with `create_custom_fields`.
- **Sequences**: `settings_tools.get_last_sequencial_found` used
  `frappe.get_list(..., fields=["MAX(secuencial) as max_secuencial"])`, which
  v16 rejects ("SQL functions are not allowed as strings in SELECT"). Replaced
  with a `frappe.db.sql` aggregate.
- **Signing (`xades_tool_v4`)**: the inserted XAdES block carried a leading and
  trailing whitespace tail, so removing the `Signature` element during the
  enveloped-signature transform changed the document digest and invalidated the
  signature. The block is now stripped before insertion; the reference digest
  matches and the signature verifies (RSA-SHA1).
- The external `XadesSignerCmd` requires the .NET 6 runtime, which is not
  installed here, so signing uses the bundled Python signer
  (`Regional Settings Ec.signature_tool = "Python Native (With Fails)"`).

### Added
- `CHANGELOG.md`.
- `erpnext_ec/tests/test_sri_xml.py`: validates generated Factura, Guía de
  Remisión, Comprobante de Retención, Nota de Crédito and Liquidación de Compra
  XML against the bundled SRI XSDs, plus regression tests for the Ficha Técnica
  v2.34 alignment and for non-SRI invoices.

### Ficha Técnica SRI v2.34 alignment
- **Non-SRI invoices**: `Company.facturacion_electronica` (master switch) and
  `Sales Invoice.emitir_sri` let the app run with the localization installed and
  still issue normal (non-electronic) sales invoices. `estab`/`ptoemi` are only
  mandatory when `emitir_sri` is set, the invalid `ptoemi` default (`002`) was
  removed, and SRI buttons/actions are hidden for non-electronic documents.
- **Retention**: `<codigo>` now uses the SRI tax code (from the withholding
  account) instead of the child row index.
- **Debit note**: `codDoc` set to `05` and the document rebuilt per the Ficha
  (`impuestos`, `valorTotal`, `pagos`, `motivos/motivo/razon/valor`).
- **RIMPE**: `contribuyenteRimpe` is conditional and driven by
  `Company.tipo_contribuyente`, including RIMPE Negocio Popular (45 chars).
- **Liquidación**: reembolso totals are omitted when `codDocReembolso` is not 41.
- **Formatting**: monetary/quantity values emitted with 2 decimals.
- **Sequences**: `estab`/`ptoemi` Link values are normalised to `record_name`
  before `setSecuencial`, so sequences are assigned and the XML uses `001/002`.
- **Additional fields**: `direccionComprador`/`guiaRemision` (factura),
  `dirEstablecimiento`/`rise` (guía), `dirEstablecimiento`/`contribuyenteEspecial`
  (retención); `placa` (transporte); Gran Contribuyente and RUC Proveedor in
  `infoAdicional`.
- New optional Company fields: `facturacion_electronica`, `tipo_contribuyente`,
  `resolucion_gran_contribuyente`, `regimen_microempresas`,
  `ruc_proveedor_sistemas`.

### Usability and permissions fixes
- **v16 auto-fixtures**: `sync_fixtures` imports every `fixtures/*.json`
  automatically, which conflicted with the Custom Field loader. Seeds were moved
  to `fixtures/seed/*.json` (subfolder, not auto-imported) and the loader was
  updated.
- **Permissions**: added read access for role `All` to the SRI catalogues
  (Sri Environment, Sri Establishment, Sri Ptoemi, Sri Sequence, Sri Type Doc,
  Sri Type Id, Sri External Establishment, Sri Establishment Link,
  Regional Settings Ec, Xml Responses) and read for `Accounts Manager` on
  `Sri Signature`.
- **Emitir al SRI**: fixed `PermissionError: Sri Ptoemi.parent` (v16 forbids
  filtering child tables by `parent` from the client API). Default
  establishment/emission point are now resolved server-side
  (`utilities.tools.get_sri_default_establishment`).
- **Puntos de Emisión**: added a standard **Script Report**
  `Puntos de Emision SRI`; the workspace shortcut pointed to a child DocType and
  returned 404.
- **`ptoemi` is now a Data field** (stores the SRI emission point code, e.g.
  `002`). A Link to the child DocType `Sri Ptoemi` cannot be searched in v16
  (`get_permitted_fieldnames` returns no fields for child tables without a
  parent), which caused "Insufficient Permission for Sri Ptoemi". A patch
  converts existing values from the child name to `record_name`.
- **Select permission**: link validation (`validate_link_and_fetch`) requires
  `select` (not only `read`); the SRI catalogues now grant `read`+`select` to
  role `All` (and to `Accounts Manager`/`System Manager` on `Sri Signature`).
- Fixed the **Puntos de Emisión** button inside the *Configuración SRI* page
  (routed to the child DocType list → 404); it now opens the report.

### Pending / not changed on purpose
- Some conditional annexes are not emitted yet: `valorDevolucionIva` (ANEXO 20),
  `codigoAuxiliar` (ANEXO 23/25), `maquinaFiscal` (ANEXO 13),
  `regimenMicroempresas`.
- Electronic signing is validated locally with simulation mode only; not yet
  tested against the SRI sandbox.

### Notes
- Backward compatibility with Frappe/ERPNext v13/v14/v15 has been dropped.
