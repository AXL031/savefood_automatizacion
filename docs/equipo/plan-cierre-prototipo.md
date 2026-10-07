# Plan vigente para cerrar el prototipo FoodSave

Fecha: 30-09-2026, America/Bogota. Coordinación: Axel Cueva. Preparado por Codex para la solicitud de Axel. Este plan reemplaza el seguimiento antiguo de pasos 1–4 de estado-desarrollo.md; conserva los números 1–7 documentados y define ahora los títulos de 8–10, cuya lista original no quedó registrada. Responsables: [reparto vigente](responsabilidades.md). Alcance: [criterio de demo completa](../guia-inicio-desarrollo.md#criterio-de-demo-completa).

Actualización 01-10-2026: el usuario pidió avanzar con lo pendiente después de recibir el corte visual. Se implementa ahora la recuperación L04 del paso 7: API/UI de conciliación y nuevo intento explícito, auditoría e historial, migración 0014. La pausa inicial aplica al avance visual anterior y deja de bloquear este trabajo autorizado. Falta la demostración automática real autorizada; los pasos 8–10 y recurrencia siguen pendientes.

## Regla de avance solicitada

Primero entregar el ajuste transversal de interfaz: navegación persistente, tablas paginadas y detalles visibles. **Detenerse al terminar y verificar ese corte.** Los pasos siguientes están planificados y no se implementan en este avance. No cambiar de rama, integrar ni publicar sin la tarea correspondiente. Conservar los cambios locales y los datos de la instalación.

## Base disponible

| Paso | Comportamiento disponible | Estado |
|---|---|---|
| 1 | Primera carga completa, preparación ML durable, backtest y recuperación sin reimportar | Implementado local; prueba previa con CatBoost/PostgreSQL/Beat |
| 2 | Plan reproducible con pronóstico, receta y stock conservados | Implementado y consumido por el motor |
| 3 | Necesidades agregadas y faltantes con unidades y trazas | Implementado y consumido por Compras |
| 4 | Proveedores, ofertas, pedidos agrupados y regla de una compra activa por fecha | Implementado; recompra protegida |
| 5 | Configuración cifrada del bot y verificación del chat propio | Disponible y configurado en la instalación |
| 6 | Aprobación/rechazo auditados y envío manual por worker | Mensaje real confirmado del pedido #1; message_id=2 |
| 7 | Programación única → pronóstico → plan → faltantes → envío automático; recuperación humana | Automático/conciliación/reintento implementados con transporte falso; falta prueba automática real |

La inicialización no es una carga diaria de operación. Los escenarios son históricos; no convertir fechas ausentes en ventas cero. Planes y pedidos no cambian stock. El modo queda conservado por programación/propuesta. Los cambios de kg/L son presentación y conversión de entrada, sin modificar las unidades persistidas.

## Corte previo: interfaz coherente

Coordinación E04 de Edu con A01 de Axel y consumidores de todos los bloques.

1. Mantener sesión, barra lateral y encabezado en el layout raíz; cambiar solamente el contenido con navegación de Next.js. Mantener 401, cierre de sesión y permisos; actualizar perfil/negocio sin recargar documento.
2. Paginación común: anterior/siguiente, primera/última, salto de página y tamaños 10/25/50/100. Reiniciar al cambiar filtros/lista; conservar página ante sondeo sin nuevos identificadores.
3. Ventas: paginar en PostgreSQL con total filtrado y orden estable; permitir recorrer más allá del antiguo límite de 200. Contrato aditivo limite/desplazamiento/total.
4. Detalles y edición de registros en diálogo accesible, con encabezado visible, desplazamiento propio, Escape, cierre y devolución del foco. Conservar contexto y página de la lista. Evitar cerrar operaciones en curso.
5. Comprobar rutas, listas vacías/largas, cambio de filtros, teclado y móvil con datos aislados. Typecheck/build y prueba de frontera API. Actualizar guías y bitácora.

Límite explícito: las APIs de planes/compras/modelos/programaciones/ejecuciones conservan listas recientes de hasta 50; la pantalla de movimientos consulta los últimos 50 (la API admite 100 por defecto). Su paginación visual recorre la lista recibida, rotulada como reciente. Ventas pagina todo el historial desde servidor. Extender los demás archivos históricos a paginación remota es una mejora futura distinta de ocultar ese límite.

## Paso 7: recuperación y cierre del envío automático

Responsable L03/L04 de Aguirre; A02/A03 de Axel coordina despacho. Contrato: [pedidos](../api/contrato-pedidos.md).

1. Definir transiciones de conciliación, evidencia mínima, permisos, bloqueo transaccional e idempotencia antes de implementar API/UI. Diferenciar envío confirmado, fallo definitivo y resultado incierto.
2. Publicar conciliación administrativa: confirmar una entrega con chat/message_id/fecha y evidencia; resolver una ausencia con evidencia y una acción explícita permitida por el contrato. Conservar intento anterior y responsable. No fingir aceptación del proveedor.
3. Implementar nuevo intento solamente para los estados/evidencias permitidos y por autorización expresa. Revalidar destino/credencial/mensaje; ningún timeout autoriza reenvío automático a ciegas. Mantener la protección entre planes de la misma fecha.
4. Añadir acciones al detalle de pedido con motivo, evidencia, historial e instrucciones comprensibles; rechazar Operador y solicitudes duplicadas con contenido distinto.
5. Probar caída antes/después de transmitir, timeout, respuesta tardía, dos conciliaciones concurrentes, cambio de chat/token y entrega duplicada. Verificar un mensaje automático real al chat propio con ofertas completas y una fecha histórica sin compra activa, mediante autorización concreta de esa prueba.

Cierre: evidencia persistida del automático real y recuperación humana utilizable; no se duplica stock, pedido ni mensaje por reentrega interna.

## Paso 8: promociones sugeridas integradas

Responsable V03/V04 de Vera; A02/A03 de Axel entrega motor. Dependencias: ajustes V02 y regla pura existente en promociones/reglas.py.

1. Contrato de regla versionada y evaluación: parámetros, vigencia, fecha/hora simulada, lote/movimiento, lectura de stock, aceptación/rechazo y motivo. Migración aditiva, sin reescribir revisiones anteriores.
2. Persistir reglas y evaluaciones. Reservar EVALUAR_PROMOCION al ajustar un producto en la misma sesión/transacción; si el ajuste falla no queda evento.
3. Registrar manejador idempotente que use la versión conservada. Distinguir caducidad/lectura antigua/horario/umbral y ausencia de datos con rechazo explicado.
4. API y pantalla real de promociones: configuración administrativa, lista paginada y detalle con trazas a movimiento/regla/ejecución. Enlazar desde Inventario y menú solo cuando funcione.
5. Probar ajuste→Beat→evaluación y rollback/reentrega/concurrencia. Cero, stock desconocido y fecha vencida no se confunden.

Cierre: una sugerencia o rechazo razonado queda persistido y visible. Publicar descuentos o medir alimento salvado no pertenece a este prototipo.

## Paso 9: validación completa y pruebas repetibles

Responsables: todos en sus fronteras; coordinación de Axel. No trasladar todas las pruebas al coordinador.

1. Preparar guía de pruebas y datos aislados para repetir escenarios sin borrar pedidos enviados de la instalación. Distinguir transporte falso de prueba Telegram real; destinos propios verificados y mensajes históricos rotulados.
2. Desde base vacía/migraciones: cargar 3–5 productos con recetas/lotes y ventas, entrenar modelo real, revisar cobertura y programar una ejecución próxima.
3. Comprobar predicción→plan→necesidades→pedido→manual/automático→Telegram; resultado del cálculo y entrega del mensaje se verifican por separado. Sin faltantes implica cero envíos; ofertas incompletas bloquean la propuesta.
4. Comprobar evaluación posterior/dashboard con ventas del día histórico, cobertura, ausencia distinta de cero y versiones conservadas. Ajustar stock y comprobar promoción.
5. Reinicios, errores internos, reentregas, idempotencia, concurrencia, 401/403, móvil, formularios y cantidades exactas. Verificar que plan/pedido no mueven inventario.

Cierre: recorrido íntegro reproducible, con evidencia y fallos recuperables; las comprobaciones aisladas anteriores no sustituyen esta demo conjunta.

## Paso 10: entrega reproducible

Responsables: A04 de Axel y revisión de consumidores según flujo-git.md.

1. Ejecutar controles adecuados, migraciones/cabeza única y CI de los cambios finales. Corregir fallos reales; no declarar verificaciones remotas no ejecutadas.
2. Repetir arranque y recorrido en otra computadora por un integrante, incluyendo persistencia de modelo, secreto cifrado y reinicio. Preparar respaldo/restauración privada y guía de arranque/parada.
3. Actualizar resumen vigente por bloque, dependencias, contratos, estado general y manual de demostración con limitaciones reales.
4. Revisar cambios y preparar commits/PR en las ramas documentadas cuando exista autorización para publicar/integrar. Conservar autoría y datos históricos.

Cierre: otro integrante puede instalar, iniciar y demostrar el prototipo sin depender del chat ni de fixtures confundidas con operación.

## Ampliación posterior: ejecución diaria recurrente

Petición previa del usuario, todavía pendiente y distinta del criterio de cierre histórico. Planificarla después de los pasos 7–10: horario y zona del negocio, días activos, pausa/reanudación, siguiente ejecución, unicidad por día y política ante reinicio/horas perdidas. Primero acordar fuente de ventas/stock actualizados y fecha objetivo dinámica; el modelo y el historial de 2022 no acreditan pronóstico operativo de hoy. En una demo recurrente histórica, definir avance y fin del calendario sin reutilizar una fecha con compra enviada. Requiere contratos, migración, API/UI y pruebas de horario/idempotencia antes de habilitar envíos diarios.

## Ampliación disponible: dashboard y Reportes · 01-10-2026

Solicitud expresa incorporada a K04: gráficos en Inicio y `/informes` de ventas/evaluación/estados de pedidos, filtros por fecha/modelo y CSV completo. [Contrato](../api/contrato-informes.md) y [evidencia/límites](avances/bohorquez.md#dashboard-en-inicio-y-reportes--01-10-2026). 34 pruebas correctas; typecheck/build web y lecturas reales correctas. API/frontend activos, validación visual aislada bloqueada por navegador en 3001. Esta ampliación no marca promociones, demostración automática real o despliegue reproducible en otra PC como terminados.
