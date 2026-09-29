# Avances — Kevin Bohorquez

**Responsable:** Kevin Bohorquez. **Bloque:** Modelo predictivo, evaluación histórica y dashboard. **Rama prevista:** `bohorquez`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md). Este archivo se actualiza al terminar cada avance significativo.

## Resumen vigente

- **Estado:** K01 y K03 implementados y listos para integración; K02 y K04 en preparación.
- **Punto de partida alcanzado:** Se completó el pipeline de entrenamiento offline sin Colab (`entrenar.py`), generación y validación de artefactos CBM con SHA-256 (`verificar_artefacto.py`), cálculo estricto de métricas (`metricas.py`) y evaluador histórico de tramo completo con backtest un día adelante (`evaluador.py`, `ejecutar_backtest.py`). 52 pruebas unitarias pasando en `foodsave-ml/tests/`.
- **Contrato disponible:** [CONTRATO_ARTEFACTO_INFERENCIA.md](../../../foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md) y [POLITICA_EVALUACION.md](../../../foodsave-ml/POLITICA_EVALUACION.md).
- **Entrega a consumidores:** `MODEL_ARTIFACT_DIR` recibe `catboost_model.cbm` y `metadata.json` listos para inferencia local; evaluador produce métricas en formato dict listas para persistencia K02 y dashboard K04.
- **Bloqueos:** Ninguno para K01/K03. Para K02 se requiere la migración 0002 y ventas en PostgreSQL de Edu (E01), adelantable con fixtures propios.
- **Siguiente paso:** Implementar servicio de inferencia K02 en el backend con fixtures de prueba.

| Tarea | Estado de seguimiento |
|---|---|
| K01 · Extraer entrenamiento reutilizable | LISTO_PARA_INTEGRAR |
| K02 · Implementar inferencia y persistencia | PENDIENTE DE VERIFICAR / COMPLETAR |
| K03 · Implementar evaluación histórica | LISTO_PARA_INTEGRAR |
| K04 · Construir dashboard y vistas de pronóstico | PENDIENTE DE VERIFICAR / COMPLETAR |

## Bitácora

### K03 · Implementación de métricas y evaluación histórica

- **Fecha/hora y zona:** 2026-09-29 12:30 (America/Lima)
- **Autor y responsable del bloque:** Kevin Bohorquez
- **Tareas:** K03 (Implementar evaluación histórica)
- **Estado:** LISTO_PARA_INTEGRAR
- **Qué cambió y qué comportamiento está disponible:**
  - Implementación de `metricas.py` con cálculo contractual de MAE (unidades), WAPE porcentual (retorna `None` si la suma real es cero, jamás calcula `100 - WAPE` ni lo denomina precisión), `% dentro de ±20%` y `±10%` usando `max(real, 1)` y cobertura (ausencia = desconocida, no cero).
  - Implementación de `evaluador.py` con `evaluar_dia` (suma total previsto y real exclusivamente sobre productos con venta real conocida) y `consolidar_evaluacion_tramo` (calcula MAE y WAPE sobre todos los pares producto-día juntos, sin promediar porcentajes diarios).
  - Implementación de `ejecutar_backtest.py`: CLI de simulación histórica que itera fecha por fecha sobre el tramo de prueba reservado, infiriendo un día adelante con ventas estrictamente anteriores y exportando el informe JSON.
- **Archivos clave:**
  - `foodsave-ml/metricas.py`
  - `foodsave-ml/evaluador.py`
  - `foodsave-ml/ejecutar_backtest.py`
  - `foodsave-ml/tests/test_evaluacion_k03.py`
- **Contrato/función/ruta y ejemplo de uso:**
  - `evaluar_pares(pares: Sequence[ParEvaluacion]) -> MetricasResultado`
  - `consolidar_evaluacion_tramo(version, ini, fin, pares) -> EvaluacionTramoCompleto`
  - `python foodsave-ml/ejecutar_backtest.py --artefacto-dir model_artifacts --csv ventas.csv --salida reporte.json`
- **Migración/configuración necesaria:** Ninguna en BD; utiliza dependencias de `requirements.txt`.
- **Pruebas:** `python -m pytest foodsave-ml/tests/test_evaluacion_k03.py -v` (20 passed de K03; 52 passed en total en el módulo).
- **Qué necesita el siguiente desarrollador y quién es:**
  - Max Rojas (M02) y Kevin (K02/K04) reciben la estructura de métricas y evaluación consolidada.
- **Dependencias/bloqueos:** Ninguno para evaluación offline. Persistencia en DB dependerá de K02.
- **Siguiente paso concreto:** Conectar la evaluación histórica al servicio de backend K02 y al panel K04.
- **Commit/PR:** Commits `694b05b` a `85d0fcb` en rama `bohorquez`.

### K01 · Entrenador CatBoost independiente de Colab

- **Fecha/hora y zona:** 2026-09-29 11:15 (America/Lima)
- **Autor y responsable del bloque:** Kevin Bohorquez
- **Tareas:** K01 (Extraer entrenamiento reutilizable)
- **Estado:** LISTO_PARA_INTEGRAR
- **Qué cambió y qué comportamiento está disponible:**
  - Pipeline de entrenamiento local CLI (`entrenar.py`) independiente de Google Colab.
  - Partición temporal según `POLITICA_EVALUACION.md` por meses completos (6, 12 o 24 meses).
  - Vector de 13 características contractuales en orden estricto (`features.py`).
  - Ventanas temporales por días calendario sin imputar ceros en ausencias (`ventanas.py`).
  - Guardado atómico de `catboost_model.cbm` y generación de `metadata.json` con SHA-256 (`artefacto.py`, `metadata.py`).
  - Verificador de integridad CLI (`verificar_artefacto.py`).
- **Archivos clave:**
  - `foodsave-ml/entrenar.py`
  - `foodsave-ml/particion.py`
  - `foodsave-ml/features.py`
  - `foodsave-ml/ventanas.py`
  - `foodsave-ml/artefacto.py`
  - `foodsave-ml/metadata.py`
  - `foodsave-ml/verificar_artefacto.py`
  - `foodsave-ml/tests/test_entrenador_k01.py`
- **Contrato/función/ruta y ejemplo de uso:**
  - `python foodsave-ml/entrenar.py --csv ventas.csv --comercio piloto --sucursal principal --salida model_artifacts`
  - `python foodsave-ml/verificar_artefacto.py --directorio model_artifacts`
- **Migración/configuración necesaria:** Ninguna en BD; escribe en volumen `MODEL_ARTIFACT_DIR`.
- **Pruebas:** `python -m pytest foodsave-ml/tests/test_entrenador_k01.py -v` (27 passed).
- **Qué necesita el siguiente desarrollador y quién es:**
  - Axel (A04) y Kevin (K02) pueden montar el directorio de artefactos y consumir el CBM verificado.
- **Dependencias/bloqueos:** Ninguno; K01 completado e integrado en `main` mediante PR #4.
- **Siguiente paso concreto:** Completar K03 (métricas y backtest) e iniciar K02 (inferencia en backend).
- **Commit/PR:** Pull Request #4 mergeado en `main` (`d016c35`).

### Preparación del registro

- **Autor:** IA que preparó el reparto y guías, sin atribuir implementación a Kevin Bohorquez.
- **Cambio:** se definieron las tareas y el lugar de documentación; no se implementó lógica de este bloque en esta entrega documental.
- **Pruebas:** la revisión de documentación comprueba enlaces, cobertura de carpetas y coherencia del reparto; no acredita funcionamiento del módulo.
- **Próximo autor:** registrar el primer avance con la plantilla y actualizar el resumen vigente.
