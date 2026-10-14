# WhatsApp para Pastelería Maria Juanita

Estado al 14-10-2026: **preparación pendiente de integración**. FoodSave tiene Telegram implementado; todavía no incluye adaptador, configuración administrativa ni webhook de WhatsApp. Este documento prepara la primera conexión a tu propio número. No acredita mensajes enviados.

## Preparación en Meta

1. Entrar en [Meta for Developers](https://developers.facebook.com/apps/) y crear una aplicación con WhatsApp Business Platform, asociada a un portafolio empresarial. El flujo de inicio prepara una cuenta de WhatsApp Business (WABA).
2. Usar inicialmente el número emisor de pruebas que proporciona Meta. Tu número personal será el **destinatario**, no el emisor: no hace falta migrarlo ni quitarlo de tu WhatsApp habitual para esta prueba.
3. En la configuración de API de WhatsApp, añadir tu propio número a los destinatarios permitidos y completar la verificación que solicite Meta. No compartir el código de verificación.
4. Guardar de forma privada el token temporal, el identificador del número emisor (`PHONE_NUMBER_ID`), el identificador de la cuenta (`WABA_ID`) y la versión Graph API que indique la configuración. El token temporal vence; para un uso continuo se prepara un token de usuario del sistema con los permisos y activos correspondientes. No guardarlo en Git, documentación, capturas o el chat.
5. Comprobar la configuración usando el mensaje de prueba de Meta dirigido al número verificado. Este paso envía un WhatsApp real y se ejecuta solo cuando el usuario lo solicite con el destinatario concreto.

Fuentes primarias consultadas: [Developer Hub de WhatsApp](https://whatsappbusiness.com/developers/developer-hub/) y [colección oficial de Meta en Postman](https://www.postman.com/meta/whatsapp-business-platform/collection/wlk6lh4/whatsapp-cloud-api).

## Lo que falta conectar en FoodSave

- Añadir el canal WhatsApp como adaptador de Compras/Proveedores, manteniendo aprobación, deduplicación por plan/fecha, reserva transaccional y tratamiento de resultado incierto.
- Publicar configuración administrativa para `PHONE_NUMBER_ID`, `WABA_ID`, versión API y token cifrado, con respuestas que no devuelvan el secreto. No reutilizar el chat de Telegram como si fuera un teléfono.
- Registrar teléfono destinatario en formato internacional (código de país + número) y autorización. Para esta primera prueba usar únicamente el número propio verificado.
- Adaptar la evidencia del envío: WhatsApp devuelve un identificador de mensaje de texto (`wamid`); el `message_id` entero actual de Telegram no representa ese contrato. La aceptación HTTP no acredita entrega ni aceptación comercial del proveedor.
- Conectar un webhook HTTPS accesible por Meta para estados enviado/entregado/leído/fallido. El backend local en `localhost` no es accesible desde Meta. Preparar URL pública para ese endpoint, verificación y firma de eventos; no publicar toda la aplicación como parte de esta configuración.
- Preparar una plantilla de pedido con nombre del comercio, fecha, referencia y resumen de ingredientes. Las conversaciones iniciadas por la empresa requieren plantilla aprobada; los mensajes libres se permiten como respuesta dentro de las 24 horas del último mensaje del usuario. Mantener revisión de importes/disponibilidad y opt-in del destinatario.

La [política vigente de WhatsApp Business](https://whatsappbusiness.com/policy/) establece consentimiento, plantillas y ventana de 24 horas. El precio depende del mensaje y las tarifas vigentes de Meta; consultar la configuración antes de habilitar envíos continuos.

## Primera prueba de extremo a extremo

Cuando estén disponibles los activos de Meta: implementar el adaptador con transporte falso, probar estados/duplicados/timeouts y después autorizar un único envío a tu propio teléfono. Conectar el pedido real de FoodSave al canal sin alterar stock. Registrar identificador de mensaje y estado del webhook por separado; no reintentar a ciegas un envío incierto.

Coordinación: Cueva por infraestructura/automatización y Aguirre por Compras/Proveedores/canal. La configuración de la cuenta Meta y la autorización del destinatario corresponden al usuario.
