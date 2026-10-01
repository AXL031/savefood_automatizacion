# Contrato de pedidos derivados del pronóstico

## Corte vigente · Envío automático y prueba real · 30-09-2026

Este corte sustituye las restricciones sobre AUTOMATICO de los pasos 4–6 conservados abajo. Generar un pedido con modo AUTOMATICO, necesidades completas, ofertas preferidas activas y destinos verificados reserva todos sus envíos en la misma transacción. Si cualquier pedido tiene bloqueo o mensaje demasiado largo no se reserva ninguno. No se inventa una decisión APROBAR: decision_json/actor/clave de decisión quedan vacíos; la autorización es el modo conservado de propuesta y pedido. La programación conserva además creado_por y el modo elegido. El worker exige propuesta GENERADA activa, sin incidencias/bloqueos, pedido PENDIENTE_ENVIO, modo automático coincidente y destino/credencial vigentes. El modo manual conserva la aprobación administrativa auditada.

Interfaz pública: generar_pedidos(sesion, plan_id, *, modo_envio=None), sin commit. A02 admite modo_envio_pedidos opcional por programación (REQUIERE_APROBACION o AUTOMATICO); GENERAR_PROPUESTA lo pasa a compras. Omitirlo usa el modo del negocio al ejecutar, como antes. Cada propuesta conserva su modo; cambiar preferencias no modifica pedidos anteriores. Igual plan recupera su resultado y no duplica el outbox. Una propuesta activa por fecha sigue impidiendo recompra; una ya enviada no se cancela para eludir esa regla. RECOMPRA_FECHA conserva su código HTTP 409, pero el motivo depende del estado: borrador cancelable indica cancelación explícita; envío autorizado/intento registrado indica revisar su estado; ENVIADO indica que el mensaje ya se transmitió y que una nueva prueba requiere otra fecha histórica. Cambiar solamente la hora real no libera la fecha objetivo.

Actualizar destinos de una propuesta automática bloqueada no reserva envíos ni la convierte a manual: queda AUTOMATICO_REQUIERE_NUEVO_PLAN. Corregir ofertas/destinos, cancelar explícitamente la propuesta no transmitida y programar otro plan. Los mensajes inciertos siguen sin reintento ciego; conciliación manual completa continúa pendiente. Sin faltantes no se envía nada. No se mueve stock al planificar, comprar o enviar.

Presentación: cantidades >=1000 g/ml se muestran en kg/L en mensajes nuevos y UI (1503 g → 1,503 kg). La API, recetas y snapshots conservan unidades base exactas; el texto ya autorizado queda congelado. UI de inventario/ofertas acepta kg/g y L/ml y convierte exactamente antes de llamar la API.

Prueba real autorizada por Axel: propuesta #4/plan #4 (2022-08-24), pedido #1 ENVIADO al chat propio ya verificado, message_id=2. El snapshot inicial tenía destino_verificado=false: configurar el chat no actualizaba el borrador anterior por sí solo. La reserva se aprobó con actor administrativo existente y clave específica de prueba; Beat/worker confirmó la entrega. Sin secretos en el registro. Esta prueba acredita envío manual real; el flujo automático completo se acredita con transporte falso en PostgreSQL, no con un segundo mensaje real.

Pruebas: 54 passed en compras/aprobación/programación/planificación con PostgreSQL aislado, incluido motor → plan → outbox → transporte falso, duplicados y cambios de destino/credencial. No requiere nueva migración sobre 0013.

## Paso 6 local · Revisión, aprobación y envío manual

`POST /pedidos/{id}/aprobar` recibe `{clave_idempotencia,chat_id_revisado}` y responde 202 con el
detalle del pedido. Solo Administrador; exige propuesta activa/generada, pedido
pendiente, modo REQUIERE_APROBACION y destino vigente. Conserva decisión APROBAR,
usuario, nombre de referencia, fecha y clave; congela chat/huella y mensaje
completo de los snapshots. Reserva un envio_pedido PENDIENTE_ENVIO en la misma
transacción. Igual clave/acción/usuario/motivo recupera resultado; cambio da 409.
`POST /pedidos/{id}/rechazar` recibe `{clave_idempotencia,motivo}`: guarda rechazo
con responsable/fecha/motivo; admite pendiente o bloqueado sin exigir Telegram y
no reserva envío. No se rechaza/cancela después de
aprobar o transmitir. Rechazar no libera la fecha automáticamente; cancelación
global explícita admite pedidos rechazados si ninguno fue aprobado.

`POST /compras/propuestas/{id}/verificar-destinos` permite actualizar el bloqueo
de destino antes de decidir. No cambia cantidades, ofertas, proveedor, modo ni
snapshots iniciales; propuestas con faltantes/proveedores incompatibles conservan
su bloqueo y requieren otro plan. Destino actual se muestra aparte en detalle;
aprobar solo admite el chat mostrado en revisión mediante `chat_id_revisado`
obligatorio, rechazando si cambió. El payload de envío congela esa elección.

Consultas incluyen decisión (acción, actor, hora, motivo), texto completo y
destino actual para revisión, estado de envío y evidencia persistida (message_id,
hora Telegram/real y responsable). Todo pedido del escenario histórico lleva
**DEMOSTRACIÓN — NO SURTIR** en vista previa y mensaje. Texto plano, <=4096 unidades
UTF-16; nunca fragmentar un pedido silenciosamente. El plan/pedido/envío no mueve
inventario. Confirmación de Telegram no implica aceptación comercial del proveedor.

Beat despacha outbox de envíos cada 30s; publicación después del commit, lease y
token de despacho permiten recuperar publicación perdida sin repetir llamada
externa. Worker revalida proveedor/chat/credencial y confirma ENVIANDO en una
transacción antes de llamar sendMessage; confirma resultado en otra. Reentrega
solo actúa sobre PENDIENTE_ENVIO con token vigente; nunca reenvía ENVIANDO/ENVIADO.
Una respuesta ok=true con chat/message_id válidos guarda ENVIADO. Error inequívoco
queda FALLIDO; timeout, respuesta inválida/HTTP5xx o interrupción quedan
PENDIENTE_VERIFICACION sin retry. Recuperación/conciliación/reenvío humanos completos
y comprobación del modo AUTOMATICO se entregan en paso 7; automático sigue bloqueado.
Solo pedidos explícitamente aprobados por Administrador generan envíos en este corte.

Migración aditiva 0013 sobre 0012: decisión nullable en pedido_compra y tabla
envio_pedido con UNIQUE(pedido_id), número de intento 1, snapshot de destino,
texto, tiempos, lease/token, estado y evidencia. Servicios participantes sin
commit; worker de envío coordina su propia sesión y no usa motor de retries internos.
Downgrade a 0012 solo antes de decisiones; si existen, se bloquea para conservar
la auditoría y se debe usar una migración correctiva.

Ejemplo administrativo: `POST /api/v1/pedidos/12/aprobar` con
`{"clave_idempotencia":"revision-pedido-12","chat_id_revisado":"123"}` devuelve
`datos.estado=PENDIENTE_ENVIO`, `decision={accion,usuario_id,nombre_usuario,fecha,motivo}`
y `envio={id,numero_intento:1,chat_id,estado,message_id:null,...}`. GET del mismo pedido
tras confirmación conserva la decisión e incorpora `message_id` y `fecha_telegram`.

## Paso 5 local · Configuración Telegram

Administración desde Proveedores: `GET /proveedores/telegram/configuracion` devuelve
`{configurado, origen, codigo, detalle, bot:null}` sin consultar Telegram; `POST` en la
misma ruta recibe `{token}` y comprueba `getMe` antes de guardar; `POST
/proveedores/telegram/comprobar` comprueba la credencial guardada; `DELETE` en
configuración deshabilita el bot incluso si hay fallback de entorno. Todas estas
rutas requieren Administrador. Respuestas bajo `datos`; comprobaciones fallidas
devuelven `bot:null`, código y detalle propios (nunca respuesta ni URL externa).
Token nuevo inválido no reemplaza el anterior. Guardar falla con error HTTP 503
si el volumen o secreto de instalación no permiten cifrar/escribir.

El token entra solo en un formulario password y cuerpo HTTP administrativo; nunca
se devuelve ni persiste en navegador, PostgreSQL o logs. Fernet cifra el archivo
`bot.enc` en `TELEGRAM_CONFIG_DIR`, volumen local privado compartido con worker
(solo lectura). La clave deriva de JWT_SECRET con dominio propio; conservar este
secreto de instalación. Cambiarlo exige volver a configurar Telegram. El archivo
local prevalece sobre TELEGRAM_BOT_TOKEN opcional, también después de deshabilitar.
No incluir secretos/volúmenes en Git, contexto Docker ni respaldo público.

`PUT /proveedores/{id}/chat?chat_id=...` vincula un identificador numérico canónico
(privado positivo o grupo negativo); cambiarlo invalida la verificación. `POST
/proveedores/{id}/verificar-destino` consulta getMe/getChat y, en grupos, permisos
del bot con getChatMember. Canales no admitidos. Devuelve `{verificado, codigo,
detalle}` y conserva fecha/huella SHA-256 de credencial (sin token) solo al verificar.
`GET /proveedores` incorpora destino_verificado_en; destino_verificado es efectivo
para la credencial actual, nunca heredado de otro bot/token. Migración aditiva
0012 invalida verificaciones previas sin huella. Cambiar credencial o deshabilitar
invalida inmediatamente su uso por UI/Compras. Servicios no hacen commit; HTTP
coordina. Las escrituras/verificaciones bloquean la fila del proveedor.

Crear bot propio con BotFather, pegar token en Proveedores, iniciar `/start` en su
chat o añadirlo al grupo propio; obtener su chat_id numérico y vincular/verificar.
Verificar comprueba acceso/permisos; no prueba entrega de mensajes ni propiedad del
chat. El Administrador declara que el chat le pertenece. No se envía mensaje de
prueba o pedido en este paso. `POST /proveedores/telegram/chats-pruebas` (Administrador)
lista `{chat_id,tipo}` de los últimos `/start` pendientes, sin nombres ni textos.
Comprueba getWebhookInfo y rechaza bot con webhook (409 BOT_CON_WEBHOOK); consulta
getUpdates sin offset ni allowed_updates, sin confirmar/descartar actualizaciones
ni cambiar la suscripción. Sin `/start` pendiente indica que se repita el comando.
Aprobación/envío/conciliación y automático quedan en pasos 6/7.

Fuente del protocolo: [Telegram Bot API](https://core.telegram.org/bots/api).

**Estado vigente:** L01/L02 generan borradores con API/UI local. Pasos 5/6 implementan configuración cifrada, verificación, aprobación/rechazo y worker de envío Telegram con evidencia. Validación con bot/chat real del usuario pendiente; pruebas usan transporte simulado. Conciliación y modo automático siguen en paso 7. Rige [ADR-008](../arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md); vista previa y mensajes históricos ya incluyen «DEMOSTRACIÓN — NO SURTIR».

## Origen y cálculo

### Corte L02 del paso 4 local · 30-09-2026

Se implementa la generación persistida desde M03 y la interfaz de proveedores/ofertas/pedidos, sin envío externo. `POST /pedidos/generar` administrativo recibe {"plan_id":12}; GET /pedidos lista propuestas y GET /pedidos/{id} detalla un pedido. Cada propuesta conserva plan, fecha, modo y necesidades; agrupa líneas por proveedor con conversión explícita, mínimo y múltiplo. Decimal: cantidad_compra Numeric(20,4), cantidad_base_pedida Numeric(30,8); exceso de rango devuelve 422 sin escritura parcial. Idempotencia por plan: repetir devuelve los snapshots originales, aunque cambien ofertas o modo.

Política local entre planes: una sola propuesta de compra activa por fecha objetivo, protegida por índice único parcial y lock transaccional de fecha en PostgreSQL. Otra propuesta de esa fecha queda bloqueada con 409 RECOMPRA_FECHA y referencia a la anterior; se conserva el nuevo plan. El administrador puede cancelar explícitamente la propuesta anterior con POST /compras/propuestas/{id}/cancelar y motivo; conserva registros y libera la fecha solo si no hay aprobación ni estado de envío. Repetir el plan cancelado devuelve su historial cancelado; corregir requiere otro plan. No hay recompra incremental ni sustitución automática.

Propuesta: GENERADA, BLOQUEADA, SIN_FALTANTES o CANCELADA. Producción/stock incompletos o ingrediente sin oferta generan incidencias persistidas; no se inventan líneas. Si hay alguna incidencia global, todos sus pedidos quedan BLOQUEADO. Sin faltantes no se crean pedidos ni se reserva la fecha. Proveedor inactivo no aporta línea; destino no verificado permite conservar borrador bloqueado. AUTOMATICO conserva modo pero queda bloqueado CANAL_PENDIENTE_L03; el paso 4 no implementa llamadas Telegram. El modo manual con destino verificado permite PENDIENTE_APROBACION, cuyo endpoint de aprobación se entregará en L03. Nunca se marca ENVIADO sin evidencia real.

GET /compras/propuestas (filtro plan_id opcional) y GET /compras/propuestas/{id} incluyen incidencias, pedidos y trazas. GENERAR_PROPUESTA llama generar_pedidos después de M03, en la misma transacción; un conflicto de fecha se informa en datos_salida sin perder plan ni evaluación. Servicios públicos compartidos sin commit; solo HTTP o motor confirman.

**Entrega M03 local (30-09-2026):** `planificacion.servicio.obtener_necesidades(sesion, plan_id)` ya entrega snapshots con cantidades decimales en cadenas, unidad base y faltante nullable. El consumidor L02 deberá exigir `necesidades_estado=CALCULADAS`; `INCOMPLETAS` contiene subtotales y motivos, no autoriza compras. L02 local consume esta entrega; el corte del paso 4 fija la política de propuesta activa por fecha. Envío automático sigue pendiente de L03.

`GENERAR_PROPUESTA` conserva `corrida_pronostico → plan_produccion → necesidad_ingrediente`. Cada necesidad positiva se asigna a una `oferta_ingrediente` activa de un proveedor activo. En esta etapa hay como máximo una oferta preferida por ingrediente; si falta, la necesidad queda `SIN_PROVEEDOR` y no se crea una línea ficticia. Se agrupan las líneas válidas en un `pedido_compra` por `plan_id` y `proveedor_id`. Si cualquier necesidad positiva queda sin proveedor, los pedidos de ese plan permanecen `BLOQUEADO` y no salen parcialmente sin una decisión explícita; después de completar el mapeo se genera un plan nuevo.

Una oferta declara `unidad_compra`, `factor_a_unidad_base > 0` (cuántas unidades base contiene una unidad de compra), `multiplo_compra > 0` y `minimo_compra >= 0`. El cálculo usa decimal exacto:

```text
cantidad_compra = techo_al_multiplo(max(faltante_base / factor_a_unidad_base,
                                      minimo_compra), multiplo_compra)
cantidad_base_pedida = cantidad_compra × factor_a_unidad_base
```

El pedido guarda copia de faltante, factor, múltiplo, mínimo y cantidad calculada. No se convierte `kg` a `g` ni paquetes a unidades por inferencia; el factor explícito es obligatorio. Una venta histórica, un plan o un pedido no descuentan stock. La recepción física queda fuera de esta demo.

## Modo y estados

`PATCH /negocios/actual` permite `modo_envio_pedidos = REQUIERE_APROBACION | AUTOMATICO`; el valor inicial es `REQUIERE_APROBACION`. Solo Administrador puede cambiarlo. Cada pedido copia el modo vigente al crearse. En modo manual inicia `PENDIENTE_APROBACION`; `POST /pedidos/{id}/aprobar` registra usuario y hora y pasa a `PENDIENTE_ENVIO`; rechazar termina en `RECHAZADO`. En el corte vigente AUTOMATICO conserva el valor pero queda BLOQUEADO con CANAL_PENDIENTE_L03 hasta verificarlo en paso 7. El diseño futuro iniciará PENDIENTE_ENVIO automáticamente con líneas/destino válidos; todavía no está habilitado. Un pedido sin destino verificado o con datos incompatibles queda `BLOQUEADO` con motivo; nunca se transmite.

Transiciones del envío: `PENDIENTE_ENVIO → ENVIANDO → ENVIADO | FALLIDO | PENDIENTE_VERIFICACION`. `ENVIADO` requiere respuesta `ok=true` de Telegram con `message_id`; significa mensaje aceptado por Telegram, no proveedor conforme. Una respuesta inequívoca de error queda `FALLIDO`. Timeout o resultado incierto queda `PENDIENTE_VERIFICACION` y requiere conciliación humana antes de cualquier reenvío. La confirmación comercial del proveedor y recepción de mercancía no se infieren del estado de envío. Sin token del bot o `chat_id` verificado, `BLOQUEADO` con motivo visible.

## Rutas vigentes y diseño pendiente bajo `/api/v1`

| Ruta | Acción | Acceso |
|---|---|---|
| `GET /proveedores` | Listar proveedor, vínculo de chat y ofertas, sin exponer el token del bot. | Bearer |
| `POST /proveedores` | Crear proveedor de la demo con código y nombre. | Administrador |
| `POST /proveedores/{id}/ofertas` | Asociar ingrediente, unidad, factor, múltiplo y mínimo. | Administrador |
| `PUT /proveedores/{id}/chat`, `POST /proveedores/{id}/verificar-destino` | Vincular y verificar por separado un chat propio de pruebas. | Administrador |
| `GET /pedidos?plan_id={id}` | Listar pedidos y necesidades sin proveedor de un plan. | Bearer |
| `GET /pedidos/{id}` | Mostrar plan, proveedor, líneas, modo, estado, intentos y mensaje de Telegram. | Bearer |
| `POST /pedidos/{id}/aprobar` | Autorizar envío solo si el pedido está `PENDIENTE_APROBACION`; requiere clave y chat revisado. | Administrador |
| `POST /pedidos/{id}/rechazar` | Rechazo motivado de pendiente/bloqueado; conserva actor/fecha, sin envío. | Administrador |
| `POST /compras/propuestas/{id}/verificar-destinos` | Revisa bloqueos de destino antes de decisiones; no recalcula líneas. | Administrador |
| `POST /pedidos/{id}/conciliar` | Diseño pendiente de paso 7; todavía no existe. | Administrador |

Las rutas nuevas siguen [convenciones HTTP](contratos.md): sobre `datos`, errores con `error.codigo`, `409` para clave reutilizada o transición inválida. El envío efectivo lo realiza el worker: no se espera la respuesta de Telegram dentro de `POST /aprobar`. La generación de pedidos es un efecto de `GENERAR_PROPUESTA`, no una ruta que calcule otro pronóstico.

## Idempotencia y evidencia

- `UNIQUE(plan_id, proveedor_id)` y `UNIQUE(necesidad_ingrediente_id)` en líneas impiden duplicar borradores o asignar una necesidad a dos proveedores por reentrega del worker. Misma clave y misma huella recupera el pedido; parámetros diferentes con la misma clave producen `409`.
- Antes de llamar a Telegram, el worker reclama el envío en PostgreSQL. Un envío ya `ENVIADO` no vuelve a llamar la API. El texto incluye código de pedido, fecha histórica, proveedor simulado, líneas y aviso **DEMOSTRACIÓN — NO SURTIR**.
- Se conserva por intento instante, resultado, `message_id` si existe y error sin guardar el token del bot. Un resultado ambiguo nunca se reintenta automáticamente porque Telegram no recibe una clave de idempotencia de FoodSave.
- El `chat_id` es un identificador técnico, no un número telefónico. El usuario del chat de pruebas inicia conversación con el bot o lo agrega al grupo antes de vincularlo. La vinculación se prueba antes de habilitar modo automático.

Fuentes del canal: [Telegram Bot API](https://core.telegram.org/bots/api), [introducción oficial a bots](https://core.telegram.org/bots).
