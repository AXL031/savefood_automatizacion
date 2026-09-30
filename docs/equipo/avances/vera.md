# Avances — Leonardo Vera

**Responsable:** Leonardo Vera. **Bloque:** Inventario por lotes y promociones sugeridas. **Rama prevista:** `vera`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md). Este archivo se actualiza al terminar cada avance significativo.

## Resumen vigente

- **Coordinación verificada (2026-09-30):** entrega V01/V02 de `rojas` integrada localmente por Codex para Axel. Apertura real en sesión de Edu, cero conocido, caducidad, ajuste idempotente y rechazo de saldo negativo verificados por API en SQLite. Misma clave con otro motivo/hora ahora es conflicto. Pruebas PostgreSQL añadidas para CI; no se declara verificada concurrencia en SQLite. V03 y detalle de promociones siguen pendientes.

- **Estado:** V01 y V02 `LISTO_PARA_INTEGRAR`, implementadas por **Max Rojas por encargo** de Leonardo Vera. V03 y V04 (promociones) pendientes.
- **Disponible:** lotes de producto e ingrediente, apertura en la sesión de la primera carga, ajustes con bloqueo y clave idempotente, disponibilidad por fecha con la regla de vida útil de pastelería. Pantalla `/inventario` con disponibilidad, lotes, ajuste y movimientos.
- **Contrato:** [V01/V02 en contratos.md](../../api/contratos.md#v01v02-disponibles-apertura-ajustes-y-stock-por-fecha-30-09-2026).
- **Vida útil:** producto 5 días máximo; días 1–3 óptimo, 4–5 prioridad, 6+ merma. Ver [vigencia.py](../../../backend/app/modules/inventario/vigencia.py).
- **Bloqueos:** ninguno. Para V03 falta agendar `EVALUAR_PROMOCION` tras un ajuste de producto con `programar_ejecucion` de Axel.
- **Siguiente paso:** V03, dentro de `registrar_ajuste` o en la ruta, en la misma transacción.

| Tarea | Estado de seguimiento |
|---|---|
| V01 · Implementar lotes y apertura | LISTO_PARA_INTEGRAR (por Max Rojas) |
| V02 · Implementar ajustes y disponibilidad | LISTO_PARA_INTEGRAR (por Max Rojas) |
| V03 · Integrar regla de promoción | PENDIENTE |
| V04 · Entregar inventario y promoción en UI | PARCIAL: inventario hecho; falta detalle de promoción |

## Bitácora

### Integración coordinada de entregas Rojas/Aguirre · 30-09-2026

- **Fecha/zona y autor:** 2026-09-30, America/Bogota. Codex a solicitud de Axel Cueva, coordinación transversal A04; se conserva autoría original de Max/Leonardo y la entrega delegada registrada en [Vera](vera.md).
- **Estado:** integración local verificada en SQLite; LISTO_PARA_INTEGRAR en Git, PostgreSQL/Redis y revisión remota pendientes. No declara completa la demo.
- **Comportamiento:** entrega V01/V02 de `rojas` integrada localmente por Codex para Axel. Apertura real en sesión de Edu, cero conocido, caducidad, ajuste idempotente y rechazo de saldo negativo verificados por API en SQLite. Misma clave con otro motivo/hora ahora es conflicto. Pruebas PostgreSQL añadidas para CI; no se declara verificada concurrencia en SQLite. V03 y detalle de promociones siguen pendientes.
- **Archivos/contrato:** [contratos](../../api/contratos.md), [importaciones](../../api/contrato-importaciones.md), [pedidos](../../api/contrato-pedidos.md), rutas de inicialización/ingredientes/recetas/inventario/proveedores, `backend/migrations/env.py`, nuevas revisiones 0005/0006/0007 y `backend/tests/integration/test_api_inicializacion_ventas.py`, `test_proveedores_l01.py`, `test_migraciones_entregas.py`, `test_inventario_concurrencia_pg.py`. Enlaces de coordinación: [Axel](cueva.md), [Max](rojas.md), [Vera](vera.md), [Aguirre](aguirre.md), [Edu](sanchez.md).
- **Ejemplo público:** POST autenticado `/api/v1/inicializacion/confirmar` con los cinco CSV y fechas válidas devuelve DATOS_CARGADOS; POST administrativo `/api/v1/proveedores/{id}/ofertas` exige ingrediente existente y conversión explícita. Servicios participantes hacen flush, el llamador confirma.
- **Migraciones/configuración:** continuar desde 0004 con 0005→0006→0007; registrar todos los modelos, incluido ConfiguracionInicial. Revisiones previas conservadas. Para concurrencia activar V02_POSTGRES_TEST=1 sobre esquema de pruebas aislado; no habilitar Telegram ni cambiar modo automático.
- **Pruebas realmente ejecutadas:** `.venv/Scripts/python.exe -m pytest backend/tests foodsave-ml/tests -q` → 112 passed, 10 skipped (8 A03 y 2 V02 por PostgreSQL/Redis), 6 subtests passed. `npm run typecheck` y `npm run build` correctos. Delta 0004→0007 arriba/abajo/arriba y comparación de metadatos en SQLite correctos; el índice de expresión del núcleo no se puede reflejar en SQLite. Docker Desktop no logró arrancar; CI incorpora alembic check y concurrencia V02. No se ejecutaron envíos externos.
- **Dependencias y siguiente paso:** revisión de la entrega conjunta y CI PostgreSQL; después integrar a main. Max continúa M02/M03; Aguirre completa adaptador/UI L01 y L02–L04; Vera V03; Edu/Kevin/Axel conectan ML desde asistente completo.
- **Commit/PR:** cambios locales en cueva; publicación de PR de integración pendiente.


### Preparación del registro

- **Autor:** IA que preparó el reparto y guías, sin atribuir implementación a Leonardo Vera.
- **Cambio:** se definieron las tareas y el lugar de documentación; no se implementó lógica de este bloque en esta entrega documental.
- **Pruebas:** la revisión de documentación comprueba enlaces, cobertura de carpetas y coherencia del reparto; no acredita funcionamiento del módulo.
- **Próximo autor:** registrar el primer avance con la [plantilla](README.md) y actualizar el resumen vigente.

### V01/V02 · Apertura de lotes, ajustes y stock disponible por fecha

- **Fecha/hora y zona:** 30-09-2026, America/Lima.
- **Autor y responsable del bloque:** Max Rojas (con asistencia de IA, Claude) realizando tareas del bloque de Leonardo Vera por acuerdo del equipo. Leonardo Vera sigue como responsable de V03–V04.
- **Tareas:** V01, V02 y la parte de inventario de V04.
- **Estado:** LISTO_PARA_INTEGRAR.
- **Qué cambió:** tablas `lote_producto`, `lote_ingrediente` y `movimiento_inventario` (incluye `saldo_resultante` para auditar cada movimiento). `ServicioInventarioV01` implementa el puerto de Edu. `registrar_ajuste` bloquea el lote y aplica la clave idempotente. `consultar_disponibilidad` aplica la vida útil y devuelve huella de lectura. Un ítem sin lotes vuelve con `cantidad_disponible = null`.
- **Archivos clave:** [inventario/servicio.py](../../../backend/app/modules/inventario/servicio.py), [inventario/vigencia.py](../../../backend/app/modules/inventario/vigencia.py), [0006_v01_inventario.py](../../../backend/migrations/versions/0006_v01_inventario.py), [app/inventario/page.tsx](../../../frontend/src/app/inventario/page.tsx).
- **Contrato:** [contratos.md, sección V01/V02](../../api/contratos.md#v01v02-disponibles-apertura-ajustes-y-stock-por-fecha-30-09-2026).
- **Migración:** `0006_v01_inventario` sobre `0005_m01_ingredientes_recetas`.
- **Pruebas ejecutadas:**
  - SQLite: `tests/integration/test_inventario_v01_v02.py` y `tests/unit/test_vigencia_lotes.py` pasan, incluido el rollback completo de la primera carga cuando falla el stock.
  - PostgreSQL 16: `V02_POSTGRES_TEST=1 DATABASE_URL=postgresql+psycopg://… python -m pytest tests/integration/test_inventario_concurrencia_pg.py` → 2 passed. Dos ajustes simultáneos de -3 sobre saldo 4 dejan saldo 1 y un `409 SALDO_INSUFICIENTE`; la misma clave enviada dos veces a la vez aplica una sola. Prueba de control: sin `FOR UPDATE` ambas fallan.
  - Carga real y ajuste por la API sobre PostgreSQL con la fecha objetivo 2022-08-24: baguette en día 4 (prioridad), mantequilla vencida excluida.
- **Límite conocido:** `VIDA_UTIL_EXCEDIDA` aparece al confirmar la carga, no en la vista previa; conviene que Edu lo valide también en `validacion.py`.
- **Siguiente desarrollador:** Leonardo Vera (V03) y Max Rojas (M02).
- **Commit/PR:** cambios locales, sin commit.

