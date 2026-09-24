# Backend

Aquí irá la API FastAPI. `app/modules/` agrupa los dominios; `app/core/` tendrá configuración y seguridad; `app/workers/` alojará tareas asíncronas; `app/integrations/` contendrá adaptadores externos. Las pruebas generales irán en `tests/`.

En cada módulo, la estructura prevista es `router.py`, `service.py`, `repository.py`, `models.py`, `schemas.py`, `dependencies.py`, `exceptions.py` y `tests/`. Estos archivos aparecerán al implementar cada módulo, con código y pruebas reales.

El documento maestro también propone `pyproject.toml`, `alembic.ini`, `Dockerfile` y `app/main.py`. Se crearán junto con el primer backend ejecutable.
