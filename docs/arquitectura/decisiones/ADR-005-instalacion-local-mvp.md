# ADR-005: una instalación local por comercio en el MVP

**Estado:** Decisión del MVP.

## Decisión

FoodSave se instala localmente para un solo comercio y una sola sucursal. Cada instalación tiene su propia base PostgreSQL, su API, interfaz, cola de tareas y archivo de modelo. Las ventas, existencias, pronósticos y demás datos operativos permanecen en esa instalación. No hay una tabla de sucursales ni separación de comercios dentro de la misma base.

La tabla `negocio` contiene exactamente un registro con la identidad y configuración de ese comercio. Las tablas operativas no necesitan `negocio_id`. Los usuarios y roles pertenecen a esa instalación.

El CSV del experimento de predicción conserva `comercio_id` y `sucursal_id` como metadatos de intercambio. Al importar se acepta un único par de identificadores por instalación; esos campos no implican soporte para varias sucursales en PostgreSQL. Las fechas operativas son locales a la zona horaria configurada en `negocio` y los instantes de auditoría se guardan en UTC.

Para el prototipo universitario, [ADR-006](ADR-006-identidades-lotes-pronosticos.md) concreta que FoodSave guarda las ventas diarias y el stock en su base local. El dataset y el Excel estático son carga inicial de demostración; después de la carga no son una fuente de saldos paralela.

El sistema sigue funcionando sin internet para registrar datos y calcular pronósticos. La decisión posterior [ADR-008](ADR-008-pedidos-desde-el-plan.md) incorporó pedidos desde el plan y envío real a un chat de pruebas por Telegram. Esa salida requiere internet; si no está disponible, el pedido y el fallo quedan visibles y no se declara enviado.

## Fuera del MVP

La comercialización por suscripción requerirá un servicio de licencias externo y una política de uso sin conexión. No forma parte de la base operativa actual. Una futura instalación compartida por varios comercios o con varias sucursales exigirá un diseño y migración explícitos.

## Consecuencias

- El diagrama y el diccionario de datos del MVP describen una instalación independiente.
- Cada desarrollador usa su propia base local creada con Compose. Git comparte migraciones y datos ficticios de demostración, nunca el volumen de PostgreSQL ni secretos.
- Las rutas existentes `/negocios/actual` se refieren al único comercio de la instalación.
- [ADR-006](ADR-006-identidades-lotes-pronosticos.md) concreta la validación del par externo y el mapeo de SKU sin introducir múltiples comercios o sucursales en esta base.
