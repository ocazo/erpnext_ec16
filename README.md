# ERPNext Ec

Localización de **Ecuador** para **ERPNext v16**: facturación electrónica del
**SRI** (comprobantes electrónicos), retenciones, notas de crédito/débito, guías
de remisión y liquidaciones de compra.

Repositorio: <https://github.com/ocazo/erpnext_ec16>

## Compatibilidad

| Componente | Versión |
|---|---|
| ERPNext / Frappe Framework | v16 |
| Python | 3.14 |

La compatibilidad con Frappe/ERPNext v13/v14/v15 fue **eliminada**.

## Documentación

- [Guía de instalación y uso](docs/FUNCTIONAL.md)
- [Documentación técnica / cambios de migración](docs/TECHNICAL.md)
- [Changelog](CHANGELOG.md)

## Instalación rápida

```bash
cd ~/frappe-bench

# 1) Obtener la app
bench get-app https://github.com/ocazo/erpnext_ec16

# 2) Instalar en el sitio (ERPNext debe estar instalado)
bench --site <tu-sitio> install-app erpnext_ec

# 3) Compilar assets
bench build --app erpnext_ec
```

Las dependencias Python (`suds`, `python-barcode`, `dicttoxml`, `xmltodict`,
`pycryptodome`) se instalan en el entorno del bench al hacer `get-app`. Si hace
falta instalarlas manualmente:

```bash
./env/bin/pip install -r apps/erpnext_ec/requirements.txt
```

## Uso básico

1. Configure la **Compañía**: pestaña SRI (RUC, ambiente, firma, régimen,
   resolución de gran contribuyente, RUC del proveedor de sistemas, etc.).
2. Cree la **Firma Electrónica** (`.p12` + contraseña) y enlácela en la Compañía.
3. Cree **Establecimientos** y sus **Puntos de Emisión**.
4. Genere **Secuencias** y **Formatos de impresión** SRI.
5. Revise **Sri → Configuración SRI** hasta que el estado sea **Ready**.

Para emitir una **Factura de Venta**:

- Marque **Emitir al SRI** (`emitir_sri`) para generar el comprobante electrónico
  (XML + firma + envío), o
- **Desmárquelo** para emitir una factura **normal**, sin validaciones ni campos
  del SRI.

## Funcionalidad

- Factura electrónica (FAC), Nota de Crédito (NCR), Nota de Débito (NDE),
  Guía de Remisión (GRS), Comprobante de Retención (CRE) y Liquidación de
  Compra (LIQ).
- Generación de XML conforme a la **Ficha Técnica SRI v2.34** y validación
  contra los XSD oficiales.
- Firma electrónica **XAdES-BES** (firmador Python incluido; `XadesSignerCmd`
  requiere .NET 6).
- Envío/autorización al SRI (ambiente de desarrollo/producción) y modo
  simulación.
- Página **Configuración SRI** para revisar el estado de la configuración en
  cualquier momento.

## Licencia

MIT. Ver [license.txt](license.txt).
