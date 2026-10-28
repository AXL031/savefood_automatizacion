# Bases del módulo de ventas

**Estado vigente · 26-10-2026:** la primera caja PRESENCIAL está implementada por solicitud posterior de Axel. Rige el [contrato de caja disponible](../api/contrato-caja-presencial.md): precios versionados, cotización, ticket, stock y anulación limitada. Tienda, promociones comerciales, simuladores, cierre y ML quedan pendientes. Las notas documentales anteriores se conservan como historial.

**26-10-2026 · Diseño original por fases; primera caja implementada en el corte posterior indicado arriba.** Solicitud de Axel: definir el módulo para registrar ventas presenciales y preparar la futura integración con la tienda independiente. Autor: Codex para Axel, coordinación documental. Ventas y productos: Edu Sanchez; inventario y promociones: Leonardo Vera; integración del proyecto tienda: Max Rojas; identidad, infraestructura y automatizaciones: Axel Cueva; lectura futura para ML: Kevin Bohorquez. No se atribuye implementación ni aprobación técnica de estas bases a los integrantes.

## Alcance de esta definición

Esta sección conserva el planteamiento original previo al primer corte de caja. Los archivos de carga, agregados diarios y revisiones existentes son antecedentes técnicos; no constituyen una caja ni una integración de ventas de tienda. Esta entrega define comportamiento, responsabilidades, contratos propuestos y criterios de aceptación. No añade código de ejecución, pantallas, endpoints, migraciones ni configuración.

La primera entrega funcional futura permitirá registrar una venta presencial desde FoodSave y consultar su detalle e historial. La integración con tienda será una fase posterior: FoodSave enviará productos y promociones aprobadas por API HTTP y recibirá las ventas de la tienda por API. Los dos canales usarán un mismo servicio de ventas y las mismas reglas de inventario.

Esto amplía como **diseño futuro** la exclusión de ventas de tienda en el módulo de Ventas del contrato anterior. No convierte los pagos de ejemplo de Payme sandbox en ventas del comercio, ni habilita pagos reales. Incorporar tickets al histórico de ML será otra entrega con cierre y cobertura validados; no ocurrirá por recibir un ticket.

## Autoridad de cada sistema y recorrido

| Dato o decisión | Fuente responsable | Consumidor |
|---|---|---|
| Identidad, nombre, precio vigente, publicación y versión de producto | FoodSave / Productos | Ventas presencial y copia de catálogo de tienda |
| Aprobación, vigencia y alcance de promoción | FoodSave / Promociones | Cotización y copia comercial de tienda |
| Saldo por lote, reservas futuras, vencimiento y movimientos | FoodSave / Inventario | Ambos canales mediante servicios de FoodSave |
| Operación de pago y comprobación con Payme sandbox | Backend de tienda, según ADR-010 | Integración envía referencia/estado verificado, nunca credenciales o datos de tarjeta |
| Ticket confirmado, cantidades, precios aplicados y canal | FoodSave / Ventas | Pantalla administrativa y acuse a tienda |
| Pedido del cliente, datos de entrega y experiencia de checkout | Proyecto `tienda/` | Conserva el ID del ticket FoodSave; no duplica el descuento de stock |
| Día observado y fuente admitida para ML | Ventas con validación de Bohorquez | Adaptador histórico futuro |

Recorrido presencial: **seleccionar productos → cotizar → revisar → registrar venta → ticket y salida de inventario confirmados juntos**. No requiere cuenta Google ni conexión con tienda.

Recorrido futuro de integración: **FoodSave publica catálogo/promociones → tienda confirma recepción → tienda solicita cotización/reserva → verifica su pago → envía evento de venta → FoodSave valida y registra el ticket → devuelve el acuse**. El carrito y la creación de una operación de pago no confirman una venta.

La tienda solo se comunica con FoodSave por HTTP. No importa módulos, monta archivos ni consulta su PostgreSQL. El navegador de tienda no posee la credencial del integrador ni envía directamente una orden administrativa de descuento. Se mantiene [ADR-010](../arquitectura/decisiones/ADR-010-tienda-independiente-payme.md).

## Primera versión del módulo

- Lista de ventas con fecha, número, canal, estado, productos/unidades y total; filtros por rango, canal y estado, búsqueda por referencia externa y paginación.
- Acción **Registrar venta presencial**: selección de productos, cantidad, cotización, importe recibido/declaración del medio de pago y revisión antes de confirmar. Sin cliente nominal obligatorio; se identifica al usuario que la registró.
- Detalle con líneas, precios/descuentos conservados, fecha del negocio, instante de registro, canal, usuario o integración, referencias de inventario y trazabilidad. Una consulta no genera otra venta.
- Resumen de unidades e importes confirmados, anulaciones y totales netos por canal; no presentarlo como cierre contable o conciliación bancaria.
- Anulación administrativa motivada bajo las condiciones de este diseño; no editar ni borrar un ticket confirmado. No confundirla con un reembolso Payme.
- Sección separada **Histórico importado** para la funcionalidad técnica existente. Corregir un agregado no simula una venta presencial ni modifica stock.

Operador podrá registrar y consultar ventas presenciales; Administrador, además, mantener precios/publicación, aprobar promociones y anular. El integrador solo tendrá permisos de los contratos de tienda, nunca el rol de Administrador. Permisos pendientes de implementación.

## Modelo de datos lógico propuesto

Nombres y relaciones para preparar la implementación; **no son tablas creadas ni un ER físico aplicado**. IDs, longitudes y migraciones definitivas se revisarán con los responsables antes de programar.

| Concepto | Información mínima y restricción |
|---|---|
| `ticket_venta` | ID, número local único, canal `PRESENCIAL`/`TIENDA`, estado, instante de venta UTC, fecha local calculada, zona conservada, moneda, subtotal/descuento/total, usuario o integración, clave y huella, referencia externa opcional. Canal tienda exige integración y `venta_externa_id` únicos como par. |
| `linea_ticket_venta` | Producto FoodSave, cantidad entera positiva, nombre/código conservados, versión del precio, segmentos con precio base/final y promoción aplicada. Total de línea exacto. No se recalcula el pasado al cambiar el catálogo. |
| `salida_lote_venta` | Línea, lote, cantidad y movimiento de inventario. Puede haber varios lotes por línea. Una asignación no se vuelve a aplicar al reintentar. La suma asignada debe cubrir exactamente la cantidad de la línea. |
| `cotizacion_venta` | ID, identidad solicitante, canal, líneas/importes/versiones conservados y vencimiento; no descuenta stock. La presencial no reserva; una cotización online deberá vincular su reserva futura. |
| `anulacion_venta` | Una por ticket, clave/huella, administrador, motivo, instante, comprobación de mercancía no entregada y movimientos compensatorios. Conservar ticket y salidas originales. |
| `precio_producto_version` | Producto, precio final en PEN, vigencia, versión y actor. FoodSave es la autoridad del precio; el modelo actual de producto no contiene este contrato comercial. |
| `publicacion_producto_version` | Producto, datos comerciales autorizados, versión y estado publicado/retirado. Desactivar conserva su identidad e historial. |
| `promocion_publicada_version` | Referencia a sugerencia/aprobación, producto y alcance por lote si corresponde, precio/regla, inicio/fin, canales y versión. Sugerencia y promoción publicada son conceptos distintos. |
| `evento_salida_comercial` | ID, tipo, recurso/versión, contenido público conservado, destino, intentos, próximo intento y acuse. Se guarda con el cambio de publicación en una misma transacción de FoodSave. |
| `evento_entrada_venta` | Integración, evento y venta externa, huella, carga comercial mínima, estado, ticket resultante o motivo de revisión. Único por integración/evento; conservar evidencia de recepciones repetidas. |
| `jornada_venta` / cobertura | Futura: fecha, estado abierto/cerrado, procedencias por producto/canal, observación explícita, versiones y cierre. Necesaria antes de alimentar ML; no parte de la primera caja. |

La cotización/reserva online será un recurso futuro de Inventario/comercial con ID, líneas y precios congelados, cantidad reservada por lote y vencimiento. Debe definirse y probarse antes de integrar un checkout con pago; no se sustituye por la disponibilidad visual del catálogo.

## Reglas de confirmación

1. Una venta representa **productos terminados vendidos**, no compra a proveedor, fabricación ni consumo de ingredientes. Solo Inventario modifica saldos mediante su interfaz pública.
2. Producto activo, precio vigente y stock vendible conocido son requisitos. Cantidad entera positiva, al menos una línea y sin IDs de producto duplicados; fusionar cantidades en la interfaz antes de cotizar. Descuento manual libre, productos inventados y saldo negativo quedan fuera de la primera versión.
3. Cotización presencial calculada por FoodSave; al confirmar se revalidan versión, precio, promoción y stock. Si cambió el resultado, responder conflicto y solicitar revisión, sin aceptar silenciosamente otro importe ni una venta parcial.
4. Dinero en PEN, cadenas decimales de dos posiciones y cálculo Decimal exacto. Precio final de venta, sin desglose fiscal ni facturación en este corte. Por segmento de unidades al mismo precio: bruto = cantidad × precio base, neto = cantidad × precio final, descuento = bruto − neto; total de línea = suma de segmentos y total del ticket = suma de líneas. Si una promoción afecta solo a un lote, separar segmentos, no descontar todas las unidades del producto.
5. Selección FEFO: fecha límite de venta más próxima, después caducidad conocida más próxima y luego ID; bloquear los lotes candidatos en orden global estable antes de asignar. Disponibilidad = saldo vendible menos reservas online activas cuando existan. Dos canales compiten por ese mismo disponible.
6. Política propuesta coherente con el contrato de tienda: fecha límite de venta conocida y no anterior a la fecha efectiva; caducidad nula permitida con advertencia, conocida y vencida excluida. Stock sin observación se rechaza como desconocido, no se convierte en cero. La implementación la entrega Vera.
7. Un servicio `registrar_ticket(sesion, entrada, contexto)` de Ventas orquesta el cálculo comercial y `retirar_productos_por_venta(...)` de Inventario sin commits separados. En una transacción: ticket, líneas, asignaciones, movimientos y resultado idempotente. Un fallo revierte todos los efectos locales. Los nombres son interfaces propuestas, no funciones disponibles.
8. Clave igual + identidad autenticada + solicitud igual recupera el resultado. Clave reutilizada con otro contenido da conflicto. En tienda, cambiar el ID del evento o la clave no permite registrar dos veces la misma `venta_externa_id`. Concurrencia se resuelve también con restricciones persistidas, no con una bandera del navegador.
9. La fecha local se deriva del instante de venta y la zona del negocio, no de un campo editable de fecha. Presencial usa el reloj del servidor; los eventos de tienda conservarán su instante comercial, su recepción y su posible demora. Primera caja no permite retrofechar stock: los saldos actuales no reconstruyen existencias históricas.
10. Importar/corregir ventas históricas conserva su contrato y no descuenta stock. No usar esos endpoints como atajo para registrar un ticket.

## Estados y anulación

| Entidad | Estados propuestos | Significado |
|---|---|---|
| Ticket | `CONFIRMADA` → `ANULADA` | Solo existe como confirmado tras el commit; rechazado no equivale a vendido. Nunca se borra. |
| Recepción de tienda | `RECIBIDA` → `APLICADA` o `PENDIENTE_REVISION` | APLICADA exige un ticket. RECIBIDA es acuse durable, no stock descontado. Revisión conserva el motivo; no se pierde una venta ya pagada externamente. |
| Publicación a tienda | `PENDIENTE`, `EN_ENTREGA`, `CONFIRMADA`, `REINTENTANDO`, `REQUIERE_ATENCION` | Un acuse identifica el ID/versión persistidos en la tienda; timeout puede recuperarse reenviando el mismo evento. |
| Pago | Propiedad de tienda | Su confirmación/verificación no sustituye la aceptación de la venta por FoodSave. |

Anulación inicial: solo Administrador, motivo, clave y constancia de que la mercancía no se entregó. Ventas e Inventario guardan anulación, compensación a los lotes de origen y nuevo estado juntos, una sola vez. La compensación no vuelve vendible un lote vencido ni modifica su caducidad. Si la devolución/mercancía no puede comprobarse o ya fue entregada, se requiere otro flujo futuro; no se reintegra automáticamente por una llamada de tienda. No se inicia un reembolso, ni se borra la referencia del pago. Para venta de tienda con pago confirmado, la anulación exige conciliación administrativa de ese pago y evidencia; no hay anulación online automática en la primera fase.

## Productos y promociones enviados por API

FoodSave será emisor y la tienda receptor HTTP. El cambio comercial aprobado guarda una versión y un evento de salida; un proceso posterior lo entrega. Fallar la conexión no revierte la aprobación local, pero deja la publicación sin confirmar. La pantalla administrativa deberá mostrar esa diferencia.

Cada evento contiene `evento_id`, `tipo`, `version_contrato`, `recurso_id`, `version_recurso`, `ocurrido_en` y el estado público completo del recurso. La tienda guarda su copia y el evento recibido en su propia transacción y devuelve acuse. Reenvío de igual evento/contenido no duplica; igual ID con otro contenido es conflicto; una versión antigua nunca sobrescribe una nueva. Los retiros y las expiraciones conservan identidad. Una promoción vencida deja de aplicarse por su fecha aunque todavía no llegue el evento de retiro.

No enviar todas las sugerencias del motor: solo promociones aprobadas y vigentes, con producto/precio publicados y alcance verificable. La tienda puede mostrarlas, pero FoodSave revalida su aplicación al cotizar/reservar. Precio promocional sin vigencia/aprobación es inválido.

La entrega será recuperable con reintentos acotados, acuses y consulta de estado. Hace falta una carga inicial de versiones completas y reconciliación por API para detectar faltantes; el orden entre productos y promociones se expresa con la versión de producto requerida. Si aún falta, la tienda conserva la promoción pendiente y no la ofrece. El protocolo detallado y la reserva/pago se implementarán en la fase de integración, no al construir la primera caja.

## Ventas recibidas desde la tienda

El backend de tienda envía la venta verificada con su ID externo, ID de evento, referencia comercial de pago, cotización/reserva y líneas. FoodSave no recibe PAN, CVV, token, nonce, credenciales Payme, datos de entrega ni datos personales que no necesite Ventas. La identidad del canal se obtiene de la credencial autenticada, no de un `canal` libre del body.

La recepción durable permite distinguir mensaje recibido y venta aplicada. Ticket, salida de lotes y estado APLICADA del evento se confirman juntos. Mientras no esté aplicado, el pedido de tienda muestra sincronización pendiente y puede consultar el resultado por ID externo. Una respuesta perdida se resuelve consultando o reenviando la misma identidad, sin volver a cobrar.

**No hay transacción distribuida con Payme.** Antes de conectar un pago se necesita reserva compartida en FoodSave, expiración y política para pagos tardíos/asíncronos. Si el pago se confirma pero la reserva venció, no se crea un ticket ficticio ni se pierde la referencia: queda PENDIENTE_REVISION para conciliar, cumplir o resolver el pago en tienda. No se activa checkout conectado hasta cerrar y probar ese caso, incluidas demoras de Yape/QR/PagoEfectivo. Los pagos sandbox sobre catálogo de ejemplo continúan excluidos del inventario y de las ventas del comercio.

## Histórico, cierre y predicción

El listado operativo podrá sumar ambos canales sin mezclarlo con el CSV. No se escriben agregados de ML en cada ticket: una jornada abierta no es una observación diaria completa. El cierre y su adaptador constituirán una fase independiente.

Base propuesta para esa fase: una única procedencia autoritativa por producto/fecha (`IMPORTADA` u `OPERATIVA`), sin sumar ambas para la misma clave. Un día operativo se obtiene de tickets confirmados menos anulaciones de los canales incluidos; las entradas pendientes de revisión impiden declarar cobertura completa de tienda. Cero solo con observación explícita del producto/día, no por ausencia de tickets. Un cierre crea una versión conservada y una corrección tardía crea otra, sin modificar los snapshots de evaluaciones previas. Hasta implementarlo y validarlo, las funciones históricas y el modelo mantienen sus entradas actuales y su partición temporal; recibir ventas recientes no habilita inferencia para hoy.

No mezclar operaciones sandbox o sesiones de simulación con el histórico habitual. La ampliación de [dos simuladores de jornada](plan-ventas-vivo-simulacion.md#propuesta-vigente--26-10-2026--dos-simuladores-para-la-exposición) permite, como propuesta, cerrar ambos canales y actualizar ventas/modelo/pronóstico **en la instalación aislada de demostración**. No es condición de la primera caja ni autorización para escribir datos ficticios en la instalación habitual.

## Propuesta adicional: dos simuladores y cierre de jornada

Axel añade dos simuladores: uno controlado desde este módulo para ventas PRESENCIAL y otro desde el proyecto tienda para compras TIENDA. Se podrán usar individualmente o juntos sobre una sesión/fecha y reloj coordinados por API, manteniendo agendas y almacenamiento propios. La jornada objetivo durará pocos minutos (ejemplo inicial: doce horas en 300 s). Los backends procesan eventos durables; las pantallas solo controlan y muestran ventas/stock/compras de tienda/catálogo actualizados.

El cierre conjunto deja de emitir, espera y concilia eventos de ambos canales, consolida las ventas D con cobertura/versiones y evalúa el pronóstico P(D) guardado antes de simular. Después se propone entrenar M1 incorporando el día cerrado D y generar un **pronóstico nuevo para D+1** con esa versión. P(D) y M0 permanecen conservados; no se usan las ventas de D para mejorar retroactivamente la predicción que se evalúa para D. Entrenamiento y pronóstico siguiente tienen estados propios, tiempos reales y recuperación; un cierre correcto no equivale a ML terminado.

Este ciclo diario requiere nuevos contratos temporales y tareas de Bohorquez/Cueva, además del cierre de Sanchez; el modelo histórico actual no lo admite por el solo cambio del reloj. La simulación usará datos, inventario, modelos, colas y credenciales de prueba aislados; la tienda tendrá adaptador de pago controlado y visible como simulado. La [propuesta detallada](plan-ventas-vivo-simulacion.md#cierre-del-día-d-y-actualización-de-ml) define orden, aislamiento, visualización, responsables y aceptación. **Solo planteamiento: no hay dos simuladores ni ciclo de cierre/reentrenamiento implementados en esta entrega.**

## Entregas futuras y responsables

| Orden | Entrega | Responsable principal y dependencia | Evidencia mínima |
|---|---|---|---|
| 1 | Revisar estas bases y contratos; catálogo de precios/publicación y servicio de salida por venta | Sanchez con Vera; Cueva coordina | Reglas y funciones públicas acordadas, migraciones aditivas propuestas sin reescribir las aplicadas |
| 2 | Registro presencial, historial y anulación limitada | Sanchez; Inventario por Vera | Ticket y movimiento atómicos, concurrencia/idempotencia, permisos y QA de caja |
| 3 | Publicación comercial aprobada y cola de entrega HTTP | Productos Sanchez, Promociones Vera, infraestructura Cueva | Eventos/versiones/acuses/retiros y reintentos, sin publicar una sugerencia no aprobada |
| 4 | Receptor y copia comercial en el proyecto tienda | Rojas | Consume eventos y carga inicial, ignora versiones obsoletas; sin acceso compartido a datos/servicios |
| 5 | Cotización/reserva, venta entrante y conciliación de pago | Rojas + Sanchez + Vera; identidad Cueva | Doble entrega, último stock, pago tardío y caída tras cobro resueltos, con Payme sandbox |
| 6 | Cierre/cobertura y lectura validada de ML | Sanchez + Bohorquez | No doble conteo importado/operativo ni día abierto tratado como completo |
| 7 | Dos simuladores y ciclo diario de exposición en instalación aislada | Sanchez (módulo), Rojas (tienda), Vera (stock), Bohorquez (modelo), Cueva (reloj/ejecuciones) | Ambos canales en vivo; cierre sin pendientes, evaluación P(D), M1 nuevo y pronóstico D+1 trazables; ver propuesta detallada |

Cada dueño entrega interfaz, API, datos y pruebas de su bloque; esta tabla no traslada toda la integración a Cueva. No se crean tareas externas ni se publica el cambio en esta entrega.

## Aceptación que deberá cubrir la implementación

1. Venta presencial con varios productos confirma precios/total y descuenta solo los lotes asignados; precio ausente o stock insuficiente no deja efectos parciales.
2. Dos ventas del último producto —incluida presencial contra tienda— producen como máximo una salida aceptada para ese disponible; reservas online activas se respetan.
3. Doble clic, respuesta perdida, reentrega del evento y reinicio conservan un ticket y un descuento; nueva clave con misma venta externa tampoco duplica.
4. Un cambio de precio/promoción obliga a revisar la cotización; unidades sin promoción conservan su precio base. Un precio cambiado en el navegador no se acepta.
5. Anular no borra evidencia, compensa solo una vez y no vuelve vendible mercancía vencida; devolución entregada o pago sin conciliar queda fuera del atajo de anulación.
6. FoodSave entrega productos/promociones con versión, retiro y acuse; cortes de conexión y eventos fuera de orden no producen catálogo viejo ni descuentos no aprobados.
7. Un evento válido de tienda conserva recibo aunque la venta requiera revisión; no se acredita pago ni venta por callback del navegador. Sandbox de ejemplo no afecta al comercio.
8. Sin acceso administrativo para el integrador; registro presencial atribuido a usuario; payloads y registros sin secretos de pago ni datos personales de entrega.
9. La fase de cierre distingue abierto/cerrado, importado/operativo, cero/ausencia y corrección posterior. ML solo consume la fuente explícitamente validada.
10. Pantallas de venta/historial manejan vacío, error, permisos, conflicto y recuperación en escritorio/móvil. Ninguna de estas pruebas se declara ejecutada por existir este documento.

Contrato con rutas y ejemplos propuestos: [ventas operativas e integración](../api/contrato-ventas-operativas.md). Registro de la definición y verificaciones documentales: [Cueva](avances/cueva.md).
