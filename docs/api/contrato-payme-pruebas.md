# Payme Flex en preproducción · 21-10-2026

> **Actualización 28-10-2026:** la implementación de catálogo, promociones aprobadas, reservas y ventas TIENDA por HTTP se documenta en [el contrato vigente](contrato-integracion-tienda.md). Sustituye las menciones históricas de integración pendiente de este documento para esas capacidades. El modo ejemplo sigue sin afectar inventario; Payme continúa solo en preproducción. Cierre diario, simuladores y ML siguen pendientes.

Ampliación expresa de Axel: integrar Payme para pruebas, con un botón por método.
Sustituye el pago local ficticio del checkout; no habilita cobros de producción ni
conecta el catálogo de ejemplo con inventario/Ventas/ML. Autor: Codex para Axel;
tienda bajo coordinación de Rojas, infraestructura de Cueva.

## Proyectos y frontera

La tienda es proyecto independiente (frontend 3101/API propia 8001), con Compose,
dependencias y datos propios. FoodSave solo se consume por HTTP. No imports ni DB
compartida. [ADR-010](../arquitectura/decisiones/ADR-010-tienda-independiente-payme.md)
y [arranque/configuración](../../tienda/README.md). El catálogo de ejemplo no requiere
FoodSave disponible. Las APIs reales de catálogo/stock/pedido siguen pendientes.

## Contrato antes de conectar consumidores

- Métodos exactos: `CARD`, `YAPE`, `QR`, `PAGOEFECTIVO`. Cada instancia de Flex recibe
  `display_settings.methods: [metodo]`. No captura de tarjetas propia ni PAN/CVV en API.
- Orígenes de red fijos de preproducción: auth/API Alignet y SDK `flex.dev.pay-me.cloud`.
  Secretos y Access Token solo en backend; navegador recibe nonce temporal/payload.
- Catálogo de prueba versionado en backend; cotización con Decimal/céntimos y moneda
  604/PEN. El navegador nunca decide cuánto se cobra. No utiliza precios/IDs del
  inventario administrativo; reserva y descuento de stock real siguen pendientes.
- Sesión de pago persistida con operación numérica única y snapshot de comprador,
  entrega, líneas y total. La clave UUID4 de checkout es una capacidad secreta del
  navegador: backend guarda su SHA-256. No equivale a identidad Google verificada.
- Solo Consulta autenticada del backend o notificación RSA/SHA-512 válida confirma
  pago. `meta.status.code`, abrir el formulario, cierre, QR/CIP generado y callback
  del navegador no autorizan una compra. Pendientes conservan estado y acceso.
- Repetición de clave/cuerpo devuelve la misma operación; cambiar solo `metodo`
  reutiliza ID, operación, importe y capacidad mientras siga `CREADO` sin ninguna
  transacción registrada. Otros cambios de cuerpo devuelven 409. Una operación
  con transacción registrada no cambia de método (409 `PAYME_PAGO_EN_CURSO`).
  Consulta/resultado sin la capacidad correcta devuelve 404.
- Intentos de transacción conservados; notificaciones idempotentes y fuera de orden
  no degradan un pago aprobado a pendiente. No hay reintento automático de cobro.
- Al alternar botones se termina el SDK anterior antes de preparar el siguiente,
  cada uno con un solo método. El borrador conserva su UUID aun si falla el nonce.
  El snapshot guarda los métodos efectivamente preparados: una respuesta tardía de
  un formulario anterior se verifica y conserva; no se admite un método que nunca
  se preparó. El resultado refleja el método real confirmado por Payme. Un callback
  recibido sin verificar bloquea temporalmente el cambio; el botón activo permite
  consultar el estado. Cerrar el SDK sin resultado permite volver a elegir.

## Rutas bajo `/api/v1/pagos`

| Ruta | Entrada / comportamiento |
|---|---|
| `GET /configuracion` | Solo disponibilidad, ambiente de pruebas y cuatro métodos; sin credenciales. |
| `POST /cotizar` | `{lineas:[{producto_id,cantidad}]}`; cotización del catálogo de prueba, sin efecto. |
| `POST /` | `clave_checkout` UUID4, método, líneas, comprador `{nombres,apellidos,correo}`, entrega; persiste operación, obtiene nonce y devuelve configuración Flex de un solo método. |
| `GET /{id}` | Capacidad en `Authorization: Bearer <clave_checkout>`; snapshot y resultado seguro del pago. |
| `POST /{id}/verificar` | Misma capacidad, `{transaction_id?:string}`; consulta Payme, contrasta comercio/operación/método/monto/moneda y persiste estado. |
| `POST /notificaciones` | Body crudo y header `signature`; verificación RSA PKCS1v15/SHA-512 con llave de preproducción; no acepta callbacks del navegador como evidencia. |

No se guardan respuestas completas del proveedor: solo identificador, estado,
fecha, huella del evento y datos de continuación permitidos (CIP/URL/expiración).
Sin credenciales, los cuatro métodos se muestran deshabilitados con estado de
configuración pendiente. Fallos de red no se presentan como pagos aprobados.

## Configuración y alcance de prueba

`PAYME_HABILITADO`, `PAYME_CLIENT_ID`, `PAYME_CLIENT_SECRET`, `PAYME_MERCHANT_CODE`;
llave pública S2S opcional por `PAYME_WEBHOOK_PUBLIC_KEY` si Payme rota la publicada.
Almacenamiento SQLite exclusivo del proyecto `tienda/`, volumen `pagos`; no hay
migración Payme en FoodSave ni conexión a su base. Credenciales en `tienda/.env`. Se requiere HTTPS público y registro con Payme para recibir
S2S desde fuera de localhost; Consulta permite revisar desde la página de estado.
Credenciales reales de preproducción y certificación por método quedan a cargo
del usuario; mocks no acreditan cobro externo.

## Referencias oficiales

- [Inicialización y métodos](https://docs.pay-me.com/checkout-web/flex/inicializar-el-componente)
- [Token](https://docs.pay-me.com/api-de-pagos/autenticacion), [nonce](https://docs.pay-me.com/checkout-web/flex/api-nonce)
- [Payload](https://docs.pay-me.com/checkout-web/flex/construccion-del-payload)
- [Consulta](https://docs.pay-me.com/payin/consulta), [S2S](https://docs.pay-me.com/payin/notificaciones)
- [PagoEfectivo pendiente](https://docs.pay-me.com/payin/autorizacion-pagoefectivo)


## Checkout invitado · ajuste solicitado por Axel

Sin inicio de sesión ni restricción Gmail para iniciar pagos sandbox. El checkout
muestra solo datos de entrega y método de pago; comprador con nombres/apellidos y
correo válido de cualquier proveedor como datos de facturación Payme. T02 Google
queda opcional en la navegación y separado del permiso de iniciar esta prueba.
Las rutas de checkout no aceptan ni exigen un token Google/administrativo.
