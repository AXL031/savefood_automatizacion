# Contrato propuesto de ventas operativas e integración de tienda

**26-10-2026 · DISEÑO V1 por fases.** Autor Codex para Axel. La primera fase PRESENCIAL ya existe y tiene su [contrato implementado](contrato-caja-presencial.md), que prevalece para campos y rutas disponibles. Este documento conserva el diseño futuro más amplio; integración de tienda, promociones, cierre y simuladores no están implementados. No usar sus ejemplos futuros como descripción del runtime actual. [Bases y responsabilidades](../equipo/bases-modulo-ventas.md) son parte de esta definición.

## Frontera y compatibilidad

- FoodSave registra un único ticket por venta, con canal PRESENCIAL o TIENDA. Solo sus servicios de Inventario modifican saldos. Tienda independiente intercambia HTTP, sin base, archivos, servicios ni sesión administrativa compartidos.
- `GET /api/v1/ventas`, `GET /ventas/{id}/revisiones` y `PATCH /ventas/{id}` actuales corresponden a agregados históricos; no se sustituyen ni se usan para caja. El prefijo nuevo `/ventas/tickets` deberá registrarse antes de rutas históricas dinámicas `/{id}` o desambiguarse, con prueba de compatibilidad de ambas.
- Primera entrega futura: cotización/registro presencial, consulta y anulación limitada. Publicación a tienda, reserva online, recepción de eventos, cierre y adaptación ML serán entregas posteriores. Ninguna se implementa en este corte documental.
- Sobre: `{"datos": ...}`; errores `{"error":{"codigo":"...","mensaje":"...","detalles":[]}}`. Instantes ISO 8601 con zona (UTC en respuestas); fecha local y zona derivadas por FoodSave. Dinero decimal como cadena con dos posiciones, PEN, cantidades enteras positivas.
- Cantidad máxima propuesta: 100 líneas y 1000 unidades por línea; IDs positivos únicos por producto, campos adicionales rechazados y paginación `limite` 1–100 (25 por defecto), `desplazamiento` >= 0. Importe máximo propuesto por ticket: PEN 999999.99. Límites a confirmar en revisión antes de implementar.

## Permisos y rutas propuestas de FoodSave

| Método y ruta bajo `/api/v1` | Acceso propuesto | Respuesta y significado |
|---|---|---|
| `POST /ventas/cotizaciones` | Operador/Administrador | 201 con cotización presencial guardada, precios/versiones y vencimiento; no reserva ni vende |
| `POST /ventas/tickets` | Operador/Administrador | 201 con ticket CONFIRMADA y salidas locales confirmadas; canal fijo PRESENCIAL |
| `GET /ventas/tickets` | Operador/Administrador | 200, filtros `desde`, `hasta` inclusivos, `canal`, `estado`, `venta_externa_id`, `producto_id`; `metadatos.total` |
| `GET /ventas/tickets/{ticket_id}` | Operador/Administrador | 200 con líneas, precios, canal, referencias a movimientos y auditoría; 404 si no existe |
| `POST /ventas/tickets/{ticket_id}/anular` | Administrador | 200 con anulación y compensación auditadas, o conflicto; nunca borra ni reembolsa |
| `POST /integraciones/tiendas/ventas` | Credencial backend de tienda, permiso `ventas:enviar` | 202 con recepción durable RECIBIDA; no acredita ticket ni descuento todavía |
| `GET /integraciones/tiendas/ventas/{venta_externa_id}` | Misma integración, `ventas:consultar` | 200 con recepción/ticket o motivo de revisión; 404 si nunca se recibió |
| `GET /integraciones/tiendas/publicaciones` | Integración, `catalogo:leer` | 200 con versiones comerciales completas para carga inicial/reconciliación; no acceso a lotes ni métricas |

No se propone un endpoint público que acepte un precio libre, un usuario libre o una bandera «pago realizado» del navegador. El backend receptor determina integración/canal/instalación a partir de la credencial. La credencial específica de integración debe estar limitada a una tienda y a esos permisos; no usar el JWT de un administrador, Google, tokens de Payme ni `JWT_SECRET` compartido. Credenciales solo servidor a servidor; HTTPS fuera de localhost de pruebas. Emisión/rotación/revocación se entregarán con la integración por Cueva y Rojas, no como bypass de permisos.

La alimentación de productos/promociones se realiza por **push** desde FoodSave al receptor de tienda definido abajo. GET publicaciones es recuperación y carga inicial, no un cambio del sentido de autoridad pedido por Axel. En carga inicial se fija un cursor/snapshot estable y después se entregan eventos posteriores para no perder cambios entre páginas.

## Cotización y venta presencial

Solicitud propuesta a `POST /ventas/cotizaciones`:

```json
{
  "clave_idempotencia": "caja-20261026-cotizacion-001",
  "lineas": [
    {"producto_id": 10, "cantidad": 2},
    {"producto_id": 11, "cantidad": 1}
  ]
}
```

Respuesta ilustrativa, IDs e importes ficticios:

```json
{
  "datos": {
    "id": "cot-presencial-001",
    "canal": "PRESENCIAL",
    "moneda": "PEN",
    "vence_en": "2026-10-26T15:05:00Z",
    "lineas": [
      {"producto_id": 10, "cantidad": 2, "version_precio": 3, "segmentos": [{"cantidad": 2, "precio_base": "5.00", "precio_final": "5.00", "promocion_id": null, "version_promocion": null}], "bruto": "10.00", "descuento": "0.00", "total": "10.00"},
      {"producto_id": 11, "cantidad": 1, "version_precio": 4, "segmentos": [{"cantidad": 1, "precio_base": "8.00", "precio_final": "6.00", "promocion_id": 50, "version_promocion": 1}], "bruto": "8.00", "descuento": "2.00", "total": "6.00"}
    ],
    "bruto": "18.00",
    "descuento": "2.00",
    "total": "16.00"
  }
}
```

Cotización presencial propuesta con vigencia máxima de cinco minutos; se revalida igualmente al confirmar. No garantiza stock durante esa espera. Se rechaza una identidad que use cotización ajena o de otro canal. Los segmentos indican exactamente las unidades con/sin promoción; no se acepta un descuento manual enviado por el operador. FoodSave guarda sus precios/versiones y obtiene las cantidades de esa cotización, no de un total editable del navegador.

Solicitud propuesta a `POST /ventas/tickets`:

```json
{
  "clave_idempotencia": "caja-20261026-venta-001",
  "cotizacion_id": "cot-presencial-001",
  "total_revisado": "16.00",
  "cobro_presencial": {"medio": "EFECTIVO", "importe_recibido": "20.00"}
}
```

`cobro_presencial` es declaración del operador, no procesamiento ni certificación bancaria. Medios iniciales propuestos: EFECTIVO, TARJETA, YAPE, QR y PAGOEFECTIVO; excepto efectivo, `importe_recibido` debe igualar el total y solo se guarda una referencia comercial opcional, sin datos de tarjeta. Efectivo exige recibido >= total y calcula vuelto (`4.00` en este ejemplo). Una sola forma de cobro por venta; cobro dividido, crédito y pagos reales quedan fuera de esta base.

Respuesta 201 propuesta:

```json
{
  "datos": {
    "id": 101,
    "numero": "V-00000101",
    "canal": "PRESENCIAL",
    "estado": "CONFIRMADA",
    "vendida_en": "2026-10-26T15:00:30Z",
    "registrada_en": "2026-10-26T15:00:30Z",
    "fecha_local": "2026-10-26",
    "zona_horaria": "America/Lima",
    "moneda": "PEN",
    "total": "16.00",
    "vuelto": "4.00",
    "usuario_id": 7,
    "movimiento_ids": [201, 202]
  }
}
```

El detalle completo incluye las líneas de la cotización y las asignaciones reales de lote; no depende de los precios vigentes al consultarlo. La ruta solo responde confirmado después del commit local. El número es referencia interna, no comprobante fiscal. No se pide Gmail, identidad nominal del comprador ni una orden de tienda para esta operación presencial.

Anulación propuesta: `{"clave_idempotencia":"anular-101","motivo":"Operación de caja registrada por error","mercancia_no_entregada":true}`. Permite una compensación completa, no devolución parcial. Administrador confirma el hecho; si es una venta de tienda, debe aportar además `conciliacion_pago_referencia`, vinculada a evidencia administrativa verificable, nunca una bandera que simule reembolso. Ese proceso de conciliación debe implementarse antes de permitir anular ventas pagadas de tienda. No se implementa anulación por llamada automática del integrador ni reembolso Payme. Lotes vencidos conservan su condición al compensar. Repetir misma solicitud devuelve la anulación existente; cambiar motivo/cuerpo bajo la misma clave da conflicto.

## Idempotencia y errores

`clave_idempotencia`: 8–80 caracteres `[A-Za-z0-9._:-]`. Unicidad por identidad autenticada y tipo de operación, con huella canónica de contenido. No incluir valores derivados como la hora del servidor en esa huella. Cotización y venta usan claves diferentes. Respuesta de recuperación: 200 con el recurso original; el cliente no vuelve a cobrar ni cambia la clave para resolver un timeout.

Además, una cotización presencial solo puede originar un ticket, aunque llegue otra clave. Para tienda son únicos `(integracion_id, evento_id)` y `(integracion_id, venta_externa_id)`: incluso si se cambia el evento/clave, igual venta externa devuelve su recepción/ticket; otro contenido comercial con esa referencia se rechaza. La huella comercial de esa venta excluye `evento_id` y tiempos de recepción generados por FoodSave; incluye instante de venta, cotización/reserva, líneas normalizadas por producto e importes/referencia de pago. Conservar las identidades durante toda la vida del ticket; no vencerlas dejando que un reenvío antiguo vuelva a vender.

| HTTP/código propuesto | Situación y efecto |
|---|---|
| 401 / 403 | Identidad ausente, permiso incorrecto o acceso a recurso de otra integración; sin efectos de venta |
| 404 `RECURSO_NO_ENCONTRADO` | Producto, ticket, cotización o referencia de venta inexistente |
| 409 `CLAVE_REUTILIZADA` | Misma identidad/clave con otro contenido |
| 409 `VENTA_EXTERNA_EN_CONFLICTO` | Referencia comercial ya recibida con otro contenido; no crea otra venta |
| 409 `COTIZACION_VENCIDA` / `COTIZACION_CAMBIO` | Revisar precios/vigencia/stock antes de confirmar; sin ticket parcial |
| 409 `STOCK_INSUFICIENTE` / `STOCK_DESCONOCIDO` | Venta presencial rechazada sin ticket confirmado ni movimientos |
| 409 `PRODUCTO_NO_VENDIBLE` / `PRECIO_NO_DISPONIBLE` | Inactivo, precio sin configurar o publicación requerida ausente |
| 409 `ANULACION_NO_PERMITIDA` | Mercancía entregada, pago de tienda sin conciliar u otra condición incumplida |
| 422 `VENTA_INVALIDA` | Tipo, cantidad, importe, línea duplicada o moneda inválidos; validación sin efectos de venta |
| 503 `SERVICIO_NO_DISPONIBLE` | No se puede confirmar/consultar el resultado; conservar clave e identificar el estado antes de repetir |

Error comercial de una venta de tienda **ya recibida** no elimina el recibo ni produce un 409 ambiguo después del cobro: el recurso pasa a PENDIENTE_REVISION con `motivo_codigo`. Un 401/403/422 o conflicto de identidad previo a recepción significa que el evento no quedó aceptado con ese cuerpo; la tienda conserva su copia durable y corrige/consulta antes de reenviar.

## FoodSave → tienda: productos y promociones

**Fase posterior.** Receptor propuesto en el proyecto tienda: `POST /api/v1/integracion-foodsave/eventos`, servidor a servidor. FoodSave entrega una proyección pública completa del recurso, no filas privadas ni parches que dependan de un orden de llegada implícito.

Ejemplo de publicación de producto:

```json
{
  "evento_id": "catalogo-producto-10-v3",
  "version_contrato": 1,
  "tipo": "PRODUCTO_PUBLICADO",
  "recurso_id": "10",
  "version_recurso": 3,
  "ocurrido_en": "2026-10-26T14:00:00Z",
  "datos": {"producto_id": 10, "codigo": "PAN-010", "nombre": "Pan de ejemplo", "moneda": "PEN", "precio": "5.00", "version_precio": 3, "publicado": true, "estado_stock": "DISPONIBLE"}
}
```

Eventos V1 propuestos: `PRODUCTO_PUBLICADO`, `PRODUCTO_RETIRADO`, `PROMOCION_PUBLICADA`, `PROMOCION_RETIRADA`. Actualización usa el mismo tipo con una versión de recurso mayor. Producto retirado conserva ID y `publicado=false`; no borra ventas previas. Los eventos comerciales no exponen saldo exacto, lotes, proveedores ni datos de entrenamiento.

`PROMOCION_PUBLICADA.datos` contendrá `promocion_id`, `producto_id`, `version_producto_requerida`, `estado="APROBADA"`, `canales`, `precio_promocional`, `vigente_desde`, `vigente_hasta` y `alcance="UNIDADES_ELEGIBLES"`. Moneda del producto; vigencia en instantes UTC, inicio incluido y fin excluido. La asignación real por lote se resuelve en FoodSave: la tienda muestra «desde» cuando la cotización pueda mezclar precios. Una sugerencia aún no aprobada nunca genera este evento.

El receptor guarda recurso + ID/huella de evento juntos. Responde 200 con `{"datos":{"evento_id":"catalogo-producto-10-v3","estado":"APLICADO","version_recurso":3}}`. Estados de acuse: APLICADO, YA_APLICADO, OBSOLETO o PENDIENTE_DEPENDENCIA. Solo los dos primeros confirman esa versión aplicada; OBSOLETO informa la versión superior que se conserva. PENDIENTE_DEPENDENCIA conserva la entrega recibida pero exige consulta/reconciliación antes de declararla publicada. Igual ID con otro contenido da 409; contrato desconocido da 422, sin aplicar.

El estado COMPLETADA de un worker no sustituye el acuse del receptor. Cada destino tiene entrega/intentos propios; reenvío conserva `evento_id`. Caída después de persistir y antes del acuse se recupera sin duplicar. Promoción sin producto requerido queda oculta; sin aprobación, fuera de vigencia o retirada no se aplica aunque el catálogo local esté atrasado. Cotizar y reservar vuelve a validar en FoodSave.

## Tienda → FoodSave: venta y acuse

**Fase posterior, bloqueada hasta cerrar cotización/reserva y conciliación.** El backend de tienda envía la operación una vez que verifica el resultado de pago con su propio backend. El contrato de reserva y sus endpoints aún deben completarse con Rojas y Vera; la presencia de `reserva_id` en este ejemplo no declara esa API disponible.

Ejemplo de evento (ficticio; referencias a cotización/reserva inexistentes):

```json
{
  "version_contrato": 1,
  "evento_id": "evento-venta-tienda-00042",
  "venta_externa_id": "pedido-tienda-00042",
  "vendida_en": "2026-10-26T15:10:00Z",
  "cotizacion_id": "cot-tienda-00042",
  "reserva_id": "reserva-tienda-00042",
  "moneda": "PEN",
  "total": "10.00",
  "lineas": [{"producto_id": 10, "cantidad": 2}],
  "pago": {"estado_verificado": "CONFIRMADO", "referencia": "pago-tienda-00042", "medio": "TARJETA"}
}
```

FoodSave contrasta integración, cotización/reserva, cantidades, precio, moneda y referencia comercial; el contenido recibido no sustituye sus registros. No se admiten IDs de productos propios de tienda sin mapeo explícito a los IDs publicados por FoodSave. El ambiente y la autorización de integración se configuran en servidor: un campo del body no permite convertir pagos de ejemplo/sandbox en ventas habituales. Pruebas de este contrato usarán una instalación aislada; los pagos actuales del catálogo de ejemplo siguen sin producir ventas reales.

Respuesta inicial propuesta:

```json
{
  "datos": {
    "recepcion_id": "rec-00042",
    "venta_externa_id": "pedido-tienda-00042",
    "estado": "RECIBIDA",
    "ticket_id": null,
    "consulta": "/api/v1/integraciones/tiendas/ventas/pedido-tienda-00042"
  }
}
```

El procesador local aplica el evento idempotentemente. En una misma transacción cambia a APLICADA, crea ticket con canal TIENDA, consume la reserva y registra la salida. Consulta devuelve 200 con `estado`, `ticket_id`, `registrada_en`, `vendida_en`, `motivo_codigo` y `motivo` (null cuando no corresponda).

Sin reserva válida, pago tardío, día ya cerrado, datos comerciales inconsistentes o desorden temporal incompatible con el inventario: PENDIENTE_REVISION, sin ticket confirmado ni descuento ficticio. Se conserva el evento y la referencia para resolverlo; la tienda muestra venta pendiente de sincronización y no vuelve a cobrar. Una futura acción administrativa de conciliación deberá conservar esa misma identidad, documentar el resultado y resolver el evento; no hay endpoint de forzar/reembolso en estas bases.

Si FoodSave no está accesible, la tienda conserva el evento en su propia cola y reintenta con el mismo ID. Si el pago no está confirmado, no envía venta confirmada. Pago fallido/pendiente y liberación de reserva son otro flujo futuro; no descontar stock por iniciar checkout, abrir QR/Yape o recibir un callback del navegador.

## Ampliación propuesta: contexto de los dos simuladores y cierre

**26-10-2026 · Solo propuesta, sin rutas ni campos nuevos implementados.** El [plan de dos simuladores](../equipo/plan-ventas-vivo-simulacion.md#propuesta-vigente--26-10-2026--dos-simuladores-para-la-exposición) requiere un simulador iniciado desde Ventas y otro desde tienda; podrán operar solos o coordinados. Cada backend conserva sus eventos; la tienda usa los contratos HTTP de publicación/reserva/venta/acuse y no comparte tablas o servicios con FoodSave.

La futura sesión contendrá `sesion_simulacion_id`, fecha D, canales incluidos, semillas, configuración/instantánea, duración y versión/estado del reloj. Cada canal mantendrá cursor, IDs de evento y manifiesto final; el cierre verificará qué se emitió y qué se aplicó. La preparación de una sesión no agenda ni registra una venta por sí sola. Pausa/reanudación y fin de emisión se coordinan por API con acuse; cerrar con un canal incluido desconectado o eventos sin conciliar queda pendiente.

La identidad/configuración de servidor de la instalación de prueba autoriza el contexto de escenario. Un campo, query o header libre del cliente no activa simulación ni admite pagos simulados en la instalación habitual. En esa instalación aislada, `vendida_en` y vigencias comerciales se obtienen del reloj de escenario compartido, `fecha_local` se deriva de él y `registrada_en`/auditoría/leases siguen usando tiempo real. La excepción al reloj de servidor presencial se limita a ese contexto validado, no permite retrofechar ventas habituales. La tienda consulta el reloj por HTTP, no lo modifica por su cuenta.

Las identidades de simulación serán estables por sesión/canal/posición. Reintento mantiene la misma identidad de venta/evento; una sesión nueva usa otras identidades. El backend de tienda podrá usar un adaptador de pagos de prueba explícito solo en ese entorno, con estado de demostración visible. No se transmite un pago real ni se acelera Payme externo; su sandbox seguirá teniendo una prueba separada de la jornada sintética.

Al cierre, las proyecciones diarias se actualizan solo en el escenario aislado y con revisión/cobertura. Las operaciones de cierre, evaluación, entrenamiento y pronóstico siguiente tendrán claves por sesión + versión de cierre + fase/configuración, además de IDs de modelo/corrida. Repetir una petición no publica dos veces ni entrena otra vez el mismo cierre/configuración. La revisión de cierre por evento tardío produce otra versión y conserva las anteriores; nunca vuelve a descontar el ticket.

Resultado de cierre y tareas ML se consultarán por separado: cierre confirmado; evaluación de P(D) con M0; entrenamiento de M1 con datos hasta D; validación y pronóstico D+1 con M1. Falta de historia, entrenamiento fallido o fase sin terminar no se convierten en éxito. Los contratos de sesión/reloj, reservas de escenario y tareas diarias de ML deben revisarse antes de fijar sus endpoints; esta ampliación no declara disponibles rutas de simulación ni modifica el contrato del artefacto actual. Ver [orden de cierre y condición temporal](../equipo/plan-ventas-vivo-simulacion.md#cierre-del-día-d-y-actualización-de-ml).

## Implementación posterior y pruebas necesarias

Antes de programar: revisar contratos de precios/promoción y salida de lotes con Sanchez/Vera; integrar autenticación técnica y recepción/versiones con Rojas/Cueva; añadir migraciones nuevas desde la cabeza vigente sin modificar las aplicadas. Los modelos lógicos de las [bases](../equipo/bases-modulo-ventas.md#modelo-de-datos-lógico-propuesto) no se añaden al ER físico implementado.

Las pruebas deberán cubrir todos los [criterios de aceptación](../equipo/bases-modulo-ventas.md#aceptación-que-deberá-cubrir-la-implementación), compatibilidad con histórico, rollback común, dos canales concurrentes, precios mixtos por promoción/lote, duplicados con otra clave/evento, pérdida de acuse, eventos obsoletos, reserva vencida tras pago y segregación de pruebas. No se han ejecutado aún por tratarse solo de definición.
