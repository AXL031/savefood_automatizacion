# Contrato de pedidos derivados del pronóstico

**Estado:** diseño para implementar, sin rutas ni tablas existentes. Rige [ADR-008](../arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md). El canal de la demo es Telegram real dirigido a un chat de pruebas propio; el mensaje se rotula «demostración, no surtir» porque la fecha de pronóstico es histórica.

## Origen y cálculo

`GENERAR_PROPUESTA` conserva `corrida_pronostico → plan_produccion → necesidad_ingrediente`. Cada necesidad positiva se asigna a una `oferta_ingrediente` activa de un proveedor activo. En esta etapa hay como máximo una oferta preferida por ingrediente; si falta, la necesidad queda `SIN_PROVEEDOR` y no se crea una línea ficticia. Se agrupan las líneas válidas en un `pedido_compra` por `plan_id` y `proveedor_id`. Si cualquier necesidad positiva queda sin proveedor, los pedidos de ese plan permanecen `BLOQUEADO` y no salen parcialmente sin una decisión explícita; después de completar el mapeo se genera un plan nuevo.

Una oferta declara `unidad_compra`, `factor_a_unidad_base > 0` (cuántas unidades base contiene una unidad de compra), `multiplo_compra > 0` y `minimo_compra >= 0`. El cálculo usa decimal exacto:

```text
cantidad_compra = techo_al_multiplo(max(faltante_base / factor_a_unidad_base,
                                      minimo_compra), multiplo_compra)
cantidad_base_pedida = cantidad_compra × factor_a_unidad_base
```

El pedido guarda copia de faltante, factor, múltiplo, mínimo y cantidad calculada. No se convierte `kg` a `g` ni paquetes a unidades por inferencia; el factor explícito es obligatorio. Una venta histórica, un plan o un pedido no descuentan stock. La recepción física queda fuera de esta demo.

## Modo y estados

`PATCH /negocios/actual` permite `modo_envio_pedidos = REQUIERE_APROBACION | AUTOMATICO`; el valor inicial es `REQUIERE_APROBACION`. Solo Administrador puede cambiarlo. Cada pedido copia el modo vigente al crearse. En modo manual inicia `PENDIENTE_APROBACION`; `POST /pedidos/{id}/aprobar` registra usuario y hora y pasa a `PENDIENTE_ENVIO`. En automático inicia `PENDIENTE_ENVIO` si todas las líneas y el destino pasaron validación; el worker lo envía sin acción adicional. Un pedido sin destino verificado o con datos incompatibles queda `BLOQUEADO` con motivo; nunca se transmite.

Transiciones del envío: `PENDIENTE_ENVIO → ENVIANDO → ENVIADO | FALLIDO | PENDIENTE_VERIFICACION`. `ENVIADO` requiere respuesta `ok=true` de Telegram con `message_id`; significa mensaje aceptado por Telegram, no proveedor conforme. Una respuesta inequívoca de error queda `FALLIDO`. Timeout o resultado incierto queda `PENDIENTE_VERIFICACION` y requiere conciliación humana antes de cualquier reenvío. La confirmación comercial del proveedor y recepción de mercancía no se infieren del estado de envío. Sin token del bot o `chat_id` verificado, `BLOQUEADO` con motivo visible.

## Rutas propuestas bajo `/api/v1`

| Ruta | Acción | Acceso |
|---|---|---|
| `GET /proveedores` | Listar proveedor, vínculo de chat y ofertas, sin exponer el token del bot. | Bearer |
| `POST /proveedores` | Crear proveedor de la demo con código y nombre. | Administrador |
| `POST /proveedores/{id}/ofertas` | Asociar ingrediente, unidad, factor, múltiplo y mínimo. | Administrador |
| `POST /proveedores/{id}/vincular-telegram` | Registrar y verificar un `chat_id` al que el bot pueda enviar. | Administrador |
| `GET /pedidos?plan_id={id}` | Listar pedidos y necesidades sin proveedor de un plan. | Bearer |
| `GET /pedidos/{id}` | Mostrar plan, proveedor, líneas, modo, estado, intentos y mensaje de Telegram. | Bearer |
| `POST /pedidos/{id}/aprobar` | Autorizar envío solo si el pedido está `PENDIENTE_APROBACION`; requiere `clave_idempotencia`. | Administrador |
| `POST /pedidos/{id}/conciliar` | Registrar resolución humana de un envío incierto, con motivo y evidencia; no reenvía automáticamente. | Administrador |

Las rutas nuevas siguen [convenciones HTTP](contratos.md): sobre `datos`, errores con `error.codigo`, `409` para clave reutilizada o transición inválida. El envío efectivo lo realiza el worker: no se espera la respuesta de Telegram dentro de `POST /aprobar`. La generación de pedidos es un efecto de `GENERAR_PROPUESTA`, no una ruta que calcule otro pronóstico.

## Idempotencia y evidencia

- `UNIQUE(plan_id, proveedor_id)` y `UNIQUE(necesidad_ingrediente_id)` en líneas impiden duplicar borradores o asignar una necesidad a dos proveedores por reentrega del worker. Misma clave y misma huella recupera el pedido; parámetros diferentes con la misma clave producen `409`.
- Antes de llamar a Telegram, el worker reclama el envío en PostgreSQL. Un envío ya `ENVIADO` no vuelve a llamar la API. El texto incluye código de pedido, fecha histórica, proveedor simulado, líneas y aviso **DEMOSTRACIÓN — NO SURTIR**.
- Se conserva por intento instante, resultado, `message_id` si existe y error sin guardar el token del bot. Un resultado ambiguo nunca se reintenta automáticamente porque Telegram no recibe una clave de idempotencia de FoodSave.
- El `chat_id` es un identificador técnico, no un número telefónico. El usuario del chat de pruebas inicia conversación con el bot o lo agrega al grupo antes de vincularlo. La vinculación se prueba antes de habilitar modo automático.

Fuentes del canal: [Telegram Bot API](https://core.telegram.org/bots/api), [introducción oficial a bots](https://core.telegram.org/bots).
