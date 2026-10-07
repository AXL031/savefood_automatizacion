# Diccionario de datos — prototipo universitario

**Estado:** definiciones canónicas; qué tabla existe y en qué migración está en el [esquema](esquema-objetivo-mvp.md). [ADR-005](../arquitectura/decisiones/ADR-005-instalacion-local-mvp.md) fija una instalación por comercio/sucursal; [ADR-006](../arquitectura/decisiones/ADR-006-identidades-lotes-pronosticos.md) fija ventas y stock propios. Columnas, tipos y restricciones: [esquema](esquema-objetivo-mvp.md).

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
| Plan | M02 local: `plan_produccion` cita corrida y ejecución y conserva versión de cálculo. `elemento_plan` guarda snapshots de pronóstico, receta y stock; producción nullable con estado/motivo si falta un dato. `necesidad_ingrediente` (M03 local, migración 0010) conserva cantidad_necesaria, stock_disponible/faltante nullable, unidad_base, estado, aportes_json y stock_json; faltante positivo es sugerencia de compra, no pedido enviado. |
| Pedido | `pedido_compra` agrupa necesidades positivas por proveedor y plan; `linea_pedido` conserva la conversión y cantidad de compra. El modo `REQUIERE_APROBACION` o `AUTOMATICO` se copia del negocio. `envio_pedido` registra el resultado real de Telegram; `ENVIADO` no equivale a aceptación del proveedor. |
| Idempotencia | `importacion_venta`, `movimiento_inventario` y `corrida_pronostico` usan clave única; misma clave con datos distintos es conflicto. |
| Inicialización | `configuracion_inicial` conserva la carga y `preparacion_ejecucion_id` vincula su entrenamiento durable; un fallo no vuelve a importar ventas ni abrir stock. |
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
## Corte local L02 · Migración 0011

`propuesta_compra` conserva plan/fecha/modo/necesidades/incidencias, estado y cancelación con usuario/motivo/hora. UNIQUE(plan_id) y fecha única solo mientras activa; SIN_FALTANTES y CANCELADA no reservan fecha. `pedido_compra` conserva proveedor y modo, UNIQUE(plan_id,proveedor_id), BLOQUEADO/PENDIENTE_APROBACION/CANCELADO. `linea_pedido` conserva necesidad y oferta, UNIQUE(necesidad_ingrediente_id), faltante Numeric(14,3), compra Numeric(20,4), equivalencia base Numeric(30,8), unidades y snapshots. No hay tabla/envío Telegram implementado en este corte. Ninguna compra modifica inventario.

## Paso 5 · Configuración Telegram (0012)

Proveedor conserva chat_id_pruebas, destino_verificado, destino_verificado_en y destino_credencial_huella String(64) nullable. Esta última es SHA-256 de credencial para invalidar evidencia tras rotación/deshabilitación; nunca es token y no se expone en API. Destino efectivo exige coincidencia con la credencial actual. Migración 0012 invalida verificaciones heredadas sin huella. Secreto del bot cifrado con Fernet en volumen privado, fuera de PostgreSQL; configuración de UI prevalece sobre entorno. Aprobación y envío no implementados en este paso.

## Paso 6 · decisión y envío (0013)

pedido_compra agrega clave_decision varchar(80) única nullable, decidido_por FK usuario nullable, decidido_en timestamptz nullable y decision_json nullable; CHECK exige los cuatro completos o todos NULL. Snapshot de nombre/acción/motivo, sin credencial. Estados incluyen RECHAZADO/PENDIENTE_ENVIO/ENVIANDO/ENVIADO/FALLIDO/PENDIENTE_VERIFICACION además de los previos.

envio_pedido es outbox y evidencia: UNIQUE(pedido_id), numero_intento=1 en este corte, chat_id varchar(64), credencial_huella SHA-256, texto plano congelado, estado, creado_en/inicio_en/fin_en/fecha_telegram, message_id bigint, código/error saneado, despachado_en/lease_hasta/token_despacho. CHECK ENVIADO requiere message_id>0 y fin; otros estados sin message_id. Índice estado/lease. Huella/token_despacho son internos; token del bot sigue cifrado fuera de PostgreSQL. Creación junto a aprobación; llamada externa después de confirmar ENVIANDO. Nuevos intentos/conciliación pendientes del paso 7; nunca borrar auditoría mediante downgrade con decisiones.

## Corte vigente L04 · Recuperación (0014)

Sustituye la restricción de intento único del corte 0013 anterior. envio_pedido conserva UNIQUE(pedido_id,numero_intento), CHECK numero_intento>=1 y UNIQUE(chat_id,message_id); NULL no representa evidencia. El último intento determina pedido.estado; anteriores se conservan. Una entrega confirmada exige message_id positivo y fin_en, por respuesta del worker o conciliación humana claramente auditada.

recuperacion_envio pertenece a Aguirre: id PK, envio_id FK RESTRICT, clave_idempotencia varchar(80) UNIQUE, accion varchar(24) CHECK CONFIRMAR_ENVIO/CONFIRMAR_NO_ENVIO/REINTENTAR, usuario_id FK usuario RESTRICT, nombre_usuario varchar(150), creado_en timestamptz, evidencia varchar(1500) CHECK longitud 10–1500, solicitud_json JSONB, resultado_anterior_json JSONB, nuevo_envio_id FK envio_pedido nullable RESTRICT. Conserva resultado/error previos, actor y evidencia. El vínculo al nuevo intento se usa solo al reintentar. No hay token del bot ni movimiento de inventario. Downgrade con auditoría o intento N>1 se bloquea para no eliminar evidencia.
