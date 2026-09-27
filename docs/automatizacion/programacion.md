# Programación de la exposición

**Estado:** A03 configura un solo Beat cada 30 segundos y un worker que reclama ejecuciones con lease recuperable. La prueba controlada usa PostgreSQL y Redis; los servicios de pronóstico, plan y promoción deben conectar sus manejadores públicos para producir resultados de dominio. Rige [ADR-007](../arquitectura/decisiones/ADR-007-automatizaciones-demo.md). El administrador puede elegir una hora real **muy próxima**, por ejemplo dentro de un minuto; el disparo depende del siguiente ciclo de Beat y de la disponibilidad del worker.

| Automatización | Disparador de la demo | Efecto |
|---|---|---|
| `PREPARAR_MODELO` | Evento: primera carga aceptada. | Un solo entrenamiento CatBoost y registro de artefacto/métricas; reentrega idempotente. |
| `EVALUAR_MODELO` | Evento: modelo preparado. | Backtest cronológico de un día adelante sobre el tramo de prueba; registra métricas y cobertura sin entrenar de nuevo. |
| `GENERAR_PROPUESTA` | El administrador fija `ejecutar_desde_utc` próximo; Beat despacha al vencer. | Inferencia para `fecha_objetivo_demo` histórica, plan, faltantes y pedidos por proveedor. El envío por Telegram sigue el modo configurado; no descuenta stock. |
| `EVALUAR_PRONOSTICO` | Evento: propuesta persistida. | Compara el pronóstico programado con la venta conocida del día objetivo, después de inferir. |
| `EVALUAR_PROMOCION` | Ajuste de lote de producto terminado agenda una hora real próxima; Beat despacha al vencer. | Aplica regla de stock, fecha límite y horario simulado; guarda propuesta o motivo de rechazo, sin activar descuentos. |

Un **solo** proceso Beat publica periódicamente `foodsave.despachar_pendientes` cada 30 segundos. El despachador toma en PostgreSQL programaciones vencidas y eventos internos pendientes con `FOR UPDATE SKIP LOCKED`, registra un token y un lease de 120 segundos y confirma el reclamo **antes** de publicar en Redis. Una programación pasa a `DESPACHADA`; la ejecución conserva su estado hasta que el worker registra el intento. Si se cae entre confirmar y publicar, el lease vence y el siguiente ciclo gira el token y reenvía la misma identidad de ejecución. Un mensaje antiguo con otro token se ignora. Mientras el servicio de dominio mantiene el bloqueo de fila, un segundo worker no puede ejecutar ese mismo efecto local. Una caída posterior al inicio deja un intento activo visible; al vencer su lease se registra fallo transitorio y espera el siguiente intento. La pantalla presenta hora real programada, primer despacho, inicio, fin, estado e intentos.

La **hora real** solo dispara. `fecha_objetivo_demo` y `fecha_hora_simulada_local` determinan los datos históricos calculados y se muestran separados de la hora real. Ejemplo: programar a las 10:31 de hoy una propuesta para el 24-08-2022. Para promoción, ajustar stock con hora efectiva simulada 24-08-2022 17:45 y evaluar con reloj simulado 18:00; la regla de frescura observa quince minutos. No se utiliza la fecha de hoy como si fuera la fecha del dataset.

El cierre diario real a `negocio.hora_cierre` y una evaluación intradía repetida cada 30 minutos son evolución posterior. Requieren ventas operativas actuales; el CatBoost diario no estima ventas restantes del día. Los pedidos del escenario histórico se envían solo al chat de pruebas y se rotulan «DEMOSTRACIÓN — NO SURTIR».
