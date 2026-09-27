# ADR-008: pedidos a proveedores derivados del plan

**Estado:** aceptada para el prototipo el 26-09-2026. El usuario confirmó envío real por Telegram y aprobación configurable por negocio. Amplía [ADR-007](ADR-007-automatizaciones-demo.md). Ante una contradicción sobre compras, prevalece esta decisión.

## Decisión de producto

El pronóstico no genera directamente una orden. El recorrido es: pronóstico diario → producción propuesta → ingredientes requeridos por recetas → comparación con stock elegible → faltantes → pedido por proveedor. Se conserva el plan y los valores de stock usados para poder explicar cada línea de pedido. Un nuevo plan puede producir otra propuesta; repetir la misma ejecución no crea dos pedidos.

FoodSave crea pedidos **borrador** con líneas de insumos faltantes y proveedor seleccionado. Cada línea identifica ingrediente, cantidad faltante en unidad base, cantidad a pedir, unidad de compra y regla de conversión aplicada. No se debe convertir un faltante a un formato de compra sin un factor explícito. Se muestran precio y plazo solo si hay datos configurados; no se inventan valores. No se crea un pedido si ningún proveedor activo cubre el ingrediente: el faltante queda visible como `SIN_PROVEEDOR`.

La integración inicial permite un proveedor asignado por ingrediente para el escenario. Si distintos ingredientes tienen proveedores distintos, se crea un pedido por proveedor. `UNIQUE(plan_id, proveedor_id)` protege el borrador generado; regenerarlo con el mismo plan recupera el resultado. Si cambia la asignación, la cantidad o el stock, se crea un nuevo plan y nuevas propuestas sin alterar pedidos enviados.

`negocio.modo_envio_pedidos` se configura como `REQUIERE_APROBACION` (valor inicial) o `AUTOMATICO`. En el primer modo, el pedido queda `PENDIENTE_APROBACION` y solo un Administrador puede aprobarlo y solicitar el envío. En el segundo, el worker lo envía tras guardar el pedido y verificar proveedor, chat vinculado, unidades y datos de entrada. Cambiar el modo afecta solo a pedidos creados después del cambio; cada pedido guarda el modo que lo originó. Ningún modo autoriza un envío con proveedor o conversión desconocidos.

La demo usa un objetivo histórico y stock simulado. El usuario confirmó que el destino será **un chat de pruebas propio que simula al proveedor**. El mensaje saliente debe identificarse de forma visible como **pedido de demostración, no surtir**, con fecha del escenario, para impedir confundirlo con una orden de abastecimiento del día actual. Un pedido borrador es un dato interno; una sugerencia de compra no prueba que el proveedor haya recibido nada.

## Frontera de Telegram

FoodSave registra el `chat_id` del proveedor previamente vinculado y usa un bot con credencial guardada como secreto para llamar `sendMessage` por HTTPS. El bot no puede iniciar una conversación privada: el proveedor debe escribirle primero o añadirlo a un grupo. Una respuesta exitosa de la API de Telegram devuelve un `message_id`; eso prueba aceptación del mensaje por Telegram, **no confirmación del pedido por el proveedor**. Se guardan pedido, intento, mensaje, hora y respuesta. Una confirmación del proveedor requiere una acción o respuesta separada y vinculada al pedido.

La clave idempotente local evita repetir una preparación, pero Telegram no ofrece una clave de idempotencia de `sendMessage`. Si el envío queda en estado incierto por timeout después de salir, se marca `PENDIENTE_VERIFICACION`; no se reenvía a ciegas. Los errores definitivos de destinatario o permisos se muestran al administrador. En desarrollo y CI se usa un adaptador falso que permite verificar formato, estados y fallos sin enviar mensajes a proveedores.

## Límites

La creación o el envío de un pedido no modifica el stock. Recepción física, entregas parciales, facturas, pagos, precios negociados y automatización comercial completa requieren contratos posteriores. El prototipo demuestra el vínculo trazable entre pronóstico, plan, faltante y pedido, más el estado real del envío por Telegram.

Fuentes del canal: [Telegram Bot API](https://core.telegram.org/bots/api) y [introducción oficial a bots](https://core.telegram.org/bots).
