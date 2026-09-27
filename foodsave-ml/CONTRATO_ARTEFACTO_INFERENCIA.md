# Contrato del artefacto CatBoost para inferencia local

**Estado:** especificación para desarrollar la integración; el repositorio aún no incluye un CBM cargado por el backend. En el prototipo universitario, la primera inicialización entrena una vez con las ventas históricas importadas y guarda un artefacto `listo_demo` para inferencia local sobre fechas históricas. Esto no equivale a aprobación comercial. El notebook actual exporta un artefacto experimental que debe ampliarse con versión y huella antes de usarlo en el prototipo.

## Entrega offline

Cada instalación conserva juntos `catboost_model.cbm` y `metadata.json` en un directorio local de solo lectura para la API. El entrenamiento es un **paso separado de la primera inicialización**; el botón «Generar» nunca entrena ni descarga un modelo. El archivo de metadatos debe contener:

**Infraestructura disponible en A04:** API y worker reciben `MODEL_ARTIFACT_DIR=/code/model_artifacts`, respaldado por el volumen persistente `model_artifacts` de Compose. El worker puede escribir allí el CBM y sus metadatos; la API monta el mismo directorio en solo lectura. El directorio empieza vacío: Kevin debe implementar la escritura atómica, lectura/verificación de huella y gestión de versiones antes de declarar `listo_demo`. El código del modelo y sus pruebas siguen bajo su responsabilidad.

| Campo | Regla |
|---|---|
| `estado` | `experimental_pendiente_de_aceptacion`, `listo_demo` o `aprobado`. `listo_demo` solo permite la simulación histórica local; `aprobado` sería una evaluación futura para uso operativo. |
| `version_modelo` | Texto estable y no vacío. Cambia al sustituir el CBM o su contrato de características. Se conserva en `corrida_pronostico`. |
| `fecha_corte_entrenamiento` | Último día cuyos datos pudieron intervenir en entrenamiento/selección. Debe ser anterior a `fecha_objetivo_demo`; para el caso `2022-08-24` se propone `2022-06-30`. |
| `particion` | Versión de la [política temporal](POLITICA_EVALUACION.md) y fechas inclusivas de inicio/fin de entrenamiento, validación y prueba. La prueba queda fuera de ajuste, selección de características, hiperparámetros y parada temprana. |
| `artefacto` | Nombre local del archivo `.cbm`, sin rutas ascendentes ni URL. |
| `sha256_artefacto` | Huella SHA-256 del CBM. La carga rechaza una huella distinta. |
| `comercio_id`, `sucursal_id` | El único par externo configurado en `negocio`; una discrepancia impide inferencia. |
| `features` | Lista ordenada exacta de las 13 variables siguientes. Se compara también con los nombres grabados dentro del CBM. |
| `productos_entrenados` | SKUs externos conocidos por el entrenamiento. Para inferir se resuelven mediante `sku_producto` al producto interno. |
| `min_observaciones_previas_28_dias` | Entero positivo; inicialmente `7`, según el contrato de datos. |
| `horizonte` | `un_dia_con_historial_real`. El modelo estima el día local siguiente tras el cierre. |
| `politica_ausencias` | `desconocido`; no se completan fechas sin fila con cero. |

`version_modelo`, `sha256_artefacto`, `fecha_corte_entrenamiento` y `particion` son ampliaciones exigidas al exportador del notebook antes de marcar `listo_demo`. El `metadata.json` experimental actual no los garantiza. `fecha_corte_entrenamiento` coincide con el último día de validación si esta intervino en seleccionar el modelo; no puede alcanzar la prueba.

## Vector de características

El orden es contractual y coincide con `FEATURES` del notebook:

1. `article` — SKU externo textual usado al entrenar, categoría CatBoost.
2. `dia_semana` — lunes `0` a domingo `6` de `fecha_objetivo` local.
3. `mes` — `1` a `12`.
4. `dia_mes` — `1` a `31`.
5. `fin_semana` — `1` si sábado o domingo; `0` en otro caso.
6. `ventas_ayer` — valor conocido un día antes o faltante.
7. `ventas_hace_7_dias` — valor conocido siete días antes o faltante.
8. `promedio_7_dias` — promedio de observaciones conocidas de los siete días anteriores; faltante si no hay ninguna.
9. `promedio_14_dias` — misma regla para catorce días.
10. `promedio_28_dias` — misma regla para veintiocho días.
11. `conteo_7_dias` — cantidad de observaciones conocidas en siete días.
12. `conteo_14_dias` — cantidad de observaciones conocidas en catorce días.
13. `conteo_28_dias` — cantidad de observaciones conocidas en veintiocho días.

Las ventanas avanzan por **días calendario**, no por filas de ventas; un día ausente conserva valor faltante. Todas las entradas proceden de fechas anteriores a `fecha_objetivo`. Se emite `HISTORIAL_INSUFICIENTE` si faltan observaciones y `PRODUCTO_NO_CUBIERTO` si el SKU no figura en `productos_entrenados`; no se inventa un cero ni se aplica la métrica global del modelo a ese producto.

El resultado del CBM debe ser finito; se limita a cero como mínimo y se redondea a unidades enteras con la misma regla que el notebook (`np.rint`, empates al par). Una corrida persiste `version_modelo`, `fecha_objetivo`, estado y pronósticos por producto. Una corrida repetida con la misma clave recupera el resultado durable; una nueva versión o recálculo usa otra clave y conserva la anterior.

## Puerta de uso en la demo y aprobación futura

Para `listo_demo`, el responsable registra versión, huella, par de identidad, lista de variables, fecha de corte del entrenamiento, cobertura y métricas históricas; el resultado se rotula «demostración con datos históricos». El backend rechaza artefactos ausentes, experimentales, corruptos o incompatibles. Para marcar `aprobado` en el futuro harían falta datos posteriores no usados para ajustar ni seleccionar el modelo, además de criterios de calidad de cada comercio. La evaluación de promociones cada 30 minutos es **otro problema de inferencia**; este CBM de un día adelante no se reutiliza como predicción intradía.
