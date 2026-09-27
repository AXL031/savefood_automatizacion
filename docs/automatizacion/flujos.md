# Flujos automatizados del prototipo

**Estado:** diseño, sin tareas operativas implementadas. El worker actual solo tiene `tarea_prueba`. La [programación](programacion.md) y [ADR-007](../arquitectura/decisiones/ADR-007-automatizaciones-demo.md) fijan disparadores y reloj real/simulado.

## 1. Primera carga → entrenamiento

Tras aceptar ventas, catálogo, recetas y stock inicial, `configuracion_inicial` queda `DATOS_CARGADOS` y se encola `PREPARAR_MODELO` una sola vez por huella. El worker registra ejecución e intento, separa entrenamiento, validación y prueba por [meses calendario](../../foodsave-ml/POLITICA_EVALUACION.md), entrena CatBoost sin mirar el tramo de prueba, valida vector, guarda `.cbm`/metadatos y marca `MODELO_LISTO`. Entonces se encola `EVALUAR_MODELO`, también idempotente: genera pronósticos de un día adelante por fecha de prueba, compara posteriormente con ventas conocidas y persiste la serie de métricas/cobertura. Un fallo transitorio se reintenta; un error de datos queda visible sin reentrenar a ciegas.

## 2. Hora programada → pronóstico → plan → faltantes

El administrador elige una hora real próxima y una fecha histórica dentro del tramo de prueba. Beat despacha `GENERAR_PROPUESTA` al vencer. El worker lee el modelo listo y las ventas anteriores a `fecha_objetivo_demo`, persiste corrida con versión, lee lotes/recetas locales, persiste plan y calcula faltantes. A partir de necesidades positivas crea pedidos por proveedor según [ADR-008](../arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md). En modo `REQUIERE_APROBACION` espera al administrador; en modo `AUTOMATICO` solicita el envío por Telegram tras validar el chat y las unidades. Tras persistir la corrida se encola `EVALUAR_PRONOSTICO`, que lee la venta real del objetivo solo para comparar. La pantalla muestra el flujo, la fecha histórica, el pedido y el estado real del mensaje. Reentregar tareas con las mismas claves recupera los mismos efectos. Generar el plan o enviar el pedido no consume inventario.

## 3. Ajuste de stock → evaluación programada de promoción

Un ajuste de stock de producto terminado registra movimiento con hora local **efectiva del escenario** y agenda `EVALUAR_PROMOCION` para una hora real próxima. Beat despacha la evaluación. Se aplica la regla pura existente con fecha límite de venta, stock umbral, horario simulado y frescura máxima; cada lote guarda `proponer=true/false`, descuento si procede y motivo. La tarea no modifica precio, venta, stock ni un POS. El CatBoost diario no estima ventas intradía.

## Control visible

Cada automatización conserva programación, ejecución, hasta tres intentos, error o salida, instantes reales y parámetros del escenario histórico. Un duplicado inocuo queda marcado como resultado ya existente; una clave con entrada diferente es conflicto. La vista de exposición permite mostrar una ejecución completa y una sin sugerencia por vencimiento o stock insuficiente, sin simular éxito donde no hubo efecto.

La confirmación comercial del proveedor, recepción física, promoción publicada y cierre diario real pertenecen a la [visión futura](../vision-futura.md). El envío por Telegram de la demo usa un chat propio que simula al proveedor y se marca «no surtir».
