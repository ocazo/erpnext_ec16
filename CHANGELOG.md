# Changelog

## [migrate-v16] - ERPNext v16 / Python 3.14

### Changed
- `pyproject.toml`: `requires-python` bumped to `>=3.14`; `frappe` dependency
  range changed to `>=16.0.0,<17.0.0`.
- `requirements.txt`: dropped unused `xmlsig`, `xades` and `web3`. The active
  signer is `utilities/xades_tool_v4.py` (lxml + cryptography) and the external
  `utilities/apps/XadesSignerCmd`, so those packages were only pulled into the
  login/XML import path without being used.
- `hooks.py`: `app_license` set to `gpl-3.0` (matches `license.txt`).
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
- Custom fields defined in `fixtures/*.json` (Sales Invoice, Purchase Invoice,
  Company, Customer, Item, etc.) had typos (`inser_after`,
  `is_custom_field`) and had no loader under v16. A `load_custom_fields` patch
  now applies them idempotently with `create_custom_fields`.

### Added
- `CHANGELOG.md`.
- `erpnext_ec/tests/test_sri_xml.py`: validates generated Factura, Guía de
  Remisión, Comprobante de Retención, Nota de Crédito and Liquidación de Compra
  XML against the bundled SRI XSDs.

### Pending / not changed on purpose
- Fiscal logic and formatting (e.g. number formatting of `importeTotal`) was
  left untouched.
- Electronic signing (`.p12`, XAdES, SRI authorization) is not validated in
  this branch yet.

### Notes
- Backward compatibility with Frappe/ERPNext v13/v14/v15 has been dropped.
