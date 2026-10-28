# ADR-009: tienda del cliente con compra simulada y promociones aprobadas

> Actualización 21-10-2026 solicitada por Axel: la tienda es el proyecto independiente `tienda/`; solo se comunica con FoodSave por API HTTP. Payme Flex se integra exclusivamente en preproducción con cuatro botones. El inventario real sigue pendiente de T01/T03/T04. Prevalece ADR-010 y el contrato Payme; las ubicaciones y pagos simulados descritos abajo son el corte previo.


**Estado:** aceptada para diseño el 20-10-2026 por solicitud de Max Rojas, autor y coordinador del bloque Tienda. **Sin implementación** en este corte: primero se revisa la documentación. Amplía [ADR-006](ADR-006-identidades-lotes-pronosticos.md), [ADR-007](ADR-007-automatizaciones-demo.md) y [ADR-008](ADR-008-pedidos-desde-el-plan.md). Ante contradicción sobre ventas a clientes, precios publicados o promociones visibles, prevalece esta decisión. Contrato: [contrato-tienda.md](../../api/contrato-tienda.md).

## Contexto

El prototipo solo modifica stock por apertura, ajustes y recepción, y las promociones son sugerencias internas que nadie publica. Se quiere mostrar el efecto de las automatizaciones desde el lado del cliente: un cliente compra, el stock baja, el motor evalúa una promoción, el administrador la aprueba y el cliente la ve.

## Decisión

1. **Módulo separado.** Backend en `backend/app/modules/tienda/`, rutas del cliente bajo `/api/v1/tienda/*` y rutas administrativas bajo `/api/v1/tienda-admin/*`. La interfaz del cliente vivirá en `frontend/src/app/tienda/` con layout propio, sin la barra administrativa. Tienda consume Productos, Inventario, Promociones, Negocio y el motor **solo por interfaces públicas**.
2. **Cliente con cuenta de Google.** El cliente inicia sesión con Google (Google Identity Services). El backend verifica el ID token con `GOOGLE_CLIENT_ID`, exige `email_verified` y emite un token propio de cliente con audiencia `tienda`. Un token de cliente nunca accede a rutas administrativas, y un token administrativo no compra como cliente. Los roles `ADMINISTRADOR` y `OPERADOR` no cambian.
3. **Pago simulado y fin de la operación.** El checkout pide nombre de quien recibe, celular de contacto y dirección de envío, y un método simulado: tarjeta o billetera digital (Yape o Plin). El pago se registra como aprobado. Con tarjeta, la interfaz pide número, titular, vencimiento y CVV y los valida en el navegador (Luhn, marca, fecha), pero **esos datos nunca salen del navegador**: no se envían a la API, no se guardan (ni en la base ni en `localStorage`) y no se registran. Tampoco se llama a pasarelas. *(Actualizado 21-10-2026 a pedido de Max Rojas; antes la interfaz no pedía campos de tarjeta.)* La operación termina al confirmar: el pedido queda `CONFIRMADO` como estado final.
4. **La compra descuenta stock real.** Confirmar un pedido crea movimientos `VENTA_TIENDA` por lote, en la misma transacción que el pedido, con asignación por fecha límite de venta más próxima (FEFO) y sin saldo negativo. Esto sustituye la regla "solo apertura, ajustes y recepción mueven stock" **únicamente para la tienda**. El plan y los pedidos a proveedores siguen sin mover stock.
5. **Las compras no alimentan Ventas ni ML.** Los pedidos de tienda no se escriben en `venta_diaria` ni se usan para entrenar o evaluar. El plan sí lee el stock resultante, porque consulta la disponibilidad vigente.
6. **Reloj de la tienda.** La configuración de la tienda define `modo_fecha`: `ESCENARIO` (fecha fija elegida por el administrador) o `ACTUAL` (fecha de hoy en la zona del negocio). La hora local real del negocio se combina con esa fecha para obtener el instante efectivo de cada movimiento. El administrador puede abrir lotes nuevos de producto con fechas actuales por una interfaz pública de Inventario.
7. **Precios en soles.** Los precios se guardan versionados en PostgreSQL con la moneda del negocio (`PEN`). Se cargan por CSV o a mano. Sin precio vigente, un producto no se publica. No se inventan precios.
8. **Promociones con aprobación.** Toda venta de tienda reserva `EVALUAR_PROMOCION`, igual que un ajuste. Una evaluación con `proponer=true` queda pendiente hasta que un administrador la **aprueba** (se publica) o la **rechaza** con motivo. La promoción publicada aplica solo a las unidades del lote evaluado, mientras ese lote tenga saldo y siga vigente. No hay publicación automática en este corte.
9. **Stock visible en tres estados.** El cliente ve `DISPONIBLE`, `ULTIMAS_UNIDADES` o `AGOTADO`, nunca la cantidad exacta. El stock desconocido o sin fecha límite de venta se muestra como `AGOTADO` y no se vende. La pantalla consulta cada 5 segundos; no se usa SSE ni WebSocket en este corte.

## Consecuencias

- Migración aditiva nueva (prevista `0019_tienda`). No reescribe migraciones aplicadas. Amplía el CHECK de `movimiento_inventario.tipo` con `VENTA_TIENDA`.
- Inventario debe publicar `retirar_para_tienda` y `abrir_lote_producto`; Promociones debe generalizar la reserva tras un movimiento y publicar la aprobación. Son fronteras de Vera: Max las implementa por coordinación, con contrato y pruebas, sin cambiar la lógica existente de ajustes.
- Datos personales (correo, celular, dirección) solo los ven su dueño y los administradores. No se escriben en logs ni en trazas del motor.
- El login de Google necesita red y un cliente OAuth registrado con el origen local. En CI y pruebas se usa un verificador falso.

## Fuera de esta decisión

Pasarelas de pago, facturación, comprobantes electrónicos, cálculo de envío, impuestos desglosados, estados posteriores a `CONFIRMADO` (preparación, despacho, entrega), cancelaciones, reembolsos y devoluciones, notificaciones al cliente por Telegram o WhatsApp, publicación automática de promociones, producción física y uso de las ventas de tienda en ML. Cada una requiere una decisión posterior.
