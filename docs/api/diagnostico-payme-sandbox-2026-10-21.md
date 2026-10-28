# Diagnóstico de Yape/QR en Flex sandbox · 21-10-2026

Codex para Axel, coordinación A04 con Tienda de Rojas. Estado: **bloqueo externo
reproducido**, sin corrección remota acreditada. No cambiar credenciales ni
afirmar que el portal carece de habilitación: solo se verificó qué ofrece Flex.

## Evidencia observada

Con las credenciales locales de `tienda/.env`, sin imprimir sus valores, se obtuvo
un nonce y se reprodujo la preparación de sesión que realiza el SDK oficial.
Datos del comprador ficticios, moneda 604, importe 455 céntimos, operación de
prueba numérica y `payment_method: {}` como indica la documentación Flex.

| Selección en `displaySettings.methods` | HTTP de preparación Flex | Resultado |
|---|---:|---|
| `CARD` | 200 | Devuelve formulario Tarjetas. |
| `YAPE` | 500 | `{"error":"invalid request","error_message":"list index out of range"}` |
| `QR` | 500 | Mismo error. |
| Sin filtro (consulta diagnóstica, no visible al comprador) | 200 | Lista `CARD`, `PAGOEFECTIVO`. No incluye `YAPE` ni `QR`. |

Esta lista demuestra que **el servicio Flex consultado no ofrece Yape/QR a este
comercio**. Es consistente con un filtro que termina sin elementos, pero no tenemos
acceso al backend de Payme para confirmar la causa interna de la excepción. La
habilitación en el portal, el vínculo con la procesadora y la correspondencia del
merchant con el ambiente requieren revisión del proveedor.

La librería publicada en
`https://flex.dev.pay-me.cloud/flex-payment-forms.min.js` usa internamente OAuth
`https://auth.preprod.alignet.io` y prepara sesiones en
`https://api.dev.alignet.io/flex-capture/flex-session`. Ese destino interno se
observó en el artefacto oficial; no es un endpoint de integración pública que la
tienda deba copiar ni un destino configurable por el comprador. Conviene incluirlo
en el diagnóstico para que Payme revise el comercio correcto. **No se modifica el
SDK ni se conecta a producción como alternativa.**

## Texto para compartir con soporte (envío a cargo del usuario)

> En Flex de preproducción, usando la librería oficial de flex.dev.pay-me.cloud,
> la sesión sin filtro devuelve únicamente CARD y PAGOEFECTIVO para nuestro
> merchant. Con display_settings.methods:["YAPE"] o ["QR"], Flex responde HTTP
> 500: invalid request / list index out of range. CARD devuelve 200 con el mismo
> payload de prueba. Los métodos figuran habilitados según nuestra configuración.
> ¿Pueden revisar YAPE y QR para este merchant en Flex sandbox, su configuración
> con la procesadora y su correspondencia con las credenciales de preproducción?
> El SDK publicado llama internamente a api.dev.alignet.io/flex-capture/flex-session.

Añadir el merchant code solo en el canal de soporte correspondiente. No adjuntar
client_secret, Access Token, nonce ni el archivo `.env`. No se envió ningún mensaje
a soporte durante este trabajo.

## Límites y siguiente comprobación

Solo se solicitaron tokens/nonces y sesiones de configuración. No se llamó al
endpoint de ejecución de pago, no se ingresaron tarjetas/OTP, no se generó un QR
pagable ni se confirmó transacción. Las sesiones diagnósticas no escribieron
registros en la base de la tienda ni en FoodSave. Las pruebas anteriores siguen
vigentes como regresión local, no prueban la habilitación externa por método.

Después de que Payme confirme la configuración: recargar el checkout, verificar
Yape y QR individualmente y confirmar que el servicio ya devuelve sus métodos.
Si entregan nuevas credenciales, actualizar `tienda/.env` y recrear solo la API
según el [README](../../tienda/README.md). No reiniciar para resolver una excepción
remota sin un cambio de configuración. No marcar una operación como pagada por
abrir el formulario ni generar QR/CIP.

Referencias oficiales:
[payload Flex](https://docs.pay-me.com/checkout-web/flex/construccion-del-payload),
[selección de métodos](https://docs.pay-me.com/checkout-web/flex/inicializar-el-componente),
[librería sandbox](https://docs.pay-me.com/checkout-web/flex/libreria-y-estilos-basicos).
