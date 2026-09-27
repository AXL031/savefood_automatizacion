# Rutas HTTP: existentes y objetivo del prototipo

Base `/api/v1`, salvo `/salud`. **Solo la primera tabla está implementada**; las rutas del prototipo son contratos para desarrollar, no endpoints disponibles hoy. Los contratos de cuerpo, unidades, errores e idempotencia están en [contratos.md](contratos.md) y [primera inicialización](contrato-importaciones.md).

| Ruta actual | Autorización |
|---|---|
| `POST /autenticacion/iniciar-sesion` | Pública |
| `GET /autenticacion/mi-perfil` | Bearer |
| `GET /negocios/actual` | Bearer |
| `PATCH /negocios/actual` | Administrador |
| `GET /salud` | Pública, fuera de `/api/v1` |

`POST /autenticacion/renovar` **no existe**. El JWT actual expira en 30 minutos; el cliente solicita nuevo inicio de sesión. Las rutas actuales aún responden errores `detail` de FastAPI; deben homologarse al contrato de error antes de añadir las siguientes.

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
| `POST /programaciones-demo` | Agenda `GENERAR_PROPUESTA` para una hora UTC real próxima con fecha histórica explícita. | Administrador |
| `GET /programaciones-demo/{id}` | Hora elegida, disparo y estado. | Bearer |
| `GET /ejecuciones-automatizacion/{id}` | Entradas, intentos, error y efectos. | Bearer |
| `GET /pronosticos/corridas/{id}` | Resultados, versión y cobertura. | Bearer |
| `GET /pronosticos/evaluacion` | Partición, versión y serie diaria del backtest reservado con MAE, WAPE, ±20% y cobertura. | Bearer |
| `GET /pronosticos/corridas/{id}/evaluacion` | Comparación por producto del día elegido: previsto, real conocido, error y cobertura. | Bearer |
| `GET /planes/{id}` | Elementos y necesidades; faltante positivo es sugerencia. | Bearer |
| `GET /promociones/evaluaciones` | Sugerencia o motivo de rechazo por lote; no activa descuentos. | Bearer |

La preparación ML usa el worker existente **solo a demanda** y un estado durable en `configuracion_inicial`. Celery Beat ejecuta cada 30 segundos el despachador de programaciones de pronóstico/plan y promoción; el primer entrenamiento se encola por evento de carga, no por horario. Una segunda solicitud mientras entrena recupera la misma preparación, no inicia otro entrenamiento. Si falla, el estado vuelve a datos cargados con error visible y se permite reintentar.

## Visión futura, fuera de la demo

Proveedores, pedidos/enviar/recibir, **activación** de promociones, excedentes intradía, notificaciones, informes, importación recurrente, Google Sheets y automatización diaria con ventas reales. Sus pantallas históricas no implican que haya API implementada ni tablas en la migración `0002` del prototipo.
