# Guía de desarrollo — Pronósticos y evaluación histórica

**Carpeta:** `backend/app/modules/pronosticos`.

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

## Punto de partida

**Paso 2 local · 30-09-2026:** consultar_corrida devuelve CorridaLeida inmutable con fecha/modelo/versión/huella y permite bloqueo para serializar planes M02. El consumidor usa este servicio y obtener_pronosticos; no accede a las tablas privadas de Kevin.

**Paso 1 · 30-09-2026:** El adaptador PREPARAR_MODELO con huella_inicializacion notifica inicio durable, completa estado/modelo en su transacción y devuelve evaluacion_ejecucion_id. preparar_modelo acepta clave_evaluacion opcional: tras fallo de backtest reutiliza el artefacto y agenda otra evaluación sin reentrenar. El piloto/manual conserva su comportamiento.

El corte K01–K04 implementa modelos/migración `0003_pronosticos`, entrenamiento desde ventas PostgreSQL (`entrenamiento.py`), vector sin venta objetivo (`caracteristicas.py`), inferencia idempotente (`servicio.py`), evaluación por revisión (`evaluacion.py`), handlers de Kevin y rutas de consulta (`rutas.py`). Max llama `generar_corrida` y `solicitar_evaluacion_corrida` en su sesión; Edu reserva PREPARAR_MODELO al terminar E03. No llamar `commit` desde esos servicios. Consultar el resumen vigente de [Kevin Bohorquez](../../../../docs/equipo/avances/bohorquez.md) para pruebas y límites de integración.

Desde `piloto-q65v2-*`, el entrenador conserva el cuantil 0.65 y usa esa misma pérdida para elegir la iteración en validación. Es una nueva versión del artefacto; los modelos y backtests anteriores siguen disponibles para trazabilidad. La prueba histórica de julio–septiembre de 2022 es exploratoria porque se consultó durante el desarrollo.

## Integración E03/K01

E03/K01: `preparar` confirma el modelo listo mediante la frontera pública de inicialización cuando su entrada incluye la identidad de la carga. El piloto y el entrenamiento a demanda permanecen independientes. La evaluación histórica continúa como tarea durable separada; modelo listo no equivale a backtest terminado.

## Trabajo en esta carpeta

1. Integrar entrenamiento reutilizable y artefacto verificado con versión/huella/partición.
2. Construir exactamente 13 características por días calendario, usando historial anterior al objetivo.
3. Persistir corrida y estados de cobertura; entregar cantidad o null a Max.
4. Ejecutar backtest idempotente y enlazar cada comparación con revisión de venta.
5. Exponer métricas y construir dashboard histórico con serie, producto, fecha, versión y cobertura.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `artefacto_modelo`, `corrida_pronostico`, `pronostico`, `evaluacion_pronostico`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

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

## Dashboard y Reportes de lectura · 01-10-2026

Ampliación expresa: Inicio con ventas diarias, ranking y pedidos; `/informes` con períodos inclusivos, versión del modelo, tablas paginadas, detalle en diálogo y CSV completo del período. [Contrato](../../../../docs/api/contrato-informes.md). Ventas publica `resumen_ventas`/`periodo_ventas`; Compras `resumen_pedidos`/`periodo_propuestas` cuenta pedidos sin multiplicar intentos; K03 admite filtros `desde`/`hasta` opcionales conservando la consulta anterior sin filtros. Informes coordina únicamente interfaces públicas. No migra, entrena, modifica stock ni envía mensajes. Fechas ausentes no se rellenan con cero. Registro/evidencia en Bohorquez y coordinación Cueva.
