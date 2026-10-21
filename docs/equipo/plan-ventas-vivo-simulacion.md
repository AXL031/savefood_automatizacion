# Plan de ventas en vivo y simulación de una jornada

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

Los tickets son la fuente del día operativo. El agregado diario se actualiza en la misma transacción mediante un adaptador de Ventas y conserva revisiones. No sumar otra vez el agregado importado del mismo producto/día: definir procedencia y exclusión o abrir la jornada en una fecha sin datos de caja importados. ML no debe tratar una jornada incompleta como un día completo. Al cerrar, publicar totales y cobertura sin rellenar fechas ausentes con ceros; un cero solo se publica si hubo observación explícita del día/producto.

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
