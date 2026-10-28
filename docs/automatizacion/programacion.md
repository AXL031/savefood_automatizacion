# Programación de la exposición

## Seguimiento y predicción vigentes · 21-10-2026

La vista de ejecución presenta espera, despacho, procesamiento y resultado, con consulta cada tres segundos mientras esté activa. Distingue reintento/fallo/cancelación y pérdida de conexión, enlaza resultados por sus IDs y conserva intentos. El listado destaca hasta tres tareas activas de su página del historial. Una ejecución COMPLETADA no confirma por sí sola envío al proveedor ni conclusión de la evaluación reservada.

El worker confirma el inicio del intento antes de procesar; el manejador de propuesta guarda pronóstico, plan y compras juntos en su transacción. No publica telemetría por subetapa, por lo que las tarjetas de dominio son explicación del recorrido, sin porcentaje ni etapa interna fingidos. No cambia el contrato HTTP ni la política de recuperación. Comprobación SSR/estados sin datos operativos: `node scripts/verificar-flujo-automatizacion.cjs`.

La predicción programada ya usa ventas históricas anteriores al objetivo. Ventas tiene importación, consulta y corrección de agregados diarios; caja/tickets, cierre y alimentación continua siguen en [diseño pendiente](../equipo/plan-ventas-vivo-simulacion.md). Además de historia suficiente, la inferencia actual exige una fecha dentro de la partición de prueba del modelo. Consultas de solo lectura en la instalación de este corte: ventas 11-01-2025–09-10-2026 (88 543 filas), modelo #1 LISTO_DEMO con prueba 01-07-2026–30-09-2026; API/Beat/worker activos. Es un estado local, no una configuración portable ni evidencia de pronóstico operativo para hoy.

## Referencia vigente · 20-10-2026

Para preparar diagramas usar [flujos implementados](flujos-implementados.md), contrastados con el registro y sus consumidores. El sistema admite todo el catálogo y calendario finito de 1–31 días; los avisos de ofertas permiten planificar, mientras Compras conserva sus bloqueos de envío. Hay ejecución adelantada explícita, reevaluación por corrección de ventas, promoción tras ajuste y recepción administrativa. El [contrato configurable](../api/contrato-flujo-promociones.md), el [contrato de pedidos](../api/contrato-pedidos.md) y los flujos enlazados describen el estado actual. Las secciones siguientes son **historial**: sus límites de cinco productos, rótulos y pendientes no describen el corte vigente.

## Historial de funcionamiento · 30-09-2026

El flujo completo de GENERAR_PROPUESTA está conectado: modelo listo → pronóstico anterior al objetivo → plan/recetas/stock → faltantes → ofertas por proveedor → outbox Telegram. En /automatizaciones el administrador elige entre 1 y 5 productos por nombre, fecha/hora real del equipo, fecha/hora histórica y envío manual o automático. La elección queda conservada por programación; automático tiene una confirmación explícita de chat propio de pruebas en la UI. El modo del negocio sirve de valor inicial. API/Beat/worker deben permanecer encendidos; el disparo y envío dependen de sus ciclos de 30 segundos.

Es una ejecución única, no un calendario recurrente. No confundir la fecha real de ejecución con el objetivo histórico. Para otra prueba no se puede reutilizar una fecha que ya tenga compra activa/enviada. Completar ofertas preferidas para todos los faltantes y verificar los chats; datos incompletos bloquean toda la propuesta. El resultado enlaza al plan y a pedidos; ENVIADO se confirma aparte con message_id. Ningún plan ni mensaje modifica stock. [Contrato](../api/contrato-pedidos.md).

Stock pequeño aplicado en la instalación por solicitud de Axel: 5 lotes de productos con 2 u.; ingredientes medidos en g/ml con 500 g/ml y huevo con 2 u. Son 14 ajustes auditados (movimientos 17–30), efectivos en el escenario 2022-08-24 10:00. Las aperturas y el historial se conservan. Un lote vencido para otra fecha sigue sin contar. El pedido #1 del 24-08-2022 ya fue enviado; esa fecha conserva la protección de recompra.

Las secciones Paso 2/Paso 4 que siguen documentan cortes anteriores y no describen la integración actual.

**Paso 2 local · 30-09-2026:** GENERAR_PROPUESTA ya consume el modelo y produce
una corrida y un plan M02 con snapshots; reserva EVALUAR_PRONOSTICO después
de guardar el plan, en la misma transacción. Su salida declara PLAN_M02 y
necesidades/pedidos pendientes. La tabla de efectos siguientes describe la demo
objetivo: faltantes, compras, Telegram y promoción todavía no están conectados.
Ver [contrato M02](../api/contratos.md#m02--paso-2-local-plan-reproducible).

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

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.

## Corte configurable vigente · 11-10-2026

El asistente admite una tarea o calendario histórico de 1–31 días reales en la zona del negocio. Cada tarea avanza un día histórico y conserva modelo/modo. Configuración guardada, diagnóstico, gestión de pendientes y paginación real: [contrato](../api/contrato-flujo-promociones.md). Promoción se reserva dentro del ajuste nuevo, no al generar plan/pedido. Se reevalúa la vigencia del movimiento antes de registrar sugerencia o rechazo. Ningún cálculo publica descuentos ni modifica saldos.


## Repetir una prueba completa · 21-10-2026

Opción administrativa explícita «Prueba repetible» en Horario. Permite otra programación y nuevos pedidos para la misma fecha aunque una propuesta anterior ya esté enviada, sin cancelarla ni borrarla. El flujo conserva pronóstico/plan/compras/evaluación y el modo manual/automático; misma ejecución/plan sigue sin duplicar. Compras muestra la marca y el mensaje indica PRUEBA REPETIBLE — NO SURTIR. Modo normal mantiene una compra activa por fecha. Véanse los contratos de [pedidos](../api/contrato-pedidos.md#pruebas-repetibles-autorizadas--21-10-2026) y [flujo](../api/contrato-flujo-promociones.md#prueba-repetible-del-flujo--21-10-2026); aplicar 0020 antes de activar API/worker nuevos.

Para la prueba local: abrir Horario, marcar la opción, elegir el día dentro del rango del modelo y pulsar Probar en un minuto; comprobar requisitos, elegir aprobación/envío y confirmar Programar prueba nueva. Repetir requiere otra solicitud/horario futuro, no reintentar la misma ejecución finalizada. Guardar no programa ni envía. Se utilizan datos y servicios habituales; Telegram no está simulado en la aplicación y una recepción administrativa explícita mantiene su efecto de inventario. Las verificaciones automatizadas usan datos aislados y transporte falso.
