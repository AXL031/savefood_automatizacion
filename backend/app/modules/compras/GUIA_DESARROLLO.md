# Guía de desarrollo — Pedidos, aprobación y envío

**Carpeta:** `backend/app/modules/compras`.

**Responsable:** Leonardo Aguirre. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Proveedores, pedidos y Telegram. **Tareas:** L02, L03, L04.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-pedidos.md](../../../../docs/api/contrato-pedidos.md).
- [docs/arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md](../../../../docs/arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Leonardo Aguirre](../../../../docs/equipo/avances/aguirre.md) para el último estado.

## Trabajo en esta carpeta

1. Agrupar necesidades de Max por proveedor y copiar cálculo de conversión/cantidades.
2. Cerrar política de recompra entre planes de una misma fecha con Max antes de habilitar automático.
3. Guardar modo de aprobación y estados; aprobación requiere rol Administrador.
4. Invocar adaptador Telegram desde tarea de dominio y persistir evidencia.
5. Conciliar resultado incierto; no dejar que reintentos genéricos repitan envíos.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `pedido_compra`, `linea_pedido`, `envio_pedido`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Plan/necesidades de Max, ofertas propias y modo de negocio de Axel.
- **Entrega:** Pedidos trazables, estado de aprobación y resultado real del canal.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Repetir plan no duplica pedido; plan nuevo de misma fecha pasa control de recompra.
- Modo manual espera aprobación; automático usa datos/destino validados.
- Timeout después de transmitir queda PENDIENTE_VERIFICACION.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/aguirre.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.

## Paso 6 local · L03 · 30-09-2026

Aprobación/rechazo administrativos con clave idempotente, responsable, nombre y fecha; rechazo motivado de pendiente/bloqueado sin exigir canal. Aprobar exige modo manual, propuesta válida y chat revisado/verificado con credencial vigente. Congela texto/chat/huella y reserva envio_pedido en la misma transacción. Consultas/UI incluyen decisión, destino actual separado de snapshots, mensaje DEMOSTRACIÓN — NO SURTIR e intento/evidencia de Telegram. Aprobar no confirma envío; Beat/worker lo ejecutan y guardan message_id/fecha solo con respuesta válida.

Outbox con lease y token de despacho: revalida antes de transmitir y confirma ENVIANDO antes del efecto externo. Reentrega no vuelve a enviar; timeout, respuesta inválida o worker interrumpido quedan PENDIENTE_VERIFICACION sin retry. Cambiar destino/credencial bloquea antes de red. Ninguna acción mueve stock ni libera por sí sola la reserva de fecha. AUTOMATICO, conciliación y nuevos intentos humanos siguen en paso 7. Migración aditiva 0013; downgrade bloqueado si existen decisiones para no borrar evidencia. Contrato vigente: docs/api/contrato-pedidos.md; prueba test_aprobacion_envio_l03.py. Implementación local por Codex para Axel, responsabilidad de Aguirre, sin commit ni remoto; bot real pendiente del usuario.

## Claridad y flujo completo · 30-09-2026

generar_pedidos(sesion,plan_id,modo_envio=None) permite automático validado sin commit; prepara todos los envíos antes de reservar cualquiera. Sin decisiones APROBAR ficticias; worker autoriza modo conservado y revalida destino/credencial. Actualizar automático bloqueado exige nuevo plan. Protección de recompra y no retry incierto vigentes. Ver corte vigente contrato-pedidos.md.

## Aviso de recompra según estado · 30-09-2026

_conflicto_fecha mantiene RECOMPRA_FECHA/409 y consulta estados de pedidos bajo el bloqueo de fecha. Solo recomienda cancelar si todos son BLOQUEADO/PENDIENTE_APROBACION/RECHAZADO; ENVIADO explica entrega confirmada y otra fecha de escenario, otros estados con envío explican revisión sin cancelación. ESTADOS_CANCELABLES se comparte con cancelar_propuesta para conservar coherencia. No se libera automáticamente una fecha después de transmitir.

## Recuperación L04 · 01-10-2026

Codex para Axel bajo responsabilidad de Aguirre: POST /pedidos/{id}/conciliar registra ENVIADO o NO_ENVIADO con evidencia del último intento incierto; no transmite. POST /pedidos/{id}/reintentar reserva N+1 solo desde FALLIDO y con chat actual revisado/verificado. Conserva texto, plan, cantidades, autorización original e historial. GET incorpora envios/recuperaciones; envio sigue siendo el último. Locks fecha→propuesta→pedido→envío en recuperación/despacho/worker, respuesta tardía obsoleta ignorada. Clave/contenido/actor idempotentes, evidencia chat/message_id única. Usuario Operador consulta; solo Administrador actúa.

Migración aditiva 0014_l04_recuperacion sobre 0013, sin reescribir anteriores; downgrade bloqueado con acciones/reintentos. 57 pruebas PostgreSQL y 7 de migraciones correctas; typecheck/build correctos, API/UI/worker locales actualizados y alembic check sin diferencias. QA visual nuevo no acreditado: navegador integrado rechazó el entorno temporal con ERR_BLOCKED_BY_CLIENT. Pruebas usan transporte falso; no se envió otro Telegram. Contrato vigente: docs/api/contrato-pedidos.md, registro detallado en docs/equipo/avances/aguirre.md. Automático real, promociones y demo conjunta pendientes.

## Dashboard y Reportes de lectura · 01-10-2026

Ampliación expresa: Inicio con ventas diarias, ranking y pedidos; `/informes` con períodos inclusivos, versión del modelo, tablas paginadas, detalle en diálogo y CSV completo del período. [Contrato](../../../../docs/api/contrato-informes.md). Ventas publica `resumen_ventas`/`periodo_ventas`; Compras `resumen_pedidos`/`periodo_propuestas` cuenta pedidos sin multiplicar intentos; K03 admite filtros `desde`/`hasta` opcionales conservando la consulta anterior sin filtros. Informes coordina únicamente interfaces públicas. No migra, entrena, modifica stock ni envía mensajes. Fechas ausentes no se rellenan con cero. Registro/evidencia en Bohorquez y coordinación Cueva.

## Conciliación de cueva

Conciliación 06-10-2026: la FK de decidido_por declara en los modelos el mismo nombre fk_pedido_decidido_por de la migración publicada. No se altera esa revisión ni la evidencia de envíos. La prueba M03 retira las revisiones dependientes en orden antes de comprobar su delta.

## Corte vigente · 11-10-2026 · Flujo y promociones

Codex para Axel implementó configuración reutilizable, comprobación de requisitos por interfaces públicas, calendario histórico diario de 1–31 días, modelo/modo conservados y pausa/cancelación/reprogramación de tareas sin despacho. Promociones tienen regla inmutable versionada, reserva transaccional después de cada ajuste nuevo de producto y evaluación idempotente con snapshot/motivo; API y pantalla reales. Se conserva la propiedad de cada dominio.

[Contrato vigente, APIs y límites](../../../../docs/api/contrato-flujo-promociones.md). Aplicar `0015_flujo_promociones` antes de actualizar API/worker/Beat. El diagnóstico no ejecuta inferencia ni envía mensajes; guardar configuración no agenda. Consultas de tareas/evaluaciones admiten paginación real con total. La pausa no recupera horas perdidas: reprogramar antes de reanudar. Deshabilitar promociones afecta ajustes nuevos; tareas ya reservadas conservan su versión. Hora simulada de evaluación avanza por el tiempo real transcurrido desde el ajuste para comprobar frescura.

Las notas fechadas de cortes anteriores son historial; no usar sus pendientes como estado actual. Pruebas y límites finales en los registros Cueva/Vera/Sanchez, incluyendo PostgreSQL/Redis y Telegram real solo si fueron ejecutados. No confundir fixtures QA con datos de operación.

## Corte solicitado · 14-10-2026

Codex para Axel. Pedidos nuevos incorporan nombre_negocio(sesion), fecha de planificación, proveedor y cantidades. Formato comercial sin rótulos de demostración por solicitud expresa de Axel. Textos ya autorizados conservados; estados, stock, autorización y deduplicación intactos. WhatsApp pendiente: docs/api/configurar-whatsapp.md.


## Recepción y corrección autorizadas · 15-10-2026

Codex para Axel coordina Compras/Inventario/Planificación. Contrato vigente: docs/api/contrato-pedidos.md y frontera de inventario en docs/api/contratos.md. Migración aditiva 0018: corrección enlazada de propuesta bloqueada sin envíos, nuevo plan y modo manual; recepción administrativa parcial/completa sobre pedido ENVIADO, con factor guardado, lotes y movimientos RECEPCION atómicos e idempotentes. UI distingue envío del mensaje y llegada física, muestra pendientes/historial y tabla de cantidades. Inventario etiqueta Recepción y filtra nuevas entradas anteriores a fecha_ingreso. Pruebas test_recepcion_compras.py; CI incluye su corte PostgreSQL. No implementa ventas en vivo ni simulación: solo plan en docs/equipo/plan-ventas-vivo-simulacion.md. Registro transversal y resultados reales en avances/cueva.md.

## Operación integrada · 27-10-2026

Ampliación expresa del usuario, implementada por Codex; responsabilidades conservadas. [Contrato](../../../../docs/api/contrato-operacion-integrada.md) y [guía de reproducción/variables](../../../../docs/operacion-integrada.md). Migración aditiva 0020: producción por tandas, venta interna/tienda con movimientos, respuesta del proveedor de una hora, recepción asistida/avisos y monitor cada diez minutos con aprobación. Código en operaciones y fronteras públicas de inventario/ventas. No hay reposición ni pagos reales automáticos. Docker separado para pruebas; túnel gratuito y Render opcional de pago. Credenciales privadas fuera de Git. Consultar bitácora Cueva para pruebas realmente ejecutadas y límites.
