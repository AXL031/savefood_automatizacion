# ADR-005: una instalación local por comercio en el MVP

**Estado:** Decisión del MVP.

## Decisión

FoodSave se instala localmente para un solo comercio y una sola sucursal. Cada instalación tiene su propia base PostgreSQL, su API, interfaz, cola de tareas y archivo de modelo. Las ventas, existencias, pronósticos y demás datos operativos permanecen en esa instalación. No hay una tabla de sucursales ni separación de comercios dentro de la misma base.

La tabla `negocio` contiene exactamente un registro con la identidad y configuración de ese comercio. Las tablas operativas no necesitan `negocio_id`. Los usuarios y roles pertenecen a esa instalación.

El CSV del experimento de predicción conserva `comercio_id` y `sucursal_id` como metadatos de intercambio. Al importar se acepta un único par de identificadores por instalación; esos campos no implican soporte para varias sucursales en PostgreSQL. Las fechas operativas son locales a la zona horaria configurada en `negocio` y los instantes de auditoría se guardan en UTC.

El sistema sigue funcionando sin internet para registrar datos, calcular pronósticos y preparar pedidos. El envío a Telegram necesita internet: se registra como pendiente si falla la conexión y se reintenta. La aceptación por la API de Telegram y la confirmación del proveedor son estados diferentes. Para pruebas se usa un adaptador de Telegram; otros canales se agregarán detrás del mismo contrato.

## Fuera del MVP

La comercialización por suscripción requerirá un servicio de licencias externo y una política de uso sin conexión. No forma parte de la base operativa actual. Una futura instalación compartida por varios comercios o con varias sucursales exigirá un diseño y migración explícitos.

## Consecuencias

- El diagrama y el diccionario de datos del MVP describen una instalación independiente.
- Cada desarrollador usa su propia base local creada con Compose. Git comparte migraciones y datos ficticios de demostración, nunca el volumen de PostgreSQL ni secretos.
- Las rutas existentes `/negocios/actual` se refieren al único comercio de la instalación.
