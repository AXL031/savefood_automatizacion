# Avances — Max Rojas

**Responsable:** Max Rojas. **Bloque:** Ingredientes, recetas y planificación. **Rama:** `rojas`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md).

## Resumen vigente

- **Estado (30-09-2026):** M01 `LISTO_PARA_INTEGRAR`; M02–M04 `PENDIENTE`. Además hizo V01 y V02 por encargo de Leonardo Vera ([vera.md](vera.md)).
- **Integración:** Codex para Axel integró M01 y V01/V02 en la rama `cueva` y reconstruyó las migraciones `0005`/`0006` desde los modelos, porque no estaban publicadas en `origin/rojas`. Esas migraciones reconstruidas se probaron en SQLite; su verificación en PostgreSQL depende del CI.
- **Disponible:** catálogo de ingredientes con unidad base, recetas versionadas, servicio de primera carga conectado al asistente de Edu y lectura versionada para el plan. Pantallas `/ingredientes` y `/recetas`.
- **Contrato:** [M01 en contratos.md](../../api/contratos.md#m01-disponible-ingredientes-y-recetas-versionadas-30-09-2026).
- **Para M02:** usar `recetas_activas(sesion, producto_ids)` y guardar `receta_id`; leer stock con `consultar_disponibilidad(sesion, fecha, producto_ids=…, ingrediente_ids=…)` y guardar su `huella`. La corrida de Kevin (K02) ya está disponible.
- **Pendiente de definir:** regla de recompra entre planes de la misma fecha, con Aguirre.
- **Siguiente paso:** publicar M01 en `origin/rojas` y empezar M02.

| Tarea | Estado |
|---|---|
| M01 · Implementar ingredientes y recetas | LISTO_PARA_INTEGRAR |
| M02 · Calcular plan de producción | PENDIENTE |
| M03 · Calcular necesidades y faltantes | PENDIENTE |
| M04 · Entregar pantalla y contrato del plan | PENDIENTE |

## Bitácora

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
