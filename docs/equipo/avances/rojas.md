# Avances — Max Rojas

**Responsable:** Max Rojas. **Bloque:** Ingredientes, recetas y planificación. **Rama prevista:** `rojas`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md). Este archivo se actualiza al terminar cada avance significativo.

## Resumen vigente

- **Estado:** M01 `LISTO_PARA_INTEGRAR`. M02–M04 pendientes. Además se implementaron V01 y V02 por encargo de Leonardo Vera (ver [vera.md](vera.md)).
- **Disponible:** catálogo de ingredientes con unidad base, recetas versionadas, servicio de primera carga conectado al asistente de Edu y lectura versionada para el plan. Pantallas `/ingredientes` y `/recetas`.
- **Contrato:** [M01 en contratos.md](../../api/contratos.md#m01-disponible-ingredientes-y-recetas-versionadas-30-09-2026).
- **Para M02:** usar `recetas_activas(sesion, producto_ids)` y guardar `receta_id` en el plan; leer stock con `consultar_disponibilidad(sesion, fecha, producto_ids=…, ingrediente_ids=…)` y guardar su `huella`.
- **Bloqueos:** ninguno para M02 más allá de K02 (corrida) ya disponible.
- **Siguiente paso:** M02, plan de producción con snapshots de receta y stock.

| Tarea | Estado de seguimiento |
|---|---|
| M01 · Implementar ingredientes y recetas | LISTO_PARA_INTEGRAR |
| M02 · Calcular plan de producción | PENDIENTE |
| M03 · Calcular necesidades y faltantes | PENDIENTE |
| M04 · Entregar pantalla y contrato del plan | PENDIENTE |

## Bitácora

### Preparación del registro

- **Autor:** IA que preparó el reparto y guías, sin atribuir implementación a Max Rojas.
- **Cambio:** se definieron las tareas y el lugar de documentación; no se implementó lógica de este bloque en esta entrega documental.
- **Pruebas:** la revisión de documentación comprueba enlaces, cobertura de carpetas y coherencia del reparto; no acredita funcionamiento del módulo.
- **Próximo autor:** registrar el primer avance con la [plantilla](README.md) y actualizar el resumen vigente.

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
  - `alembic upgrade head`, `downgrade 0004_e03_inicializacion` y `upgrade head` sobre PostgreSQL 16 local → sin error; `alembic check` sin diferencias en tablas de M01/V01.
  - Carga real por `POST /inicializacion/confirmar` sobre PostgreSQL → `DATOS_CARGADOS`, `pendiente_de: []`.
  - `cd frontend && npx tsc --noEmit` y `npx next build` → sin errores.
- **Aviso para Edu/Axel:** `migrations/env.py` no importa `ConfiguracionInicial`; un autogenerate propondría borrar `configuracion_inicial`. No se modificó.
- **Siguiente desarrollador:** Max (M02) consume `recetas_activas` y `consultar_disponibilidad`. Aguirre puede ligar `oferta_ingrediente.ingrediente_id` a `ingrediente.id`.
- **Siguiente paso concreto:** M02.
- **Commit/PR:** cambios locales, sin commit.

