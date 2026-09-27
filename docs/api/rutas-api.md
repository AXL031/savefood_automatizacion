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
| `GET /salud` | Pública, fuera de `/api/v1` |

`POST /autenticacion/renovar` **no existe**. El JWT actual expira en 30 minutos; el cliente solicita nuevo inicio de sesión. Las rutas actuales responden el sobre `error.codigo/mensaje` y los 422 incluyen `detalles`; [A01](contratos.md#contrato-a01-disponible-acceso-y-configuración) y [A02](contratos.md#contrato-a02-programación-y-trazas-persistidas) documentan sus cuerpos y errores. `GET/PATCH /negocios/actual` incluyen `modo_envio_pedidos` tras aplicar `0001a_configuracion`. Las rutas A02 requieren `0001b_automatizaciones` y solo reservan/consultan ejecuciones; no despachan trabajo.

## Objetivo de la demo

| Ruta propuesta | Propósito | Autorización |
|---|---|---|
| `GET /inicializacion/estado` | Estado de carga y modelo. | Administrador |
| `POST /inicializacion/validar` | Recibe dos XLSX o cinco CSV, devuelve vista previa y errores **sin persistir**. | Administrador |
| `POST /inicializacion/cargar` | Revalida los archivos, guarda datos iniciales y devuelve conteos/huellas. | Administrador |
| `POST /inicializacion/entrenar` | Reintenta preparación ML si falló; la primera carga aceptada la encola automáticamente. Devuelve `202` y se consulta estado. | Administrador |
| `GET /productos` | Catálogo y productos seleccionados para demo. | Bearer |
| `GET /ventas-diarias` | Historial agregado, con fecha/producto y paginación. | Bearer |
| `PATCH /ventas-diarias/{id}` | Corrección explícita con motivo; conserva revisión. | Administrador |
| `GET /inventario` | Saldos por lote y agregado con unidad/caducidad. | Bearer |
| `POST /inventario/ajustes` | Movimiento explícito con motivo, hora efectiva simulada y clave única; agenda evaluación de promoción. | Administrador |
| `GET /pronosticos/corridas/{id}` | Resultados, versión y cobertura. | Bearer |
| `GET /pronosticos/evaluacion` | Partición, versión y serie diaria del backtest reservado con MAE, WAPE, ±20% y cobertura. | Bearer |
| `GET /pronosticos/corridas/{id}/evaluacion` | Comparación por producto del día elegido: previsto, real conocido, error y cobertura. | Bearer |
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

La preparación ML usa el worker existente **solo a demanda** y un estado durable en `configuracion_inicial`. Celery Beat ejecuta cada 30 segundos el despachador de programaciones de pronóstico/plan y promoción; el primer entrenamiento se encola por evento de carga, no por horario. Una segunda solicitud mientras entrena recupera la misma preparación, no inicia otro entrenamiento. Si falla, el estado vuelve a datos cargados con error visible y se permite reintentar.

## Visión futura, fuera de la demo

Recepción física de pedidos, **activación** de promociones, excedentes intradía, notificaciones, informes, importación recurrente, Google Sheets y automatización diaria con ventas reales. Proveedor mínimo, pedido y envío real a chat de pruebas sí están en la [demo](contrato-pedidos.md); sus rutas aún no están implementadas.
