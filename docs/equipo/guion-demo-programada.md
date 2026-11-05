# Recorrido de exposición con tareas próximas

Actualizado 05-11-2026 por Codex para Axel. Este guion distingue promoción, inferencia y entrenamiento. La jornada del [04/11](guion-demo-2026-11-04.md) conserva sus datos y evidencias; sus lotes que vencían ese día ya no son elegibles el 05. Preparar una exposición para otra fecha exige lotes vigentes y modelo con esa fecha objetivo disponible. No se cambian fechas de lotes históricos para simular vigencia.

## Promoción que aparece dos minutos después

Requiere desplegar la migración 0026 junto con API, worker y frontend. En Operación diaria → Promociones:

1. Seleccionar una sugerencia pendiente/aprobada de un producto publicado, con precio, saldo superior al umbral y límite de venta en el día que se quiere mostrar. La regla debe permitir la hora prevista; modificar su horario no retira otras promociones.
2. Pulsar **Programar publicación → Dentro de dos minutos → Publicar automáticamente si cumple la regla → Confirmar programación**. Si estaba activa, esa promoción se retira mientras espera. Si el producto tiene otros lotes promocionados, estos siguen ofreciendo su descuento.
3. Mostrar estado PROGRAMADA, producto, lote y cuenta atrás. En la tienda, comprobar que ese descuento todavía no se aplica. La retirada y la nueva publicación pasan por la entrega HTTP, con unos segundos de demora.
4. Al cumplirse la hora, Beat recoge la tarea en hasta unos treinta segundos. El motor vuelve a comprobar stock, vencimiento y regla; si cumple, aprueba y Comercio publica. La tienda actualiza su disponibilidad. El resultado y el aviso quedan trazados.
5. Si se necesita empezar otra vez, se puede programar nuevamente una aprobada. **Cancelar programación** antes del reclamo del motor la deja pendiente de aprobación, no la reactiva. No se borran evaluaciones ni se manipula stock para ocultar una promoción.

El modo elegido queda conservado para esa reserva; cambiar después la configuración global no lo altera. Elegir modo manual produce una sugerencia pendiente al llegar la hora. Un lote agotado, vencido o fuera de la ventana no se publica aunque el contador termine.

## Predicción → plan → faltantes → Telegram

En Automatizaciones → Programar tareas:

1. Seleccionar los productos de la demo y un modelo listo que admita la fecha objetivo. El modelo preparado #4 admite el 05/11; no inferir que sirve para el 06/11 o cualquier fecha por cambiar el calendario.
2. Poner **Primera ejecución** en una hora real próxima, por ejemplo dentro de dos minutos. En **Primer día a planificar**, elegir el día objetivo disponible. Son dos campos distintos: cuándo ejecutar y para qué día predecir.
3. Activar **Prueba repetible** si ya existen pedidos para la misma fecha. Comprobar recetas, stock conocido, ofertas y chats verificados.
4. Elegir **Enviar automáticamente por Telegram** y marcar la autorización al chat verificado si se quiere mostrar el envío sin aprobación adicional. En manual, los pedidos se generan pero esperan aprobación. Confirmar la programación.
5. Esperar al motor y abrir la ejecución: primero calcula **un pronóstico nuevo con el modelo elegido**, luego el plan, las necesidades y los pedidos por faltantes. Si el modo es automático y los destinos/ofertas siguen válidos, el outbox los envía por Telegram. COMPLETADA acredita el cálculo; ENVIADO/message_id acredita el mensaje.
6. Mostrar el pronóstico por producto y fecha, el detalle del plan con receta y stock, y el mensaje recibido en los chats de prueba. Sin faltantes no debe fabricarse un pedido. Si un envío queda incierto, revisar y conciliar antes de reenviar.

## Cómo explicar la predicción

La tarea programada **hace inferencia** con una versión ya entrenada; no entrena de nuevo cada vez. Para una demo rápida basta mostrar la versión elegida, los datos anteriores al objetivo y el nuevo pronóstico generado al cumplirse la hora. El plan consume esa corrida, no una cifra introducida manualmente.

El **reentrenamiento** es otro paso: produce una versión nueva y tarda un tiempo real que no debe prometerse como dos minutos. El botón estándar de Pronósticos mantiene la política histórica por meses completos. La herramienta de la jornada del 04/11 entrenó una partición manual identificada y dejó #4/05-11 disponibles; no implementa cierre diario automático ni añade tickets directamente a ML. Para otro día objetivo hay que preparar su historial y partición explícitos conservando el día objetivo fuera del entrenamiento.

Los datos sintéticos permiten demostrar el recorrido y su trazabilidad; no son evidencia de precisión o impacto comercial. El material de prueba de recepción, producción, anulación, roles y Payme continúa en el guion del 04/11, respetando fechas y alcance.
