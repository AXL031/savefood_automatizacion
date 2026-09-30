# Guía de desarrollo — Experimento y contrato de ML

**Carpeta:** `foodsave-ml`.

**Responsable:** Kevin Bohorquez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Modelo predictivo, evaluación histórica y dashboard.

## Leer antes de trabajar

- [Instrucciones para IA](../AGENTS.md).
- [Reparto vigente y criterios de entrega](../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../docs/equipo/dependencias.md).
- [Alcance de la demo](../docs/guia-inicio-desarrollo.md).
- [foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md](CONTRATO_ARTEFACTO_INFERENCIA.md).
- [foodsave-ml/POLITICA_EVALUACION.md](POLITICA_EVALUACION.md).

## Punto de partida y herramientas implementadas

Herramientas disponibles en la carpeta:
- `entrenar.py`: CLI de entrenamiento CatBoost independiente de Colab. Produce `catboost_model.cbm` y `metadata.json` con escritura atómica.
- `particion.py`: cálculo de cortes temporales según `POLITICA_EVALUACION.md` (6, 12 o 24 meses).
- `features.py`: construcción de vector de 13 variables contractuales en orden estricto.
- `ventanas.py`: lags y agregaciones por días calendario sin imputar ceros en ausencias.
- `artefacto.py`: entrenamiento y selección de la mejor iteración con `Quantile:alpha=0.65`, más guardado atómico del CBM. El MAE sigue como métrica descriptiva, no como criterio de parada para este objetivo asimétrico.
- `metadata.py`: validación de campos, hash SHA-256, orden de variables y par comercio/sucursal.
- `verificar_artefacto.py`: CLI para verificar la integridad del artefacto antes de su uso.
- `metricas.py`: cálculo estricto de MAE, WAPE (None si suma real es cero), ±20%, ±10% y cobertura.
- `evaluador.py`: evaluación por fecha (totales sumados sobre evaluables) y consolidación del tramo completo sin promediar porcentajes.
- `ejecutar_backtest.py`: CLI para comprobación histórica un día adelante sobre el tramo de prueba reservado.

El backtest CLI aplica `productos_entrenados` y `min_observaciones_previas_28_dias`, como la inferencia del backend. `fechas_evaluadas` cuenta fechas con al menos un par de pronóstico y venta real conocida; las métricas del reporte CLI y del panel usan la misma cobertura.

Coordinación: Kevin coordina la carpeta y su lógica de pronósticos; `normalizar_ventas.py` corresponde a Edu por su frontera de importación de archivos.

**Infraestructura transversal A04 de Axel:** Compose comparte `MODEL_ARTIFACT_DIR` entre worker (escritura) y API (solo lectura). Las herramientas de Kevin escriben y leen el artefacto CBM y sus metadatos en este volumen. El adaptador en `backend/app/modules/pronosticos/entrenamiento.py` exporta desde ventas persistidas el CSV canónico temporal, entrena el modelo versionado y encola el backtest. El flujo E01→K01→K03 se probó con el CSV piloto en SQLite y PostgreSQL/Compose; la carga E03 completa y el consumo M02 siguen pendientes.

## Comandos de desarrollo

```bash
# Ejecutar entrenamiento offline y generar artefacto listo_demo
python foodsave-ml/entrenar.py --csv ventas_diarias_normalizadas.csv --comercio piloto --sucursal principal --salida model_artifacts

# Verificar integridad del artefacto CBM
python foodsave-ml/verificar_artefacto.py --directorio model_artifacts --comercio piloto --sucursal principal

# Ejecutar backtest histórico (un día adelante) sobre el tramo de prueba
python foodsave-ml/ejecutar_backtest.py --artefacto-dir model_artifacts --csv ventas_diarias_normalizadas.csv --salida reporte_evaluacion.json

# Ejecutar todas las pruebas unitarias del módulo ML (52 tests)
python -m pytest foodsave-ml/tests/ -v
```

## Criterio de entrega

- K01 (LISTO_PARA_INTEGRAR): backend puede entrenar y validar CBM sin ejecutar Colab.
- K02 (LISTO_PARA_INTEGRAR): backend persiste corridas y pronósticos con historia anterior al objetivo.
- K03 (LISTO_PARA_INTEGRAR): backtest persistido y métricas calculadas sin promediar porcentajes; WAPE indefinido si la suma real es cero.
- K04 (LISTO_PARA_INTEGRAR): API y panel presentan versión, fechas, cobertura, serie y comparación por producto.


## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../docs/equipo/avances/bohorquez.md) siguiendo [la plantilla](../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
