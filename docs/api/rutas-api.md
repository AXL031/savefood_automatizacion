# Rutas HTTP: existentes y objetivo del prototipo

Base `/api/v1`, salvo `/salud`. **La primera tabla está implementada**; las rutas de la segunda son contratos pendientes. Los contratos de cuerpo, unidades, errores e idempotencia están en [contratos.md](contratos.md) y [primera inicialización](contrato-importaciones.md).

| Ruta actual | Autorización |
|---|---|
| `GET`, `POST`, `DELETE /proveedores/telegram/configuracion` | Administrador; estado sin secreto, guardar/comprobar y deshabilitar |
| `POST /proveedores/telegram/comprobar` | Administrador; getMe sin envío |
| `POST /proveedores/telegram/chats-pruebas` | Administrador; buscar /start pendiente sin consumir updates |
| `POST /autenticacion/iniciar-sesion` | Pública |
| `GET /autenticacion/mi-perfil` | Bearer |
| `GET /usuarios`, `POST /usuarios`, `PATCH /usuarios/{id}` | Administrador; cuentas, roles y activación |
| `GET /negocios/actual` | Bearer |
| `PATCH /negocios/actual` | Administrador |
| `POST /programaciones-demo` | Administrador |
| `GET /programaciones-demo` | Bearer |
| `GET /programaciones-demo/{id}` | Bearer |
| `GET /ejecuciones-automatizacion` | Bearer |
| `GET /ejecuciones-automatizacion/{id}` | Bearer |
| `GET /pronosticos/modelos` | Bearer |
| `POST /pronosticos/preparar-modelo` | Administrador; reserva `PREPARAR_MODELO` y responde 202 |
| `GET /pronosticos/corridas` | Bearer; filtro opcional `modelo_id` |
| `GET /pronosticos/corridas/{id}` | Bearer |
| `GET /pronosticos/evaluacion` | Bearer; filtro opcional `modelo_id` |
| `GET /pronosticos/corridas/{id}/evaluacion` | Bearer |
| `POST /planes` | Administrador; M02 local, plan desde corrida y clave |
| `GET /planes`, `GET /planes/{id}` | Bearer; M02 local, snapshots y motivos |
| `POST /inicializacion/piloto-bakery` | Administrador; recibe un CSV bakery y reserva `PREPARAR_MODELO` |
| `GET /inicializacion/estado` | Bearer; estado durable de primera carga |
| `POST /inicializacion/vista-previa` | Administrador; valida dos XLSX o cinco CSV sin escribir |
| `POST /inicializacion/reintentar-preparacion` | Administrador; 202, sin archivos, preparación/evaluación idempotente |
| `POST /inicializacion/confirmar` | Administrador; carga completa con recetas e inventario reales |
| `GET /productos` | Bearer; consulta el catálogo |
| `GET /ventas` | Bearer; consulta ventas diarias |
| `GET /ventas/{id}/revisiones` | Bearer; historial de correcciones |
| `PATCH /ventas/{id}` | Administrador; corrige con revisión |
| `GET /ingredientes` | Bearer; catálogo y uso de unidad |
| `POST /ingredientes`, `PATCH /ingredientes/{id}` | Administrador |
| `GET /recetas`, `GET /recetas/{id}` | Bearer; receta activa o versión concreta |
| `GET /recetas/productos/{id}/versiones` | Bearer; historial |
| `POST /recetas/productos/{id}/versiones` | Administrador; crea nueva versión |
| `GET /inventario/disponibilidad`, `GET /inventario/movimientos` | Bearer; lectura por fecha/lote |
| `POST /inventario/ajustes` | Administrador; movimiento idempotente, promoción pendiente |
| `GET /proveedores`, `GET /proveedores/{id}/ofertas` | Bearer |
| `GET /proveedores/ofertas/preferida/{ingrediente_id}` | Bearer; consulta para Compras |
| `POST /proveedores`, `POST /proveedores/{id}/ofertas` | Administrador |
| `PATCH /proveedores/{id}/estado`, `PUT /proveedores/{id}/chat` | Administrador |
| `POST /proveedores/{id}/verificar-destino` | Administrador; comprueba bot/chat/permisos con credencial vigente |
| `GET/POST/DELETE /proveedores/telegram/configuracion` | Administrador; estado, guardar token protegido o deshabilitar |
| `POST /proveedores/telegram/comprobar`, `POST /proveedores/telegram/chats-pruebas` | Administrador; comprobar bot y buscar su chat por /start |
| `POST /proveedores/ofertas/{id}/preferida`, `PATCH /proveedores/ofertas/{id}/desactivar` | Administrador |
| `POST /planes/{id}/necesidades` | Administrador; completar una vez un plan anterior |
| `POST /pedidos/generar` | Administrador; borradores desde plan, sin envío |
| `GET /pedidos`, `GET /pedidos/{id}` | Bearer; cantidades y ofertas conservadas |
| `GET /compras/propuestas`, `GET /compras/propuestas/{id}` | Bearer; historial e incidencias |
| `POST /compras/propuestas/{id}/cancelar` | Administrador; motivo obligatorio, historial conservado |
| `POST /pedidos/{id}/aprobar` | Administrador; clave y chat revisado, 202 con decisión/envío pendiente |
| `POST /pedidos/{id}/rechazar` | Administrador; clave y motivo, sin envío |
| `POST /compras/propuestas/{id}/verificar-destinos` | Administrador; revisar bloqueos de destino sin alterar snapshots |
| `GET /salud` | Pública, fuera de `/api/v1` |

`POST /autenticacion/renovar` **no existe**. El JWT actual expira en 30 minutos; el cliente solicita nuevo inicio de sesión. Las rutas actuales responden el sobre `error.codigo/mensaje` y los 422 incluyen `detalles`; [A01](contratos.md#contrato-a01-disponible-acceso-y-configuración), [A02](contratos.md#contrato-a02-programación-y-trazas-persistidas) y [A03](contratos.md#contrato-a03-despacho-recuperable-y-servicios-consumidores) documentan sus cuerpos y estados. `GET/PATCH /negocios/actual` incluyen `modo_envio_pedidos` tras aplicar `0001a_configuracion`. Las rutas de programación requieren `0001b_automatizaciones` y el motor A03 requiere `0001c_motor`. Pronósticos requiere `0002_e01_ventas` y `0003_pronosticos`; PREPARAR_MODELO, EVALUAR_MODELO y EVALUAR_PRONOSTICO están registrados, la carga completa ya reserva preparación; GENERAR_PROPUESTA conecta inferencia, plan M02/M03 y evaluación en el corte local.

## Objetivo de la demo

| Ruta propuesta | Propósito | Autorización |
|---|---|---|
| `GET /inventario` | Saldos por lote y agregado con unidad/caducidad. | Bearer |
| Evento tras `POST /inventario/ajustes` | Conectar promoción V03 al ajuste implementado. | Administrador |
| `POST /pedidos/{id}/conciliar` | Resolver resultado de envío incierto con evidencia. | Administrador |
| `GET /promociones/evaluaciones` | Sugerencia o motivo de rechazo por lote; no activa descuentos. | Bearer |

Actualmente `POST /pronosticos/preparar-modelo` reserva el entrenamiento a demanda y el worker registra el backtest al publicar el artefacto. El estado durable `configuracion_inicial` ya existe y el asistente consume recetas/inventario reales; la confirmación ya reserva su entrenamiento y el reintento no vuelve a importar. Aplicar 0008; el estado expone preparación, modelo y evaluación. Celery Beat revisa programaciones cada 30 segundos. La misma clave idempotente recupera la ejecución, y otra entrada con esa clave devuelve conflicto.

El acceso rápido `POST /inicializacion/piloto-bakery` recibe el CSV original del piloto desde la web y reserva su preparación en la misma transacción. Es independiente del asistente completo y no cambia `configuracion_inicial`.

## Visión futura, fuera de la demo

Recepción física de pedidos, **activación** de promociones, excedentes intradía, notificaciones, informes, importación recurrente, Google Sheets y automatización diaria con ventas reales. Proveedor mínimo, pedido y envío a chat de pruebas están implementados en el corte local de pasos 5/6 del [contrato](contrato-pedidos.md); bot real pendiente de configuración del usuario, conciliación y automático en paso 7.
## Paso 2 local · Planificación M02

| Método | Ruta bajo `/api/v1` | Acceso | Estado |
|---|---|---|---|
| POST | `/planes` | Administrador | Generar plan desde corrida persistida; clave y snapshots, sin movimiento de stock |
| GET | `/planes?corrida_id=...` | Sesión | Últimos 50 planes persistidos |
| GET | `/planes/{id}` | Sesión | Detalle de los snapshots y motivos por producto |

Contrato y ejemplo: [M02](contratos.md#m02--paso-2-local-plan-reproducible).
Necesidades y pedidos siguen pendientes en este corte local.
## Ampliación M03 local · 30-09-2026

`POST /api/v1/planes/{plan_id}/necesidades` (Administrador, sin cuerpo) completa una sola vez las necesidades de un plan anterior y devuelve su detalle. GET del plan incluye necesidades, faltantes y trazas persistidas. POST de planes nuevos ya incluye M03 de forma atómica. No crea pedidos ni movimientos.
