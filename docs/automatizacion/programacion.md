# Programación de la exposición

**Estado:** contrato de diseño; Beat aún no está configurado. Rige [ADR-007](../arquitectura/decisiones/ADR-007-automatizaciones-demo.md). El administrador puede elegir una hora real **muy próxima**, por ejemplo dentro de un minuto, y ver una cuenta regresiva. No se promete precisión al segundo: Beat inspecciona vencimientos cada 30 segundos y el worker necesita tomar el mensaje de la cola.

| Automatización | Disparador de la demo | Efecto |
|---|---|---|
| `PREPARAR_MODELO` | Evento: primera carga aceptada. | Un solo entrenamiento CatBoost y registro de artefacto/métricas; reentrega idempotente. |
| `EVALUAR_MODELO` | Evento: modelo preparado. | Backtest cronológico de un día adelante sobre el tramo de prueba; registra métricas y cobertura sin entrenar de nuevo. |
| `GENERAR_PROPUESTA` | El administrador fija `ejecutar_desde_utc` próximo; Beat despacha al vencer. | Inferencia para `fecha_objetivo_demo` histórica, plan, faltantes y pedidos por proveedor. El envío por Telegram sigue el modo configurado; no descuenta stock. |
| `EVALUAR_PRONOSTICO` | Evento: propuesta persistida. | Compara el pronóstico programado con la venta conocida del día objetivo, después de inferir. |
| `EVALUAR_PROMOCION` | Ajuste de lote de producto terminado agenda una hora real próxima; Beat despacha al vencer. | Aplica regla de stock, fecha límite y horario simulado; guarda propuesta o motivo de rechazo, sin activar descuentos. |

Un **solo** proceso Beat publica periódicamente `despachar_programaciones_demo` cada 30 segundos. El despachador reclama en PostgreSQL las programaciones vencidas con transición atómica `PROGRAMADA → DESPACHADA`, un `lease_hasta` y una tarea por clave. Si se cae entre reclamar y encolar, el lease vence y la siguiente inspección reenvía **la misma clave**. El worker crea o recupera `ejecucion_automatizacion`; si Beat, Redis o el worker repiten una entrega, la unicidad en base conserva un efecto. La pantalla presenta `programada_para`, `despachada_en`, `inicio_en`, `fin_en`, estado e intentos.

La **hora real** solo dispara. `fecha_objetivo_demo` y `fecha_hora_simulada_local` determinan los datos históricos calculados y se muestran separados de la hora real. Ejemplo: programar a las 10:31 de hoy una propuesta para el 24-08-2022. Para promoción, ajustar stock con hora efectiva simulada 24-08-2022 17:45 y evaluar con reloj simulado 18:00; la regla de frescura observa quince minutos. No se utiliza la fecha de hoy como si fuera la fecha del dataset.

El cierre diario real a `negocio.hora_cierre` y una evaluación intradía repetida cada 30 minutos son evolución posterior. Requieren ventas operativas actuales; el CatBoost diario no estima ventas restantes del día. Los pedidos del escenario histórico se envían solo al chat de pruebas y se rotulan «DEMOSTRACIÓN — NO SURTIR».
