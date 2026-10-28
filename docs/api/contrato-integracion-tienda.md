# Integración de tienda independiente · desarrollo autorizado 28-10-2026

Codex para Axel; coordinación Cueva, tienda Rojas, Ventas/UI Sanchez, inventario/promociones Vera. Este contrato concreta las etapas 1–3 del [análisis](../equipo/analisis-adaptacion-tienda-bohorquez-2026-10-28.md); simuladores/cierre/ML conservan su fase futura. ADR-010 y Payme solo preproducción; ninguna base, servicio Python ni archivo se comparte entre proyectos.

FoodSave envía un catálogo completo versionado a la API de tienda. Su backend solicita cotización/reserva a FoodSave, prepara Payme por el importe congelado, verifica por Consulta/S2S y emite un evento de venta. FoodSave registra ticket TIENDA y salida de lotes en una transacción; acuse/reintentos idempotentes. El invitado no necesita Google ni credencial administrativa.

## API FoodSave

Base /api/v1, sobres datos/error habituales. /tienda-admin requiere sesión administrativa (lecturas Operador/Admin, escrituras Admin). /integracion-tienda requiere Bearer privado TIENDA_INTEGRACION_TOKEN, habilitación explícita TIENDA_INTEGRACION_HABILITADA=1 e identidad TIENDA_INTEGRACION_ID (por defecto tienda-local), sin permisos de usuario.

- GET /tienda-admin/productos: precio vigente de caja, metadatos/publicación/versiones y disponibilidad; no cambia precios ni stock.
- PUT /tienda-admin/productos/{id}: version_actual, publicado, categoria, descripcion, presentacion, imagen. Precio canónico sigue en Ventas; versión incorrecta 409. Publicación requiere producto activo con precio.
- POST /tienda-admin/sincronizar: prepara snapshot durable; publicación/reintentos por despachador separado de Telegram.
- GET /tienda-admin/estado y /tienda-admin/reservas: estado de entregas y reservas, sin secretos.
- GET /integracion-tienda/stock: disponibilidad y promoción públicas actuales; no revela lotes/cantidades al navegador.
- POST /integracion-tienda/cotizar: {origen UUID,lineas[{producto_id,cantidad}]}; devuelve líneas/importes/huella/origen, sin reservar.
- POST /integracion-tienda/reservas: mismo cuerpo más clave_idempotencia y cotizacion_hash; reserva lotes exactos sobre cotización vigente. Misma integración/clave/cuerpo recupera; distinto 409. Vencimiento fijo, 20 minutos por defecto (5–60 configurables), también limitado por cambio de fecha del negocio. No descuenta saldo físico.
- GET /integracion-tienda/reservas/{id}: solo integración dueña. POST .../{id}/liberar admite motivo terminal de pago verificado; no deshace una venta consumida.
- POST /integracion-tienda/ventas: {origen,reserva_id,evento_id UUID,pedido_externo UUID,pago:{proveedor:PAYME,ambiente:PRUEBAS,verificado:true,operacion,transaccion,metodo,monto,moneda:PEN}}. Tienda autentica esa afirmación después de verificar el proveedor, nunca el navegador. Clave/evento, pedido externo, transacción e integración se correlacionan; reintento devuelve el mismo acuse. Reserva vencida/importe distinto/conflicto 409, sin otro descuento. Canal TIENDA usa el mismo ticket/stock de Ventas, sin usuario ficticio ni venta_diaria/ML.

## API propia de tienda

PUT /api/v1/integracion/catalogo autenticado con FOODSAVE_PUBLICACION_TOKEN: {origen UUID,version,fecha_generacion,categorias,productos}. Primera entrega vincula origen; versión menor se acusa sin sustituir, misma versión/contenido se recupera y misma versión/datos diferentes 409. Snapshot completo reemplaza la copia comercial de forma atómica; no borra pagos ni historia. Sin precios libres del cliente, SQL cruzado o token de integración en frontend.

GET /api/v1/catalogo y /stock sirve catálogo propio publicado/estado actualizado por HTTP. /pagos/cotizar e inicio Payme usan exclusivamente el origen de ese catálogo, precios canónicos y huella revisada; ejemplo y FoodSave nunca se mezclan. Pagos anteriores conservan su snapshot/origen. Carritos separados por origen.

Pago y estado comercial son distintos: PREPARANDO, RESERVADA, PENDIENTE_VENTA, REGISTRADA, LIBERADA, REVISION_REQUERIDA. La confirmación autenticada conserva evento durable con misma identidad antes de enviar. Error de red conserva PENDIENTE_VENTA; worker o consulta explícita reintentan sin otro pago. Pago tardío tras reserva vencida queda en revisión; no se inventa entrega/reembolso. QR/CIP, abrir/cerrar formulario o callback del navegador no confirman pago. Se mantienen cuatro botones independientes y cambios de método solo antes de registrar una transacción.

LIBERACION_PENDIENTE conserva el reintento de un rechazo/cancelación verificados. RESERVA_VENCIDA es un estado calculado de consulta, sin inventar cancelación Payme ni modificar saldo. Dos transacciones aprobadas para el mismo pago requieren revisión y nunca otro ticket; un acuse tardío conserva esa revisión y el ticket recibido. Reembolso y resolución administrativa de estas excepciones no están implementados.

GET /api/v1/pagos/recuperar permite recuperar una respuesta inicial perdida usando solo la capacidad privada Bearer de checkout. POST /api/v1/pagos/{id}/sincronizar reintenta el mismo evento comercial, sin abrir Payme ni crear pago. Mis compras y pagos conserva estas capacidades en el navegador; no usa cuenta Google obligatoria ni permisos administrativos.

## Stock, promociones y conservación

Reservas activas no vencidas reducen lo vendible para ambos canales y ajustes, pero no el saldo físico. Consumo de reserva y ticket/salidas se confirman juntos; vencimiento libera disponibilidad sin sumar stock. Lotes futuros/vencidos no elegibles según Inventario. Los segmentos de línea conservan precio, cantidad, promoción y lote, sin rebajar todo el carrito. Precio base versionado; cambios no alteran ventas anteriores.

0024 es aditiva sobre 0023: nuevas tablas comerciales y ampliación de cotización/ticket/línea para canal TIENDA. No reescribir migraciones aplicadas. La tienda agrega solo tablas propias, conservando pagos SQLite existentes. Tokens privados distintos por dirección; URLs internas por entorno, sin credenciales Payme en FoodSave. No se autoriza pago de producción, semillas sobre la base habitual ni mensajes Telegram por esta integración. Evidencia real y estado de despliegue en [Cueva](../equipo/avances/cueva.md); este documento no sustituye pruebas de consumidor.

## Configuración y prueba reproducible

Desde la raíz, node scripts/configurar-integracion-tienda.cjs respalda ambos .env, configura TIENDA_INTEGRACION_HABILITADA=1 y TIENDA_MODO=api, conserva Payme/DB/JWT/Google y genera dos Bearer privados distintos de al menos 32 caracteres. Reutiliza valores concordantes; rechaza conflictos sin sobrescribirlos. FoodSave usa TIENDA_INTEGRACION_TOKEN y TIENDA_PUBLICACION_TOKEN; tienda usa respectivamente FOODSAVE_INTEGRACION_TOKEN y FOODSAVE_PUBLICACION_TOKEN. Ninguno es NEXT_PUBLIC. URLs por defecto host.docker.internal:8000/8001. Recrear servicios según [README de tienda](../../tienda/README.md) y aplicar 0024 antes de arrancar el consumidor.

Comercio publica/reintenta cada diez segundos; conciliador de tienda recupera eventos de venta/liberación ya verificados cada diez segundos. No ejecutan automatizaciones, envíos Telegram ni entrenamiento. La consulta visual de stock cada cinco segundos no sustituye la reserva. Si no llega identificador de transacción al navegador, sigue siendo necesario S2S HTTPS registrado con Payme para verificar ese pago abandonado.

En FoodSave, Ventas → Publicar en tienda permite seleccionar fichas/precios existentes y consultar entregas/reservas. Publicar no crea stock: registrar entrada con lotes vigentes en Inventario si no hay unidades vendibles. La instalación comienza sin SKU publicados; no importar automáticamente semillas remotas ni asociar imágenes por coincidencia numérica. Modo ejemplo conserva sus precios/stock/promociones y no genera ventas ni movimientos FoodSave.

Ejemplo de cotización/reserva, con credencial del backend de tienda:

```json
{
  "origen": "00000000-0000-4000-8000-000000000001",
  "lineas": [{"producto_id": 101, "cantidad": 2}]
}
```

Usar el origen recibido en el catálogo propio; agregar clave_idempotencia UUID estable del pago y cotizacion_hash devuelto al crear la reserva. El inicio Payme propio recibe origen_catalogo, cotizacion_hash y total_revisado; los contrasta antes de reservar/preparar nonce. No reutilizar los identificadores de este ejemplo como datos del comercio.

Etapas 1–3 implementadas y consumidor/proveedor comprobados con datos ficticios mediante dos APIs. Esto no certifica una transacción financiera externa ni la habilitación efectiva de Yape/QR para las credenciales del comercio. La instalación local usa las dos APIs reales y publicación vacía; no se ejecutaron pagos ni se cambiaron lotes para demostrarlo. Simuladores, cierre y alimentación de venta_diaria/ML permanecen pendientes.

## Preparación de jornada · 28-10-2026

Prueba de jornada 28/10 sobre instalación actual: doce productos publicados y promoción de croissant aprobada, recibida/cotizada por API sin iniciar pago. Guion ../equipo/guion-prueba-2026-10-28.md. Datos sintéticos puntuales autorizados, sin alterar el contrato HTTP ni las credenciales.
