# Planificación

> Guía vigente: [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md). Responsable: **Max Rojas**. Tareas, dependencias y avances se detallan en la guía local.

Planes de producción y cálculo de ingredientes necesarios.

M02 disponible en el paso 2 local: `generar_plan`, snapshots de receta/stock/pronóstico,
estados por producto, API `/planes` y adaptador `GENERAR_PROPUESTA` con evaluación
posterior. M03 agrega necesidades y faltantes en el paso 3 local; pedidos siguen pendientes. Ver guía y
[contrato](../../../../docs/api/contratos.md#m02--paso-2-local-plan-reproducible).

**Responsable del módulo:** Max Rojas. La responsabilidad incluye interfaz, servidor y APIs según [la división del equipo](../../../../docs/equipo/responsabilidades.md).

**Estructura prevista:** `rutas.py`, `servicio.py`, `repositorio.py`, `modelos.py`, `esquemas.py`, `dependencias.py`, `errores.py` y `tests/`. Crear estos archivos con su implementación, sin acceder directamente al repositorio de otro módulo.

## Paso 3 local · M03 · 30-09-2026

Necesidades y faltantes implementados en la transacción del plan. API/UI conservan aportes, unidades, lotes y lectura de stock; decimales como cadenas, agregación antes de redondear a tres decimales. Producción o stock ausente deja estado INCOMPLETAS y motivo; no se inventan ceros ni se modifica inventario. Migración aditiva 0010_m03_necesidades sobre 0009; planes antiguos quedan PENDIENTE_M03 y el administrador puede completarlos una vez. Servicio público obtener_necesidades y contrato M03 en docs/api/contratos.md. Compras y Telegram siguen pendientes. Cambios locales por Codex para Axel, sin commit ni cambios remotos.
