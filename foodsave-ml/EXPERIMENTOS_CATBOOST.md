# Mejora del pronóstico CatBoost

La primera ejecución con MAE mostró subestimación. Para dar mayor prioridad a los faltantes, se probaron dos objetivos **dentro de CatBoost** con las mismas variables e historiales: MAE y `Quantile:alpha=0.65`. El costo relativo del piloto se definió como `2 × unidades faltantes + 1 × unidades sobrantes`; todavía no representa precios ni márgenes del comercio.

| Validación temporal | Objetivo | WAPE | Unidades faltantes | Unidades sobrantes | Costo relativo 2:1 |
| --- | --- | ---: | ---: | ---: | ---: |
| Oct–dic 2021 | MAE | 32.04% | 8,248 | 3,832 | 20,328 |
| Oct–dic 2021 | Quantile 0.65 | 32.72% | 5,550 | 6,786 | 17,886 |
| Ene–mar 2022 | MAE | 29.16% | 3,925 | 5,155 | 13,004 |
| Ene–mar 2022 | Quantile 0.65 | 33.42% | 2,543 | 7,861 | 12,946 |
| Abr–jun 2022 | MAE | 31.95% | 9,612 | 5,624 | 24,848 |
| Abr–jun 2022 | Quantile 0.65 | 35.27% | 5,981 | 10,839 | 22,800 |

Cada período se evaluó entrenando solo con fechas anteriores. Se conservaron las filas con venta conocida y al menos siete observaciones del producto en los 28 días anteriores. CatBoost usó `early_stopping_rounds=50` con la validación correspondiente. Los resultados favorecen el cuantil bajo el supuesto de costo 2:1, **a cambio de más excedentes y mayor WAPE**. Por eso el notebook ahora reporta las cuatro cantidades: MAE, WAPE, unidades faltantes y unidades sobrantes.

Tras fijar el cuantil con validación, la ejecución diagnóstica del test histórico de julio–septiembre de 2022 produjo 4,454 filas evaluables, MAE 4.38, WAPE 25.77%, 7,651 unidades faltantes y 11,841 sobrantes. El costo relativo 2:1 fue 27,144. En la versión anterior con MAE el mismo conjunto de filas dio MAE 5.42 y WAPE 31.90%. Esta comparación es **exploratoria** porque el test histórico ya se había inspeccionado durante el desarrollo; no es evidencia final independiente de despliegue.

El test de julio–septiembre de 2022 ya fue examinado al diagnosticar el primer modelo. Las siguientes mejoras no pueden tratarlo como una prueba final no vista. Para decidir si desplegar, registrar pronósticos y resultados de un período posterior, sin ajustar el modelo con esas fechas antes de evaluarlo. También se debe comprobar la calidad por producto, cobertura y días sin venta conocidos. Con solo tickets no se pueden identificar todos los ceros ni la demanda perdida por quiebre de stock.

El costo relativo se calcula **solo sobre ventas observadas**. Si un producto no tiene registro en una fecha, la venta real es desconocida; no se computa como sobrante. Por eso esta optimización puede favorecer pronósticos más altos sin medir todos los posibles excedentes. No usar estas cifras como estimación de desperdicio físico hasta obtener calendario de apertura y disponibilidad del producto.

Antes de integrar un comercio, normalizar su exportación, revisar `calidad.json`, entrenar por sucursal y publicar métricas individuales solo con la muestra mínima definida en [CONTRATO_DATOS_COMERCIOS.md](CONTRATO_DATOS_COMERCIOS.md). El notebook acepta un CSV normalizado, selecciona una sucursal y usa sus últimas 30 fechas registradas para test y las 30 anteriores para validación; el CSV legacy de panadería conserva fechas fijas para reproducir el piloto. Automatizar ejecuciones y registros de modelos por sucursal será una etapa posterior.
