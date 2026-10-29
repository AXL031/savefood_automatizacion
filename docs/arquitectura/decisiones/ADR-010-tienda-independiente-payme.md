# ADR-010: tienda como proyecto independiente y Payme en preproducción

> **Actualización 28-10-2026:** la implementación de catálogo, promociones aprobadas, reservas y ventas TIENDA por HTTP se documenta en [el contrato vigente](../../api/contrato-integracion-tienda.md). Sustituye las menciones históricas de integración pendiente de este documento para esas capacidades. El modo ejemplo sigue sin afectar inventario; Payme continúa solo en preproducción. Cierre diario, simuladores y ML siguen pendientes.

**Aceptada 21-10-2026**, por instrucciones expresas de Axel en esta sesión.
Actualiza la ubicación y el alcance de pagos de ADR-009. Autor: Codex para Axel,
coordinación A04; se conserva la autoría del prototipo de Rojas.

La tienda vive en `tienda/` con frontend, API de pagos, dependencias, configuración,
Compose y almacenamiento propios. Puede compilarse fuera de este repositorio.
Su única vía de comunicación con FoodSave es su API HTTP pública: nunca importa
sus servicios/modelos, comparte su sesión administrativa ni consulta su base.
El API de cliente de FoodSave (`/api/v1/tienda/*`) sigue siendo el contrato de
integración, separado del API de pagos de la tienda (`/api/v1/pagos/*`).

Payme Flex solo utiliza preproducción y cuatro instancias seleccionables por
botón, cada una con un método: CARD, YAPE, QR y PAGOEFECTIVO. Credenciales y token
permanecen en el backend de la tienda. Solo Consulta o S2S firmado confirman un
pago. No hay datos de tarjeta recogidos por formularios propios ni activación de
producción. El mock previo queda limitado al historial de demostración.

El catálogo sigue siendo de ejemplo: una prueba de pago no descuenta stock real,
no genera venta/entrega y no acredita integración T01/T03/T04. Antes de habilitar
compras conectadas se requiere acordar cotización/reserva por API, identidad del
integrador y confirmación idempotente/conciliación con FoodSave. Sin transacción
SQL compartida: FoodSave será responsable del movimiento de inventario y su
idempotencia; la tienda de la operación y el estado de pago. No enviar secretos
de Payme a FoodSave. No tratar un callback del navegador como orden de descuento.

Se trasladan rutas y recursos existentes, conservando sus URLs internas
`/tienda/*`. FoodSave mantiene una redirección al origen externo configurable por
`TIENDA_WEB_URL` (3101 local). Puertos, volumen y Compose de tienda son distintos.
No se añade migración Payme a la base de FoodSave ni se altera su carga de datos.

[Configuración reproducible](../../../tienda/README.md) ·
[Contrato Payme](../../api/contrato-payme-pruebas.md)
