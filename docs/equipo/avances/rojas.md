# Avances — Max Rojas

**Responsable:** Max Rojas. **Bloque:** Ingredientes, recetas y planificación. **Rama:** `rojas`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md).

## Resumen vigente

- **Corte M02–M04 (06-10-2026):** Codex a solicitud de Axel implementó planificación sobre M01 de Max, K02/K03 de Kevin y V02 de Vera/Max. No atribuye esta implementación nueva a Max. Evidencia completa y autoría en [coordinación](cueva.md).
- **Estado:** M01 disponible; M02 integrado localmente con el motor programado y servicios reales. M03 entrega necesidades persistidas, pendiente consumidor L02. M04 API/pantalla disponibles y compiladas; CI remoto, revisión de otra persona y otra PC pendientes.
- **Disponible:** `generar_plan`, `obtener_plan`, `obtener_necesidades`; POST/GET `/planes`, detalle `/planes/{id}` y pantalla `/planificacion?plan_id=...`. Pronóstico menos stock con margen 0; receta versionada y lotes guardados, suma decimal por ingrediente. Datos ausentes conservan omisiones/null y avisos; no modifica inventario.
- **Reproducibilidad:** claves únicas y huella, conflicto si cambian corrida/receta/stock con la misma clave; otra clave conserva un plan nuevo. Propuesta programada guarda corrida, plan y reserva de evaluación en una transacción; reentrega no duplica.
- **Archivos/contrato:** [servicio del plan](../../../backend/app/modules/planificacion/servicio.py), [pantalla](../../../frontend/src/app/planificacion/page.tsx), [contrato M02–M04](../../api/contratos.md), [muestras](../../../backend/tests/fixtures/primera_carga/GUIA_DESARROLLO.md). Migración nueva `0009_m02_planes` tras `0008`, sin reescribir revisiones previas.
- **Pruebas ejecutadas:** suite local 126 passed, 14 skipped, 6 subtests passed; frontera E03/M02 en Compose 18 passed con PostgreSQL/Redis/Beat, incluyendo CatBoost real, concurrencia y rollback. Typecheck frontend y build Docker correctos. Resultados sintéticos, sin acreditar precisión comercial.
- **Entrega a Aguirre:** necesidades con ID estable, ingrediente, requerido/disponible/faltante, unidad y stock conocido. Consultar también `obtener_plan`: si hay omisiones, cálculo parcial; stock desconocido o vigencia desconocida requiere revisión. Compras aún no integradas.
- **Dependencias:** cerrar con Aguirre recompra entre planes de la misma fecha; todavía no generar pedidos ni enviar Telegram.
- **Siguiente paso:** L01 UI de proveedores y L02 compras con política acordada. Cambios locales en `cueva`, sin commit/PR; conservar autoría previa de Max en M01 y V01/V02 por encargo.

| Tarea | Estado |
|---|---|
| M01 · Ingredientes y recetas | Disponible e integrado con carga y plan |
| M02 · Plan de producción | INTEGRADO localmente con K02/V02 y worker/Beat |
| M03 · Necesidades y faltantes | LISTO_PARA_INTEGRAR con L02; cálculos persistidos verificados |
| M04 · Pantalla y contrato | LISTO_PARA_INTEGRAR: API real y frontend compilado |

## Bitácora

### 06-10-2026 America/Lima — Entrega transversal M02–M04

- **Autor:** Codex a solicitud de Axel Cueva; dominio de planificación mantiene responsable Max Rojas. No modifica autoría de las entregas anteriores.
- **Resultado:** plan, necesidades, API/pantalla y handler programado disponibles; registro de archivos, contrato, migración, pruebas y límites en [Cueva](cueva.md). M03 pendiente consumo real por Aguirre; pedidos/canal fuera de este corte.
- **Commit/PR:** cambios locales en `cueva`, sin commit ni publicación.

### Integración coordinada de entregas Rojas/Aguirre · 30-09-2026

- **Fecha/zona y autor:** 2026-09-30, America/Lima. Codex a solicitud de Axel Cueva, coordinación transversal A04; se conserva autoría original de Max/Leonardo y la entrega delegada registrada en [Vera](vera.md).
- **Estado:** integración local verificada en SQLite; LISTO_PARA_INTEGRAR en Git, PostgreSQL/Redis y revisión remota pendientes. No declara completa la demo.
- **Comportamiento:** Codex para Axel concilió M01 y la entrega delegada V01/V02 con main en `cueva`. Reconstruyó las migraciones 0005/0006 a partir de los modelos publicados (no estaban en origin/rojas). Carga completa real, rollback de stock, versiones y migraciones delta verificadas en SQLite; PostgreSQL pendiente de CI. M02–M04 siguen pendientes; no se atribuye este trabajo de coordinación a Max.
- **Archivos/contrato:** [contratos](../../api/contratos.md), [importaciones](../../api/contrato-importaciones.md), [pedidos](../../api/contrato-pedidos.md), rutas de inicialización/ingredientes/recetas/inventario/proveedores, `backend/migrations/env.py`, nuevas revisiones 0005/0006/0007 y `backend/tests/integration/test_api_inicializacion_ventas.py`, `test_proveedores_l01.py`, `test_migraciones_entregas.py`, `test_inventario_concurrencia_pg.py`. Enlaces de coordinación: [Axel](cueva.md), [Max](rojas.md), [Vera](vera.md), [Aguirre](aguirre.md), [Edu](sanchez.md).
- **Ejemplo público:** POST autenticado `/api/v1/inicializacion/confirmar` con los cinco CSV y fechas válidas devuelve DATOS_CARGADOS; POST administrativo `/api/v1/proveedores/{id}/ofertas` exige ingrediente existente y conversión explícita. Servicios participantes hacen flush, el llamador confirma.
- **Migraciones/configuración:** continuar desde 0004 con 0005→0006→0007; registrar todos los modelos, incluido ConfiguracionInicial. Revisiones previas conservadas. Para concurrencia activar V02_POSTGRES_TEST=1 sobre esquema de pruebas aislado; no habilitar Telegram ni cambiar modo automático.
- **Pruebas realmente ejecutadas:** `.venv/Scripts/python.exe -m pytest backend/tests foodsave-ml/tests -q` (incluye pruebas ML y L01, por eso son más que las 82 de M01) → 112 passed, 10 skipped (8 A03 y 2 V02 por PostgreSQL/Redis), 6 subtests passed. `npm run typecheck` y `npm run build` correctos. Delta 0004→0007 arriba/abajo/arriba y comparación de metadatos en SQLite correctos; el índice de expresión del núcleo no se puede reflejar en SQLite. Docker Desktop no logró arrancar; CI incorpora alembic check y concurrencia V02. No se ejecutaron envíos externos.
- **Dependencias y siguiente paso:** revisión de la entrega conjunta y CI PostgreSQL; después integrar a main. Max continúa M02/M03; Aguirre completa adaptador/UI L01 y L02–L04; Vera V03; Edu/Kevin/Axel conectan ML desde asistente completo.
- **Commit/PR:** cambios locales en cueva; publicación de PR de integración pendiente.

### M01 · Ingredientes y recetas versionadas

- **Fecha/hora y zona:** 30-09-2026, America/Lima.
- **Autor y responsable del bloque:** Max Rojas, con asistencia de IA (Claude).
- **Tareas:** M01. En la misma entrega, V01 y V02 por encargo (registradas en [vera.md](vera.md)).
- **Estado:** LISTO_PARA_INTEGRAR.
- **Qué cambió:** tablas `ingrediente`, `receta` y `receta_ingrediente`. La unidad base no cambia si una receta o un lote la usa. Toda edición de receta crea la versión siguiente y desactiva la anterior; la misma composición no crea versión. `ServicioRecetasM01` implementa el puerto de Edu sin commit; la primera carga ahora termina en `DATOS_CARGADOS`.
- **Archivos clave:** [ingredientes/servicio.py](../../../backend/app/modules/ingredientes/servicio.py), [recetas/servicio.py](../../../backend/app/modules/recetas/servicio.py), [0005_m01_ingredientes_recetas.py](../../../backend/migrations/versions/0005_m01_ingredientes_recetas.py), [app/recetas/page.tsx](../../../frontend/src/app/recetas/page.tsx).
- **Contrato:** [contratos.md, sección M01](../../api/contratos.md#m01-disponible-ingredientes-y-recetas-versionadas-30-09-2026).
- **Migración:** `0005_m01_ingredientes_recetas` sobre `0004_e03_inicializacion`.
- **Cambios fuera del bloque (mínimos, avisar):** `inicializacion/rutas.py` pasa los dos puertos (Edu); `test_api_inicializacion_ventas.py` ahora espera `DATOS_CARGADOS` (Edu); `principal.py` y `migrations/env.py` registran rutas y modelos (Axel); menú "Producción" en `ProtectedShell.tsx` y clase `badge-prioridad` en `styles.css` (Edu).
- **Pruebas ejecutadas:**
  - `cd backend && python -m pytest -q tests` → 82 passed, 10 skipped (8 de A03 y 2 de V02 que requieren PostgreSQL).
  - En la rama `rojas`, `alembic upgrade head`, `downgrade 0004_e03_inicializacion` y `upgrade head` sobre PostgreSQL 16 local → sin error; `alembic check` sin diferencias en tablas de M01/V01.
  - Carga real por `POST /inicializacion/confirmar` sobre PostgreSQL → `DATOS_CARGADOS`, `pendiente_de: []`.
  - `cd frontend && npx tsc --noEmit` y `npx next build` → sin errores.
- **Aviso para Edu/Axel:** `migrations/env.py` no importaba `ConfiguracionInicial` (resuelto en la integración del 30-09).
- **Siguiente desarrollador:** Max (M02) consume `recetas_activas` y `consultar_disponibilidad`. Aguirre puede ligar `oferta_ingrediente.ingrediente_id` a `ingrediente.id`.
- **Siguiente paso concreto:** M02.
- **Commit/PR:** cambios locales, sin commit.

### Preparación del registro

- **Autor:** IA que preparó el reparto y guías, sin atribuir implementación a Max Rojas.
- **Cambio:** se definieron las tareas y el lugar de documentación; no se implementó lógica de este bloque en esta entrega documental.
- **Pruebas:** la revisión de documentación comprueba enlaces, cobertura de carpetas y coherencia del reparto; no acredita funcionamiento del módulo.
- **Próximo autor:** registrar el primer avance con la [plantilla](README.md) y actualizar el resumen vigente.
