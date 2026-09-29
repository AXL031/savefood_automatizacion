# Guía de desarrollo — Pronósticos y evaluación histórica

**Carpeta:** `frontend/src/app/pronosticos`.

**Responsable:** Kevin Bohorquez. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Modelo predictivo, evaluación histórica y dashboard. **Tareas:** K01, K02, K03, K04.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md](../../../../foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md).
- [foodsave-ml/POLITICA_EVALUACION.md](../../../../foodsave-ml/POLITICA_EVALUACION.md).
- [docs/api/contratos.md](../../../../docs/api/contratos.md).

## Punto de partida y componentes implementados

Componentes disponibles en la ruta `/pronosticos`:
- `page.tsx`: vista completa del dashboard dentro de `ProtectedShell`.
- `TarjetasMetricas.tsx`: tarjetas de resumen consolidado (MAE, WAPE, cobertura, ±20%, ±10%).
- `GraficoSerieHistorica.tsx`: gráfico SVG reactivo con línea temporal previsto vs real conocido e interactividad por día.
- `BarrasProductoDia.tsx`: barras horizontales comparativas por producto para el día seleccionado con diferencia absoluta.
- `TablaDesgloseProductos.tsx`: tabla de auditoría detallada con motivo de exclusión (`VENTA_REAL_DESCONOCIDA`).
- `services/pronosticos.ts`: cliente HTTP tipado (`obtenerEvaluacionHistorica`, `listarCorridasPronostico`) con respaldo determinista del escenario piloto (Q3 2022 / caso 2022-08-24).

## Organización de implementación

La ruta compone `page.tsx` dentro del layout protegido `ProtectedShell`. Todos los componentes manejan la ausencia de venta como valor desconocido (sin imputar ceros), preservando la cobertura visible y asegurando que las sumas de previsto y real se computen exclusivamente sobre pares evaluables.


## Dependencias y contrato de entrega

- **Recibe:** Historial de Edu, modelo/partición y fecha histórica de la programación.
- **Entrega:** Pronósticos para Max y evaluaciones para el panel de Kevin.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Cambiar venta objetivo no cambia características de ese objetivo.
- Predicción desconocida queda null; real ausente no equivale a cero.
- Métricas agregadas se calculan con los mismos pares evaluables.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/bohorquez.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
