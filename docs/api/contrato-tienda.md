# Contrato de la tienda del cliente · 20-10-2026

**Estado: DISEÑO, sin implementación.** Autor y coordinador: Max Rojas (tareas T01–T05). Decisión: [ADR-009](../arquitectura/decisiones/ADR-009-tienda-cliente.md). Las rutas descritas aquí son futuras; ninguna existe todavía. Cambios a este contrato se acuerdan antes de migrar.

## Resumen del recorrido

1. El administrador carga precios (CSV o manual), configura la tienda y, si hace falta, abre lotes nuevos.
2. El cliente inicia sesión con Google, ve el catálogo con precio, estado de stock y promociones vigentes.
3. Confirma la compra con datos de entrega (nombre de quien recibe, celular y dirección) y pago simulado. El stock baja en la misma transacción y **la operación termina ahí**: el pedido queda `CONFIRMADO` como estado final.
4. Cada movimiento de venta reserva `EVALUAR_PROMOCION`; Beat la despacha y guarda una sugerencia o un rechazo.
5. El administrador aprueba la sugerencia; la promoción aparece en la tienda hasta que el lote se agota o vence.

## Convenciones

- Sobre de respuesta y errores según [convenciones HTTP](contratos.md#convenciones-http): `{"datos": ...}` y `{"error": {"codigo", "mensaje", "detalles?"}}`.
- Dinero: cadena decimal con 2 decimales (`"12.50"`), moneda `PEN` tomada de `negocio.moneda`. Cálculo con `Decimal`, redondeo `ROUND_HALF_UP` por línea y total = suma de líneas.
- Cantidades de producto: enteros positivos.
- Fechas locales del negocio sin zona (`2026-10-20T15:30:00`); instantes de auditoría en UTC.
- Listas: `limite` (1–100, por defecto 25), `desplazamiento` y `metadatos.total`.
- Operaciones que crean efectos llevan `clave_idempotencia` (1–80 caracteres, `[A-Za-z0-9._:-]`). Repetir clave y contenido devuelve el mismo resultado con 200; la misma clave con otro contenido devuelve `409 CLAVE_REUTILIZADA`.

## Autenticación del cliente (T02)

| Método y ruta | Acceso | Descripción |
|---|---|---|
| `POST /api/v1/tienda/sesion/google` | Público | Recibe `{"id_token"}` de Google Identity Services. Verifica firma, `aud = GOOGLE_CLIENT_ID`, emisor, expiración y `email_verified`. Crea o actualiza el cliente por `google_sub`. Devuelve `{"token", "cliente": {id, correo, nombre}}`. |
| `GET /api/v1/tienda/sesion` | Cliente | Datos del cliente actual. |

- El token de cliente es un JWT propio con `aud = "tienda"`, `sub = cliente_id` y expiración de 8 horas. Las rutas `/tienda/*` protegidas solo aceptan esa audiencia; las rutas administrativas lo rechazan con `401`.
- Se acepta cualquier cuenta de Google con correo verificado (Gmail o Workspace). Un cliente desactivado por un administrador recibe `403 CLIENTE_INACTIVO`.
- Variables nuevas: `GOOGLE_CLIENT_ID` (público) y `TIENDA_JWT_SECRET` (secreto, distinto de `JWT_SECRET`; si falta, se deriva de `JWT_SECRET` con HMAC). En pruebas se inyecta un verificador falso; ninguna prueba llama a Google.
- **Implementado 21-10-2026** (migración `0019_tienda_clientes`): ambas rutas, verificación con las claves públicas de Google (RS256, `aud`, emisor, vigencia) y errores `GOOGLE_NO_CONFIGURADO` (503), `GOOGLE_NO_DISPONIBLE` (503), `GOOGLE_TOKEN_INVALIDO` (401), `CORREO_NO_VERIFICADO` y `CLIENTE_INACTIVO` (403). Configuración: [configurar-google-tienda.md](configurar-google-tienda.md). El frontend usa el botón oficial de Google cuando `NEXT_PUBLIC_GOOGLE_CLIENT_ID` existe, aunque el catálogo siga en modo ejemplo.

## Catálogo y stock visible (T03)

| Método y ruta | Acceso | Descripción |
|---|---|---|
| `GET /api/v1/tienda/catalogo` | Público | `{categorias, productos}`. Cada producto publicado trae `id`, `codigo`, `nombre`, `categoria`, `descripcion`, `presentacion` (peso o formato), `imagen` (URL), `precio`, `moneda`, `estado_stock` y `promocion` (o `null`). Filtro `buscar`. |
| `GET /api/v1/tienda/catalogo/{producto_id}` | Público | Detalle del producto publicado. |
| `GET /api/v1/tienda/stock` | Público | Respuesta liviana `[{producto_id, estado_stock, promocion_id}]` para consultar cada 5 s. |
| `POST /api/v1/tienda/carrito/cotizar` | Público | `{"lineas": [{producto_id, cantidad}]}`. Devuelve por línea `precio_unitario_base`, `unidades_con_promocion`, `precio_promocional`, `subtotal`, `disponible` y `estado_stock`, más `total`. No reserva ni modifica nada. |
| `GET /api/v1/tienda/imagenes/{nombre}` | Público | Imagen ilustrativa de un producto o categoría. |

`categorias` = `[{codigo, nombre, descripcion, imagen}]`. La cotización existe porque una línea puede mezclar unidades con y sin promoción (la promoción vale solo para el lote evaluado). `disponible=false` indica que la cantidad pedida supera lo vendible, sin decir cuánto queda.

Un producto aparece si está activo, marcado como publicado y tiene precio vigente. `estado_stock` se calcula sobre los lotes **vendibles** a la fecha efectiva de la tienda:

- Lote vendible: saldo > 0, `fecha_limite_venta` conocida y ≥ fecha efectiva, y caducidad desconocida o ≥ fecha efectiva.
- `AGOTADO`: suma vendible = 0, o stock desconocido.
- `ULTIMAS_UNIDADES`: 0 < suma ≤ `umbral_ultimas_unidades` (configuración de la tienda, por defecto 5).
- `DISPONIBLE`: suma > umbral.

Nunca se expone la cantidad exacta ni el código de lote al cliente. Leer el catálogo no modifica nada.

## Configuración de la tienda (T01)

`GET/PUT /api/v1/tienda-admin/configuracion` (lectura Operador, escritura Administrador):

| Campo | Tipo | Regla |
|---|---|---|
| `abierta` | bool | Con `false` el catálogo se muestra, pero comprar devuelve `409 TIENDA_CERRADA`. |
| `modo_fecha` | `ESCENARIO` \| `ACTUAL` | `ESCENARIO` usa `fecha_escenario`; `ACTUAL` usa la fecha de hoy en `negocio.zona_horaria`. |
| `fecha_escenario` | fecha | Obligatoria en `ESCENARIO`. |
| `umbral_ultimas_unidades` | entero 1–1000 | Por defecto 5. |
| `max_unidades_por_linea` | entero 1–100 | Por defecto 20. |

**Fecha efectiva** = fecha según `modo_fecha` combinada con la hora local real del negocio. Se usa para la vigencia de lotes, el `efectivo_en_demo` de los movimientos y la vigencia de promociones. Cada cambio de configuración guarda una versión con actor y fecha; los pedidos conservan la versión con la que se confirmaron.

## Precios y productos (T01)

| Método y ruta | Acceso | Descripción |
|---|---|---|
| `GET /api/v1/tienda-admin/productos` | Operador | Productos con precio vigente, `publicado` y estado de stock interno (con cantidades). |
| `PUT /api/v1/tienda-admin/productos/{id}/precio` | Administrador | `{"precio", "publicado", "clave_idempotencia"}`. Crea una nueva versión de precio. |
| `POST /api/v1/tienda-admin/productos` | Administrador | Alta manual: `{"codigo", "nombre", "categoria", "descripcion", "presentacion", "precio", "publicado", "clave_idempotencia"}`. Crea el producto por la interfaz pública de Productos, su ficha y su primer precio en una transacción. |
| `PUT /api/v1/tienda-admin/productos/{id}/ficha` | Administrador | `{"categoria", "descripcion", "presentacion"}`. Nueva versión de la ficha visible. |
| `POST /api/v1/tienda-admin/productos/{id}/imagen` | Administrador | `multipart/form-data` con `imagen` JPEG, PNG o WebP de hasta 2 MB. Guarda el archivo en el volumen de la tienda y devuelve su nombre. |
| `GET/PUT /api/v1/tienda-admin/categorias` | Operador / Administrador | Lista y actualización de categorías `{codigo, nombre, descripcion, imagen, orden}`. |
| `POST /api/v1/tienda-admin/precios/importar` | Administrador | CSV `codigo_producto,precio,publicado,categoria,descripcion,presentacion,imagen`. Las cuatro últimas columnas son opcionales; `imagen` es el nombre de un archivo ya subido. `?confirmar=false` valida y devuelve vista previa; `true` aplica todo o nada. |

- `precio`: decimal > 0 y ≤ 99999.99, máximo 2 decimales. Moneda siempre la del negocio.
- El CSV usa UTF-8, separador coma y `publicado` = `si`/`no`. Un código desconocido, precio inválido o fila duplicada rechaza todo el archivo con `422 CSV_INVALIDO` y `detalles` por fila. Reimportar el mismo archivo (misma huella) no crea versiones nuevas.
- Los precios se guardan versionados en `precio_producto` (PostgreSQL). Cambiar un precio no altera pedidos ya confirmados, que guardan su precio por línea.
- Un producto sin precio vigente no se publica, aunque tenga stock.
- **Ficha visible del producto** (`ficha_producto_tienda`): `categoria` (código existente), `descripcion` (hasta 300 caracteres), `presentacion` (peso o formato, hasta 80, por ejemplo `500 g · 4-5 porciones`) e `imagen`. La imagen es ilustrativa; sin imagen la tienda muestra un marcador neutro. Un producto sin categoría aparece en «Otros».
- Las imágenes se guardan en un volumen local (`TIENDA_IMAGENES_DIR`), no en la base; la base guarda el nombre y la huella SHA-256.

## Lotes nuevos (T01, frontera de Inventario)

`POST /api/v1/tienda-admin/lotes` (Administrador): `{"producto_id", "codigo_lote", "cantidad", "fecha_limite_venta", "fecha_caducidad?", "motivo", "clave_idempotencia"}`.

Llama a `abrir_lote_producto` de Inventario: crea el lote y un movimiento `APERTURA` con la fecha efectiva de la tienda. Rechaza `fecha_limite_venta` anterior a la fecha efectiva (`422 LOTE_VENCIDO`) y respeta la vida máxima de producto ya definida en Inventario. Repetir la clave no vuelve a sumar.

## Pedido del cliente y pago simulado (T04)

### Confirmar compra

`POST /api/v1/tienda/pedidos` (Cliente)

```json
{
  "clave_idempotencia": "web-7f3c2a",
  "lineas": [{"producto_id": 12, "cantidad": 2, "subtotal_esperado": "17.00"}],
  "entrega": {
    "nombre_receptor": "Ana Pérez",
    "celular": "987654321",
    "direccion": "Av. Universitaria 1801",
    "distrito": "San Martín de Porres",
    "referencia": "Puerta 3"
  },
  "metodo_pago_simulado": "YAPE_SIMULADO"
}
```

Validaciones antes de cualquier efecto:

- Tienda abierta; 1–30 líneas; productos publicados y sin repetir; cantidad 1..`max_unidades_por_linea`.
- `nombre_receptor` 3–120 caracteres; `celular` peruano de 9 dígitos que empieza con 9; `direccion` 5–200; `distrito` 2–80; `referencia` opcional hasta 200.
- `metodo_pago_simulado`: `TARJETA_SIMULADA` o billetera digital `YAPE_SIMULADO` / `PLIN_SIMULADO`. **No se aceptan números de tarjeta, teléfonos de billetera, códigos de aprobación ni otros datos de pago**: un campo adicional se rechaza (`extra="forbid"`). Con `TARJETA_SIMULADA` la interfaz pide número, titular, vencimiento y CVV con validación local (Luhn, marca Visa/Mastercard/Amex/Diners, fecha futura, largo del CVV) y `autocomplete="off"`; **ninguno de esos valores forma parte de esta petición** ni se guarda en ningún lugar. La interfaz no muestra rótulos de simulación.
- `subtotal_esperado` de cada línea igual al `subtotal` de la cotización vigente (incluidas las unidades con promoción). Si difiere: `409 PRECIO_CAMBIADO` con las líneas recotizadas en `detalles`; la interfaz vuelve a cotizar y pide revisar antes de pagar.

Transacción única:

1. Bloquear la configuración vigente y los lotes vendibles de los productos, **ordenados por `lote_producto.id`** para evitar bloqueos mutuos.
2. Asignar unidades por FEFO (fecha límite de venta más próxima; desempate por `id`). Si falta stock en cualquier línea: `409 STOCK_INSUFICIENTE` con `detalles` por producto (sin cantidades exactas, solo `estado_stock`) y **no se guarda nada**.
3. Calcular precio por asignación: las unidades tomadas de un lote con promoción `ACTIVA` usan su precio promocional; el resto, el precio vigente.
4. Crear `pedido_cliente`, `linea_pedido_cliente`, `asignacion_lote_tienda` y `pago_simulado` (`APROBADO`, referencia `SIM-<pedido>`).
5. Por cada asignación, llamar a `retirar_para_tienda` de Inventario: movimiento `VENTA_TIENDA` con delta negativo, clave `tienda-pedido-{id}-lote-{lote_id}` y fecha efectiva.
6. Por cada movimiento, llamar a `reservar_tras_movimiento` de Promociones (reserva `EVALUAR_PROMOCION` si la regla está habilitada).
7. Si una promoción agota su lote, pasa a `FINALIZADA`.
8. Un solo `commit`. Ningún servicio participante confirma por separado.

Respuesta `201` con el pedido; repetición idempotente `200`. Dos clientes que compran la última unidad a la vez: uno obtiene el pedido y el otro `409 STOCK_INSUFICIENTE`; el saldo nunca queda negativo.

### Estado del pedido

En este corte el pedido tiene un único estado: **`CONFIRMADO`**, que es final. Significa pago simulado `APROBADO` y stock descontado. La operación termina cuando el cliente confirma los datos de entrega y el pago simulado; no hay preparación, despacho, entrega, cancelación ni reembolso. Ver [desarrollo futuro](#desarrollo-futuro).

### Rutas del pedido

| Método y ruta | Acceso | Descripción |
|---|---|---|
| `POST /api/v1/tienda/pedidos` | Cliente | Confirmar compra (arriba). |
| `GET /api/v1/tienda/pedidos` | Cliente | Solo los pedidos propios. |
| `GET /api/v1/tienda/pedidos/{id}` | Cliente | Detalle propio (comprobante simulado); pedido ajeno devuelve `404 PEDIDO_NO_ENCONTRADO`. |
| `GET /api/v1/tienda-admin/pedidos` | Operador | Todos, con filtros `desde` y `hasta`. |
| `GET /api/v1/tienda-admin/pedidos/{id}` | Operador | Detalle con lotes, movimientos y evaluaciones de promoción enlazadas. |

## Promociones publicadas (T05)

Las evaluaciones existentes (`evaluacion_promocion`) siguen siendo de Vera. Tienda añade la decisión y la publicación:

| Método y ruta | Acceso | Descripción |
|---|---|---|
| `GET /api/v1/tienda-admin/promociones/pendientes` | Operador | Evaluaciones con `proponer=true` sin decisión, cuyo lote sigue vendible. |
| `POST /api/v1/tienda-admin/promociones/{evaluacion_id}/aprobar` | Administrador | `{"clave_idempotencia"}`. Crea la promoción `ACTIVA`. |
| `POST /api/v1/tienda-admin/promociones/{evaluacion_id}/rechazar` | Administrador | `{"motivo", "clave_idempotencia"}`. |
| `POST /api/v1/tienda-admin/promociones/{id}/retirar` | Administrador | `{"motivo", "clave_idempotencia"}`. Pasa a `RETIRADA`. |
| `GET /api/v1/tienda-admin/promociones` | Operador | Historial con estado y decisión. |
| `GET /api/v1/tienda/promociones` | Público | Promociones `ACTIVA` con producto, precio normal, precio promocional, `descuento_pct` y `vigente_hasta`. |

- Aprobar exige que la evaluación proponga, que el lote siga vendible con saldo > 0 y que el producto tenga precio vigente. Si no: `409 PROMOCION_NO_VIGENTE` o `409 EVALUACION_NO_PROPONE`.
- `precio_promocional = precio_vigente × (1 − descuento_pct/100)`, redondeado a 2 decimales, guardado al aprobar junto con el precio base.
- `vigente_hasta` = el menor entre la fecha límite de venta del lote (fin del día) y la `hora_cierre` de la regla en la fecha efectiva de aprobación.
- Una evaluación tiene como máximo una decisión (`UNIQUE(evaluacion_id)`). Un lote tiene como máximo una promoción `ACTIVA`; aprobar otra para el mismo lote retira la anterior con motivo automático.
- Estados: `ACTIVA` → `FINALIZADA` (lote agotado o fuera de vigencia, evaluado al leer o al vender) o `RETIRADA` (administrador). Ninguno vuelve a `ACTIVA`.
- Aprobar o rechazar no cambia stock ni la evaluación original.

## Integración con automatizaciones

| Evento | Efecto automático | Frontera |
|---|---|---|
| Compra en la tienda | Movimiento de inventario + reserva `EVALUAR_PROMOCION` en la misma transacción | Inventario y Promociones (Vera), consumidos por Tienda |
| Beat despacha `EVALUAR_PROMOCION` | Evaluación con sugerencia o rechazo explicado | Motor (Axel) y Promociones (Vera), sin cambios |
| Administrador aprueba | Promoción `ACTIVA` visible en `/tienda` | Tienda (Max) |
| Lote agotado o vencido | Promoción `FINALIZADA` | Tienda |
| `GENERAR_PROPUESTA` | El plan lee el stock que ya refleja las ventas de tienda | Planificación (Max), sin cambios |

Las compras de la tienda **no** se escriben en `venta_diaria`, no entrenan ni evalúan modelos y no generan pedidos a proveedores por sí mismas.

## Fronteras públicas nuevas

| Servicio | Dueño del dominio | Descripción | Confirma |
|---|---|---|---|
| `retirar_para_tienda(sesion, asignaciones, contexto)` | Inventario (Vera) | Bloquea lotes en orden, crea `VENTA_TIENDA`, rechaza saldo negativo. | No |
| `abrir_lote_producto(sesion, entrada, contexto)` | Inventario (Vera) | Lote nuevo y movimiento `APERTURA` idempotente. | No |
| `lotes_vendibles(sesion, producto_ids, fecha)` | Inventario (Vera) | Lectura de lotes vendibles con saldo, sin bloquear. | No |
| `reservar_tras_movimiento(sesion, movimiento_id, usuario_id)` | Promociones (Vera) | Generaliza `reservar_tras_ajuste` a cualquier movimiento de producto. `reservar_tras_ajuste` se conserva como alias. | No |
| `crear_producto_manual(sesion, codigo, nombre)` | Productos (Edu) | Alta de producto activo sin SKU de ventas. | No |

Max implementa estas funciones por coordinación, con pruebas en el módulo de su dueño, sin cambiar el comportamiento de ajustes, apertura inicial ni evaluaciones existentes. Se avisa a Vera y Edu antes de integrar.

## Datos (migraciones aditivas: `0019_tienda_clientes` aplicada; el resto, prevista `0020_tienda`)

| Tabla | Claves y restricciones principales |
|---|---|
| `cliente` | `google_sub` UNIQUE, `correo`, `nombre`, `activo`, `creado_en`, `ultimo_acceso_en`. **Creada en `0019_tienda_clientes`.** |
| `configuracion_tienda` | Versiones con `id` creciente; la vigente es la mayor. Campos de la tabla de configuración + actor. |
| `precio_producto` | `producto_id`, `version` (UNIQUE juntos), `precio NUMERIC(10,2) > 0`, `moneda CHAR(3)`, `publicado`, `origen` (`CSV`/`MANUAL`), actor, fecha. |
| `categoria_tienda` | `codigo` UNIQUE, `nombre`, `descripcion`, `imagen`, `orden`. |
| `ficha_producto_tienda` | `producto_id`, `version` (UNIQUE juntos), `categoria_codigo?`, `descripcion`, `presentacion`, `imagen_nombre?`, `imagen_sha256?`, actor, fecha. |
| `pedido_cliente` | `cliente_id`, `clave_idempotencia` UNIQUE por cliente, `huella`, `estado` (CHECK `CONFIRMADO`; se ampliará en el futuro), `total NUMERIC(12,2)`, `moneda`, `configuracion_id`, `fecha_efectiva`, datos de entrega. |
| `linea_pedido_cliente` | `pedido_id`, `producto_id` (UNIQUE juntos), `cantidad > 0`, `precio_unitario_base`, `subtotal`. |
| `asignacion_lote_tienda` | `linea_id`, `lote_producto_id`, `cantidad > 0`, `precio_unitario`, `promocion_id?`, `movimiento_venta_id`. |
| `pago_simulado` | `pedido_id` UNIQUE, `metodo` (`TARJETA_SIMULADA`/`YAPE_SIMULADO`/`PLIN_SIMULADO`), `estado` (`APROBADO`), `referencia`, `monto`. |
| `decision_promocion` | `evaluacion_id` UNIQUE, `accion` (`APROBAR`/`RECHAZAR`), motivo, actor, fecha. |
| `promocion_publicada` | `evaluacion_id` UNIQUE, `producto_id`, `lote_producto_id`, `descuento_pct`, `precio_base`, `precio_promocional`, `vigente_desde`, `vigente_hasta`, `estado`; índice único parcial de una `ACTIVA` por lote. |

Además: ampliar `ck_movimiento_inventario_tipo` con `VENTA_TIENDA` (cabe en `VARCHAR(12)`) y `CHECK tipo <> 'VENTA_TIENDA' OR lote_producto_id IS NOT NULL`. El downgrade se niega si hay datos de tienda.

## Errores nuevos

| HTTP | Código | Cuándo |
|---|---|---|
| 401 | `GOOGLE_TOKEN_INVALIDO` | ID token de Google inválido, vencido o de otra audiencia. |
| 403 | `CORREO_NO_VERIFICADO` | Cuenta de Google sin correo verificado. |
| 403 | `CLIENTE_INACTIVO` | Cliente desactivado. |
| 404 | `PRODUCTO_NO_PUBLICADO` | Producto inexistente, inactivo o sin publicar. |
| 404 | `PEDIDO_NO_ENCONTRADO` | Pedido inexistente o de otro cliente. |
| 404 | `PROMOCION_NO_ENCONTRADA` | Evaluación o promoción inexistente. |
| 409 | `TIENDA_CERRADA` | Compra con la tienda cerrada. |
| 409 | `STOCK_INSUFICIENTE` | No hay unidades vendibles suficientes. |
| 409 | `PRECIO_CAMBIADO` | El subtotal esperado de una línea no coincide con la cotización actual. |
| 409 | `EVALUACION_NO_PROPONE` | Se intenta aprobar una evaluación que rechazó la promoción. |
| 409 | `PROMOCION_YA_DECIDIDA` | La evaluación ya fue aprobada o rechazada con otra clave. |
| 409 | `PROMOCION_NO_VIGENTE` | El lote ya no es vendible o no tiene saldo. |
| 409 | `CLAVE_REUTILIZADA` | Misma clave con otro contenido (código existente). |
| 422 | `CARRITO_INVALIDO` | Sin líneas, productos repetidos o cantidades fuera de rango. |
| 422 | `DATOS_ENTREGA_INVALIDOS` | Nombre, celular, dirección o distrito inválidos. |
| 422 | `PRECIO_INVALIDO` | Precio ≤ 0, con más de 2 decimales o fuera de rango. |
| 422 | `PRECIO_FALTANTE` | Publicar un producto sin precio vigente. |
| 422 | `CSV_INVALIDO` | Archivo de precios con errores (detalle por fila). |
| 422 | `LOTE_VENCIDO` | Lote nuevo con fecha límite anterior a la fecha efectiva. |
| 422 | `CONFIGURACION_INVALIDA` | Modo `ESCENARIO` sin fecha u otros valores fuera de rango. |

## Pruebas de aceptación (PostgreSQL)

- Login con verificador falso: correo no verificado → 403; token de cliente en ruta administrativa → 401.
- Compra concurrente de la última unidad: un pedido y un `STOCK_INSUFICIENTE`; saldo ≥ 0.
- Repetir `POST /tienda/pedidos` con la misma clave devuelve el mismo pedido sin otro movimiento; otro contenido → 409.
- Fallo inyectado después de crear el pedido y antes del movimiento revierte todo.
- FEFO: con dos lotes, se descuenta primero el de fecha límite más próxima; lote vencido o sin fecha no se vende.
- Una compra reserva exactamente una `EVALUAR_PROMOCION` por movimiento; Beat la evalúa; aprobar la publica y el catálogo la muestra; agotar el lote la finaliza.
- El pedido confirmado no admite cambios de estado ni cancelación; no existen rutas para ello.
- `PRECIO_CAMBIADO` al cambiar el precio entre carrito y compra.
- CSV inválido no aplica ninguna fila; reimportar el mismo archivo no crea versiones.
- Ninguna compra crea filas en `venta_diaria`, `pedido_compra` ni envíos de Telegram.
- El catálogo público nunca incluye cantidades ni códigos de lote; un cliente no lee pedidos ajenos.

## Desarrollo futuro

No forma parte de este corte; requiere ampliar este contrato y una migración aditiva:

- Estados posteriores del pedido: `EN_PREPARACION` → `EN_CAMINO` → `ENTREGADO`, con actor, motivo y fecha por transición.
- Cancelación (cliente mientras esté `CONFIRMADO`, administrador hasta `EN_PREPARACION`) con movimientos compensatorios `ANULA_TIENDA` sobre los lotes de origen, función `devolver_de_tienda` de Inventario, pago `REEMBOLSADO_SIMULADO` y nueva reserva de `EVALUAR_PROMOCION`.
- Notificaciones al cliente, cálculo de envío y devoluciones tras la entrega.

## Interfaz del cliente · 21-10-2026

Implementada en `frontend/src/app/tienda/` (rutas) y `frontend/src/tienda/` (tipos, servicios, contexto y componentes), a partir del prototipo Figma «PaginaCliente». Rutas: `/tienda`, `/tienda/menu`, `/tienda/carrito`, `/tienda/pedido/{id}` y `/tienda/pedidos`. **Funciona con datos de ejemplo** (`NEXT_PUBLIC_TIENDA_MODO` sin definir): catálogo, stock y pedidos se guardan en el navegador y el login con Google se simula pidiendo un correo Gmail, rotulado como simulado. Con `NEXT_PUBLIC_TIENDA_MODO=api` y `NEXT_PUBLIC_GOOGLE_CLIENT_ID` usa las rutas de este contrato y el botón oficial de Google. Las imágenes de ejemplo están en `frontend/public/tienda/`.

## Pendiente antes de implementar

1. Revisión de este contrato por Vera (Inventario y Promociones) y Edu (Productos); Axel por el token de cliente y las variables nuevas.
2. Registrar el cliente OAuth de Google con el origen `http://localhost:3100` y documentar la configuración sin publicar valores secretos.
3. Carpetas `backend/app/modules/tienda/` y del frontend creadas con su guía. Falta T01, T03, T04 y T05 en el backend.
