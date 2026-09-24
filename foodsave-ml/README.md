# FoodSave ML

Primer experimento de predicción diaria basado en la guía proporcionada. El notebook es autónomo y no depende del backend ni del frontend.

Para incorporar otros comercios, consulta el [contrato mínimo de datos](CONTRATO_DATOS_COMERCIOS.md). El piloto acepta solo ventas; el calendario de apertura y la disponibilidad por producto se incorporarán cuando existan esos datos.

Las validaciones temporales y el costo de los faltantes frente a los sobrantes están documentados en [EXPERIMENTOS_CATBOOST.md](EXPERIMENTOS_CATBOOST.md).

Para comprobar y uniformar un archivo diario de otro comercio, ejecuta `python foodsave-ml/normalizar_ventas.py --entrada ventas.csv --salida carpeta`. Si el archivo contiene líneas de tickets, añade `--formato transacciones`. Genera `ventas_diarias_normalizadas.csv` y `calidad.json`. Para inspeccionar el CSV histórico de la panadería, usa `--formato bakery --comercio piloto --sucursal principal`. Ningún modo interpreta una fila ausente como cero.

## Ejecutar en Google Colab

1. Abre https://colab.research.google.com/ y selecciona **Subir notebook**.
2. Sube `notebooks/foodsave_colab.ipynb`.
3. Ejecuta las celdas en orden. En la carga, sube el CSV legacy con `date`, `article` y `Quantity`, o el CSV normalizado con `comercio_id`, `sucursal_id`, `fecha_local`, `producto_id` y `unidades_vendidas`. Si hay varias sucursales, indica `COMERCIO_ID` y `SUCURSAL_ID`. El CSV normalizado usa por defecto las 30 últimas fechas registradas para test y las 30 anteriores para validación; el CSV legacy conserva las fechas fijas del piloto.
4. Revisa formato de fechas y política de días sin ventas. Por defecto, las ausencias son desconocidas; activa la imputación a cero solo si corresponde al dataset. Las cantidades negativas se excluyen de este primer modelo de ventas brutas y el notebook informa cuántas quitó.
5. Entrena CatBoost y revisa sus métricas de validación: MAE, WAPE, ±10% y ±20%. Después evalúa el mismo modelo en el test de julio–septiembre de 2022.
6. Cambia `FECHA_PRUEBA` para probar una fecha del test y activa `MOSTRAR_REALES` para comparar.
7. Descarga el ZIP con modelo, metadatos y resultados antes de cerrar la sesión.

Se necesita historial anterior a abril de 2022, validación abril–junio y test julio–septiembre de 2022. Una fila requiere al menos siete días conocidos del producto en los 28 días anteriores. Los lags faltantes permanecen como NaN; CatBoost puede procesarlos. Así, un día sin registros no elimina automáticamente las siguientes cuatro semanas. El notebook muestra qué fechas, productos y unidades cubre cada período.

El experimento predice un día adelante con ventas históricas reales disponibles hasta ayer; no es un pronóstico de varios meses desde un único punto. Los productos sin historial suficiente no se predicen y se informa la cobertura. El simulador selecciona productos por el historial previo, sin mirar la venta del día; una ausencia de venta real aparece como desconocida. Los resultados posteriores a este cambio no son directamente comparables con las métricas del notebook anterior, porque ahora se evalúan más productos y fechas. No se infiere demanda no atendida ni desperdicio real a partir de ventas.

El CSV `bakery_sales_limpio.csv` está en esta carpeta para el piloto local; Colab sigue solicitando que lo subas al ejecutar el notebook. El CSV original se conserva y no hay un modelo preentrenado. El modelo exportado es experimental, pendiente de aceptación con los criterios de cada comercio.

CatBoost recibe `article` como categoría. En este piloto se usa `Quantile:alpha=0.65` porque producir de menos tiene prioridad; el costo relativo provisional es 2 por unidad faltante y 1 por unidad sobrante. Esta configuración redujo faltantes en validaciones temporales, pero aumentó el WAPE. Los porcentajes ±10% y ±20% usan error / max(real, 1), siguiendo la guía. Las métricas usan predicciones continuas; el simulador redondea unidades. El ZIP guarda CatBoost en formato CBM, las métricas de validación y los resultados del test final. El test histórico ya se ha inspeccionado durante el desarrollo, por lo que se necesitarán fechas futuras nuevas para una evaluación final independiente.

## Verificación local

Instala `requirements.txt` y ejecuta `python foodsave-ml/verificar_notebook.py` desde la raíz del repositorio. La verificación ejecuta el notebook completo con un CSV sintético temporal y comprueba la exclusión de negativos, ausencia de fuga temporal, uso de historial parcial, límites del simulador y exportación de CatBoost. No sustituye la evaluación con el CSV real.
