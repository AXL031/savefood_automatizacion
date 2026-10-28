# Caja presencial implementada

> **Actualización 28-10-2026:** la implementación de catálogo, promociones aprobadas, reservas y ventas TIENDA por HTTP se documenta en [el contrato vigente](contrato-integracion-tienda.md). Sustituye las menciones históricas de integración pendiente de este documento para esas capacidades. El modo ejemplo sigue sin afectar inventario; Payme continúa solo en preproducción. Cierre diario, simuladores y ML siguen pendientes.

**26-10-2026 · Primer corte funcional, solicitado por Axel.** Implementación de Codex para Axel en `cueva`; dominio Ventas de Sanchez e Inventario de Vera. Este documento describe la API disponible. El [diseño de integración](contrato-ventas-operativas.md) conserva las fases futuras; sus ejemplos de tienda/promociones no son rutas disponibles.

## Uso y límites

En `/ventas`, la pestaña **Ventas presenciales** permite configurar precios (Administrador), seleccionar productos, cotizar, revisar y confirmar el cobro recibido (Operador/Administrador). Hay consulta paginada por fechas/estado, detalle, lotes y movimientos. **Histórico importado** conserva consulta, revisiones y corrección anteriores.

Acceso desde el módulo independiente **Ventas → Caja e historial** en el menú; su contexto de página es Ventas. Preparar datos contiene la inicialización y el catálogo de productos.

Solo canal PRESENCIAL, moneda PEN, una instalación/sucursal y fecha actual del servidor en la zona del negocio. No se admiten fecha retrospectiva, precio o usuario libres desde el navegador. Los medios EFECTIVO, TARJETA, YAPE, QR y PAGOEFECTIVO son cobros **declarados por el operador**; la caja no procesa pagos, pide tarjetas ni llama a Payme.

La tienda independiente no consume ni emite estas rutas todavía. Promociones comerciales, publicación de catálogo, reservas online, simuladores, facturación, devoluciones después de entrega, cierre, cobertura diaria y alimentación/entrenamiento de ML siguen pendientes. Registrar un ticket no inserta `venta_diaria`, no cambia el histórico importado ni activa evaluaciones de promociones. Dashboard/Informes actuales siguen leyendo ese histórico.

Requisito de uso: productos con precio y lotes vigentes. La caja no crea lotes, cambia caducidades ni convierte saldo histórico vencido en mercadería actual. Desde el 28-10 Inventario permite [registrar entradas de varios productos/lotes](contrato-entradas-productos.md), conservando apertura y ajustes anteriores. Ventas solo cuenta lotes ingresados en la fecha consultada o antes. El corte inicial tenía 139 productos sin precio ni stock vendible al 26-10. Posteriormente, por solicitud de Axel, se cargaron [139 estimaciones en PEN](../../datos_carga/referencias/precios_estimados_ventas_pen.md), conservando stock e histórico. Las pruebas completas se realizaron con lotes ficticios aislados.

Sin productos elegibles, Registrar venta abre un diálogo con el motivo: cantidad sin precio y/o sin stock vendible, acceso para abrir catálogo/precios y enlace a inventario. Los controles vacíos quedan deshabilitados; la ausencia de productos no se presenta como un selector vacío sin explicación.

## Rutas

Base `/api/v1`, Bearer administrativo habitual. Sobre `{"datos": ...}` y errores estándar `{"error":{"codigo":"...","mensaje":"...","detalles":[]}}`.

| Método y ruta | Permiso | Resultado |
|---|---|---|
| GET `/ventas/catalogo` | Operador/Administrador | Fecha local, zona, moneda, productos activos con precio/versiones y stock vendible |
| PUT `/ventas/precios/{producto_id}` | Administrador | Nueva versión de precio; mismo contenido/clave devuelve la versión original |
| POST `/ventas/cotizaciones` | Operador/Administrador | 201, cotización propia guardada durante cinco minutos; repetición 200 |
| POST `/ventas/tickets` | Operador/Administrador | 201, venta y descuento atómicos; repetición 200 |
| GET `/ventas/tickets` | Operador/Administrador | Filtros `desde`, `hasta` inclusivos, `estado`, `producto_id`, `limite` 1–100, `desplazamiento` >= 0 |
| GET `/ventas/tickets/{ticket_id}` | Operador/Administrador | Ticket, líneas, precio original, cobro, movimientos y anulación |
| GET `/ventas/tickets/por-clave/{clave}` | Autor de la venta | Recupera resultado de una confirmación propia; 404 si aún no existe |
| POST `/ventas/tickets/{ticket_id}/anular` | Administrador | Compensación auditada, conservando ticket y salidas |

El router de caja se registra antes de las rutas históricas dinámicas. Se mantienen GET `/ventas`, GET `/ventas/{id}/revisiones` y PATCH `/ventas/{id}`.

## Precio, cotización y confirmación

Dinero como cadena positiva de dos decimales, máximo `999999.99` por importe/ticket; sin floats, precios cero ni descuentos libres. Cantidades enteras estrictas 1–1000, 1–100 productos distintos. Campos extra rechazados. Claves 8–80 caracteres `[A-Za-z0-9._:-]`, por usuario y operación; otra carga con la misma clave produce 409 `CLAVE_REUTILIZADA`.

Ejemplos ficticios, IDs sustituidos por los del catálogo:

```json
{"clave_idempotencia":"precio-pan-001","precio":"2.50","version_actual":0}
```

PUT precio usa `version_actual` del catálogo (0 sin precio). Una edición concurrente incompatible devuelve `PRECIO_MODIFICADO`; actualizar/reabrir catálogo antes de editar. Cada versión conserva producto, autor, clave, huella y hora. Una venta anterior no cambia al editar su precio.

```json
{"clave_idempotencia":"cotizar-caja-001","lineas":[{"producto_id":10,"cantidad":3}]}
```

Respuesta `datos`: `id` UUID, `moneda`, `canal`, `vence_en`, `total` y `lineas` con `producto_id`, `nombre`, `codigo`, `cantidad`, `precio_id`, `version_precio`, `precio`, `subtotal`. Cotizar valida catálogo/precio/stock; no reserva ni descuenta. Repetir devuelve la misma cotización aunque ya haya vencido, sin renovar su plazo.

```json
{"clave_idempotencia":"confirmar-caja-001","cotizacion_id":"00000000-0000-0000-0000-000000000001","total_revisado":"7.50","cobro_presencial":{"medio":"EFECTIVO","importe_recibido":"10.00"}}
```

La confirmación exige cotización del usuario, no consumida, vigente y con catálogo/precios actuales idénticos. Servidor fija fecha, usuario, canal, importes y lotes. EFECTIVO recibido debe cubrir total (vuelto `2.50` en el ejemplo); otros medios deben igualarlo. El servidor vuelve a comprobar stock bajo bloqueo. Si falla cualquier línea, se revierte toda la operación.

Detalle: `id`, `numero` (`V-00000001`), `canal`, `estado`, `total`, `moneda`, `fecha_local`, `vendida_en` UTC, `zona_horaria`, `nombre_usuario`, `usuario_id`, `cobro` (medio/recibido/vuelto), `cotizacion_id`, `anulacion` y `lineas`. Cada línea guarda precio y nombre/código de la venta, y `salidas[{lote_id,cantidad,movimiento_id,compensacion_id}]`.

Listado añade `unidades` por ticket y `metadatos` con total, límite, desplazamiento e `importe_confirmado` de **todo el filtro**; anuladas excluidas del importe, presentes en historial. No representa cierre/cobertura diaria.

## Stock y transacción

Interfaz pública de Inventario en `inventario/ventas.py`: `disponibilidad_para_venta`, `retirar_productos_por_venta`, `reintegrar_venta`. Productos publica `catalogo_para_ventas`; Negocios publica moneda/zona. Los servicios comparten sesión sin commit interno; la ruta confirma una vez.

Stock ausente es desconocido. Un lote exige `fecha_limite_venta` conocida y >= fecha actual; caducidad, si existe, >= fecha actual. Caducidad desconocida se advierte; fecha límite desconocida excluye el lote. Prioridad por fecha límite, caducidad conocida e ID. Se bloquean lotes por ID en orden global, se valida todo el carrito y se crean movimientos VENTA negativos solo de producto terminado. No se consumen ingredientes ni se simula producción. PostgreSQL verifica la última unidad concurrente y repetición de una clave sin duplicar venta/movimiento.

## Anulación limitada y recuperación

```json
{"clave_idempotencia":"anular-caja-001","motivo":"Mercancía no entregada","mercancia_no_entregada":true}
```

Solo Administrador y mercancía no entregada. Ticket pasa CONFIRMADA → ANULADA; movimientos ANULA_VENTA compensan exactamente las salidas originales una vez, con autor, motivo, hora y referencias. No se borra evidencia, no se reembolsa ni se extienden fechas de lotes. Una anulación posterior al vencimiento no vuelve vendible el lote. Repetición idéntica devuelve resultado; otra solicitud sobre la anulada devuelve 409.

En el navegador la solicitud completa se conserva **antes** de POST en `sessionStorage`, por usuario. Doble clic se bloquea. Ante red/5xx o sesión vencida se conserva clave/payload; al remontar, GET por clave recupera la venta y el reintento usa el mismo POST. No cerrar la pestaña ni borrar su almacenamiento mientras una confirmación siga pendiente. No es una cola offline ni sincronización entre dispositivos.

Errores relevantes: 403 permisos; 404 cotización/venta propia inexistente; 409 producto no vendible, precio ausente/modificado, stock desconocido/insuficiente, cotización usada/vencida/modificada o clave reutilizada; 422 formato, rango o cobro inválido.

## Persistencia, verificación y siguiente fase

Migración aditiva `0021_ventas_presenciales` sobre 0020: `precio_producto_venta`, `cotizacion_venta`, `ticket_venta`, `linea_ticket_venta`, `salida_lote_venta`; amplía tipos y signos del movimiento de producto. No migra ventas históricas a tickets ni asigna precios ficticios. Downgrade se bloquea si hay operaciones de caja para conservar evidencia.

Pruebas: `backend/tests/integration/test_ventas_presenciales.py` (SQLite o `E03_POSTGRES_TEST=1` con esquemas temporales), cadena Alembic y metadatos en `test_migraciones_entregas.py`; `node scripts/verificar-caja.cjs` usa React/jsdom y HTTP falso para doble clic, cambio de medio, permisos y respuesta perdida/remontaje. Sin Telegram ni pagos reales. Resultados y revisión visual en [avance de Cueva](../equipo/avances/cueva.md). La siguiente fase exige contrato específico antes de conectar tienda/cierre/ML.
