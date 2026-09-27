# Diccionario de datos — prototipo universitario

**Estado:** diseño objetivo, sin tablas operativas creadas. [ADR-005](../arquitectura/decisiones/ADR-005-instalacion-local-mvp.md) fija una instalación por comercio/sucursal; [ADR-006](../arquitectura/decisiones/ADR-006-identidades-lotes-pronosticos.md) fija ventas y stock propios. El [esquema objetivo](esquema-objetivo-mvp.md) contiene columnas, tipos y restricciones para la futura `0002`.

| Concepto | Definición canónica |
|---|---|
| Identidad | `negocio.id = 1`. SKU textual del archivo se traduce por `sku_producto` a `producto.id` entero. No hay `negocio_id` en las demás tablas. |
| Venta | `venta_diaria` es agregado no negativo por producto y fecha local. Una fila ausente es desconocida; una corrección crea `revision_venta`. No se guardan tickets ni pagos. |
| Producto e insumo | `producto` y `ingrediente` son catálogos propios. `receta` se versiona; `receta_ingrediente` expresa cantidad por unidad en la unidad base del insumo. |
| Stock | `lote_producto` y `lote_ingrediente` guardan saldos. `movimiento_inventario` registra apertura/ajuste con clave única y actualiza el saldo en la misma transacción. `INVENTARIO`, `inventario_ingrediente` y `existencia_producto` son lecturas agregadas, no tablas. |
| Caducidad | `fecha_caducidad` opcional por lote; producto puede tener `fecha_limite_venta` distinta. La falta de fecha se muestra como desconocida, nunca como vigencia comprobada. |
| Tiempo | `fecha_local` y `fecha_objetivo` son `date` de la zona del negocio. `creado_en` y auditoría son instantes UTC. |
| Cantidades | Unidades de producto y ventas enteras; ingrediente `numeric(14,3)` en su unidad base. Importación inicial y movimientos no admiten saldo negativo. |
| Pronóstico | `artefacto_modelo` identifica `.cbm`, huella y versión; `corrida_pronostico` fija fecha y entradas; `pronostico` es único por corrida/producto. Sin cobertura, cantidad `null` y estado explicativo. |
| Evaluación | `evaluacion_pronostico` compara una predicción con una revisión concreta de venta real **después** de inferir. El dashboard muestra MAE, WAPE, ±20% y cobertura; una venta ausente no equivale a cero. |
| Plan | `plan_produccion` cita corrida. `elemento_plan` es el nombre físico canónico. `necesidad_ingrediente` guarda requerido, disponible, faltante y unidad; faltante positivo es sugerencia de compra, no pedido enviado. |
| Pedido | `pedido_compra` agrupa necesidades positivas por proveedor y plan; `linea_pedido` conserva la conversión y cantidad de compra. El modo `REQUIERE_APROBACION` o `AUTOMATICO` se copia del negocio. `envio_pedido` registra el resultado real de Telegram; `ENVIADO` no equivale a aceptación del proveedor. |
| Idempotencia | `importacion_venta`, `movimiento_inventario` y `corrida_pronostico` usan clave única; misma clave con datos distintos es conflicto. |
| Automatización | `programacion_demo` guarda el disparo real y el reloj histórico simulado. `ejecucion_automatizacion` e `intento_automatizacion` registran estado, reintentos y efectos sin duplicarlos. |
| Promoción | `regla_promocion_demo` versiona la regla pura existente. `evaluacion_promocion` registra sugerencia o rechazo por lote con motivo; no activa ni publica descuentos. |

## Propiedad de módulos

| Responsable | Entidades de la demo |
|---|---|
| Axel Cueva | `usuario`, `negocio`, `programacion_demo`, `ejecucion_automatizacion`, `intento_automatizacion`. |
| Edu Sanchez | `configuracion_inicial`, `producto`, `sku_producto`, `importacion_venta`, `venta_diaria`, `revision_venta`. |
| Kevin Bohorquez | `artefacto_modelo`, `corrida_pronostico`, `pronostico`, `evaluacion_pronostico`. |
| Leonardo Vera | `lote_producto`, `lote_ingrediente`, `movimiento_inventario`, `regla_promocion_demo`, `evaluacion_promocion`. |
| Leonardo Aguirre | `proveedor`, `oferta_ingrediente`, `pedido_compra`, `linea_pedido`, `envio_pedido`. |
| Max Rojas | `ingrediente`, `receta`, `receta_ingrediente`, `plan_produccion`, `elemento_plan`, `necesidad_ingrediente`. |

Recepción física, pagos, **publicación** de promociones, desperdicio y notificaciones quedan fuera de `0002`. Proveedor mínimo, pedido y envío a chat de pruebas sí pertenecen a esta demo según [ADR-008](../arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md). El ER solo dibuja entidades de esta etapa. Antes de implementar una tabla, su responsable compara el modelo SQLAlchemy, la migración y los nombres de este diccionario en una misma revisión.
