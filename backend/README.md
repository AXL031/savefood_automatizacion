# Servidor

> Guía vigente: [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md). Responsable de coordinación: **Axel Cueva**. Tareas, dependencias y avances se detallan en la guía local.

La API FastAPI incluye acceso y roles, negocio, catálogos/ventas, carga inicial, modelos y evaluación, inventario, recetas/planes, compras/Telegram, promociones sugeridas y reportes. `app/modules/` agrupa los dominios; `app/core/` mantiene sesión y seguridad; `app/workers/` registra manejadores y despacho durable; `app/integrations/` contiene el adaptador Telegram. Las pruebas van en `tests/`. Producción física, pagos y recepción no forman parte del prototipo.

Cada módulo conserva reglas y persistencia de su dominio y publica interfaces para consumidores. Los servicios que participan en una carga o ejecución comparten sesión y no confirman por separado. Consultar [contratos](../docs/api/contratos.md), guías locales y registros de avance para distinguir implementación de evidencia de integración.

El [README principal](../README.md) explica Compose y Alembic. La imagen instala el extra `ml`; `model_artifacts` permite que el worker escriba el artefacto y la API lo lea. La cadena de migraciones llega a `0016_nombre_comercio`; no reescribir revisiones aplicadas. Una imagen construida no acredita el estado de una instalación ni un envío real. Pruebas y límites actuales en [Bohorquez](../docs/equipo/avances/bohorquez.md) y [Cueva](../docs/equipo/avances/cueva.md).
