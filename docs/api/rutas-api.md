# Rutas HTTP: existentes y objetivo del prototipo

Base `/api/v1`, salvo `/salud`. **La primera tabla está implementada**; las rutas de la segunda son contratos pendientes. Los contratos de cuerpo, unidades, errores e idempotencia están en [contratos.md](contratos.md) y [primera inicialización](contrato-importaciones.md).

| Ruta actual | Autorización |
|---|---|
| `POST /autenticacion/iniciar-sesion` | Pública |
| `GET /autenticacion/mi-perfil` | Bearer |
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
| `POST /inicializacion/piloto-bakery` | Administrador; recibe un CSV bakery y reserva `PREPARAR_MODELO` |
| `GET /inicializacion/estado` | Administrador; estado durable de primera carga |
| `POST /inicializacion/vista-previa` | Administrador; valida dos XLSX o cinco CSV sin escribir |
| `POST /inicializacion/confirmar` | Administrador; confirma la carga y reporta dominios pendientes |
| `GET /productos` | Bearer; consulta el catálogo |
| `GET /ventas` | Bearer; consulta ventas diarias |
| `GET /ventas/{id}/revisiones` | Bearer; historial de correcciones |
| `PATCH /ventas/{id}` | Administrador; corrige con revisión |
| `GET /salud` | Pública, fuera de `/api/v1` |

`POST /autenticacion/renovar` **no existe**. El JWT actual expira en 30 minutos; el cliente solicita nuevo inicio de sesión. Las rutas actuales responden el sobre `error.codigo/mensaje` y los 422 incluyen `detalles`; [A01](contratos.md#contrato-a01-disponible-acceso-y-configuración), [A02](contratos.md#contrato-a02-programación-y-trazas-persistidas) y [A03](contratos.md#contrato-a03-despacho-recuperable-y-servicios-consumidores) documentan sus cuerpos y estados. `GET/PATCH /negocios/actual` incluyen `modo_envio_pedidos` tras aplicar `0001a_configuracion`. Las rutas de programación requieren `0001b_automatizaciones` y el motor A03 requiere `0001c_motor`. Pronósticos requiere `0002_e01_ventas` y `0003_pronosticos`; PREPARAR_MODELO, EVALUAR_MODELO y EVALUAR_PRONOSTICO están registrados, pero Edu y Max aún deben conectar sus disparadores de carga y plan.

## Objetivo de la demo

| Ruta propuesta | Propósito | Autorización |
|---|---|---|
| `GET /inventario` | Saldos por lote y agregado con unidad/caducidad. | Bearer |
| `POST /inventario/ajustes` | Movimiento explícito con motivo, hora efectiva simulada y clave única; agenda evaluación de promoción. | Administrador |
| `GET /planes/{id}` | Elementos y necesidades; faltante positivo es sugerencia. | Bearer |
| `GET /proveedores` | Proveedores y ofertas de la demo. | Bearer |
| `POST /proveedores` | Alta de proveedor. | Administrador |
| `POST /proveedores/{id}/ofertas` | Asociar ingrediente y conversión explícita de compra. | Administrador |
| `POST /proveedores/{id}/vincular-telegram` | Vincular y verificar chat de destino. | Administrador |
| `GET /pedidos?plan_id={id}` | Pedidos generados y necesidades sin proveedor. | Bearer |
| `GET /pedidos/{id}` | Líneas, aprobación, estado e intentos de Telegram. | Bearer |
| `POST /pedidos/{id}/aprobar` | Aprobar envío en modo manual. | Administrador |
| `POST /pedidos/{id}/conciliar` | Resolver resultado de envío incierto con evidencia. | Administrador |
| `GET /promociones/evaluaciones` | Sugerencia o motivo de rechazo por lote; no activa descuentos. | Bearer |

Actualmente `POST /pronosticos/preparar-modelo` reserva el entrenamiento a demanda y el worker registra el backtest al publicar el artefacto. El estado durable `configuracion_inicial` ya existe; el disparador desde la confirmación del asistente completo espera los servicios de Max y Vera. Celery Beat revisa programaciones cada 30 segundos. La misma clave idempotente recupera la ejecución, y otra entrada con esa clave devuelve conflicto.

El acceso rápido `POST /inicializacion/piloto-bakery` recibe el CSV original del piloto desde la web y reserva su preparación en la misma transacción. Es independiente del asistente completo y no cambia `configuracion_inicial`.

## Visión futura, fuera de la demo

Recepción física de pedidos, **activación** de promociones, excedentes intradía, notificaciones, informes, importación recurrente, Google Sheets y automatización diaria con ventas reales. Proveedor mínimo, pedido y envío real a chat de pruebas sí están en la [demo](contrato-pedidos.md); sus rutas aún no están implementadas.
