# Contrato de datos para el pronóstico diario de FoodSave

**Versión inicial para el piloto.** El objetivo es predecir las **unidades vendidas por producto, sucursal y fecha local**, un día adelante, una vez cerrado el día anterior. Estos requisitos son criterios de FoodSave para aceptar y evaluar datos; no garantizan por sí solos un error bajo.

## Mínimo aceptado ahora: solo ventas

Se aceptan transacciones o ventas diarias. Como cada comercio entregará **solo ventas** en esta etapa, una combinación sucursal × producto × fecha que no aparezca se marca **desconocida**, nunca cero. Los identificadores deben ser estables; un cambio de nombre comercial no debe crear un producto nuevo.

Formato de intercambio: CSV UTF-8 con encabezado, fechas locales `YYYY-MM-DD` y cantidades enteras no negativas. Si el POS usa otro formato, se transforma antes de aplicar este contrato y se conserva el archivo original.

| Archivo | Campos obligatorios | Regla |
| --- | --- | --- |
| `ventas_diarias.csv` | `comercio_id`, `sucursal_id`, `fecha_local`, `producto_id`, `unidades_vendidas` | Una fila única por sucursal, fecha y producto. `unidades_vendidas` es un entero ≥ 0. No se agregan sucursales distintas. Una fila ausente permanece desconocida. |

Si el comercio solo puede exportar tickets, el formato `transacciones` requiere las cinco columnas de la tabla más `transaccion_id` y `linea_id`. `fecha_local` debe reflejar el día comercial de la sucursal; hora y zona horaria se guardan como metadatos cuando el POS pueda exportarlas. FoodSave comprobará claves de línea duplicadas y agregará las líneas a ventas diarias. Si cada archivo corresponde a una sola sucursal pero no tiene IDs, la carga deberá asignar `comercio_id` y `sucursal_id` desde una configuración explícita antes de usar el formato estándar. Los nombres de productos sirven provisionalmente si no existen SKU, pero el comercio deberá mantenerlos estables o entregar un mapeo de cambios.

**Para evaluar ceros reales y pasar a decisiones de producción** se solicitarán dos archivos adicionales: `calendario_sucursal.csv` con `comercio_id`, `sucursal_id`, `fecha_local`, `estado_dia` (`abierto`, `cerrado`, `sin_datos`) y zona horaria de la sucursal; y `disponibilidad_producto.csv` con las mismas claves más `producto_id` y `estado_producto` (`ofrecido`, `no_ofrecido`, `agotado`, `sin_datos`). Estos archivos no son obligatorios para ejecutar el piloto de ventas observadas.

Las devoluciones y cancelaciones se entregan por separado o marcadas con `tipo_movimiento`. No se mezclan cantidades negativas con unidades vendidas positivas sin una política de negocio acordada. Precio, promociones, stock inicial/final y categoría son útiles, pero no son variables obligatorias de **esta primera versión**. Si hubo quiebre de stock, el dato de ventas no revela toda la demanda; sin el indicador de agotamiento no se podrá evaluar ese sesgo.

Ejemplo: sucursal abierta y croissant `ofrecido` con `unidades_vendidas=0` es un cero real. Si la sucursal está `cerrado`, no se genera objetivo de venta. Si el estado es `sin_datos`, la cantidad queda desconocida. Si el producto es `no_ofrecido`, tampoco se convierte en cero de demanda.

## Controles antes de entrenar

1. Verificar claves únicas, fechas válidas, cantidades y correspondencia de identificadores. Si se entregan transacciones, revisar duplicados por `transaccion_id` antes de agregarlas.
2. Medir por sucursal y período días con alguna venta, días sin transacciones y días por producto con venta registrada. En modo `solo ventas`, no completar automáticamente ausencias con cero.
3. Construir historial solo con información conocida antes de la fecha pronosticada. Separar entrenamiento, validación y test por fecha; nunca mezclar fechas futuras en el entrenamiento. La evaluación debe reproducir la hora real en que se hará el pronóstico.
4. Informar MAE, WAPE, error de subestimación y cobertura por sucursal y producto. Un resultado global puede ocultar productos con errores graves. Mostrar también fechas y productos descartados.

**Puertas provisionales del piloto de solo ventas**, sujetas a revisión con datos reales: al menos 180 fechas con ventas registradas por sucursal para reservar entrenamiento, validación y test; al menos 90 fechas con venta registrada en entrenamiento y 20 en cada período de validación y test por producto para publicar su métrica individual. Productos nuevos o esporádicos quedan como `historial_insuficiente`; no se les atribuye la calidad global de CatBoost. Exigir además que cada fecha pronosticada tenga al menos siete observaciones conocidas del producto en los 28 días previos. Estos números son umbrales operativos iniciales, no propiedades del algoritmo. Se evalúan solo fechas y productos con ventas conocidas: la cobertura debe mostrarse junto a cualquier métrica.

Para integrar más comercios, la primera implementación entrenará y evaluará **un modelo por sucursal**; no se mezclarán nombres de productos ni ventas entre comercios. Los períodos de validación y test se fijarán por calendario de cada sucursal. Un modelo compartido entre comercios sería una etapa distinta y requeriría conservar `comercio_id` y `sucursal_id` como claves y variables. El notebook actual es un **piloto de una sola panadería**; su CSV no proporciona calendario ni disponibilidad, por lo que las ausencias siguen siendo desconocidas y las métricas se limitan a ventas registradas en filas evaluables.

## Decisiones pendientes con cada comercio

- Para una etapa posterior, confirmar si cada sucursal puede reportar aperturas, cierres, ceros explícitos y disponibilidad por producto. Sin ellos, FoodSave podrá entrenar una prueba exploratoria, pero no certificar cobertura de demanda ni una recomendación de producción.
- Acordar cuándo se cierra el día de ventas, con qué frecuencia se corrigen tickets y a qué hora se solicitará el pronóstico del día siguiente.
- Acordar cuánto cuesta una unidad de producción faltante frente a una unidad sobrante. El piloto usa pesos relativos 2:1 por preferencia expresada por el equipo; son una hipótesis configurable, no costos monetarios reales.

## Referencias técnicas

- [CatBoost: tratamiento de valores numéricos faltantes](https://catboost.ai/docs/en/concepts/algorithm-missing-values-processing).
- [Forecasting: Principles and Practice, validación temporal](https://otexts.com/fpp3/tscv.html).

Los umbrales de días de historial y de muestra de este documento son decisiones provisionales de FoodSave, no recomendaciones universales de esas fuentes.
