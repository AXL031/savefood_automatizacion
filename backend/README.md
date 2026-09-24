# Servidor

La API FastAPI inicial incluye conexión a PostgreSQL, autenticación básica, configuración del único negocio local y una tarea de prueba de Celery. `app/modules/` agrupa los dominios; `app/core/` contiene la sesión de datos y seguridad inicial; `app/workers/` aloja tareas asíncronas; `app/integrations/` contendrá adaptadores externos. Las pruebas generales van en `tests/`.

En cada módulo, la estructura prevista es `rutas.py`, `servicio.py`, `repositorio.py`, `modelos.py`, `esquemas.py`, `dependencias.py`, `errores.py` y `tests/`. Estos archivos aparecerán al implementar cada módulo, con código y pruebas reales.

El [README principal](../README.md) explica el arranque con Compose y Alembic. Las tablas de los demás dominios no existen todavía: cada responsable debe documentar su esquema y agregar su propia migración.
