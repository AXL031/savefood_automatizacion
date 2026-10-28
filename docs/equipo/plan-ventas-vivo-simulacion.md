# Plan de ventas y propuesta de dos simuladores de jornada

**26-10-2026 · Punto de partida actualizado:** caja PRESENCIAL disponible según [contrato implementado](../api/contrato-caja-presencial.md). Los dos simuladores y cierre de este documento continúan como propuestas; no se ejecuta una jornada acelerada por registrar ventas manualmente.

## Propuesta vigente · 26-10-2026 · Dos simuladores para la exposición

**SOLO PROPUESTA, NO IMPLEMENTADA.** Ampliación expresa de Axel: dos simuladores, uno iniciado desde el módulo de ventas y otro desde la tienda independiente, para demostrar en vivo una jornada completa en pocos minutos, observar los cambios de tablas y cerrar con actualización de ventas, evaluación, entrenamiento y pronóstico siguiente. Autor: Codex para Axel, coordinación documental; responsabilidades de los dominios conservadas. [Bases de Ventas](bases-modulo-ventas.md) y [contrato propuesto](../api/contrato-ventas-operativas.md) siguen siendo requisitos previos, no funcionalidades disponibles.

### Dos entradas, una jornada coordinada

| Simulador propuesto | Dónde se controla | Qué genera y por qué recorrido |
|---|---|---|
| **Ventas presenciales** | Módulo de ventas de FoodSave, panel de simulación | Agenda tickets sintéticos PRESENCIAL y llama al mismo servicio de cotización/venta que usará la caja. Respeta precios, promociones, stock, errores y trazabilidad; no escribe directamente los agregados de ML. |
| **Compras de tienda** | Panel de simulación del proyecto independiente `tienda/` | Agenda carritos/compras sintéticos TIENDA en el backend de tienda; consume productos/promociones recibidos, solicita cotización/reserva y envía sus eventos de venta por HTTP a FoodSave. Conserva la recepción y el ticket devueltos. No accede a tablas o módulos internos de FoodSave. |

Se podrán probar por separado, cada uno en su sesión, o **juntos en una sesión de exposición**. En el modo conjunto comparten `sesion_simulacion_id`, fecha D y reloj de negocio coordinado por FoodSave mediante API. Cada simulador mantiene su agenda, semilla, cursor y estado en su propio backend. Dos botones o dos pestañas no significan dos descuentos sobre la misma venta: cada evento tiene una identidad estable por sesión/canal/posición.

El arranque conjunto requiere que ambos backends confirmen preparación para la misma sesión y que la copia de catálogo/precios/promociones esté sincronizada. Abrir sus páginas no inicia ventas. El coordinador inicia el reloj una sola vez; los navegadores muestran y controlan, no son quienes mantienen el proceso corriendo. En modo individual se declara desde el inicio qué canal está incluido para que el cierre no espere un canal que no participa.

### Tiempo de la demostración y controles

Configuración inicial propuesta: fecha simulada D, apertura 08:00, cierre 20:00, duración real objetivo **300 segundos**, canales incluidos, semillas, catálogo y volumen de eventos. La duración será configurable para ensayar la exposición. Fórmula general:

`factor = segundos_del_día_simulado / duración_real_configurada`

`hora_simulada = min(cierre, apertura + tiempo_real_activo × factor)`

Para 08:00–20:00 en 300 s: 43 200 / 300 = **144 segundos simulados por segundo real**. Ese reloj rige fechas de venta, vencimientos de reserva, promociones y elegibilidad de lotes de ambos canales. Las horas de auditoría UTC, tiempos de red y leases de procesamiento permanecen reales. La tienda obtiene el reloj por API; nunca se cambia el reloj del equipo ni se confía en una fecha libre del navegador.

Controles propuestos: preparar, iniciar, pausar/reanudar la jornada, detener nuevas ventas y cerrar, consultar resultados y crear una nueva sesión con la misma configuración. En conjunto, pausar congela el reloj compartido y detiene nuevas emisiones en ambos canales; las solicitudes ya enviadas pueden terminar y quedan contadas una vez. La pausa efectiva requiere acuse de ambos backends; hasta recibirlo se muestra pausa pendiente. Si uno pierde comunicación se muestra desconexión y se conserva su cursor, sin fingir sincronización.

No se reescribe una jornada anterior al repetir. Una nueva sesión tiene nuevos IDs y una instantánea inicial reproducible; las agendas son deterministas por semilla. El orden global de eventos incluye un desempate estable entre canales; la concurrencia libre podrá ser otro perfil de estrés con resultados de asignación no necesariamente idénticos. No prometer reproducibilidad de un entrenamiento sin fijar además datos, configuración, semilla y versiones de librerías.

Los cinco minutos son el objetivo de **emisión de la jornada**. Drenar ventas pendientes, consolidar, entrenar y pronosticar consume tiempo de cómputo real adicional. Se medirán esos tiempos antes de fijar una duración total para la exposición. La interfaz mostrará cada fase y sus tiempos; no declarará entrenamiento completado por terminar el reloj ni lo sustituirá silenciosamente por un artefacto precalculado.

### Qué debe verse cambiar en vivo

- **Tabla de ventas de FoodSave:** tickets de ambos canales, hora simulada, estado, cantidad e importe. Filtros PRESENCIAL/TIENDA, contador y totales de la sesión; una recepción RECIBIDA todavía no se muestra como venta confirmada.
- **Tabla/historial de compras de la tienda:** operación local, envío a FoodSave, acuse/pendiente de sincronización y ticket confirmado. Permite ver el paso por API, no solo una animación local.
- **Catálogo y promociones de tienda:** disponibilidad y promociones aprobadas/publicadas cambian tras los movimientos y las entregas por API. Conservar la diferencia entre sugerencia generada, aprobación y publicación confirmada; no publicar automáticamente una sugerencia para hacer avanzar la demo.
- **Inventario:** saldo inicial, unidades reservadas/vendidas, compensaciones y disponible; se observan conflictos si ambos canales piden la última unidad. Demanda no atendida se presenta aparte y no cuenta como venta.
- **Panel de jornada:** reloj, eventos emitidos/aplicados/pendientes/rechazados, estado de cada simulador y retraso de sincronización. Consulta inicial cada 2–5 s; SSE solo como evolución si es necesario. Los valores se leen de operaciones persistidas, no de contadores inventados en el navegador.
- **Panel de cierre y ML:** fase en curso, versión del cierre, ventas del día, evaluación contra el pronóstico guardado, modelo anterior/nuevo, duración y pronóstico del día siguiente con versión/fecha visibles. Error o falta de cobertura se muestran con su motivo.

Se interpreta la visualización de tablas solicitada como seguimiento tanto en FoodSave como en la tienda: ventas por canal, compras recibidas y cambios comerciales del catálogo. La propuesta no presupone un módulo de administración de múltiples tiendas; sigue siendo un comercio y una sucursal.

### Cierre del día D y actualización de ML

Antes de iniciar se conserva una historia compatible y suficiente **hasta D−1**, un modelo inicial M0 con corte anterior a D y el pronóstico P(D) producido antes de emitir las ventas de D. Los tickets sintéticos de D no provienen de filas reales futuras expuestas como datos de entrada del modelo. Si se elige una fecha que ya tiene agregado importado en la copia de datos, se prepara un escenario con fuente explícita y sin esa fila duplicada; no se suma importado y simulado.

| Orden | Fase futura | Resultado y condición de avance |
|---|---|---|
| 1 | **Detener y drenar ambos simuladores** | Al llegar al cierre se detiene la emisión. Cada canal entrega su último cursor y manifiesto de eventos emitidos. Esperar ventas en vuelo, reentregas, reservas y acuses; reconciliar pendientes. Un canal desconectado o PENDIENTE_REVISION impide declarar un cierre completo. |
| 2 | **Consolidar las ventas de D** | Tickets confirmados menos anulaciones, por producto y canal; conciliar asignaciones de inventario. Guardar cierre/versiones/cobertura una sola vez y actualizar la proyección diaria del **escenario aislado**. Cero solo con observación explícita, no por faltar tickets. |
| 3 | **Evaluar el pronóstico que ya existía para D** | Comparar P(D), producido con historia anterior, con las ventas consolidadas de D. Conservar corrida, M0 y revisión de cierre. No recalcular P(D) con las ventas del mismo D y presentarlo como si se hubiese anticipado. |
| 4 | **Entrenar una nueva versión con el cierre** | Crear ejecución durable e idempotente por sesión/cierre/configuración. El candidato M1 incorpora los datos nuevos hasta D junto al historial suficiente. Registrar corte, huellas, configuración y métricas; conservar M0. Nueva preparación/entrenamiento no es la reserva única de primera carga ni se dispara con cada ticket. |
| 5 | **Validar y registrar el resultado del entrenamiento** | Bohorquez define una política temporal para el ciclo diario: selección/validación cronológica y ajuste final hasta D, sin usar D+1 ni reutilizar como prueba no vista el período ya incorporado. Presentar las métricas de evaluación de M0 separadas de las de entrenamiento/validación de M1. No asumir que un día añadido mejora el modelo o que permite entrenarlo desde cero. |
| 6 | **Generar el pronóstico de D+1** | Solo con M1 utilizable y cierre publicado. Usa historia con fechas <= D, conserva el ID de M1 y crea corrida nueva. La pantalla muestra el nuevo pronóstico para el día siguiente, junto al anterior de D y su evaluación. Sin M1 válido la fase queda pendiente/fallida; no se acredita que se usó el modelo nuevo. |

El cierre de ventas y el flujo ML tienen estados separados. Un cierre confirmado no se revierte si después falla el entrenamiento: se muestra «Ventas cerradas · entrenamiento pendiente/fallido» y se reanuda esa fase con la misma identidad. La demostración completa solo se marca terminada cuando ambas fuentes incluidas están conciliadas, cierre/evaluación/artefacto nuevo y pronóstico siguiente constan disponibles. Correcciones o eventos tardíos crean revisión del cierre y nuevas identidades derivadas; conservan los resultados previos, sin volver a descontar la venta.

La inferencia actual está acotada al período histórico reservado y la preparación inicial evalúa un modelo fijo. **El ciclo cierre → reentrenamiento → D+1 requiere ampliar y versionar sus contratos y tareas antes de implementarlo.** No se elimina el control de fechas existente ni se cambia la partición de un artefacto guardado para simular compatibilidad. Bohorquez entrega ese contrato temporal; Cueva su programación/recuperación y Sanchez el cierre/cobertura.

### Aislamiento y pagos de prueba

La demostración se ejecutará en una instalación de FoodSave aislada, con su base, inventario, modelos, cola y tareas propios; el proyecto tienda tendrá también su instancia y almacenamiento de prueba. Solo HTTP comunica ambos proyectos. Se usan credenciales de integración de la sesión de prueba, no la sesión administrativa ni las credenciales del comercio. Los tickets, agregados y modelos sintéticos nunca alimentan el histórico/modelo de la instalación habitual.

Para que la jornada acelerada sea repetible, el simulador de tienda usará un **adaptador de pagos de prueba en su backend**, que produzca resultados controlados y visibles como SIMULADOS, incluidos pendiente/fallo/pago tardío. FoodSave admite esos eventos únicamente en la instalación aislada y con identidad de integración de prueba vinculada al escenario. Un campo enviado por el navegador no activa esta capacidad. Probar Payme sandbox real seguirá siendo un recorrido separado: no acelerar su reloj externo, sus confirmaciones ni sus códigos como parte de la agenda de cinco minutos. No se realizan cobros reales ni envíos Telegram por iniciar la simulación.

La prueba base de ventas iniciará con stock de productos terminados suficiente. Se pueden mostrar planificación, compras y recepción usando sus servicios/adaptadores de prueba; la fabricación que convierte insumos en productos sigue siendo otra ampliación pendiente. Denominar «flujo completo de jornada de ventas y cierre» a esta demo no acredita producción física, entrega real ni conciliación bancaria.

### Responsables y aceptación de esta ampliación

| Entrega propuesta | Responsable y frontera |
|---|---|
| Panel y agenda del simulador presencial, tickets y cierre por canal | Sanchez; servicio de stock de Vera |
| Panel/agenda del simulador de tienda, pagos controlados y API de venta/acuse | Rojas, con contrato de ventas de Sanchez y reservas de Vera |
| Sesión compartida, reloj por API, arranque/pausa/cierre coordinados y recuperación | Cueva; cada backend mantiene su cursor propio |
| Publicación y visualización de producto/promoción, disponibilidad y límites | Sanchez/Vera como emisores; Rojas como receptor |
| Evaluación de P(D), nuevo entrenamiento M1 y pronóstico D+1 | Bohorquez; cierre por Sanchez y ejecuciones durables por Cueva |
| Instalaciones aisladas y pruebas de jornada | Infraestructura de Cueva; cada dueño implementa y verifica su consumidor |

Criterios adicionales para dar por implementada la propuesta:

1. Cada simulador funciona solo y ambos funcionan juntos; total común = ventas presenciales + ventas de tienda aplicadas, sin contar dos veces el mismo evento.
2. Ventas, compras de tienda, stock y catálogo cambian en vivo desde operaciones persistidas; fallo de red o evento fuera de orden se ve como pendiente, nunca como éxito ficticio.
3. Pausa/reinicio y dos pestañas conservan reloj/cursor e identidades; no se regeneran ventas ya aplicadas. La agenda determinista y la regla de desempate permiten repetir una sesión.
4. El cierre espera manifiestos/cursores y eventos pendientes de ambos canales. Repetir el cierre no duplica agregados, movimientos, evaluación ni entrenamiento del mismo cierre/configuración.
5. P(D) permanece inmutable; su evaluación usa el cierre D. M1 incorpora D y el siguiente pronóstico se produce para D+1, con corte/modelo/revisiones trazables y sin datos futuros.
6. Entrenamiento fallido conserva cierre y M0; la interfaz permite continuar la fase pendiente y no marca toda la demo completada antes del pronóstico siguiente.
7. Los datos sintéticos y modelos nuevos solo existen en el escenario aislado. Payme, Telegram y credenciales habituales no reciben efectos por activar el simulador.
8. Se mide duración de jornada, drenaje, cierre y ML por separado; la exposición informa el tiempo total medido y distingue claramente resultado real calculado de cualquier material precalculado que se muestre aparte.

**Entrega actual: definición documental.** Sesión, reloj compartido, simuladores, tablas en vivo y ciclo ML diario no se han implementado ni probado por escribir esta propuesta.

## Referencia del planteamiento inicial · 15-10-2026

Las secciones siguientes conservan el plan previo como antecedente. La ampliación anterior define ahora los dos simuladores y el ciclo de cierre diario; ante diferencias prevalece esta propuesta del 26-10 y las bases actuales de Ventas. Ninguna sección histórica acredita funcionalidad disponible.

> **Actualización 26-10-2026, solo planteamiento:** la solicitud actual separa el módulo de ventas de la simulación. [Bases del módulo](bases-modulo-ventas.md) y [contrato propuesto](../api/contrato-ventas-operativas.md) concretan primero venta presencial y después integración HTTP bidireccional con tienda (productos/promociones hacia tienda, ventas hacia FoodSave). Prevalecen sobre las decisiones preliminares de ventas de este plan. Sin código ni migraciones; el simulador de 300 s no se implementa ni es requisito de la primera caja.

**15-10-2026 · Solo diseño solicitado por Axel. No implementado.** Coordinación: Cueva. El código de este corte añade recepción de compras; no añade caja, ventas por ticket, producción ni simulador. Este documento propone una ampliación posterior y no sustituye los contratos vigentes.

## Resultado esperado

Una pantalla de Ventas permite registrar un ticket, descontar productos terminados por lote y ver el inventario y el total de la jornada. Una pantalla de Simulación reproduce una jornada completa en cinco minutos mediante los mismos servicios de negocio, usando datos aislados. Al terminar se puede revisar ventas, faltantes, compras, recepción y existencias.

## Base existente y brechas

Actualmente Ventas conserva agregados diarios importados y sus revisiones. No hay ticket de caja ni descuento de inventario por venta. Inventario tiene apertura, ajustes y recepción explícita de insumos; un plan no produce físicamente ni consume ingredientes. Compras mantiene aprobación, Telegram, recuperación e impedimento de recompra por fecha. El modelo utiliza una ventana histórica y no puede recibir fechas actuales por el solo cambio del reloj. El simulador deberá respetar esa ventana o contar con una ampliación de inferencia validada por Bohorquez.

No se puede simular el ciclo insumos→productos→ventas usando únicamente un plan: hace falta una confirmación de producción que consuma insumos y cree lotes terminados. Se propone como fase independiente antes de declarar el flujo completo. Hasta entonces la simulación de ventas deberá iniciar con lotes de producto suficientes y señalar ese límite.

## Entregas y orden

| Fase | Entrega | Responsable y frontera | Criterio para avanzar |
|---|---|---|---|
| 1 | Contrato de tickets, reloj y escenario | Sanchez, Vera y Cueva; revisión temporal de Bohorquez | Estados, dinero, idempotencia, lotes, anulación y agregado diario acordados antes de migrar |
| 2 | Registro de ventas y movimientos | Sanchez orquesta; Vera expone salida de stock | Ticket y descuento atómicos; stock insuficiente no deja ticket ni movimientos |
| 3 | Pantalla de caja e historial | Sanchez con piezas comunes | Lista de tickets primero, Crear venta, buscador/carrito, revisión, anular con motivo y permisos |
| 4 | Cierre y lectura para ML | Sanchez y Bohorquez | Agregados compatibles, día abierto distinguido del cerrado y ausencia de venta conservada |
| 5 | Motor y pantalla de simulación | Cueva; servicios de Sanchez/Vera/Rojas/Aguirre | Jornada de 300 s reproducible, pausable y recuperable, sin contaminar datos habituales |
| 6 | Producción confirmada y ciclo completo | Rojas y Vera; Cueva integra | Confirmar una fabricación consume lotes de insumo y abre producto terminado de forma atómica e idempotente |
| 7 | Compras y recepción dentro del escenario | Aguirre y Vera | Se conserva aprobación/incertidumbre/recompra; recibir suma una vez; resumen final cuadra |

Cada responsable mantiene su interfaz, API, datos y pruebas según [responsabilidades](responsabilidades.md). Las fases son propuestas; no se atribuye implementación al equipo.

## Ventas en vivo

Proponer `ticket_venta`, `linea_ticket_venta`, relación de consumo con lotes y claves únicas por operación. Guardar identificador externo opcional, origen, usuario, fecha efectiva local, instante real UTC, versión/precio unitario al vender, cantidades enteras, moneda y total decimal exacto. Estado inicial CONFIRMADO tras la transacción; ANULADO mediante operación compensatoria con motivo. No borrar tickets confirmados.

Sanchez publica un servicio `registrar_ticket(sesion, entrada, contexto)`; Vera publica `retirar_productos(sesion, lineas, contexto)`. Ninguno confirma por separado. Seleccionar lotes vendibles por caducidad más próxima, con desempate estable; bloquear lotes en orden consistente. Cero stock o stock desconocido rechaza o deja un intento rechazado separado, nunca genera saldo negativo ni una venta parcial silenciosa. No vender producto vencido; la política de fecha desconocida debe quedar definida antes de implementar.

Precio/moneda e impuestos aún no existen como contrato de caja: acordar catálogo de precios y cálculo antes de guardar importes. No añadir pagos, facturación ni conciliación bancaria en esta entrega.

Proponer `POST /ventas/tickets`, `GET /ventas/tickets`, `GET /ventas/tickets/{id}` y `POST /ventas/tickets/{id}/anular`. Son rutas futuras. Repetir clave+actor+contenido devuelve el mismo ticket; cambiar contenido devuelve conflicto. Una anulación crea compensación trazable sobre los lotes de origen; si el lote ya no es vendible, no vuelve al disponible comercial sin revisión.

Los tickets serán la fuente operativa de ambos canales. **Definición del 26-10:** ticket, asignaciones de lote y movimientos se confirman juntos, pero no se actualiza automáticamente el agregado histórico de ML por cada ticket. El cierre/cobertura y su adaptador serán otra entrega; se elige una procedencia autoritativa por producto/fecha, sin sumar importado y operativo. Un día abierto no se trata como completo; un cero requiere observación explícita. Ver [bases de histórico y cierre](bases-modulo-ventas.md#histórico-cierre-y-predicción).

La pantalla se actualiza inicialmente por consulta cada 2–5 s. Añadir SSE solo si la carga y la experiencia lo requieren; el refresco del navegador no puede ser el motor que registra ventas.

## Jornada completa en cinco minutos

Configuración inicial: fecha compatible con la historia/modelo, horario 08:00–20:00, duración real 300 s, catálogo, lotes iniciales, semilla aleatoria y cantidad/distribución de eventos. Doce horas equivalen a **144 segundos simulados por segundo real**. Fórmula: `hora_simulada = inicio + tiempo_real_activo × 144`; limitar al cierre. Pausar detiene el tiempo activo y no envejece lotes durante la pausa.

Conservar una sesión durable con estados PREPARADA, EN_CURSO, PAUSADA, FINALIZADA, CANCELADA y FALLIDA; semilla, configuración, tiempos, cursor y resumen. Preparar una agenda determinista de eventos con identificadores únicos por sesión/posición. El worker procesa eventos vencidos, no una tarea por cada segundo. Si se retrasa, procesa el atraso en orden y con límites; el tiempo de ejecución puede exceder cinco minutos y se muestra el retraso. Cerrar sesión solo después de resolver todos sus eventos.

Reiniciar worker o abrir dos pestañas no vuelve a vender un ticket: reservar eventos con lease y usar claves únicas de negocio, no confiar en una bandera del navegador. Pausar/cancelar deja los eventos ya aplicados auditables. Reiniciar crea otra sesión a partir de la misma instantánea, nunca borra movimientos anteriores.

La primera implementación debe usar **una base/instalación de simulación separada** con inventario, tickets, ventas y tareas propios. Copiar la instantánea autorizada sin credenciales Telegram y usar un adaptador de proveedor de prueba que conserve evidencia local. El usuario no habilita efectos externos por iniciar una simulación. Los informes del comercio y el entrenamiento habitual no leen los eventos simulados. No basta una etiqueta visual sobre las tablas reales compartidas.

El reloj de dominio debe entrar explícitamente por contexto a Inventario, Planificación, Promociones, Ventas y Compras. El reloj UTC de auditoría, los leases y la red siguen siendo reales. No cambiar el reloj del equipo ni reinterpretar `datetime.now()` globalmente. La disponibilidad actual usa saldos vigentes y fecha de caducidad; `fecha_ingreso` excluye nuevas recepciones de fechas anteriores, pero no reconstruye todo el historial de saldos. Para reproducir consultas pasadas, implementar lectura de movimientos a fecha o instantáneas coherentes y fijar reglas para eventos fuera de orden.

Los CSV diarios originales no aportan horas de ticket: la agenda intradía será sintética, identificada y reproducible; no afirmar que representa ventas observadas. Puede repartir cantidades agregadas de un día con una semilla, conservando el total de demanda. Cuando no haya stock, guardar demanda no atendida separada de ventas efectivas.

## Recorrido que se verificará

1. Abrir escenario aislado y comprobar stock inicial/modelo/recetas/ofertas.
2. Calcular plan y compra por faltantes sin mover inventario.
3. Registrar envío por adaptador de prueba y recepción explícita; el stock de insumos aumenta una vez.
4. Cuando exista fase 6, confirmar producción y crear producto terminado consumiendo los insumos exactos. Antes de esa fase, usar productos de apertura e informar el límite.
5. Reproducir la jornada; ver ventas, disponibilidad, caducidad y demanda no atendida.
6. Cerrar y contrastar existencias iniciales + entradas − salidas = existencias finales; totales diarios = tickets confirmados − anulaciones. Revisar decisiones y promociones sugeridas sin publicarlas.

La regla actual de una compra activa por fecha sigue vigente. Simular varias reposiciones en el día exige diseñar por separado reserva/cobertura por necesidad y cantidades ya pedidas/recibidas; no desactivar la protección para conseguir que la demostración avance.

## Pruebas y aceptación

- Dos ventas simultáneas del último producto dejan una venta aceptada y ningún saldo negativo.
- Repetir ticket o recepción, perder la respuesta o reiniciar el worker conserva un único efecto.
- Un fallo entre guardar ticket y descontar lote revierte ambos; una anulación conserva evidencia y compensación.
- Descuento por lote y caducidad coinciden al mismo instante simulado; no hay ventas de lotes vencidos.
- La misma semilla e instantánea producen los mismos eventos/totales en 5 minutos, con pausa y reinicio incluidos.
- Cerrar con retraso muestra los eventos pendientes; no declara cierre antes de terminarlos.
- Cambiar la velocidad no cambia cantidades, precios ni orden de eventos.
- Un día abierto no entra como día completo en ML; el día objetivo no entra en sus propias características.
- Simular no cambia la base del comercio ni envía Telegram; compras enviadas/recibidas no se duplican entre planes.
- QA de caja/simulador en escritorio y móvil; mostrar estado vacío, fallo, permisos y recuperación.

Antes de implementar, convertir estas decisiones en contratos revisables y migraciones aditivas. El siguiente trabajo concreto es la fase 1; las demás permanecen pendientes.
