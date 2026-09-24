# Servidor

Aquí irá la API FastAPI. `aplicacion/modulos/` agrupa los dominios; `aplicacion/nucleo/` tendrá configuración y seguridad; `aplicacion/trabajos_asincronos/` alojará tareas asíncronas; `aplicacion/integraciones/` contendrá adaptadores externos. Las pruebas generales irán en `pruebas/`.

En cada módulo, la estructura prevista es `rutas.py`, `servicio.py`, `repositorio.py`, `modelos.py`, `esquemas.py`, `dependencias.py`, `errores.py` y `pruebas/`. Estos archivos aparecerán al implementar cada módulo, con código y pruebas reales.

El [README principal](../README.md) también propone `pyproject.toml`, `alembic.ini`, `Dockerfile` y `aplicacion/principal.py`. Se crearán junto con el primer servidor ejecutable.
