# Servidor

> Guía vigente: [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md). Responsable de coordinación: **Axel Cueva**. Tareas, dependencias y avances se detallan en la guía local.

La API FastAPI incluye PostgreSQL, acceso, configuración del único negocio local y el motor de automatizaciones con Beat, worker y recuperación. `app/modules/` agrupa los dominios; `app/core/` contiene la sesión de datos y seguridad; `app/workers/` aloja tareas asíncronas; `app/integrations/` contendrá adaptadores externos. Las pruebas generales van en `tests/`. Los manejadores de negocio aún no están conectados.

En cada módulo, la estructura prevista es `rutas.py`, `servicio.py`, `repositorio.py`, `modelos.py`, `esquemas.py`, `dependencias.py`, `errores.py` y `tests/`. Estos archivos aparecerán al implementar cada módulo, con código y pruebas reales.

El [README principal](../README.md) explica el arranque con Compose y Alembic. La imagen instala el extra `ml` de ejecución (pandas, NumPy, scikit-learn y CatBoost); el volumen `model_artifacts` se monta en `MODEL_ARTIFACT_DIR` para que el worker escriba el modelo y la API lo lea. Esto prepara el entorno de Kevin, sin declarar entrenado ni integrado un modelo. Las tablas de los demás dominios no existen todavía: cada responsable debe documentar su esquema y agregar su propia migración sobre `0001c_motor`.
