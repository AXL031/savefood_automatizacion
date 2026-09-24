# Servidor

Aquí irá la API FastAPI. `app/modules/` agrupa los dominios; `app/core/` tendrá configuración y seguridad; `app/workers/` alojará tareas asíncronas; `app/integrations/` contendrá adaptadores externos. Las pruebas generales irán en `tests/`.

En cada módulo, la estructura prevista es `rutas.py`, `servicio.py`, `repositorio.py`, `modelos.py`, `esquemas.py`, `dependencias.py`, `errores.py` y `tests/`. Estos archivos aparecerán al implementar cada módulo, con código y pruebas reales.

El [README principal](../README.md) también propone `pyproject.toml`, `alembic.ini`, `Dockerfile` y `app/principal.py`. Se crearán junto con el primer servidor ejecutable.
