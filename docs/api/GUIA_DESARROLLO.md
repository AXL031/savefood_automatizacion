# Guía de desarrollo — Catálogo y contratos HTTP

**Carpeta:** `docs/api`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../equipo/responsabilidades.md).
- [Dependencias entre integrantes](../equipo/dependencias.md).
- [Alcance de la demo](../guia-inicio-desarrollo.md).
- [docs/api/rutas-api.md](rutas-api.md).

## Punto de partida

**30-09-2026 · Paso 5: contrato-pedidos.md define configuración cifrada/bot/chat, búsqueda /start, códigos, permisos y límites; rutas-api.md publica rutas reales. Verificación de acceso no acredita entrega. Pasos 6/7 pendientes.**

**Paso 2 local · 30-09-2026:** contratos.md y rutas-api.md documentan /planes y la frontera M02; necesitan migración 0009. Necesidades M03 y compras siguen como diseño pendiente.

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](../equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

**26-10-2026 · Dos simuladores, propuesta adicional:** el [contrato de Ventas](contrato-ventas-operativas.md#ampliación-propuesta-contexto-de-los-dos-simuladores-y-cierre) incorpora contexto aislado de sesión/reloj, agendas por canal, manifiestos de cierre y claves por fase/revisión. Todavía no fija ni implementa endpoints de control o reentrenamiento diario; su definición depende de Sanchez/Vera/Rojas/Bohorquez/Cueva. [Propuesta de exposición](../equipo/plan-ventas-vivo-simulacion.md#propuesta-vigente--26-10-2026--dos-simuladores-para-la-exposición).

**26-10-2026 · Contrato propuesto de Ventas:** [contrato-ventas-operativas.md](contrato-ventas-operativas.md) define cotización/ticket presencial y futuras APIs de publicación comercial/recepción de ventas con tienda independiente. Todas sus rutas son diseño; no añadirlas a la tabla de implementadas. [Bases y etapas](../equipo/bases-modulo-ventas.md). Compatibilidad con GET/PATCH de agregados históricos, permisos, idempotencia y reserva/pago tardío pendientes de implementación por sus dominios; ML se conserva hasta otro corte validado.

La [guía de Telegram](configurar-telegram.md) documenta el bot público indicado por Axel, configuración desde la aplicación, métodos externos consumidos y rutas internas, con diagrama. Mantenerla alineada con el adaptador y Proveedores; nunca guardar tokens, chats privados ni URLs con credenciales en la documentación. La guía es reproducción documental, no evidencia de transmisión en otra instalación.

1. Cada dueño define cuerpos, campos, permisos, errores y ejemplos de sus rutas.
2. Edu mantiene importación; Kevin pronóstico/evaluación; Max receta/plan; Vera stock/promoción; Aguirre pedido/canal.
3. Axel coordina sobre y catálogo de rutas; cambios de contrato incluyen consumidor.
4. Indicar estado propuesto o implementado y enlazar prueba de aceptación.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

El frontend se implementa contra un ejemplo completo sin adivinar nombres o estados.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../equipo/avances/cueva.md) siguiendo [la plantilla](../equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Paso 3 local · M03 · 30-09-2026

Necesidades y faltantes implementados en la transacción del plan. API/UI conservan aportes, unidades, lotes y lectura de stock; decimales como cadenas, agregación antes de redondear a tres decimales. Producción o stock ausente deja estado INCOMPLETAS y motivo; no se inventan ceros ni se modifica inventario. Migración aditiva 0010_m03_necesidades sobre 0009; planes antiguos quedan PENDIENTE_M03 y el administrador puede completarlos una vez. Servicio público obtener_necesidades y contrato M03 en docs/api/contratos.md. Compras y Telegram siguen pendientes. Cambios locales por Codex para Axel, sin commit ni cambios remotos.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.

## Claridad y flujo completo · 30-09-2026

Corte vigente de contrato-pedidos.md y ampliación A02 en contratos.md describen automático integrado y presentación kg/L. No hay migración nueva; restricciones de pasos anteriores quedan como historial.


## Paginación de ventas · 30-09-2026

contratos.md documenta el contrato aditivo limite/desplazamiento/total de GET /ventas. solicitarSobre permite conservar metadatos en cliente sin cambiar los consumidores existentes de solicitar. Sin migración.

## Recuperación L04 · 01-10-2026

Codex para Axel bajo responsabilidad de Aguirre: POST /pedidos/{id}/conciliar registra ENVIADO o NO_ENVIADO con evidencia del último intento incierto; no transmite. POST /pedidos/{id}/reintentar reserva N+1 solo desde FALLIDO y con chat actual revisado/verificado. Conserva texto, plan, cantidades, autorización original e historial. GET incorpora envios/recuperaciones; envio sigue siendo el último. Locks fecha→propuesta→pedido→envío en recuperación/despacho/worker, respuesta tardía obsoleta ignorada. Clave/contenido/actor idempotentes, evidencia chat/message_id única. Usuario Operador consulta; solo Administrador actúa.

Migración aditiva 0014_l04_recuperacion sobre 0013, sin reescribir anteriores; downgrade bloqueado con acciones/reintentos. 57 pruebas PostgreSQL y 7 de migraciones correctas; typecheck/build correctos, API/UI/worker locales actualizados y alembic check sin diferencias. QA visual nuevo no acreditado: navegador integrado rechazó el entorno temporal con ERR_BLOCKED_BY_CLIENT. Pruebas usan transporte falso; no se envió otro Telegram. Contrato vigente: docs/api/contrato-pedidos.md, registro detallado en docs/equipo/avances/aguirre.md. Automático real, promociones y demo conjunta pendientes.

## Dashboard y Reportes de lectura · 01-10-2026

Ampliación expresa: Inicio con ventas diarias, ranking y pedidos; `/informes` con períodos inclusivos, versión del modelo, tablas paginadas, detalle en diálogo y CSV completo del período. [Contrato](contrato-informes.md). Ventas publica `resumen_ventas`/`periodo_ventas`; Compras `resumen_pedidos`/`periodo_propuestas` cuenta pedidos sin multiplicar intentos; K03 admite filtros `desde`/`hasta` opcionales conservando la consulta anterior sin filtros. Informes coordina únicamente interfaces públicas. No migra, entrena, modifica stock ni envía mensajes. Fechas ausentes no se rellenan con cero. Registro/evidencia en Bohorquez y coordinación Cueva.

## Corte vigente · 11-10-2026 · Flujo y promociones

Codex para Axel implementó configuración reutilizable, comprobación de requisitos por interfaces públicas, calendario histórico diario de 1–31 días, modelo/modo conservados y pausa/cancelación/reprogramación de tareas sin despacho. Promociones tienen regla inmutable versionada, reserva transaccional después de cada ajuste nuevo de producto y evaluación idempotente con snapshot/motivo; API y pantalla reales. Se conserva la propiedad de cada dominio.

[Contrato vigente, APIs y límites](contrato-flujo-promociones.md). Aplicar `0015_flujo_promociones` antes de actualizar API/worker/Beat. El diagnóstico no ejecuta inferencia ni envía mensajes; guardar configuración no agenda. Consultas de tareas/evaluaciones admiten paginación real con total. La pausa no recupera horas perdidas: reprogramar antes de reanudar. Deshabilitar promociones afecta ajustes nuevos; tareas ya reservadas conservan su versión. Hora simulada de evaluación avanza por el tiempo real transcurrido desde el ajuste para comprobar frescura.

Las notas fechadas de cortes anteriores son historial; no usar sus pendientes como estado actual. Pruebas y límites finales en los registros Cueva/Vera/Sanchez, incluyendo PostgreSQL/Redis y Telegram real solo si fueron ejecutados. No confundir fixtures QA con datos de operación.

## Corte solicitado · 14-10-2026

Codex para Axel. Contratos de flujo/pedidos documentan EJECUTAR_AHORA y formato comercial nuevo. configurar-whatsapp.md identifica claramente preparación pendiente, activos Meta y adaptación requerida; no representa un canal implementado.

## Tienda separada · 21-10-2026

[Contrato Payme](contrato-payme-pruebas.md): API del proyecto independiente tienda/, sin migraciones Payme en FoodSave. ADR-010 prevalece sobre la ubicación y pago ficticio anteriores de ADR-009. Catálogo/inventario/pedido reales por API siguen pendientes.

[Diagnóstico Yape/QR](diagnostico-payme-sandbox-2026-10-21.md): HTTP 500 externo y
lista de métodos de Flex sin YAPE/QR observada el 21-10-2026. No confundir pruebas
locales correctas con habilitación efectiva del comercio en el proveedor.


## Caja presencial · 26-10-2026

`contrato-caja-presencial.md` describe la primera caja realmente implementada. `contrato-ventas-operativas.md` conserva fases futuras. Consultar el contrato nuevo para campos/estados/rutas de caja; no conectar tienda con los ejemplos de diseño. [Contrato implementado](contrato-caja-presencial.md). Autor de este corte: Codex para Axel; se conservan las responsabilidades de cada dominio. Evidencia y límites en el registro de Cueva.


## Entradas de productos · 28-10-2026

contrato-entradas-productos.md documenta la ampliación vigente: entrada administrativa múltiple, historial, límites, fechas, recuperación y relación con caja. No es fabricación con consumo de recetas ni integración de tienda. [Contrato implementado](contrato-entradas-productos.md). Autor Codex para Axel; dominio Inventario de Vera y responsabilidades de los demás integrantes conservados. Evidencia en avances/cueva.md.

## Ampliación vigente · 28-10-2026 · Tienda por API

contrato-integracion-tienda.md es vigente para catálogo/versiones, reservas/cotización y tickets TIENDA; amplía ADR-010 y contrato Payme. Contratos históricos de cliente/caja se conservan con su corte temporal.
