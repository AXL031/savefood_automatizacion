# Avances — Kevin Bohorquez

**Responsable:** Kevin Bohorquez. **Bloque:** Modelo predictivo, evaluación histórica y dashboard. **Rama prevista:** `bohorquez`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md). Este archivo se actualiza al terminar cada avance significativo.

## Resumen vigente

- **Estado:** K01–K04 implementados y listos para integrar en el prototipo local; no se declara integración con el plan de Max ni con la inicialización E03.
- **Punto de partida alcanzado:** Entrenamiento desde historial E01, artefacto CBM versionado y verificado, inferencia persistida con 13 características temporales, backtest por fecha/revisión, API protegida y panel histórico. El piloto tiene una versión nueva `piloto-q65v2-*` que selecciona iteración con el mismo cuantil 0.65 usado para entrenar. En PostgreSQL/Compose, 4 047 pares evaluables dieron 66 de 90 días con total pronosticado superior al real; la versión anterior se conserva para comparación.
- **Contrato disponible:** [artefacto ML](../../../foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md), [API y servicios](../../api/contratos.md#ventas--pronósticos) y [política de evaluación](../../../foodsave-ml/POLITICA_EVALUACION.md).
- **Entrega a consumidores:** `generar_corrida`/`obtener_pronosticos` y `solicitar_evaluacion_corrida` reciben la sesión del plan sin confirmarla; API `/pronosticos/*`, páginas `/pronosticos` y `/panel`, y adaptadores A03 para preparación/evaluación.
- **Bloqueos:** el CSV piloto ya dispara preparación y evaluación desde la carga web parcial de Edu; falta E03 completo y que Max consuma la corrida en su plan. No se ha probado el flujo plan/pedido.
- **Siguiente paso:** integrar E03 completo y M02 con prueba de transacción compartida; verificar el recorrido en otra computadora.

| Tarea | Estado de seguimiento |
|---|---|
| K01 · Extraer entrenamiento reutilizable | LISTO_PARA_INTEGRAR; entrenó CSV piloto desde E01 en PostgreSQL |
| K02 · Implementar inferencia y persistencia | LISTO_PARA_INTEGRAR; Max aún no consume el servicio |
| K03 · Implementar evaluación histórica | LISTO_PARA_INTEGRAR; backtest PostgreSQL con 4 047 pares |
| K04 · Construir dashboard y vistas de pronóstico | LISTO_PARA_INTEGRAR; API respondió en PostgreSQL y frontend compiló |

## Bitácora

### K01/K03 · Preferencia moderada por pronóstico superior

- **Fecha/hora y zona:** 2026-09-29 (America/Lima).
- **Autor y responsable del bloque:** Codex por solicitud de Axel, trabajando en el bloque de Kevin Bohorquez; no atribuye esta corrección a Kevin.
- **Tareas y estado:** K01/K03, LISTO_PARA_INTEGRAR para el piloto histórico; calidad futura sin validar.
- **Comportamiento disponible:** `artefacto.py` conserva `Quantile:alpha=0.65` y usa la misma pérdida como `eval_metric` para escoger la iteración. Antes usaba MAE para esa selección. Se entrenó la nueva versión `piloto-q65v2-554d4ae35f90`, se evaluó automáticamente y se conservó `piloto-554d4ae35f90` con sus corridas originales. La inferencia sigue redondeando, limitando a cero y excluyendo historial insuficiente/ventas ausentes como antes.
- **Archivos clave:** `foodsave-ml/artefacto.py`, [experimento](../../../foodsave-ml/EXPERIMENTOS_CATBOOST.md), [contrato](../../../foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md), [versión desde la carga](sanchez.md).
- **Contrato/ejemplo:** `PREPARAR_MODELO` con `version_modelo="piloto-q65v2-554d4ae35f90"` guarda otro CBM; `EVALUAR_MODELO` produce backtest de esa versión. El consumidor toma el último modelo `LISTO_DEMO` salvo que pida un `modelo_id` concreto.
- **Configuración/migraciones:** sin migración; imágenes locales de API y worker reconstruidas, volumen y modelos anteriores conservados.
- **Pruebas ejecutadas:** comparación de cuantiles 0.65, 0.7, 0.72, 0.75, 0.8, 0.85 y 0.9 con selección cuantílica en validación. La nueva versión real en PostgreSQL completó `PREPARAR_MODELO` y `EVALUAR_MODELO`: 92 corridas, 4 047 pares evaluables, MAE 4.448 y WAPE 24.20%. En los 90 días evaluables, el total quedó por debajo 24 veces y por encima 66, frente a 52/38 en la versión anterior; faltantes 6 840 frente a 14 940 y sobrantes 11 161 frente a 9 410. Suite backend: 27 passed, 8 skipped, 6 subtests passed. La prueba julio–septiembre 2022 ya estaba inspeccionada y esta comparación es exploratoria, no una validación independiente.
- **Dependencias y siguiente paso:** Max debe consumir una corrida de la versión elegida; Kevin debe comprobar días posteriores no usados para ajuste antes de afirmar calidad fuera del piloto y acordar el costo real entre faltantes y sobrantes con el negocio.
- **Commit/PR:** commit local de `cueva`; push pendiente por Axel.

### K01/K03/K04 · Verificación del consumidor CSV en PostgreSQL

- **Fecha/hora y zona:** 2026-09-29 (America/Lima).
- **Autor y responsable del bloque:** Codex verificando el bloque de Kevin tras la carga parcial de Edu; no atribuye cambios de Kevin a Codex.
- **Tareas y estado:** K01/K03/K04, LISTO_PARA_INTEGRAR; M02 de Max sigue pendiente.
- **Comportamiento disponible:** el CSV real enviado por la nueva ruta de Edu reservó `PREPARAR_MODELO`; Beat/worker completaron el entrenamiento y `EVALUAR_MODELO` en PostgreSQL. API de modelos y evaluación respondió con datos reales. No se modificó código de Kevin.
- **Archivos clave:** [carga de Edu](sanchez.md), `backend/app/modules/pronosticos/entrenamiento.py`, `backend/app/modules/pronosticos/evaluacion.py`.
- **Contrato/ejemplo:** `POST /inicializacion/piloto-bakery` → ejecución `PREPARAR_MODELO` → `EVALUAR_MODELO` → `GET /pronosticos/evaluacion`.
- **Configuración/migraciones:** `0002_e01_ventas` y `0003_pronosticos` aplicadas en Compose; volumen de artefactos compartido.
- **Pruebas:** 1 modelo, 92 corridas y 4 047 evaluaciones persistidas; API de evaluación devolvió 4 047 pares; frontend `/inicializacion` respondió 200. Falta probar consumo M02 y el recorrido en otra PC.
- **Dependencias y siguiente paso:** Edu completa E03; Max integra `generar_corrida` en M02.
- **Commit/PR:** verificación incluida en el commit local de `cueva`; push pendiente por Axel.

### K01–K04 · Intento de arranque en Docker Desktop

- **Fecha/hora y zona:** 2026-09-29 15:01 (America/Bogota).
- **Autor y responsable del bloque:** Codex, verificando el bloque de Kevin Bohorquez a pedido del usuario; no atribuye esta prueba a Kevin.
- **Tareas:** verificación de despliegue de K01–K04 y dependencia A04.
- **Estado:** EN_CURSO; arranque de Compose bloqueado por configuración del host Windows.
- **Qué cambió y qué comportamiento está disponible:** se localizó Docker Desktop 4.93.0 y Docker Compose v5.5.1 en la instalación de usuario; se creó `.env` ignorado por Git con claves aleatorias locales y `docker compose config --quiet` pasó. El motor Linux no arranca; los registros indican `Virtual Machine Platform not enabled` y `No virtualization available`. El procesador reporta virtualización de firmware activada.
- **Archivos clave:** `.env` local ignorado (sin publicar secretos), `compose.yaml`, `backend/Dockerfile`.
- **Contrato/función/ruta y ejemplo:** el recorrido previsto es migración `0002`/`0003` → carga piloto E01 → `PREPARAR_MODELO` → `EVALUAR_MODELO` → `/panel`; aún no se ejecutó en Compose.
- **Migración/configuración necesaria:** habilitar `VirtualMachinePlatform` y WSL 2 en Windows con permisos de administrador, reiniciar la PC y comprobar `docker info` antes de `docker compose up --build -d`.
- **Pruebas:** `docker --version` y `docker compose version` correctos; `docker compose config --quiet` correcto. `docker desktop status` pasó de `starting` a `stopped`; `docker info` devolvió 500. No se ejecutaron migraciones ni carga en PostgreSQL.
- **Qué necesita el siguiente desarrollador y quién es:** Axel o el usuario con permisos de administrador habilita la característica de Windows; después Codex puede continuar el recorrido de prueba.
- **Dependencias/bloqueos:** requiere cambio del sistema y reinicio; la sesión actual no tiene elevación administrativa (`DISM` devolvió error 740).
- **Siguiente paso concreto:** habilitar Virtual Machine Platform y WSL 2 en PowerShell como administrador, reiniciar y volver a comprobar Docker.
- **Commit/PR:** cambios locales, sin commit.

### K03 · Comandos locales verificados y cobertura consistente

- **Fecha/hora y zona:** 2026-09-29 14:47 (America/Bogota).
- **Autor y responsable del bloque:** Codex, trabajando por solicitud del usuario en el bloque de Kevin Bohorquez; no atribuye este ajuste a Kevin.
- **Tareas:** K01/K03, verificación para la demo local.
- **Estado:** LISTO_PARA_INTEGRAR; CLI local ejecutado, Compose pendiente.
- **Qué cambió y qué comportamiento está disponible:** se ejecutaron normalización, entrenamiento CatBoost y verificación del artefacto con el CSV real. Se ajustó el backtest CLI para excluir SKU fuera del modelo o con menos de siete observaciones previas, contar fechas con pares evaluables y coincidir con el resumen backend. El panel usa solo corridas canónicas `backtest-{modelo_id}-{fecha}` para no duplicar una fecha por pruebas adicionales.
- **Archivos clave:** `foodsave-ml/ejecutar_backtest.py`, `foodsave-ml/tests/test_evaluacion_k03.py`, `backend/app/modules/pronosticos/evaluacion.py`.
- **Contrato/función/ruta y ejemplo:** `python foodsave-ml/normalizar_ventas.py --entrada foodsave-ml/bakery_sales_limpio_final.csv --formato bakery --comercio piloto --sucursal principal --salida .tmp/demo_manual`; después `python foodsave-ml/entrenar.py --csv .tmp/demo_manual/ventas_diarias_normalizadas.csv --comercio piloto --sucursal principal --salida .tmp/demo_manual/modelo --version demo-manual-v1`.
- **Migración/configuración necesaria:** ninguna para la CLI independiente; usa dependencias ML de `backend[ml]`. Para el panel persiste la necesidad de `0002_e01_ventas` y `0003_pronosticos`.
- **Pruebas:** los tres comandos locales y `ejecutar_backtest.py` finalizaron correctamente. El reporte CLI y el resumen backend coincidieron en 4047 pares, MAE 6.0168, WAPE 32.73 %, cobertura 79.89 % y 90 fechas evaluables del tramo julio–septiembre 2022. `python -m pytest backend/tests foodsave-ml/tests -q -p no:cacheprovider`: 78 passed, 8 skipped, 6 subtests passed. La CLI no registra el modelo en PostgreSQL ni lo muestra en el panel.
- **Qué necesita el siguiente desarrollador y quién es:** Axel o quien prepare la demo instala Docker/Compose, carga el CSV en PostgreSQL y comprueba la ruta administrativa de preparación; Edu y Max conservan las dependencias E03/M02 indicadas en el resumen.
- **Dependencias/bloqueos:** esta PC no tiene Docker ni PostgreSQL; el arranque completo sigue sin validarse.
- **Siguiente paso concreto:** verificar Compose y el recorrido manual cargar→preparar→evaluar→panel en una máquina con Docker.
- **Commit/PR:** cambios locales, sin commit.

### K01–K04 · Backend, evaluación persistida y panel del piloto

- **Fecha/hora y zona:** 2026-09-29 14:27 (America/Bogota).
- **Autor y responsable del bloque:** Codex, trabajando por solicitud del usuario en el bloque de Kevin Bohorquez; no atribuye estos cambios a Kevin.
- **Tareas:** K01, K02, K03 y K04; coordinación con el corte E01 de Edu.
- **Estado:** LISTO_PARA_INTEGRAR en entorno local; integración externa parcial.
- **Qué cambió y qué comportamiento está disponible:** el worker entrena desde ventas persistidas, exporta CBM/metadata con huella y versión, registra la partición y reserva `EVALUAR_MODELO`. La inferencia usa solo los 28 días previos, valida cobertura/artefacto y guarda corrida y cantidad nullable por producto. K03 conserva evaluaciones por revisión de venta y consolida MAE, WAPE, ±20% y cobertura sobre pares conocidos. K04 expone modelos, corridas, evaluaciones y un panel con serie, fecha, producto y enlace directo a la corrida. Se evitó acceder a tablas privadas de Edu desde los servicios de Kevin.
- **Archivos clave:** `backend/app/modules/pronosticos/{entrenamiento,servicio,evaluacion,rutas,modelos}.py`, `backend/migrations/versions/0003_pronosticos.py`, `backend/app/workers/tasks/manejadores.py`, `frontend/src/app/{pronosticos,panel}/page.tsx`, `frontend/src/components/charts/SerieHistorica.tsx`, `backend/tests/integration/test_pronosticos_k02_k03.py`.
- **Contrato/función/ruta y ejemplo:** `generar_corrida(sesion, ejecucion_id=1, clave_ejecucion="demo-1", fecha_objetivo=date(2022, 8, 24), producto_ids=[1])` devuelve una corrida; `obtener_pronosticos(sesion, corrida.id)` entrega estado y cantidad nullable. `GET /api/v1/pronosticos/evaluacion?modelo_id=1` entrega serie y métricas; `GET /api/v1/pronosticos/corridas/1` entrega trazas por producto. [Contrato completo](../../api/contratos.md#ventas--pronósticos).
- **Migración/configuración necesaria:** `0003_pronosticos` depende de `0002_e01_ventas`; `MODEL_ARTIFACT_DIR`, `ML_COMERCIO_ID`, `ML_SUCURSAL_ID`. El contenedor backend copia `foodsave-ml`; worker comparte el volumen de modelos con API.
- **Pruebas:** `python -m pytest backend/tests foodsave-ml/tests -q -p no:cacheprovider`: **78 passed, 8 skipped, 6 subtests passed**, incluida API protegida. `npm run typecheck` y `npm run build`: correctos. Prueba integral local con CSV real y SQLite temporal: 228936 líneas aceptadas, 1264 negativas excluidas, 27740 ventas diarias, CBM verificado, primera corrida de 139 productos (54 pronósticos disponibles, 38 pares evaluables); backtest canónico del tramo de 92 días: 4047 pares evaluables en 90 fechas, MAE 6.0168 y WAPE 32.73 %. Se excluyó del resumen una corrida exploratoria adicional de la primera fecha, que duplicaba 38 pares; el CLI independiente ahora usa la misma regla de cobertura y arroja iguales métricas. Estos valores son exploratorios de la muestra, no rendimiento comercial. Alembic generó SQL offline PostgreSQL de toda la cadena; no se ejecutó upgrade real ni Compose: Docker y `psql` no están instalados aquí.
- **Qué necesita el siguiente desarrollador y quién es:** Max (M02) llama `generar_corrida` y `obtener_pronosticos` en su transacción de plan, luego `solicitar_evaluacion_corrida`; Edu (E03) reserva `PREPARAR_MODELO` tras primera carga; Axel verifica despliegue A04 con PostgreSQL/Compose.
- **Dependencias/bloqueos:** E01 está consumido localmente, pero su carga integrada E03 y la migración PostgreSQL siguen pendientes; no se declara M02 integrado.
- **Siguiente paso concreto:** aplicar migraciones en PostgreSQL, probar worker/API y enlazar E03 y M02 conservando idempotencia y sesión compartida.
- **Commit/PR:** cambios locales, sin commit.

### K04 · Dashboard y vistas de pronóstico y evaluación histórica

- **Fecha/hora y zona:** 2026-09-29 13:15 (America/Lima)
- **Autor y responsable del bloque:** Kevin Bohorquez
- **Tareas:** K04 (Construir dashboard y vistas de pronóstico)
- **Estado:** LISTO_PARA_INTEGRAR
- **Qué cambió y qué comportamiento está disponible:**
  - Creación de tipos TypeScript en `frontend/src/types/pronosticos.ts` alineados con los contratos de métricas y evaluación.
  - Implementación de `frontend/src/services/pronosticos.ts` con clientes tipados para evaluación histórica y corridas, integrando el escenario demo 2022-08-24 precalculado.
  - Componente `TarjetasMetricas.tsx` mostrando MAE en unidades, WAPE porcentual (con "No definido" si la suma real es 0; sin restar de 100), cobertura y porcentaje dentro de ±20% / ±10%.
  - Componente `GraficoSerieHistorica.tsx`: gráfico SVG reactivo que compara total previsto vs total real por fecha (sumados exclusivamente sobre evaluables), con selector interactivo de fecha e indicación de productos excluidos.
  - Componente `BarrasProductoDia.tsx`: barras horizontales por producto con diferencia absoluta en unidades y badges de tolerancia.
  - Componente `TablaDesgloseProductos.tsx`: auditoría tabular con motivo de exclusión `VENTA_REAL_DESCONOCIDA` para ausencias.
  - Integración en `frontend/src/app/pronosticos/page.tsx` dentro de `ProtectedShell`, y adición del enlace "Pronósticos" en la barra lateral de navegación.
- **Archivos clave:**
  - `frontend/src/types/pronosticos.ts`
  - `frontend/src/services/pronosticos.ts`
  - `frontend/src/components/panel/TarjetasMetricas.tsx`
  - `frontend/src/components/charts/GraficoSerieHistorica.tsx`
  - `frontend/src/components/charts/BarrasProductoDia.tsx`
  - `frontend/src/components/tables/TablaDesgloseProductos.tsx`
  - `frontend/src/app/pronosticos/page.tsx`
  - `frontend/src/components/layout/ProtectedShell.tsx`
- **Contrato/función/ruta y ejemplo de uso:**
  - Ruta frontend: `/pronosticos`
  - Servicios: `obtenerEvaluacionHistorica(token)`, `listarCorridasPronostico(token)`
- **Migración/configuración necesaria:** Ninguna en BD; requiere `npm install` en `frontend/`.
- **Pruebas:** `npm run typecheck` (0 errores de tipos en TypeScript) y `npm run build` en `frontend` (ruta `/pronosticos` compilada y empaquetada estáticamente con éxito).
- **Qué necesita el siguiente desarrollador y quién es:**
  - Todo el equipo puede visualizar el desempeño del modelo y el caso objetivo demo 2022-08-24 directamente desde la interfaz web.
- **Dependencias/bloqueos:** Ninguno; K04 completamente funcional y validado.
- **Siguiente paso concreto:** Implementar modelos y servicio de inferencia K02 en el backend.
- **Commit/PR:** Commits en rama `bohorquez`.

### K03 · Implementación de métricas y evaluación histórica

- **Fecha/hora y zona:** 2026-09-29 12:30 (America/Lima)
- **Autor y responsable del bloque:** Kevin Bohorquez
- **Tareas:** K03 (Implementar evaluación histórica)
- **Estado:** LISTO_PARA_INTEGRAR
- **Qué cambió y qué comportamiento está disponible:**
  - Implementación de `metricas.py` con cálculo contractual de MAE (unidades), WAPE porcentual (retorna `None` si la suma real es cero, jamás calcula `100 - WAPE` ni lo denomina precisión), `% dentro de ±20%` y `±10%` usando `max(real, 1)` y cobertura (ausencia = desconocida, no cero).
  - Implementación de `evaluador.py` con `evaluar_dia` (suma total previsto y real exclusivamente sobre productos con venta real conocida) y `consolidar_evaluacion_tramo` (calcula MAE y WAPE sobre todos los pares producto-día juntos, sin promediar porcentajes diarios).
  - Implementación de `ejecutar_backtest.py`: CLI de simulación histórica que itera fecha por fecha sobre el tramo de prueba reservado, infiriendo un día adelante con ventas estrictamente anteriores y exportando el informe JSON.
- **Archivos clave:**
  - `foodsave-ml/metricas.py`
  - `foodsave-ml/evaluador.py`
  - `foodsave-ml/ejecutar_backtest.py`
  - `foodsave-ml/tests/test_evaluacion_k03.py`
- **Contrato/función/ruta y ejemplo de uso:**
  - `evaluar_pares(pares: Sequence[ParEvaluacion]) -> MetricasResultado`
  - `consolidar_evaluacion_tramo(version, ini, fin, pares) -> EvaluacionTramoCompleto`
  - `python foodsave-ml/ejecutar_backtest.py --artefacto-dir model_artifacts --csv ventas.csv --salida reporte.json`
- **Migración/configuración necesaria:** Ninguna en BD; utiliza dependencias de `requirements.txt`.
- **Pruebas:** `python -m pytest foodsave-ml/tests/test_evaluacion_k03.py -v` (20 passed de K03; 52 passed en total en el módulo).
- **Qué necesita el siguiente desarrollador y quién es:**
  - Max Rojas (M02) y Kevin (K02/K04) reciben la estructura de métricas y evaluación consolidada.
- **Dependencias/bloqueos:** Ninguno para evaluación offline. Persistencia en DB dependerá de K02.
- **Siguiente paso concreto:** Conectar la evaluación histórica al servicio de backend K02 y al panel K04.
- **Commit/PR:** Commits `694b05b` a `85d0fcb` en rama `bohorquez`.

### K01 · Entrenador CatBoost independiente de Colab

- **Fecha/hora y zona:** 2026-09-29 11:15 (America/Lima)
- **Autor y responsable del bloque:** Kevin Bohorquez
- **Tareas:** K01 (Extraer entrenamiento reutilizable)
- **Estado:** LISTO_PARA_INTEGRAR
- **Qué cambió y qué comportamiento está disponible:**
  - Pipeline de entrenamiento local CLI (`entrenar.py`) independiente de Google Colab.
  - Partición temporal según `POLITICA_EVALUACION.md` por meses completos (6, 12 o 24 meses).
  - Vector de 13 características contractuales en orden estricto (`features.py`).
  - Ventanas temporales por días calendario sin imputar ceros en ausencias (`ventanas.py`).
  - Guardado atómico de `catboost_model.cbm` y generación de `metadata.json` con SHA-256 (`artefacto.py`, `metadata.py`).
  - Verificador de integridad CLI (`verificar_artefacto.py`).
- **Archivos clave:**
  - `foodsave-ml/entrenar.py`
  - `foodsave-ml/particion.py`
  - `foodsave-ml/features.py`
  - `foodsave-ml/ventanas.py`
  - `foodsave-ml/artefacto.py`
  - `foodsave-ml/metadata.py`
  - `foodsave-ml/verificar_artefacto.py`
  - `foodsave-ml/tests/test_entrenador_k01.py`
- **Contrato/función/ruta y ejemplo de uso:**
  - `python foodsave-ml/entrenar.py --csv ventas.csv --comercio piloto --sucursal principal --salida model_artifacts`
  - `python foodsave-ml/verificar_artefacto.py --directorio model_artifacts`
- **Migración/configuración necesaria:** Ninguna en BD; escribe en volumen `MODEL_ARTIFACT_DIR`.
- **Pruebas:** `python -m pytest foodsave-ml/tests/test_entrenador_k01.py -v` (27 passed).
- **Qué necesita el siguiente desarrollador y quién es:**
  - Axel (A04) y Kevin (K02) pueden montar el directorio de artefactos y consumir el CBM verificado.
- **Dependencias/bloqueos:** Ninguno; K01 completado e integrado en `main` mediante PR #4.
- **Siguiente paso concreto:** Completar K03 (métricas y backtest) e iniciar K02 (inferencia en backend).
- **Commit/PR:** Pull Request #4 mergeado en `main` (`d016c35`).

### Preparación del registro

- **Autor:** IA que preparó el reparto y guías, sin atribuir implementación a Kevin Bohorquez.
- **Cambio:** se definieron las tareas y el lugar de documentación; no se implementó lógica de este bloque en esta entrega documental.
- **Pruebas:** la revisión de documentación comprueba enlaces, cobertura de carpetas y coherencia del reparto; no acredita funcionamiento del módulo.
- **Próximo autor:** registrar el primer avance con la plantilla y actualizar el resumen vigente.
