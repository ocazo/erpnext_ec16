# Guía de instalación y uso — ERPNext Ec

Localización de Ecuador para **ERPNext v16**. Este documento explica cómo
instalar, configurar y usar la facturación electrónica del SRI, y cómo emitir
facturas **sin** SRI.

## 1. Instalación

Requisitos: bench con **ERPNext v16** y **Python 3.14**.

```bash
cd ~/frappe-bench
bench get-app https://github.com/ocazo/erpnext_ec16
bench --site <tu-sitio> install-app erpnext
bench --site <tu-sitio> install-app erpnext_ec
bench build --app erpnext_ec
```

La instalación crea los DocTypes, los Custom Fields y los módulos
**Erpnext Ec** y **Erpnext Sri**.

## 2. Configuración

### 2.1 Compañía
En **Company** complete la pestaña de datos SRI:

| Campo | Descripción |
|---|---|
| RUC (`tax_id`) | RUC del emisor (13 dígitos) |
| Nombre Comercial | Nombre comercial del emisor |
| Obligado Contabilidad | Sí/No |
| Contribuyente Especial No | N.º de resolución (si aplica) |
| Agente Retención Resolución No | N.º de resolución (si aplica) |
| Tipo de contribuyente | Régimen General / RIMPE Emprendedor / RIMPE Negocio Popular / Gran Contribuyente |
| Resolución Gran Contribuyente | N.º de resolución (si es Gran Contribuyente) |
| Régimen Microempresas | Si aplica |
| RUC Proveedor de Sistemas | RUC de su proveedor de facturación electrónica |
| Ambiente Sri | `DES` (pruebas) o `PRO` (producción) |
| Firma Electrónica | Registro de firma (ver 2.2) |
| Facturación electrónica SRI | Interruptor maestro de emisión electrónica |
| Usar modo simulación | Para probar sin enviar al SRI |

### 2.2 Firma electrónica
1. Vaya a **Sri Signature** → **Nuevo**.
2. Complete **RUC**, **Contraseña** (clave del `.p12`) y adjunte el archivo
   **P12**.
3. Guarde y enlácelo en la Compañía (campo **Firma Electrónica**).

### 2.3 Establecimiento y punto de emisión
1. Vaya a **Sri Establishment** → **Nuevo**: enlace la compañía, indique
   **record_name** (p. ej. `001`) y descripción.
2. En la tabla **Puntos de emisión** agregue el punto (p. ej. `002`) y su
   ambiente (`DES`/`PRO`).

### 2.4 Secuencias, formatos de impresión y cuentas
En **Sri → Configuración SRI** hay accesos directos. Ejecute (una sola vez):

- **Secuencias**: botón para crear las secuencias SRI.
- **Formatos de impresión**: botón para crear los RIDE (Factura, Retención,
  Guía) y plantillas de email.
- **Cuentas contables**: importar/crear cuentas con códigos SRI.

### 2.5 Verificar configuración
Abra **Sri → Configuración SRI**. Debe mostrar el banner
**"Configuración compatible con el SRI"** y el detalle por compañía
(ambiente, configuración regional, secuencias, formatos, cuentas, firma y
expiración, estado **Ready**). El botón **Revalidar** repite la verificación.

## 3. Uso: Factura de Venta

### 3.1 Factura electrónica (SRI)
1. **Sales Invoice → Nuevo**.
2. Marque **Emitir al SRI** (`emitir_sri`).
3. Complete cliente, ítems e impuestos. Se habilitan **estab** y **ptoemi**
   (se autoseleccionan si hay configuración).
4. Guarde y **Envíe**. Aparecen las acciones SRI:
   - **Enviar al SRI** (firma y envía/simula)
   - **Descargar XML** / **Descargar PDF**
5. El estado de autorización queda en el documento (`numeroautorizacion`,
   `sri_estado`, `sri_response`).

### 3.2 Factura normal (sin SRI)
1. **Sales Invoice → Nuevo**.
2. **Deje desmarcado** **Emitir al SRI**.
3. Complete la factura con normalidad: **no** se exige `estab`/`ptoemi` ni
   aparecen acciones SRI. Guarde y envíe como cualquier factura de ERPNext.

> El interruptor maestro **Company → Facturación electrónica SRI** define el
> valor por defecto de **Emitir al SRI** en cada factura nueva. Si está
> apagado, las facturas nacen como normales.

## 4. Otros comprobantes

| Documento | Uso |
|---|---|
| **Nota de Crédito** | Sales Invoice con `is_return` (devuelve) |
| **Nota de Débito** | Sales Invoice con `is_debit_note` |
| **Guía de Remisión** | Delivery Note (usa Delivery Trip para transportista/placa) |
| **Comprobante de Retención** | Purchase Withholding Sri Ec |
| **Liquidación de Compra** | Purchase Invoice |

Todos comparten el botón **Enviar al SRI** cuando corresponden a un documento
electrónico.

## 5. Modo simulación

Active **Company → Usar modo simulación** para probar el flujo completo
(generación de XML, firma y respuesta simulada) sin enviar al SRI. Al terminar
las pruebas, desactívelo para enviar de verdad.

## 6. Preguntas frecuentes

- **"Configuración incompatible con el SRI"**: revise la página
  **Configuración SRI**; indica exactamente qué falta (ambiente, configuración,
  secuencias, formatos, cuentas, firma).
- **No aparece "Emitir al SRI"**: verifique que la Compañía tenga **Facturación
  electrónica SRI** activa o marque el campo en la factura.
- **La firma no firma**: el firmador incluido es el Python nativo. Configure
  **Regional Settings Ec → Herramienta de firma = Python Native**. El firmador
  externo `XadesSignerCmd` requiere el runtime .NET 6.
- **Error de secuencial**: cree las **Secuencias SRI** y verifique
  **Establecimiento/Punto de emisión**.

## 7. Pendientes conocidos

Algunos requisitos **condicionales** de la Ficha Técnica v2.34 aún no se
generan automáticamente: `valorDevolucionIva` (devolución de IVA),
`codigoAuxiliar` (materiales de construcción / transporte), `maquinaFiscal`
(comprobantes de máquina fiscal) y `regimenMicroempresas`. No afectan a la
facturación estándar. La firma se validó en modo **simulación**, no contra el
sandbox del SRI.
