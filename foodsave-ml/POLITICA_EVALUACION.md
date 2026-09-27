# Partición temporal y evaluación visible del modelo

**Estado:** contrato del prototipo universitario. Se aplica durante la primera inicialización, antes de entrenar. El objetivo es mostrar qué tan bien habría pronosticado CatBoost en fechas históricas reservadas, sin usar esas ventas al ajustar o seleccionar el modelo. Este resultado no garantiza precisión futura para un comercio real.

## Regla según longitud del historial

La duración se calcula con los **meses calendario completos** cubiertos entre la primera y última `fecha_local` válidas de la sucursal, no por número de filas. Si el primer o último mes está incompleto, queda fuera del conteo y de la partición; se informa por separado. Los bloques son consecutivos, sin barajado aleatorio:

| Historial válido | Entrenamiento | Validación previa | Prueba reservada al final |
|---|---|---:|---:|
| 24 meses o más | Desde el inicio hasta antes de validación | 3 meses | 6 meses |
| 12 a menos de 24 meses | Desde el inicio hasta antes de validación | 3 meses | 3 meses |
| 6 a menos de 12 meses | Desde el inicio hasta antes de validación | 1 mes | 1 mes |
| Menos de 6 meses | Sin evaluación suficiente para la demo | — | — |

Los cortes se alinean con esos meses completos. Además de la duración, se exigen las muestras mínimas del [contrato de datos](CONTRATO_DATOS_COMERCIOS.md) por producto. Un producto que no alcance el mínimo se marca `HISTORIAL_INSUFICIENTE` y no recibe una métrica individual. No se inventan ceros para fechas ausentes.

Para `bakery_sales_limpio.csv` (enero de 2021 a septiembre de 2022, menos de 24 meses), la regla da entrenamiento antes de abril de 2022, validación abril–junio y **prueba julio–septiembre de 2022**. El escenario propuesto `2022-08-24` cae en prueba. La selección de características, hiperparámetros y parada temprana usa solo entrenamiento/validación; el tramo de prueba no participa en esas decisiones. El test histórico ya se ha inspeccionado en el proyecto, por lo que la demo lo rotula como **comprobación histórica exploratoria**, nunca como prueba final no vista.

## Automatización de comprobación

Al terminar `PREPARAR_MODELO`, se encola una ejecución idempotente `EVALUAR_MODELO`. Para cada fecha del tramo reservado hace un pronóstico **un día adelante** con el modelo fijo y solo ventas fechadas antes de ese día. Dentro del tramo de prueba puede usar ventas reales de días previos como historial, tal como ocurriría al cerrar cada día; nunca usa la venta del **mismo día objetivo** como característica. Cada predicción se compara después con la venta observada, si existe. Se conservan `version_modelo`, partición, corrida, producto y revisión exacta de venta usada para evaluar. Reentregar la tarea no duplica resultados.

Cuando Beat genere `GENERAR_PROPUESTA` para una fecha elegida del tramo de prueba, la corrida de esa ejecución se evalúa también **después** de persistirse. Se puede comparar su resultado con la serie de backtest, sin presentarlo como un dato independiente nuevo.

## Métricas del dashboard

- Gráfico por fecha de **total previsto frente a total real conocido**, sumados ambos sobre los mismos productos evaluables de ese día; mostrar también cuántos productos quedaron fuera. Al seleccionar un día: barras por producto y diferencia absoluta en unidades.
- `MAE = suma(|real - previsto|) / cantidad de productos evaluables`, en unidades. `WAPE = 100 × suma(|real - previsto|) / suma(real)`; si la suma real es cero, mostrar «no definido».
- `% dentro de ±20% = 100 × productos con |real-previsto| / max(real,1) <= 0,20 / productos evaluables`. Es la convención del notebook; con real cero no es un porcentaje relativo ordinario. Puede mostrarse también ±10%, con la misma definición.
- `cobertura = productos con pronóstico y venta real conocida / productos pronosticados`. Una venta ausente es **desconocida**, no cero; no entra a MAE/WAPE/±20% y sí queda visible en la cobertura.
- Para el tramo completo, calcular MAE con todos los pares producto-día evaluables y WAPE con las sumas de error y venta real de esos pares; no promediar los porcentajes diarios. Mostrar cuántos pares y fechas fueron evaluables.
- Mostrar `fecha`, `version_modelo`, intervalo de entrenamiento/validación/prueba y estado «demostración histórica». No calcular `100-WAPE` ni llamarlo «precisión»; WAPE es un error y puede superar 100%. No colorear «aprobado» sin un umbral de calidad acordado con datos reales posteriores.

El encabezado «Último día evaluado» se refiere a la última fecha **del escenario o del tramo reservado**, no necesariamente a ayer en el calendario real. En una instalación futura con ventas actuales, la misma vista podrá mostrar ayer después del cierre y de recibir la venta real.
