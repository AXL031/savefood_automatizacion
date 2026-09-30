# Esquema objetivo del prototipo universitario

**Estado:** `0002_e01_ventas` implementa catálogo y ventas sobre `0001c_motor`; `0003_pronosticos` añade `artefacto_modelo`, `corrida_pronostico`, `pronostico` y `evaluacion_pronostico`. Las demás tablas de este esquema siguen pendientes y deben venir en revisiones posteriores de la misma cadena. `programacion_demo`, `ejecucion_automatizacion` e `intento_automatizacion` ya existen en `0001b_automatizaciones`, ampliadas por `0001c_motor`. `0001_nucleo` crea `negocio` y `usuario`; `0001a_configuracion` agrega `negocio.modo_envio_pedidos`. FoodSave guardará ventas diarias y stock en PostgreSQL tras la primera carga. Los archivos de primera inicialización son **carga de arranque**, no fuentes externas permanentes. El [alcance](../guia-inicio-desarrollo.md) manda sobre documentos históricos del producto amplio.

## Convenciones

- Instalación local para un comercio y una sucursal (`negocio.id = 1`); sin `negocio_id` operativo. IDs internos enteros; códigos de archivos son texto. FK históricas `ON DELETE RESTRICT`; catálogos se desactivan, no se borran en cascada.
- Fechas de venta, objetivo y caducidad son `date` local de `negocio.zona_horaria`. Instantes de importación, entrenamiento y auditoría son `timestamptz` UTC. Producto y ventas: `integer >= 0`; ingredientes: `numeric(14,3)` en unidad base; dinero fuera del recorrido de demo.
- Todas las escrituras con clave de idempotencia comparan además huella o parámetros: misma clave y mismo contenido recupera el resultado; misma clave y contenido diferente es conflicto. Una venta ausente sigue desconocida, no cero.

## Primera inicialización y catálogo

`0001a_configuracion` añade a `negocio` `modo_envio_pedidos` con valor inicial `REQUIERE_APROBACION` y valores permitidos `REQUIERE_APROBACION`/`AUTOMATICO`. La futura `0002` añade los campos textuales `comercio_externo` y `sucursal_externa`, configurados juntos durante la primera carga. Los identificadores externos son metadatos del archivo/modelo, no IDs de otros registros locales. El dataset `bakery` puede usar `piloto`/`principal`; se rechaza un archivo que declare otro par.

| Tabla | Campos mínimos | Claves y reglas |
|---|---|---|
| `configuracion_inicial` | `id = 1`, `estado`, `huella_ventas`, `huella_catalogo`, `huella_solicitud`, `fecha_objetivo_demo`, `fecha_referencia_stock`, `iniciada_en`, `completada_en NULL`, `mensaje_error NULL`. | Estados `PENDIENTE`, `DATOS_CARGADOS`, `ENTRENANDO`, `MODELO_LISTO`, `FALLIDA`. `huella_solicitud` cubre ambos archivos y las dos fechas; `fecha_referencia_stock < fecha_objetivo_demo`, y objetivo dentro del tramo reservado de prueba. Reintento idéntico no duplica; otra solicitud tras completar requiere reinicialización explícita de desarrollo. |
| `producto` | `id`, `codigo`, `nombre`, `demostrar boolean`, `activo`, `creado_en`. | `UNIQUE(codigo)`; nombre y código no vacíos. En demo se seleccionan 3–5 productos con historial y receta. |
| `sku_producto` | `id`, `producto_id FK`, `origen`, `sku_externo`, `activo`. | `UNIQUE(origen, sku_externo)`; `article` del dataset se resuelve aquí. Un SKU usado no se reasigna sin revisión explícita. |
| `ingrediente` | `id`, `codigo`, `nombre`, `unidad_base`, `activo`. | `UNIQUE(codigo)`; unidad base `g`, `kg`, `ml`, `l` o `unidad` según la plantilla. No cambiarla después de movimientos. |
| `receta` | `id`, `producto_id FK`, `version`, `activo`, `creado_en`. | `UNIQUE(producto_id, version)` e índice único parcial para una sola versión `activo=true` por producto. Una versión usada por un plan no se edita en sitio. |
| `receta_ingrediente` | `id`, `receta_id FK`, `ingrediente_id FK`, `cantidad_por_unidad numeric(14,3)`. | `UNIQUE(receta_id, ingrediente_id)`; cantidad `> 0` en unidad base. |

La inicialización valida **todos** los archivos y mapeos antes de confirmar cada carga. El entrenamiento a demanda pasa por `ENTRENANDO`; si falla, registra error y vuelve a `DATOS_CARGADOS` para reintentar sin cargar dos veces. La UI no ofrece «Generar plan» hasta `MODELO_LISTO`. El dataset completo puede quedar en ventas diarias; solo los 3–5 productos configurados para demo participan en recetas y plan.

## Ventas diarias propias

| Tabla | Campos mínimos | Claves y reglas |
|---|---|---|
| `importacion_venta` | `id`, `origen`, `clave_importacion`, `huella_contenido`, `filas_aceptadas`, `estado`, `creado_en`. | `UNIQUE(origen, clave_importacion)`; carga atómica. La carga inicial del dataset se ejecuta una vez. |
| `venta_diaria` | `id`, `producto_id FK`, `fecha_local`, `unidades_vendidas`, `importacion_id FK NULL`, `revision_actual`, `actualizado_en`. | `UNIQUE(producto_id, fecha_local)`; cantidad `>= 0`. Son unidades diarias agregadas, no tickets. |
| `revision_venta` | `id`, `venta_id FK`, `numero_revision`, `unidades_vendidas`, `origen_cambio`, `motivo`, `usuario_id FK NULL`, `importacion_id FK NULL`, `creado_en`. | `UNIQUE(venta_id, numero_revision)`; primera carga y cada corrección distinta permanecen auditables. Una corrección requiere motivo y crea nueva corrida si cambia historia ya usada. |

La ausencia de una fecha/producto no crea fila. Las cantidades negativas y devoluciones no se netean; no hay POS, cobros, facturas ni tickets. La importación inicial del dataset `bakery` agrega las líneas por producto/día y descarta o informa filas inválidas según el contrato ML, antes de insertar. El sistema no vuelve a descontar stock por estas ventas históricas.

## Stock por lotes administrado localmente

| Tabla | Campos mínimos | Claves y reglas |
|---|---|---|
| `lote_ingrediente` | `id`, `ingrediente_id FK`, `codigo_lote`, `lote_informado boolean`, `fecha_caducidad NULL`, `saldo_disponible numeric(14,3)`, `actualizado_en`. | `UNIQUE(ingrediente_id, codigo_lote)`; saldo `>= 0`. Un código técnico único identifica la fila si la carga inicial no conoce lote real; se muestra como «lote no informado». |
| `lote_producto` | `id`, `producto_id FK`, `codigo_lote`, `lote_informado boolean`, `fecha_caducidad NULL`, `fecha_limite_venta NULL`, `saldo_disponible integer`, `actualizado_en`. | `UNIQUE(producto_id, codigo_lote)`; saldo `>= 0`; límite de venta `<=` caducidad cuando ambas existen. |
| `movimiento_inventario` | `id`, `lote_ingrediente_id FK NULL`, `lote_producto_id FK NULL`, `delta numeric(14,3)`, `tipo`, `clave_operacion`, `motivo`, `usuario_id FK NULL`, `efectivo_en_demo`, `creado_en`. | Exactamente una FK de lote; delta distinto de cero e integral para producto. `UNIQUE(clave_operacion)`; tipos de demo `APERTURA`, `AJUSTE`. `efectivo_en_demo` es hora local simulada, distinta del instante UTC de auditoría. Misma clave con otro lote/delta/tipo es conflicto. |

La apertura positiva y cada ajuste bloquean el lote, comprueban saldo final no negativo, insertan movimiento y actualizan saldo **en una transacción**. Una fila inicial de cantidad explícita `0` crea la referencia de stock conocido con saldo cero y **sin movimiento de delta cero**. Una entrega repetida de la misma operación no vuelve a cambiarlo. Disponibilidad para `fecha_objetivo` suma lotes elegibles y muestra unidad. Un lote caducado antes de esa fecha no cuenta. Un lote sin fecha sigue visible como «vigencia desconocida» y obliga a advertirlo en el plan; no se usa para promociones por vencimiento. La demo no simula consumo real por producción ni resta stock al generar un plan: una sugerencia no es un movimiento físico. `INVENTARIO`, `inventario_ingrediente` y `existencia_producto` son lecturas, no tablas.

**Implementado (30-09-2026, migraciones `0005` y `0006`):** `movimiento_inventario` guarda además `saldo_resultante` para auditar cada paso. Vida útil de producto de pastelería: 5 días como máximo, con `fecha_caducidad` = día 5; días 1–3 óptimo, 4–5 prioridad (cuentan), 6 en adelante merma (no cuenta). La apertura rechaza una caducidad posterior a `fecha_referencia_stock + 4 días`. Detalle en el [contrato V01/V02](../api/contratos.md#v01v02-disponibles-apertura-ajustes-y-stock-por-fecha-30-09-2026).

## Modelo, pronóstico y propuesta

| Tabla | Campos mínimos | Claves y reglas |
|---|---|---|
| `artefacto_modelo` | `id`, `version_modelo`, `ruta_local`, `sha256`, `huella_datos_entrenamiento`, `fecha_corte_entrenamiento`, `particion_json`, `estado`, `metricas_json`, `entrenado_en`. | `UNIQUE(version_modelo)`; solo `LISTO_DEMO` habilita inferencia en el prototipo. `particion_json` conserva política y límites de entrenamiento, validación y prueba; el modelo no usa la prueba para ajuste. Ruta local controlada, no una URL. |
| `corrida_pronostico` | `id`, `ejecucion_id FK`, `tipo`, `clave_ejecucion`, `huella_datos_entrada`, `fecha_objetivo`, `modelo_id FK`, `estado`, `creado_en`, `finalizado_en NULL`. | `UNIQUE(clave_ejecucion)`; `tipo = BACKTEST` o `DEMO_PROGRAMADA`. Fecha, modelo y huella iguales para repetición. `version_modelo` se consulta del artefacto y se incluye en API. |
| `pronostico` | `id`, `corrida_id FK`, `producto_id FK`, `cantidad_pronosticada integer NULL`, `estado`. | `UNIQUE(corrida_id, producto_id)`; cantidad `>= 0` en `DISPONIBLE`; `NULL` en `HISTORIAL_INSUFICIENTE` o `PRODUCTO_NO_CUBIERTO`. |
| `evaluacion_pronostico` | `id`, `ejecucion_id FK`, `corrida_id FK`, `pronostico_id FK`, `revision_venta_id FK`, `producto_id FK`, `cantidad_pronosticada`, `unidades_reales`, `error_absoluto`, `creado_en`. | `UNIQUE(corrida_id, producto_id, revision_venta_id)`; solo si predicción y venta real son conocidas. La revisión fija exactamente qué valor real se comparó. No alimenta la inferencia ni modifica el pronóstico. |
| `plan_produccion` | `id`, `corrida_id FK`, `ejecucion_id FK`, `clave_ejecucion`, `huella_stock_recetas`, `fecha_objetivo`, `stock_leido_en`, `estado`, `creado_en`. | `UNIQUE(clave_ejecucion)`; misma clave y huella devuelve el mismo plan, distinta huella es conflicto. Una misma corrida admite otro plan si cambió stock o receta. Solo `PROPUESTO` en demo. No cambia stock. |
| `elemento_plan` | `id`, `plan_id FK`, `producto_id FK`, `pronostico_id FK`, `receta_id FK`, `cantidad_pronosticada`, `stock_disponible`, `cantidad_producir`, `vigencia_stock_desconocida`. | `UNIQUE(plan_id, producto_id)`; enteros no negativos. Guarda cifras leídas para reproducibilidad. |
| `necesidad_ingrediente` | `id`, `plan_id FK`, `ingrediente_id FK`, `cantidad_requerida`, `cantidad_disponible`, `cantidad_faltante`, `unidad`, `vigencia_stock_desconocida`. | `UNIQUE(plan_id, ingrediente_id)`; cantidades no negativas en unidad base. Cuando `cantidad_faltante > 0`, sirve de origen trazable para una línea de pedido si hay proveedor y conversión válidos. |

Para la demo se fija margen de seguridad **cero** y se informa como supuesto. `cantidad_producir = max(0, cantidad_pronosticada - stock_disponible)`. `cantidad_requerida` suma `cantidad_producir × cantidad_por_unidad` por ingrediente usando las recetas versionadas; se redondea hacia arriba a tres decimales **al final**. `cantidad_faltante = max(0, cantidad_requerida - cantidad_disponible)`. Un pronóstico no disponible o receta faltante genera estado explicativo y no un cero ficticio. Un nuevo cálculo con ventas, modelo, receta o stock diferentes usa nueva clave y conserva corridas/planes anteriores.

### Panel de acierto histórico

`EVALUAR_MODELO` corre después del entrenamiento sobre el tramo de prueba definido por la [política temporal](../../foodsave-ml/POLITICA_EVALUACION.md) y crea corridas `BACKTEST` por fecha. `EVALUAR_PRONOSTICO` corre **después** de persistir una propuesta programada y la compara sin mezclar el resultado con entrenamiento. El panel «último día evaluado» muestra barras de pronóstico frente a venta real por producto, diferencia absoluta en unidades, `MAE` del día, `WAPE` y porcentaje de productos dentro de ±20%, más cobertura `productos_evaluables / productos_pronosticados`. Un gráfico temporal muestra el tramo de prueba. Son métricas sobre ventas conocidas; una fila ausente no se convierte en cero ni entra al denominador. `MAE = suma(error_absoluto) / evaluables`. `WAPE = 100 × suma(error_absoluto) / suma(unidades_reales)`; si la suma real es cero, «no definido». El porcentaje ±20% usa `error_absoluto / max(unidades_reales, 1) <= 0,20`, igual que el notebook. No se presenta `100-WAPE` como «precisión» ni se oculta cobertura. Las métricas históricas no prueban rendimiento comercial futuro.

## Automatizaciones y promoción sugerida de la demo

El [ADR-007](../arquitectura/decisiones/ADR-007-automatizaciones-demo.md) fija tres automatizaciones: preparación de modelo tras la carga, propuesta programada de pronóstico/plan/faltantes y evaluación programada de promoción tras ajustar stock. Beat ejecuta cada 30 segundos un despachador; corre una sola instancia de Beat. La hora UTC real decide cuándo se lanza el trabajo; `fecha_hora_simulada_local` decide qué escenario histórico se evalúa.

| Tabla | Campos mínimos | Claves y reglas |
|---|---|---|
| `programacion_demo` | `id`, `tipo`, `ejecutar_desde_utc`, `fecha_hora_simulada_local`, `parametros_json`, `clave_idempotencia`, `huella_entrada`, `estado`, `despachada_en NULL`, `lease_hasta NULL`, `creado_por FK NULL`, `creado_en`. | **Implementada en `0001b`.** `UNIQUE(clave_idempotencia)`; tipos `GENERAR_PROPUESTA`, `EVALUAR_PROMOCION`; estados `PROGRAMADA`, `DESPACHADA`, `CANCELADA`. Repetición idéntica recupera la programación. El lease de A03 refleja el reclamo y se libera al finalizar o reintentar. |
| `ejecucion_automatizacion` | `id`, `programacion_id FK NULL`, `tipo`, `clave_idempotencia`, `huella_entrada`, `datos_entrada_json`, `estado`, `inicio_en NULL`, `fin_en NULL`, `proximo_intento_en NULL`, `despachada_en NULL`, `lease_hasta NULL`, `token_despacho NULL`, `datos_salida_json NULL`, `mensaje_error NULL`. | **Implementada en `0001b` y ampliada en `0001c`.** `UNIQUE(clave_idempotencia)` y `UNIQUE(programacion_id)` cuando no es nulo. Estados `PENDIENTE`, `EN_EJECUCION`, `REINTENTANDO`, `COMPLETADA`, `FALLIDA`. El token gira al recuperar el lease; los mensajes anteriores no ejecutan. Entrenamiento, backtest y evaluación de una propuesta son eventos sin programación. |
| `intento_automatizacion` | `id`, `ejecucion_id FK`, `numero_intento`, `inicio_en`, `fin_en NULL`, `estado`, `mensaje_error NULL`. | **Implementada en `0001b`.** `UNIQUE(ejecucion_id, numero_intento)`; hasta tres intentos totales. A03 recupera intentos abiertos y clasifica fallos internos. |
| `regla_promocion_demo` | `id`, `version`, `hora_revision`, `hora_cierre`, `stock_umbral`, `descuento_pct`, `descuento_maximo_pct`, `antiguedad_maxima_stock_min`, `habilitada`. | `UNIQUE(version)` y una sola regla habilitada. Valores compatibles con `ReglaPromocion` existente; `hora_revision < hora_cierre`, descuento entre `1` y máximo `<= 100`, antigüedad positiva. Cambiar regla crea versión nueva. |
| `evaluacion_promocion` | `id`, `ejecucion_id FK`, `lote_producto_id FK`, `regla_id FK`, `fecha_hora_simulada_local`, `stock_leido`, `proponer boolean`, `motivo`, `descuento_pct NULL`, `creado_en`. | `UNIQUE(ejecucion_id, lote_producto_id)`; registra propuesta o rechazo explicativo. `descuento_pct` solo existe cuando `proponer=true`. La versión se obtiene de `regla_id`. No cambia precio ni stock. |

La apertura tiene hora efectiva del escenario anterior al objetivo. Un ajuste de producto puede declarar, por ejemplo, `2022-08-24 17:45` y agenda evaluación para un instante real próximo con reloj simulado `2022-08-24 18:00`. La regla compara la hora efectiva del último movimiento con ese reloj para medir frescura; los dos instantes se muestran junto al disparo UTC real. Una reentrega de Beat o del worker no crea otra corrida, plan o evaluación para la misma clave y huella.

## Proveedores y pedidos de la demo

La decisión de [pedidos desde el plan](../arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md) amplió el prototipo. La `0002` debe incluir estas entidades y sus relaciones en el ER antes de escribir la migración:

| Tabla | Campos mínimos | Claves y reglas |
|---|---|---|
| `proveedor` | `id`, `codigo`, `nombre`, `telegram_chat_id NULL`, `telegram_verificado_en NULL`, `activo`, `creado_en`. | `UNIQUE(codigo)`; chat verificado para envío. El destino de la exposición es un chat propio que simula al proveedor. |
| `oferta_ingrediente` | `id`, `proveedor_id FK`, `ingrediente_id FK`, `unidad_compra`, `factor_a_unidad_base`, `multiplo_compra`, `minimo_compra`, `preferida`, `activo`. | Factor y múltiplo positivos, mínimo no negativo; una sola oferta preferida activa por ingrediente en la demo. Todas las conversiones son explícitas. |
| `pedido_compra` | `id`, `plan_id FK`, `proveedor_id FK`, `clave_idempotencia`, `huella_entrada`, `modo_envio`, `estado`, `aprobado_por FK NULL`, `aprobado_en NULL`, `creado_en`, `actualizado_en`. | `UNIQUE(plan_id, proveedor_id)` y `UNIQUE(clave_idempotencia)`; modo copiado del negocio al crear; estados según el [contrato de pedidos](../api/contrato-pedidos.md). |
| `linea_pedido` | `id`, `pedido_id FK`, `necesidad_ingrediente_id FK`, `oferta_ingrediente_id FK`, `faltante_base`, `cantidad_compra`, `unidad_compra`, `factor_a_unidad_base`, `multiplo_compra`, `minimo_compra`. | `UNIQUE(necesidad_ingrediente_id)`; cantidades positivas; una necesidad no se asigna a dos proveedores; copia inmutable del cálculo y la oferta usada. |
| `envio_pedido` | `id`, `pedido_id FK`, `numero_intento`, `estado`, `iniciado_en`, `finalizado_en NULL`, `telegram_message_id NULL`, `mensaje_enviado NULL`, `error NULL`. | `UNIQUE(pedido_id, numero_intento)`; `message_id` solo con respuesta exitosa; un resultado incierto queda pendiente de conciliación y no se reenvía solo. Nunca guarda el token del bot. |

El [contrato de pedidos](../api/contrato-pedidos.md) fija fórmula, transiciones, aprobación opcional y evidencia del envío. El mensaje de prueba lleva la marca «DEMOSTRACIÓN — NO SURTIR» y la fecha histórica. Crear o enviar un pedido no altera inventario.

## No crear en `0002` del prototipo

`recepcion_pedido`, factura, pago, publicación de descuentos, predicción intradía de excedentes y Google Sheets pertenecen a la visión futura. `programacion_demo` ya existe en `0001b`; pedidos y evaluación de promoción siguen previstos para `0002`. El [ER](diagrama-entidad-relacion.mmd) del prototipo debe reflejar estas tablas junto a las dos existentes de `0001`.
