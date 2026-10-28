# Estructura física de FoodSave

Corte: **21-10-2026**. Extraída de los modelos SQLAlchemy del código local, con tipos compilados para PostgreSQL.

**38 tablas, 357 columnas, 67 claves foráneas, 39 restricciones UNIQUE, 76 CHECK y 19 índices explícitos.** Las PK se listan aparte de UNIQUE.

## Alcance y estado

- Corresponde al esquema de código hasta `0019_tienda_clientes`, no a una introspección de la base habitual ni a evidencia de migraciones desplegadas.
- `cliente` pertenece al API de identidad de FoodSave (T02) y se incorpora en 0019. Su presencia no acredita catálogo, stock o compras de tienda integrados.
- El almacenamiento SQLite de pagos del proyecto independiente `tienda/` queda fuera: no comparte base ni FK con FoodSave (ADR-010).
- `alembic_version` es una tabla técnica de migraciones; no forma parte de las entidades del modelo ni del conteo.
- `negocio` es configuración de una instalación: no inventar relaciones `negocio_id` que el esquema no tiene.

## Lectura del ER

[Código Mermaid completo](diagrama-entidad-relacion.mmd). La fuente canónica del dibujo es ese archivo; este documento complementa los detalles que Mermaid no expresa de forma nativa.

- `PK`: clave primaria. `FK`: clave foránea. `UK`: unicidad individual e incondicional.
- `NULL` / `NOT NULL`: nulabilidad de cada columna; no son datos de ejemplo.
- Una clave UNIQUE compuesta se identifica mediante `UQ(nombre)` en sus participantes. No significa que cada columna sea única por separado.
- Los índices únicos parciales o funcionales se documentan aquí, sin marcar sus columnas como UK incondicionales.
- `||` indica exactamente uno, `|o`/`o|` cero o uno y `o{` cero o muchos. Las líneas punteadas son relaciones no identificadoras: la FK no integra la PK del hijo.
- Cada movimiento afecta **exactamente un** lote de producto o uno de ingrediente, validado por CHECK XOR. Las dos relaciones opcionales del ER deben leerse junto a esa restricción.
- Los tipos `numeric` muestran precisión/escala en el comentario del ER (por ejemplo `numeric(14,3)`) para mantener sintaxis Mermaid válida.
- Los valores por defecto de Python y los defaults del servidor se distinguen: los primeros no son defaults DDL.

## Tablas

### artefacto_modelo

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `version_modelo` | `varchar(80)` | NOT NULL | UK | — | — |
| `ruta_local` | `varchar(160)` | NOT NULL | — | — | — |
| `sha256` | `varchar(64)` | NOT NULL | — | — | — |
| `huella_datos_entrenamiento` | `varchar(64)` | NOT NULL | — | — | — |
| `fecha_corte_entrenamiento` | `date` | NOT NULL | — | — | — |
| `particion_json` | `jsonb` | NOT NULL | — | — | — |
| `estado` | `varchar(16)` | NOT NULL | — | — | — |
| `metricas_json` | `jsonb` | NULL | — | — | — |
| `entrenado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_artefacto_modelo_estado`: `estado = 'LISTO_DEMO'`.
- UNIQUE `uq_artefacto_modelo_version`: `version_modelo`.

### cliente

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `google_sub` | `varchar(255)` | NOT NULL | UK | — | — |
| `correo` | `varchar(254)` | NOT NULL | — | — | — |
| `nombre` | `varchar(160)` | NOT NULL | — | — | — |
| `activo` | `boolean` | NOT NULL | — | — | `Python: True` |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Python: función <lambda>` |
| `ultimo_acceso_en` | `timestamp with time zone` | NOT NULL | — | — | `Python: función <lambda>` |

**Restricciones e índices**

- PK: `id`.
- UNIQUE `sin nombre explícito`: `google_sub`.

### configuracion_flujo

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `parametros` | `jsonb` | NOT NULL | — | — | — |
| `actualizado_por` | `integer` | NOT NULL | FK | `usuario.id` | — |
| `actualizado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_configuracion_flujo_unica`: `id = 1`.
- FK `actualizado_por` → `usuario.id`; ON DELETE `RESTRICT`.

### configuracion_inicial

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `preparacion_ejecucion_id` | `integer` | NULL | FK | `ejecucion_automatizacion.id` | — |
| `modelo_id` | `integer` | NULL | FK | `artefacto_modelo.id` | — |
| `preparacion_numero` | `integer` | NOT NULL | — | — | `Servidor: 0; Python: 0` |
| `id` | `integer` | NOT NULL | PK | — | — |
| `estado` | `varchar(20)` | NOT NULL | — | — | `Servidor: PENDIENTE` |
| `huella_ventas` | `varchar(64)` | NULL | — | — | — |
| `huella_catalogo` | `varchar(64)` | NULL | — | — | — |
| `huella_solicitud` | `varchar(64)` | NULL | — | — | — |
| `fecha_objetivo_demo` | `date` | NULL | — | — | — |
| `fecha_referencia_stock` | `date` | NULL | — | — | — |
| `iniciada_en` | `timestamp with time zone` | NULL | — | — | — |
| `completada_en` | `timestamp with time zone` | NULL | — | — | — |
| `mensaje_error` | `text` | NULL | — | — | — |
| `actualizado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_configuracion_inicial_estado`: `estado in ('PENDIENTE', 'DATOS_CARGADOS', 'ENTRENANDO', 'MODELO_LISTO', 'FALLIDA')`.
- CHECK `ck_configuracion_inicial_fechas`: `fecha_referencia_stock is null or fecha_objetivo_demo is null or fecha_referencia_stock < fecha_objetivo_demo`.
- CHECK `ck_configuracion_inicial_fila_unica`: `id = 1`.
- CHECK `ck_inicializacion_preparacion_numero`: `preparacion_numero >= 0`.
- FK `modelo_id` → `artefacto_modelo.id`; ON DELETE `RESTRICT`.
- FK `preparacion_ejecucion_id` → `ejecucion_automatizacion.id`; ON DELETE `RESTRICT`.

### corrida_pronostico

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `ejecucion_id` | `integer` | NOT NULL | FK | `ejecucion_automatizacion.id` | — |
| `tipo` | `varchar(20)` | NOT NULL | — | — | — |
| `clave_ejecucion` | `varchar(128)` | NOT NULL | UK | — | — |
| `huella_datos_entrada` | `varchar(64)` | NOT NULL | — | — | — |
| `fecha_objetivo` | `date` | NOT NULL | — | — | — |
| `modelo_id` | `integer` | NOT NULL | FK | `artefacto_modelo.id` | — |
| `estado` | `varchar(20)` | NOT NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |
| `finalizado_en` | `timestamp with time zone` | NULL | — | — | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_corrida_pronostico_estado`: `estado IN ('COMPLETADA', 'SIN_COBERTURA')`.
- CHECK `ck_corrida_pronostico_tipo`: `tipo IN ('BACKTEST', 'DEMO_PROGRAMADA')`.
- UNIQUE `uq_corrida_pronostico_clave`: `clave_ejecucion`.
- FK `ejecucion_id` → `ejecucion_automatizacion.id`; ON DELETE `RESTRICT`.
- FK `modelo_id` → `artefacto_modelo.id`; ON DELETE `RESTRICT`.
- Índice: `CREATE INDEX ix_corrida_pronostico_fecha ON corrida_pronostico (fecha_objetivo)`.

### ejecucion_automatizacion

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `programacion_id` | `integer` | NULL | FK, UK | `programacion_demo.id` | — |
| `tipo` | `varchar(32)` | NOT NULL | — | — | — |
| `clave_idempotencia` | `varchar(128)` | NOT NULL | UK | — | — |
| `huella_entrada` | `varchar(64)` | NOT NULL | — | — | — |
| `datos_entrada_json` | `jsonb` | NOT NULL | — | — | — |
| `estado` | `varchar(16)` | NOT NULL | — | — | `Servidor: PENDIENTE; Python: PENDIENTE` |
| `inicio_en` | `timestamp with time zone` | NULL | — | — | — |
| `fin_en` | `timestamp with time zone` | NULL | — | — | — |
| `proximo_intento_en` | `timestamp with time zone` | NULL | — | — | — |
| `despachada_en` | `timestamp with time zone` | NULL | — | — | — |
| `lease_hasta` | `timestamp with time zone` | NULL | — | — | — |
| `token_despacho` | `varchar(36)` | NULL | — | — | — |
| `datos_salida_json` | `jsonb` | NULL | — | — | — |
| `mensaje_error` | `text` | NULL | — | — | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_ejecucion_automatizacion_estado`: `estado IN ('PENDIENTE', 'EN_EJECUCION', 'REINTENTANDO', 'COMPLETADA', 'FALLIDA', 'CANCELADA')`.
- CHECK `ck_ejecucion_automatizacion_tipo`: `tipo IN ('PREPARAR_MODELO', 'EVALUAR_MODELO', 'GENERAR_PROPUESTA', 'EVALUAR_PRONOSTICO', 'EVALUAR_PROMOCION')`.
- UNIQUE `uq_ejecucion_automatizacion_clave`: `clave_idempotencia`.
- UNIQUE `uq_ejecucion_automatizacion_programacion`: `programacion_id`.
- FK `programacion_id` → `programacion_demo.id`; ON DELETE `RESTRICT`.
- Índice: `CREATE INDEX ix_ejecucion_automatizacion_estado ON ejecucion_automatizacion (estado)`.
- Índice: `CREATE INDEX ix_ejecucion_automatizacion_lease ON ejecucion_automatizacion (estado, lease_hasta)`.

### elemento_plan

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `plan_id` | `integer` | NOT NULL | FK | `plan_produccion.id` | — |
| `producto_id` | `integer` | NOT NULL | FK | `producto.id` | — |
| `pronostico_id` | `integer` | NOT NULL | FK | `pronostico.id` | — |
| `receta_id` | `integer` | NULL | FK | `receta.id` | — |
| `cantidad_pronosticada` | `integer` | NULL | — | — | — |
| `stock_disponible` | `integer` | NULL | — | — | — |
| `cantidad_producir` | `integer` | NULL | — | — | — |
| `estado` | `varchar(32)` | NOT NULL | — | — | — |
| `receta_json` | `jsonb` | NULL | — | — | — |
| `stock_json` | `jsonb` | NOT NULL | — | — | — |
| `avisos_json` | `jsonb` | NOT NULL | — | — | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_elemento_plan_calculo`: `(estado = 'CALCULADO' AND cantidad_producir IS NOT NULL AND cantidad_producir >= 0 AND cantidad_pronosticada IS NOT NULL AND stock_disponible IS NOT NULL AND receta_id IS NOT NULL) OR (estado != 'CALCULADO' AND cantidad_producir IS NULL)`.
- CHECK `ck_elemento_plan_estado`: `estado IN ('CALCULADO', 'HISTORIAL_INSUFICIENTE', 'PRODUCTO_NO_CUBIERTO', 'SIN_RECETA', 'STOCK_DESCONOCIDO')`.
- CHECK `ck_elemento_plan_formula`: `estado != 'CALCULADO' OR cantidad_producir = CASE WHEN cantidad_pronosticada > stock_disponible THEN cantidad_pronosticada - stock_disponible ELSE 0 END`.
- CHECK `ck_elemento_plan_pronostico`: `cantidad_pronosticada IS NULL OR cantidad_pronosticada >= 0`.
- CHECK `ck_elemento_plan_stock`: `stock_disponible IS NULL OR stock_disponible >= 0`.
- UNIQUE `uq_elemento_plan_producto`: `plan_id, producto_id`.
- FK `plan_id` → `plan_produccion.id`; ON DELETE `RESTRICT`.
- FK `producto_id` → `producto.id`; ON DELETE `RESTRICT`.
- FK `pronostico_id` → `pronostico.id`; ON DELETE `RESTRICT`.
- FK `receta_id` → `receta.id`; ON DELETE `RESTRICT`.

### envio_pedido

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `pedido_id` | `integer` | NOT NULL | FK | `pedido_compra.id` | — |
| `numero_intento` | `integer` | NOT NULL | — | — | `Servidor: 1; Python: 1` |
| `estado` | `varchar(24)` | NOT NULL | — | — | — |
| `chat_id` | `varchar(64)` | NOT NULL | — | — | — |
| `credencial_huella` | `varchar(64)` | NOT NULL | — | — | — |
| `texto` | `text` | NOT NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |
| `inicio_en` | `timestamp with time zone` | NULL | — | — | — |
| `fin_en` | `timestamp with time zone` | NULL | — | — | — |
| `fecha_telegram` | `timestamp with time zone` | NULL | — | — | — |
| `message_id` | `bigint` | NULL | — | — | — |
| `codigo_error` | `varchar(64)` | NULL | — | — | — |
| `detalle_error` | `varchar(500)` | NULL | — | — | — |
| `despachado_en` | `timestamp with time zone` | NULL | — | — | — |
| `lease_hasta` | `timestamp with time zone` | NULL | — | — | — |
| `token_despacho` | `varchar(36)` | NULL | — | — | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_envio_confirmacion`: `(estado = 'ENVIADO' AND message_id IS NOT NULL AND message_id > 0 AND fin_en IS NOT NULL) OR (estado <> 'ENVIADO' AND message_id IS NULL)`.
- CHECK `ck_envio_estado`: `estado IN ('PENDIENTE_ENVIO','ENVIANDO','ENVIADO','FALLIDO','PENDIENTE_VERIFICACION')`.
- CHECK `ck_envio_numero`: `numero_intento >= 1`.
- UNIQUE `uq_envio_evidencia_telegram`: `chat_id, message_id`.
- UNIQUE `uq_envio_pedido_intento`: `pedido_id, numero_intento`.
- FK `pedido_id` → `pedido_compra.id`; ON DELETE `RESTRICT`.
- Índice: `CREATE INDEX ix_envio_pendiente ON envio_pedido (estado, lease_hasta)`.

### evaluacion_promocion

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `regla_id` | `integer` | NOT NULL | FK | `regla_promocion_demo.id` | — |
| `movimiento_id` | `integer` | NOT NULL | FK, UK | `movimiento_inventario.id` | — |
| `ejecucion_id` | `integer` | NOT NULL | FK, UK | `ejecucion_automatizacion.id` | — |
| `proponer` | `boolean` | NOT NULL | — | — | — |
| `motivo` | `varchar(300)` | NOT NULL | — | — | — |
| `descuento_pct` | `integer` | NULL | — | — | — |
| `lectura` | `json` | NOT NULL | — | — | — |
| `fecha_hora_simulada` | `timestamp without time zone` | NOT NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_evaluacion_promocion_descuento`: `descuento_pct IS NULL OR descuento_pct BETWEEN 1 AND 100`.
- UNIQUE `uq_evaluacion_promocion_ejecucion`: `ejecucion_id`.
- UNIQUE `uq_evaluacion_promocion_movimiento`: `movimiento_id`.
- FK `ejecucion_id` → `ejecucion_automatizacion.id`; ON DELETE `RESTRICT`.
- FK `movimiento_id` → `movimiento_inventario.id`; ON DELETE `RESTRICT`.
- FK `regla_id` → `regla_promocion_demo.id`; ON DELETE `RESTRICT`.

### evaluacion_pronostico

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `ejecucion_id` | `integer` | NOT NULL | FK | `ejecucion_automatizacion.id` | — |
| `corrida_id` | `integer` | NOT NULL | FK | `corrida_pronostico.id` | — |
| `pronostico_id` | `integer` | NOT NULL | FK | `pronostico.id` | — |
| `revision_venta_id` | `integer` | NOT NULL | FK | `revision_venta.id` | — |
| `producto_id` | `integer` | NOT NULL | FK | `producto.id` | — |
| `cantidad_pronosticada` | `integer` | NOT NULL | — | — | — |
| `unidades_reales` | `integer` | NOT NULL | — | — | — |
| `error_absoluto` | `integer` | NOT NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_evaluacion_pronostico_cantidades`: `cantidad_pronosticada >= 0 AND unidades_reales >= 0 AND error_absoluto >= 0`.
- UNIQUE `uq_evaluacion_pronostico_revision`: `corrida_id, producto_id, revision_venta_id`.
- FK `corrida_id` → `corrida_pronostico.id`; ON DELETE `RESTRICT`.
- FK `ejecucion_id` → `ejecucion_automatizacion.id`; ON DELETE `RESTRICT`.
- FK `producto_id` → `producto.id`; ON DELETE `RESTRICT`.
- FK `pronostico_id` → `pronostico.id`; ON DELETE `RESTRICT`.
- FK `revision_venta_id` → `revision_venta.id`; ON DELETE `RESTRICT`.

### importacion_venta

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `origen` | `varchar(40)` | NOT NULL | — | — | — |
| `clave_importacion` | `varchar(128)` | NOT NULL | — | — | — |
| `huella_contenido` | `varchar(64)` | NOT NULL | — | — | — |
| `filas_aceptadas` | `integer` | NOT NULL | — | — | — |
| `estado` | `varchar(16)` | NOT NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_importacion_venta_estado`: `estado = 'COMPLETADA'`.
- CHECK `ck_importacion_venta_filas`: `filas_aceptadas >= 0`.
- UNIQUE `uq_importacion_venta_clave`: `origen, clave_importacion`.

### ingrediente

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `codigo` | `varchar(160)` | NOT NULL | UK | — | — |
| `nombre` | `varchar(160)` | NOT NULL | — | — | — |
| `unidad_base` | `varchar(10)` | NOT NULL | — | — | — |
| `activo` | `boolean` | NOT NULL | — | — | `Servidor: true; Python: True` |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_ingrediente_codigo`: `length(trim(codigo)) > 0`.
- CHECK `ck_ingrediente_nombre`: `length(trim(nombre)) > 0`.
- CHECK `ck_ingrediente_unidad_base`: `unidad_base in ('g', 'kg', 'ml', 'l', 'unidad')`.
- UNIQUE `uq_ingrediente_codigo`: `codigo`.

### intento_automatizacion

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `ejecucion_id` | `integer` | NOT NULL | FK | `ejecucion_automatizacion.id` | — |
| `numero_intento` | `integer` | NOT NULL | — | — | — |
| `inicio_en` | `timestamp with time zone` | NOT NULL | — | — | — |
| `fin_en` | `timestamp with time zone` | NULL | — | — | — |
| `estado` | `varchar(16)` | NOT NULL | — | — | — |
| `mensaje_error` | `text` | NULL | — | — | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_intento_automatizacion_estado`: `estado IN ('EN_EJECUCION', 'COMPLETADA', 'FALLIDA')`.
- CHECK `ck_intento_automatizacion_numero`: `numero_intento BETWEEN 1 AND 3`.
- UNIQUE `uq_intento_automatizacion_numero`: `ejecucion_id, numero_intento`.
- FK `ejecucion_id` → `ejecucion_automatizacion.id`; ON DELETE `RESTRICT`.

### linea_pedido

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `pedido_id` | `integer` | NOT NULL | FK | `pedido_compra.id` | — |
| `necesidad_ingrediente_id` | `integer` | NOT NULL | FK, UK | `necesidad_ingrediente.id` | — |
| `oferta_ingrediente_id` | `integer` | NOT NULL | FK | `oferta_ingrediente.id` | — |
| `ingrediente_id` | `integer` | NOT NULL | FK | `ingrediente.id` | — |
| `faltante_base` | `numeric(14, 3)` | NOT NULL | — | — | — |
| `cantidad_compra` | `numeric(20, 4)` | NOT NULL | — | — | — |
| `cantidad_base_pedida` | `numeric(30, 8)` | NOT NULL | — | — | — |
| `unidad_base` | `varchar(16)` | NOT NULL | — | — | — |
| `unidad_compra` | `varchar(30)` | NOT NULL | — | — | — |
| `oferta_json` | `jsonb` | NOT NULL | — | — | — |
| `ingrediente_json` | `jsonb` | NOT NULL | — | — | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_linea_pedido_cantidades`: `faltante_base > 0 AND cantidad_compra > 0 AND cantidad_base_pedida >= faltante_base`.
- UNIQUE `uq_linea_pedido_necesidad`: `necesidad_ingrediente_id`.
- FK `ingrediente_id` → `ingrediente.id`; ON DELETE `RESTRICT`.
- FK `necesidad_ingrediente_id` → `necesidad_ingrediente.id`; ON DELETE `RESTRICT`.
- FK `oferta_ingrediente_id` → `oferta_ingrediente.id`; ON DELETE `RESTRICT`.
- FK `pedido_id` → `pedido_compra.id`; ON DELETE `RESTRICT`.

### linea_recepcion_pedido

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `recepcion_id` | `integer` | NOT NULL | FK | `recepcion_pedido.id` | — |
| `linea_pedido_id` | `integer` | NOT NULL | FK | `linea_pedido.id` | — |
| `cantidad_compra` | `numeric(20, 4)` | NOT NULL | — | — | — |
| `cantidad_base` | `numeric(14, 3)` | NOT NULL | — | — | — |
| `lote_id` | `integer` | NOT NULL | FK, UK | `lote_ingrediente.id` | — |
| `movimiento_id` | `integer` | NOT NULL | FK, UK | `movimiento_inventario.id` | — |
| `codigo_lote` | `varchar(80)` | NOT NULL | — | — | — |
| `fecha_caducidad` | `date` | NULL | — | — | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_recepcion_cantidades`: `cantidad_compra > 0 AND cantidad_base > 0`.
- UNIQUE `sin nombre explícito`: `lote_id`.
- UNIQUE `sin nombre explícito`: `movimiento_id`.
- UNIQUE `uq_recepcion_linea`: `recepcion_id, linea_pedido_id`.
- FK `linea_pedido_id` → `linea_pedido.id`; ON DELETE `RESTRICT`.
- FK `lote_id` → `lote_ingrediente.id`; ON DELETE `RESTRICT`.
- FK `movimiento_id` → `movimiento_inventario.id`; ON DELETE `RESTRICT`.
- FK `recepcion_id` → `recepcion_pedido.id`; ON DELETE `RESTRICT`.
- Índice: `CREATE INDEX ix_linea_recepcion_pedido_linea_pedido_id ON linea_recepcion_pedido (linea_pedido_id)`.
- Índice: `CREATE INDEX ix_linea_recepcion_pedido_recepcion_id ON linea_recepcion_pedido (recepcion_id)`.

### lote_ingrediente

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `ingrediente_id` | `integer` | NOT NULL | FK | `ingrediente.id` | — |
| `codigo_lote` | `varchar(80)` | NOT NULL | — | — | — |
| `lote_informado` | `boolean` | NOT NULL | — | — | — |
| `fecha_caducidad` | `date` | NULL | — | — | — |
| `fecha_ingreso` | `date` | NULL | — | — | — |
| `saldo_disponible` | `numeric(14, 3)` | NOT NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |
| `actualizado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_lote_ingrediente_codigo`: `length(trim(codigo_lote)) > 0`.
- CHECK `ck_lote_ingrediente_saldo`: `saldo_disponible >= 0`.
- UNIQUE `uq_lote_ingrediente_codigo`: `ingrediente_id, codigo_lote`.
- FK `ingrediente_id` → `ingrediente.id`; ON DELETE `RESTRICT`.

### lote_producto

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `producto_id` | `integer` | NOT NULL | FK | `producto.id` | — |
| `codigo_lote` | `varchar(80)` | NOT NULL | — | — | — |
| `lote_informado` | `boolean` | NOT NULL | — | — | — |
| `fecha_caducidad` | `date` | NULL | — | — | — |
| `fecha_limite_venta` | `date` | NULL | — | — | — |
| `saldo_disponible` | `integer` | NOT NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |
| `actualizado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_lote_producto_codigo`: `length(trim(codigo_lote)) > 0`.
- CHECK `ck_lote_producto_limite_venta`: `fecha_limite_venta is null or fecha_caducidad is null or fecha_limite_venta <= fecha_caducidad`.
- CHECK `ck_lote_producto_saldo`: `saldo_disponible >= 0`.
- UNIQUE `uq_lote_producto_codigo`: `producto_id, codigo_lote`.
- FK `producto_id` → `producto.id`; ON DELETE `RESTRICT`.

### movimiento_inventario

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `lote_ingrediente_id` | `integer` | NULL | FK | `lote_ingrediente.id` | — |
| `lote_producto_id` | `integer` | NULL | FK | `lote_producto.id` | — |
| `delta` | `numeric(14, 3)` | NOT NULL | — | — | — |
| `saldo_resultante` | `numeric(14, 3)` | NOT NULL | — | — | — |
| `tipo` | `varchar(12)` | NOT NULL | — | — | — |
| `clave_operacion` | `varchar(200)` | NOT NULL | UK | — | — |
| `motivo` | `varchar(300)` | NOT NULL | — | — | — |
| `usuario_id` | `integer` | NULL | FK | `usuario.id` | — |
| `efectivo_en_demo` | `timestamp without time zone` | NOT NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_movimiento_inventario_delta`: `delta <> 0`.
- CHECK `ck_movimiento_inventario_delta_entero_producto`: `lote_producto_id is null or delta = round(delta, 0)`.
- CHECK `ck_movimiento_inventario_motivo`: `length(trim(motivo)) > 0`.
- CHECK `ck_movimiento_inventario_saldo`: `saldo_resultante >= 0`.
- CHECK `ck_movimiento_inventario_tipo`: `tipo in ('APERTURA', 'AJUSTE', 'RECEPCION')`.
- CHECK `ck_movimiento_inventario_un_lote`: `(lote_ingrediente_id is null) <> (lote_producto_id is null)`.
- CHECK `ck_movimiento_recepcion_ingrediente`: `tipo <> 'RECEPCION' OR lote_producto_id IS NULL`.
- UNIQUE `uq_movimiento_inventario_clave`: `clave_operacion`.
- FK `lote_ingrediente_id` → `lote_ingrediente.id`; ON DELETE `RESTRICT`.
- FK `lote_producto_id` → `lote_producto.id`; ON DELETE `RESTRICT`.
- FK `usuario_id` → `usuario.id`; ON DELETE `RESTRICT`.
- Índice: `CREATE INDEX ix_movimiento_inventario_lote_ingrediente ON movimiento_inventario (lote_ingrediente_id)`.
- Índice: `CREATE INDEX ix_movimiento_inventario_lote_producto ON movimiento_inventario (lote_producto_id)`.

### necesidad_ingrediente

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `plan_id` | `integer` | NOT NULL | FK | `plan_produccion.id` | — |
| `ingrediente_id` | `integer` | NOT NULL | FK | `ingrediente.id` | — |
| `unidad_base` | `varchar(16)` | NOT NULL | — | — | — |
| `cantidad_necesaria` | `numeric(14, 3)` | NOT NULL | — | — | — |
| `stock_disponible` | `numeric(14, 3)` | NULL | — | — | — |
| `faltante` | `numeric(14, 3)` | NULL | — | — | — |
| `estado` | `varchar(24)` | NOT NULL | — | — | — |
| `aportes_json` | `jsonb` | NOT NULL | — | — | — |
| `stock_json` | `jsonb` | NOT NULL | — | — | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_necesidad_cantidad`: `cantidad_necesaria >= 0`.
- CHECK `ck_necesidad_estado`: `(estado = 'DISPONIBLE' AND stock_disponible IS NOT NULL AND stock_disponible >= 0 AND faltante IS NOT NULL AND faltante >= 0) OR (estado = 'STOCK_DESCONOCIDO' AND stock_disponible IS NULL AND faltante IS NULL)`.
- CHECK `ck_necesidad_formula`: `faltante IS NULL OR faltante = CASE WHEN cantidad_necesaria > stock_disponible THEN cantidad_necesaria - stock_disponible ELSE 0 END`.
- UNIQUE `uq_necesidad_plan_ingrediente`: `plan_id, ingrediente_id`.
- FK `ingrediente_id` → `ingrediente.id`; ON DELETE `RESTRICT`.
- FK `plan_id` → `plan_produccion.id`; ON DELETE `RESTRICT`.

### negocio

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `nombre` | `varchar(160)` | NOT NULL | — | — | — |
| `zona_horaria` | `varchar(80)` | NOT NULL | — | — | — |
| `moneda` | `varchar(3)` | NOT NULL | — | — | — |
| `modo_envio_pedidos` | `varchar(20)` | NOT NULL | — | — | `Servidor: 'REQUIERE_APROBACION'` |
| `hora_apertura` | `time without time zone` | NULL | — | — | — |
| `hora_cierre` | `time without time zone` | NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Python: función <lambda>` |
| `actualizado_en` | `timestamp with time zone` | NOT NULL | — | — | `Python: función <lambda>; onupdate Python` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_negocio_modo_envio_pedidos`: `modo_envio_pedidos IN ('REQUIERE_APROBACION', 'AUTOMATICO')`.
- CHECK `ck_negocio_moneda`: `char_length(moneda) = 3`.
- CHECK `ck_negocio_unico`: `id = 1`.

### oferta_ingrediente

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `proveedor_id` | `integer` | NOT NULL | FK | `proveedor.id` | — |
| `ingrediente_id` | `integer` | NOT NULL | FK | `ingrediente.id` | — |
| `descripcion` | `varchar(120)` | NOT NULL | — | — | — |
| `unidad_compra` | `varchar(30)` | NOT NULL | — | — | — |
| `factor_conversion` | `numeric(14, 4)` | NOT NULL | — | — | — |
| `minimo` | `numeric(14, 4)` | NOT NULL | — | — | `Python: 0` |
| `multiplo` | `numeric(14, 4)` | NOT NULL | — | — | `Python: 1` |
| `activa` | `boolean` | NOT NULL | — | — | `Python: True` |
| `preferida` | `boolean` | NOT NULL | — | — | `Python: False` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_oferta_factor`: `factor_conversion > 0`.
- CHECK `ck_oferta_minimo`: `minimo >= 0`.
- CHECK `ck_oferta_multiplo`: `multiplo > 0`.
- FK `ingrediente_id` → `ingrediente.id`; ON DELETE `RESTRICT`.
- FK `proveedor_id` → `proveedor.id`; ON DELETE `NO ACTION`.
- Índice: `CREATE INDEX ix_oferta_ingrediente_ingrediente_id ON oferta_ingrediente (ingrediente_id)`.
- Índice: `CREATE UNIQUE INDEX uq_oferta_preferida_activa ON oferta_ingrediente (ingrediente_id) WHERE preferida AND activa`.

### pedido_compra

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `propuesta_id` | `integer` | NOT NULL | FK | `propuesta_compra.id` | — |
| `plan_id` | `integer` | NOT NULL | FK | `plan_produccion.id` | — |
| `proveedor_id` | `integer` | NOT NULL | FK | `proveedor.id` | — |
| `proveedor_json` | `jsonb` | NOT NULL | — | — | — |
| `estado` | `varchar(24)` | NOT NULL | — | — | — |
| `modo_envio` | `varchar(24)` | NOT NULL | — | — | — |
| `bloqueos_json` | `jsonb` | NOT NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |
| `clave_decision` | `varchar(80)` | NULL | UK | — | — |
| `decidido_por` | `integer` | NULL | FK | `usuario.id` | — |
| `decidido_en` | `timestamp with time zone` | NULL | — | — | — |
| `decision_json` | `jsonb` | NULL | — | — | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_pedido_compra_estado`: `estado IN ('BLOQUEADO','PENDIENTE_APROBACION','CANCELADO','RECHAZADO','PENDIENTE_ENVIO','ENVIANDO','ENVIADO','FALLIDO','PENDIENTE_VERIFICACION')`.
- CHECK `ck_pedido_decision_completa`: `(clave_decision IS NULL AND decidido_por IS NULL AND decidido_en IS NULL AND decision_json IS NULL) OR (clave_decision IS NOT NULL AND decidido_por IS NOT NULL AND decidido_en IS NOT NULL AND decision_json IS NOT NULL)`.
- UNIQUE `uq_pedido_clave_decision`: `clave_decision`.
- UNIQUE `uq_pedido_plan_proveedor`: `plan_id, proveedor_id`.
- FK `decidido_por` → `usuario.id`; ON DELETE `RESTRICT`.
- FK `plan_id` → `plan_produccion.id`; ON DELETE `RESTRICT`.
- FK `propuesta_id` → `propuesta_compra.id`; ON DELETE `RESTRICT`.
- FK `proveedor_id` → `proveedor.id`; ON DELETE `RESTRICT`.

### plan_produccion

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `corrida_id` | `integer` | NOT NULL | FK | `corrida_pronostico.id` | — |
| `ejecucion_id` | `integer` | NOT NULL | FK | `ejecucion_automatizacion.id` | — |
| `clave_ejecucion` | `varchar(128)` | NOT NULL | UK | — | — |
| `huella_stock_recetas` | `varchar(64)` | NOT NULL | — | — | — |
| `fecha_objetivo` | `date` | NOT NULL | — | — | — |
| `stock_leido_en` | `timestamp with time zone` | NOT NULL | — | — | — |
| `estado` | `varchar(16)` | NOT NULL | — | — | — |
| `version_calculo` | `varchar(16)` | NOT NULL | — | — | — |
| `origen_pronostico_json` | `jsonb` | NOT NULL | — | — | — |
| `necesidades_estado` | `varchar(24)` | NOT NULL | — | — | `Servidor: PENDIENTE_M03` |
| `necesidades_meta_json` | `jsonb` | NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_plan_produccion_estado`: `estado = 'PROPUESTO'`.
- UNIQUE `uq_plan_produccion_clave`: `clave_ejecucion`.
- FK `corrida_id` → `corrida_pronostico.id`; ON DELETE `RESTRICT`.
- FK `ejecucion_id` → `ejecucion_automatizacion.id`; ON DELETE `RESTRICT`.
- Índice: `CREATE INDEX ix_plan_produccion_corrida ON plan_produccion (corrida_id)`.

### producto

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `codigo` | `varchar(160)` | NOT NULL | UK | — | — |
| `nombre` | `varchar(160)` | NOT NULL | — | — | — |
| `demostrar` | `boolean` | NOT NULL | — | — | `Servidor: false; Python: False` |
| `activo` | `boolean` | NOT NULL | — | — | `Servidor: true; Python: True` |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_producto_codigo`: `length(trim(codigo)) > 0`.
- CHECK `ck_producto_nombre`: `length(trim(nombre)) > 0`.
- UNIQUE `uq_producto_codigo`: `codigo`.

### programacion_demo

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `tipo` | `varchar(32)` | NOT NULL | — | — | — |
| `ejecutar_desde_utc` | `timestamp with time zone` | NOT NULL | — | — | — |
| `fecha_hora_simulada_local` | `timestamp without time zone` | NOT NULL | — | — | — |
| `parametros_json` | `jsonb` | NOT NULL | — | — | — |
| `clave_idempotencia` | `varchar(128)` | NOT NULL | UK | — | — |
| `huella_entrada` | `varchar(64)` | NOT NULL | — | — | — |
| `estado` | `varchar(16)` | NOT NULL | — | — | `Servidor: PROGRAMADA; Python: PROGRAMADA` |
| `despachada_en` | `timestamp with time zone` | NULL | — | — | — |
| `lease_hasta` | `timestamp with time zone` | NULL | — | — | — |
| `creado_por` | `integer` | NULL | FK | `usuario.id` | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |
| `cambios_json` | `jsonb` | NOT NULL | — | — | `Servidor: []; Python: función list` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_programacion_demo_estado`: `estado IN ('PROGRAMADA', 'DESPACHADA', 'PAUSADA', 'CANCELADA')`.
- CHECK `ck_programacion_demo_tipo`: `tipo IN ('GENERAR_PROPUESTA', 'EVALUAR_PROMOCION')`.
- UNIQUE `uq_programacion_demo_clave`: `clave_idempotencia`.
- FK `creado_por` → `usuario.id`; ON DELETE `RESTRICT`.
- Índice: `CREATE INDEX ix_programacion_demo_vencimientos ON programacion_demo (estado, ejecutar_desde_utc)`.

### pronostico

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `corrida_id` | `integer` | NOT NULL | FK | `corrida_pronostico.id` | — |
| `producto_id` | `integer` | NOT NULL | FK | `producto.id` | — |
| `cantidad_pronosticada` | `integer` | NULL | — | — | — |
| `estado` | `varchar(32)` | NOT NULL | — | — | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_pronostico_cantidad_estado`: `(estado = 'DISPONIBLE' AND cantidad_pronosticada >= 0) OR (estado != 'DISPONIBLE' AND cantidad_pronosticada IS NULL)`.
- CHECK `ck_pronostico_estado`: `estado IN ('DISPONIBLE', 'HISTORIAL_INSUFICIENTE', 'PRODUCTO_NO_CUBIERTO')`.
- UNIQUE `uq_pronostico_corrida_producto`: `corrida_id, producto_id`.
- FK `corrida_id` → `corrida_pronostico.id`; ON DELETE `RESTRICT`.
- FK `producto_id` → `producto.id`; ON DELETE `RESTRICT`.

### propuesta_compra

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `plan_id` | `integer` | NOT NULL | FK, UK | `plan_produccion.id` | — |
| `fecha_objetivo` | `date` | NOT NULL | — | — | — |
| `estado` | `varchar(24)` | NOT NULL | — | — | — |
| `activa` | `boolean` | NOT NULL | — | — | — |
| `modo_envio` | `varchar(24)` | NOT NULL | — | — | — |
| `necesidades_json` | `jsonb` | NOT NULL | — | — | — |
| `incidencias_json` | `jsonb` | NOT NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |
| `cancelado_en` | `timestamp with time zone` | NULL | — | — | — |
| `cancelado_por` | `integer` | NULL | FK | `usuario.id` | — |
| `motivo_cancelacion` | `varchar(500)` | NULL | — | — | — |
| `reemplazo_id` | `integer` | NULL | FK | `propuesta_compra.id` | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_propuesta_compra_activa`: `(estado IN ('GENERADA','BLOQUEADA') AND activa) OR (estado IN ('SIN_FALTANTES','CANCELADA') AND NOT activa)`.
- CHECK `ck_propuesta_compra_estado`: `estado IN ('GENERADA','BLOQUEADA','SIN_FALTANTES','CANCELADA')`.
- CHECK `ck_propuesta_compra_modo`: `modo_envio IN ('REQUIERE_APROBACION','AUTOMATICO')`.
- UNIQUE `uq_propuesta_compra_plan`: `plan_id`.
- FK `cancelado_por` → `usuario.id`; ON DELETE `RESTRICT`.
- FK `plan_id` → `plan_produccion.id`; ON DELETE `RESTRICT`.
- FK `reemplazo_id` → `propuesta_compra.id`; ON DELETE `RESTRICT`.
- Índice: `CREATE UNIQUE INDEX uq_propuesta_compra_fecha_activa ON propuesta_compra (fecha_objetivo) WHERE activa`.

### proveedor

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `codigo` | `varchar(30)` | NOT NULL | UK | — | — |
| `nombre` | `varchar(120)` | NOT NULL | — | — | — |
| `activo` | `boolean` | NOT NULL | — | — | `Python: True` |
| `chat_id_pruebas` | `varchar(64)` | NULL | — | — | — |
| `destino_verificado` | `boolean` | NOT NULL | — | — | `Python: False` |
| `destino_verificado_en` | `timestamp with time zone` | NULL | — | — | — |
| `destino_credencial_huella` | `varchar(64)` | NULL | — | — | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_proveedor_codigo`: `length(trim(codigo)) > 0`.
- CHECK `ck_proveedor_nombre`: `length(trim(nombre)) > 0`.
- UNIQUE `sin nombre explícito`: `codigo`.

### prueba_mensaje_proveedor

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `proveedor_id` | `integer` | NOT NULL | FK | `proveedor.id` | — |
| `usuario_id` | `integer` | NOT NULL | FK | `usuario.id` | — |
| `clave_idempotencia` | `varchar(80)` | NOT NULL | UK | — | — |
| `chat_id` | `varchar(64)` | NOT NULL | — | — | — |
| `credencial_huella` | `varchar(64)` | NOT NULL | — | — | — |
| `texto` | `text` | NOT NULL | — | — | — |
| `revision_chat_confirmada` | `boolean` | NOT NULL | — | — | `Python: False` |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: CURRENT_TIMESTAMP` |
| `estado` | `varchar(24)` | NOT NULL | — | — | `Python: PENDIENTE_VERIFICACION` |
| `message_id` | `bigint` | NULL | — | — | — |
| `fecha_telegram` | `timestamp with time zone` | NULL | — | — | — |
| `detalle` | `varchar(300)` | NOT NULL | — | — | `Python: Resultado pendiente. Revisa el chat antes de autorizar otra prueba.` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_prueba_proveedor_estado`: `estado IN ('ENVIADO','FALLIDO','PENDIENTE_VERIFICACION')`.
- UNIQUE `sin nombre explícito`: `clave_idempotencia`.
- FK `proveedor_id` → `proveedor.id`; ON DELETE `RESTRICT`.
- FK `usuario_id` → `usuario.id`; ON DELETE `RESTRICT`.
- Índice: `CREATE INDEX ix_prueba_mensaje_proveedor_proveedor_id ON prueba_mensaje_proveedor (proveedor_id)`.

### recepcion_pedido

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `pedido_id` | `integer` | NOT NULL | FK | `pedido_compra.id` | — |
| `clave_idempotencia` | `varchar(80)` | NOT NULL | UK | — | — |
| `usuario_id` | `integer` | NOT NULL | FK | `usuario.id` | — |
| `nombre_usuario` | `varchar(150)` | NOT NULL | — | — | — |
| `fecha_recepcion` | `date` | NOT NULL | — | — | — |
| `motivo` | `varchar(300)` | NOT NULL | — | — | — |
| `solicitud_json` | `jsonb` | NOT NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- UNIQUE `sin nombre explícito`: `clave_idempotencia`.
- FK `pedido_id` → `pedido_compra.id`; ON DELETE `RESTRICT`.
- FK `usuario_id` → `usuario.id`; ON DELETE `RESTRICT`.
- Índice: `CREATE INDEX ix_recepcion_pedido_pedido_id ON recepcion_pedido (pedido_id)`.

### receta

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `producto_id` | `integer` | NOT NULL | FK | `producto.id` | — |
| `version` | `integer` | NOT NULL | — | — | — |
| `activo` | `boolean` | NOT NULL | — | — | `Servidor: true; Python: True` |
| `motivo` | `varchar(300)` | NULL | — | — | — |
| `creado_por` | `integer` | NULL | FK | `usuario.id` | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_receta_version`: `version >= 1`.
- UNIQUE `uq_receta_producto_version`: `producto_id, version`.
- FK `creado_por` → `usuario.id`; ON DELETE `RESTRICT`.
- FK `producto_id` → `producto.id`; ON DELETE `RESTRICT`.
- Índice: `CREATE UNIQUE INDEX uq_receta_activa_por_producto ON receta (producto_id) WHERE activo`.

### receta_ingrediente

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `receta_id` | `integer` | NOT NULL | FK | `receta.id` | — |
| `ingrediente_id` | `integer` | NOT NULL | FK | `ingrediente.id` | — |
| `cantidad_por_unidad` | `numeric(14, 3)` | NOT NULL | — | — | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_receta_ingrediente_cantidad`: `cantidad_por_unidad > 0`.
- UNIQUE `uq_receta_ingrediente_pareja`: `receta_id, ingrediente_id`.
- FK `ingrediente_id` → `ingrediente.id`; ON DELETE `RESTRICT`.
- FK `receta_id` → `receta.id`; ON DELETE `RESTRICT`.
- Índice: `CREATE INDEX ix_receta_ingrediente_ingrediente ON receta_ingrediente (ingrediente_id)`.

### recuperacion_envio

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `envio_id` | `integer` | NOT NULL | FK | `envio_pedido.id` | — |
| `clave_idempotencia` | `varchar(80)` | NOT NULL | UK | — | — |
| `accion` | `varchar(24)` | NOT NULL | — | — | — |
| `usuario_id` | `integer` | NOT NULL | FK | `usuario.id` | — |
| `nombre_usuario` | `varchar(150)` | NOT NULL | — | — | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |
| `evidencia` | `varchar(1500)` | NOT NULL | — | — | — |
| `solicitud_json` | `jsonb` | NOT NULL | — | — | — |
| `resultado_anterior_json` | `jsonb` | NOT NULL | — | — | — |
| `nuevo_envio_id` | `integer` | NULL | FK | `envio_pedido.id` | — |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_recuperacion_accion`: `accion IN ('CONFIRMAR_ENVIO','CONFIRMAR_NO_ENVIO','REINTENTAR')`.
- CHECK `ck_recuperacion_evidencia`: `length(evidencia) BETWEEN 10 AND 1500`.
- UNIQUE `uq_recuperacion_clave`: `clave_idempotencia`.
- FK `envio_id` → `envio_pedido.id`; ON DELETE `RESTRICT`.
- FK `nuevo_envio_id` → `envio_pedido.id`; ON DELETE `RESTRICT`.
- FK `usuario_id` → `usuario.id`; ON DELETE `RESTRICT`.

### regla_promocion_demo

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `version` | `integer` | NOT NULL | UK | — | — |
| `parametros` | `json` | NOT NULL | — | — | — |
| `creado_por` | `integer` | NOT NULL | FK | `usuario.id` | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- UNIQUE `uq_regla_promocion_version`: `version`.
- FK `creado_por` → `usuario.id`; ON DELETE `RESTRICT`.

### revision_venta

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `venta_id` | `integer` | NOT NULL | FK | `venta_diaria.id` | — |
| `numero_revision` | `integer` | NOT NULL | — | — | — |
| `unidades_vendidas` | `integer` | NOT NULL | — | — | — |
| `origen_cambio` | `varchar(32)` | NOT NULL | — | — | — |
| `motivo` | `varchar(255)` | NOT NULL | — | — | — |
| `usuario_id` | `integer` | NULL | FK | `usuario.id` | — |
| `importacion_id` | `integer` | NULL | FK | `importacion_venta.id` | — |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_revision_venta_numero`: `numero_revision >= 1`.
- CHECK `ck_revision_venta_unidades`: `unidades_vendidas >= 0`.
- UNIQUE `uq_revision_venta_numero`: `venta_id, numero_revision`.
- FK `importacion_id` → `importacion_venta.id`; ON DELETE `RESTRICT`.
- FK `usuario_id` → `usuario.id`; ON DELETE `RESTRICT`.
- FK `venta_id` → `venta_diaria.id`; ON DELETE `RESTRICT`.

### sku_producto

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `producto_id` | `integer` | NOT NULL | FK | `producto.id` | — |
| `origen` | `varchar(40)` | NOT NULL | — | — | — |
| `sku_externo` | `varchar(160)` | NOT NULL | — | — | — |
| `activo` | `boolean` | NOT NULL | — | — | `Servidor: true; Python: True` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_sku_producto_origen`: `length(trim(origen)) > 0`.
- CHECK `ck_sku_producto_sku`: `length(trim(sku_externo)) > 0`.
- UNIQUE `uq_sku_producto_origen_sku`: `origen, sku_externo`.
- FK `producto_id` → `producto.id`; ON DELETE `RESTRICT`.

### usuario

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `correo` | `varchar(254)` | NOT NULL | — | — | — |
| `hash_contrasena` | `varchar(512)` | NOT NULL | — | — | — |
| `nombre` | `varchar(160)` | NOT NULL | — | — | — |
| `rol` | `varchar(20)` | NOT NULL | — | — | — |
| `activo` | `boolean` | NOT NULL | — | — | `Python: True` |
| `creado_en` | `timestamp with time zone` | NOT NULL | — | — | `Python: función <lambda>` |
| `actualizado_en` | `timestamp with time zone` | NOT NULL | — | — | `Python: función <lambda>; onupdate Python` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_usuario_rol`: `rol IN ('ADMINISTRADOR', 'OPERADOR')`.
- Índice: `CREATE UNIQUE INDEX uq_usuario_correo_normalizado ON usuario (lower(correo))`.

### venta_diaria

| Columna | Tipo PostgreSQL | Nulabilidad | Clave | Referencia | Default servidor / Python |
|---|---|---|---|---|---|
| `id` | `integer` | NOT NULL | PK | — | — |
| `producto_id` | `integer` | NOT NULL | FK | `producto.id` | — |
| `fecha_local` | `date` | NOT NULL | — | — | — |
| `unidades_vendidas` | `integer` | NOT NULL | — | — | — |
| `importacion_id` | `integer` | NULL | FK | `importacion_venta.id` | — |
| `revision_actual` | `integer` | NOT NULL | — | — | `Python: 1` |
| `actualizado_en` | `timestamp with time zone` | NOT NULL | — | — | `Servidor: now()` |

**Restricciones e índices**

- PK: `id`.
- CHECK `ck_venta_diaria_revision`: `revision_actual >= 1`.
- CHECK `ck_venta_diaria_unidades`: `unidades_vendidas >= 0`.
- UNIQUE `uq_venta_diaria_producto_fecha`: `producto_id, fecha_local`.
- FK `importacion_id` → `importacion_venta.id`; ON DELETE `RESTRICT`.
- FK `producto_id` → `producto.id`; ON DELETE `RESTRICT`.
- Índice: `CREATE INDEX ix_venta_diaria_fecha ON venta_diaria (fecha_local)`.

## Ampliación posterior · 28-10-2026 · Referencia de alcance

Este snapshot permanece fechado0019. El código/base verificados en0023 tienen50 tablas de dominio:45 hasta0022 y cinco operativas (registro_operacion, configuracion_operacion, aviso_operacion, solicitud_proveedor, promocion_operacion). Consultar migraciones0021–0023 y [contrato](../api/contrato-operacion-integrada.md). Tienda mantiene base independiente.
