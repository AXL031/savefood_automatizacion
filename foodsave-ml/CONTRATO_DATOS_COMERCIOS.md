# Contrato de datos para el pronóstico diario de FoodSave

**Versión inicial para el piloto.** El objetivo es predecir las **unidades vendidas por producto de la única sucursal local y fecha**, un día adelante, una vez cerrado el día anterior. El prototipo carga el historial desde archivo solo en la primera inicialización y después administra `venta_diaria` en PostgreSQL; no gestiona tickets ni pagos. Estos requisitos son criterios para aceptar y evaluar datos; no garantizan por sí solos un error bajo.

## Mínimo aceptado ahora: solo ventas

Se cargan ventas diarias o se agregan las líneas del dataset `bakery` durante la primera inicialización. una combinación sucursal × producto × fecha que no aparezca se marca **desconocida**, nunca cero. Los identificadores deben ser estables; un cambio de nombre comercial no debe crear un producto nuevo.

Formato canónico para ML: CSV UTF-8 con encabezado, fechas locales `YYYY-MM-DD` y cantidades enteras no negativas. El adaptador de primera carga genera esta forma desde Excel o el CSV `bakery` y conserva el original; véase el [contrato de inicialización](../docs/api/contrato-importaciones.md). `producto_id` es un identificador externo textual estable; no es el `producto.id` entero de la base local.

**Frontera del MVP local:** el CSV canónico debe contener exactamente un par `comercio_id`/`sucursal_id`, coincidente con la configuración explícita de la instalación. Si el Excel original carece de esas columnas, el adaptador añade el par configurado **antes** del normalizador y conserva el original. Si el archivo sí las incluye y hay varios pares o no coinciden, se rechaza completo. Estos metadatos no crean comercios ni sucursales adicionales en PostgreSQL.

Esta es una condición de aceptación de la primera carga. El normalizador experimental actual todavía no aplica el rechazo; sus resultados no deben ingresar a la base operativa sin esa validación.

**Resolución de producto para la primera carga:** el encabezado CSV sigue llamándose `producto_id`, pero su valor es un SKU externo textual. Junto con el identificador del origen de datos se consulta `sku_producto(origen, sku_externo, producto_id)`; la combinación `(origen, sku_externo)` es única y apunta a un `producto.id` interno. Se rechaza el archivo completo si falta un mapeo activo o si dos SKUs del mismo archivo resuelven al mismo producto y fecha. No se crean productos de forma automática ni se reasigna en el lugar un SKU ya usado por ventas. El entrenamiento ML conserva el valor externo como categoría; la persistencia operativa usa el ID interno resuelto.

| Archivo | Campos obligatorios | Regla |
| --- | --- | --- |
| `ventas_diarias.csv` | `comercio_id`, `sucursal_id`, `fecha_local`, `producto_id`, `unidades_vendidas` | Una fila única por sucursal, fecha y producto. `unidades_vendidas` es un entero ≥ 0. No se agregan sucursales distintas. Una fila ausente permanece desconocida. |

Si un futuro conector recibe tickets, debe agregar líneas por producto y día antes de esta frontera, conservando IDs de transacción y línea para deduplicar. El MVP solo acepta la plantilla de ventas diarias; nombres comerciales libres no sustituyen un SKU externo estable.

**Para evaluar ceros reales y pasar a decisiones de producción** se solicitarán dos archivos adicionales: `calendario_sucursal.csv` con `comercio_id`, `sucursal_id`, `fecha_local`, `estado_dia` (`abierto`, `cerrado`, `sin_datos`) y zona horaria de la sucursal; y `disponibilidad_producto.csv` con las mismas claves más `producto_id` y `estado_producto` (`ofrecido`, `no_ofrecido`, `agotado`, `sin_datos`). Estos archivos no son obligatorios para ejecutar el piloto de ventas observadas.

Las devoluciones y cancelaciones se entregan por separado o marcadas con `tipo_movimiento`. No se mezclan cantidades negativas con unidades vendidas positivas sin una política de negocio acordada. Precio, promociones, stock inicial/final y categoría son útiles, pero no son variables obligatorias de **esta primera versión**. Si hubo quiebre de stock, el dato de ventas no revela toda la demanda; sin el indicador de agotamiento no se podrá evaluar ese sesgo.

Ejemplo: sucursal abierta y croissant `ofrecido` con `unidades_vendidas=0` es un cero real. Si la sucursal está `cerrado`, no se genera objetivo de venta. Si el estado es `sin_datos`, la cantidad queda desconocida. Si el producto es `no_ofrecido`, tampoco se convierte en cero de demanda.

## Controles antes de entrenar

1. Verificar claves únicas, fechas válidas, cantidades y correspondencia de identificadores. Si se entregan transacciones, revisar duplicados por `transaccion_id` antes de agregarlas.
2. Medir por sucursal y período días con alguna venta, días sin transacciones y días por producto con venta registrada. En modo `solo ventas`, no completar automáticamente ausencias con cero.
3. Construir historial solo con información conocida antes de la fecha pronosticada. Separar entrenamiento, validación y test por fecha; nunca mezclar fechas futuras en el entrenamiento. La evaluación debe reproducir la hora real en que se hará el pronóstico.
4. Informar MAE, WAPE, error de subestimación y cobertura por sucursal y producto. Un resultado global puede ocultar productos con errores graves. Mostrar también fechas y productos descartados.

**Puertas provisionales del piloto de solo ventas**, sujetas a revisión con datos reales: al menos 180 fechas con ventas registradas por sucursal para reservar entrenamiento, validación y test; al menos 90 fechas con venta registrada en entrenamiento y 20 en cada período de validación y test por producto para publicar su métrica individual. Productos nuevos o esporádicos quedan como `historial_insuficiente`; no se les atribuye la calidad global de CatBoost. Exigir además que cada fecha pronosticada tenga al menos siete observaciones conocidas del producto en los 28 días previos. Estos números son umbrales operativos iniciales, no propiedades del algoritmo. Se evalúan solo fechas y productos con ventas conocidas: la cobertura debe mostrarse junto a cualquier métrica.

La longitud del historial decide si se reservan seis, tres o un mes de prueba, según la [política de evaluación](POLITICA_EVALUACION.md). Las puertas de observaciones anteriores se verifican **además** del corte calendario; duración larga por sí sola no acredita cobertura de un producto.

Cada instalación entrenará y evaluará **su propio modelo para su única sucursal**. Un modelo compartido entre comercios sería otra etapa y otra decisión arquitectónica. El notebook actual es un **piloto de una sola panadería**; su CSV no proporciona calendario ni disponibilidad, por lo que las ausencias siguen siendo desconocidas y las métricas se limitan a ventas registradas en filas evaluables.

## Decisiones pendientes con cada comercio

- Para una etapa posterior, confirmar si cada sucursal puede reportar aperturas, cierres, ceros explícitos y disponibilidad por producto. Sin ellos, FoodSave podrá entrenar una prueba exploratoria, pero no certificar cobertura de demanda ni una recomendación de producción.
- En la demo se elige manualmente una fecha histórica; una corrección posterior en `venta_diaria` crea otra corrida y otro plan versionado cuando cambia la entrada, sin borrar los anteriores. `negocio.hora_cierre` será necesario al automatizar cierres en una fase futura.
- Acordar cuánto cuesta una unidad de producción faltante frente a una unidad sobrante. El piloto usa pesos relativos 2:1 por preferencia expresada por el equipo; son una hipótesis configurable, no costos monetarios reales.

## Referencias técnicas

- [CatBoost: tratamiento de valores numéricos faltantes](https://catboost.ai/docs/en/concepts/algorithm-missing-values-processing).
- [Forecasting: Principles and Practice, validación temporal](https://otexts.com/fpp3/tscv.html).

Los umbrales de días de historial y de muestra de este documento son decisiones provisionales de FoodSave, no recomendaciones universales de esas fuentes.
