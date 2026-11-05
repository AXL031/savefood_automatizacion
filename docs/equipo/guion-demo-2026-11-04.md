# Demo del 4 de noviembre de 2026 en la instalación actual

05-11-2026: esta página conserva la jornada del 04/11. El [nuevo guion de programación cercana](guion-demo-programada.md) explica promoción puntual, inferencia y plan/Telegram; requiere desplegar 0026. No extiende las fechas de los lotes ni del modelo preparado.

Preparación real de Codex para Axel, coordinación A01–A04. Dominios conservados: Sanchez (ventas/UI), Vera (inventario/promociones), Bohorquez (ML), Rojas (planificación/tienda) y Aguirre (compras/Telegram). Datos nuevos **sintéticos y auditados**, sobre FoodSave 3100 y tienda 3101 existentes, con respaldo previo. No se crea otra instalación. Esta jornada utiliza **hoy 04/11** y pronostica **mañana 05/11**, hora America/Lima. Después del cambio de fecha, los lotes que vencen hoy dejan de venderse/promocionarse; preparar otra fecha requiere otra jornada explícita.

## Estado listo para mostrar

| Módulo | Evidencia disponible |
|---|---|
| Ventas | Cuatro tickets nuevos #10–#13 del 04/11, 154 unidades de 12 productos. El ticket anterior del día se conserva; el total de la pantalla puede incluirlo. |
| Histórico ML | 96 observaciones añadidas del 28/10 al 04/11 para esos productos, origen ESCENARIO_DEMO y motivo de simulación; las 88 759 observaciones previas y sus revisiones permanecen idénticas. No hay ventas del 05/11. |
| Inventario | Quince lotes nuevos de jornada y otro lote de ocho brownies para el caso automático. Productos con límite de venta hoy y lotes frescos; la caja usa FEFO del inventario compartido, incluidos lotes de prueba anteriores. Cada salida tiene movimiento. Insumos con ajustes explícitos y apertura pequeña para provocar faltantes. |
| Modelo | #3 entrenado para la jornada y #4 creado mediante el reentrenamiento repetible. Se conservan #1 y #2. Entrenamiento hasta 02/11, validación 03–04/11 y objetivo reservado 05/11; 7 848 filas entrenables y 24 de validación, 12 productos. Partición ESCENARIO_MANUAL_JORNADA_v1, exclusivamente de exposición. |
| Pronóstico real | Corrida #98, modelo #3, objetivo 05/11: 12 disponibles y 161 unidades. El mismo cálculo con #4 pasó el ensayo con rollback. |
| Plan/compras | Plan #8 PROPUESTO, necesidades CALCULADAS; propuesta #7 y pedidos #13/#14, nueve líneas de insumos. Ejecutar la programación de repetición generará otro plan/pedidos de prueba. |
| Telegram | Pedidos #13 y #14 ENVIADO con message_id 18 y 17 respectivamente. Mensajes reales a los dos destinos ya verificados, rotulados PRUEBA REPETIBLE — NO SURTIR. Sin reenvíos ni confirmación comercial inventada. |
| Promociones | Regla habilitada, 00:00–23:59, umbral 5, descuento 25 %, máximo 30 %; vigilancia ACTUAL de los 12 productos cada diez minutos. Croissant #99 aprobado manualmente; brownies #109 aprobado automáticamente por Beat. Otras sugerencias permanecen pendientes. |
| Configuración | Selector independiente de publicación manual/automática de promociones; estado final manual, igual que pedidos. Cambiarlo afecta sugerencias nuevas; no decide las pendientes anteriores. |
| Tienda | Catálogo de 139 productos recibido por HTTP; croissant y brownies con promoción vigente y disponibilidad actualizada. Cotización real por ambas APIs, sin abrir Payme. |
| Repetición | Programación **#5 PAUSADA**, modelo #4, objetivo 05/11, 12 productos, Prueba repetible y aprobación manual. La #4 ya ejecutada conserva su resultado. |

Pronóstico de la corrida #98:

| Producto | Unidades para el 05/11 |
|---|---:|
| Baguette | 27 |
| Croissant | 31 |
| Pain au chocolat | 31 |
| Brioche, briochette, brownies, cookie, éclair, pain de mie, sándwich JB emmental, tartelette y tartelette fraise | 8 cada uno |
| **Total** | **161** |

## Recorrido durante la exposición

1. Abrir [FoodSave](http://localhost:3100) con la cuenta administrativa habitual. En [Ventas](http://localhost:3100/ventas), filtrar 04/11 y mostrar los tickets #10–#13 y sus movimientos. Distinguir tickets de la pestaña de histórico agregado.
2. En [Inventario](http://localhost:3100/inventario), fecha 04/11, mostrar lotes DEMO-2026-11-04 y DEMO-AUTO-2026-11-04, fechas y movimientos. Los lotes PRUEBA-AXEL previos también siguen registrados; el stock real es el agregado de lotes elegibles, no solo la apertura nueva.
3. En [Configuración](http://localhost:3100/configuracion), mostrar «Publicación de promociones en tienda», independiente de «Envío de pedidos». Dejar manual para revisar una pendiente. En [Operación diaria](http://localhost:3100/operaciones), Promociones, aprobar por ejemplo baguette #94 o brioche #95 y comprobar la tienda. «Revisar ahora» ejecuta la misma regla; la vigilancia programada no depende de visitas web.
4. Mostrar el caso automático ya realizado: brownies #109 conserva AUTOMATICO, sin actor humano; el aviso registra modo, regla y lote. Para un caso automático nuevo, guardar AUTOMATICO **antes** de registrar otro lote elegible y esperar la revisión de diez minutos, o usar Revisar ahora. Cambiar el modo después de generada una pendiente no la aprueba. Volver a manual al terminar si ese es el modo deseado.
5. Abrir [Tienda](http://localhost:3101/tienda/menu), buscar croissant/brownies y revisar sus promociones. En [Publicar en tienda](http://localhost:3100/tienda-admin), mostrar el acuse de entrega. Publicar una promoción no descuenta stock.
6. Probar la canasta: **dos croissants = S/ 8,26**. **Cuatro brownies = S/ 28,00**: dos anteriores a S/ 8,00 y dos del lote automático a S/ 6,00. Juntos **S/ 36,26**. FEFO y aprobación por lote explican el descuento parcial; no se aplica 25 % a todas las unidades por compartir producto. Esos valores corresponden al estado verificado y pueden cambiar tras ventas/aprobaciones nuevas.
7. Abrir [Pronósticos](http://localhost:3100/pronosticos?corrida_id=98), mostrar modelo, partición y las 161 unidades del 05/11. No presentar la validación con datos sintéticos como precisión comercial.
8. En [Automatizaciones](http://localhost:3100/automatizaciones), localizar **#5 PAUSADA → Gestionar → Ejecutar ahora**. Beat suele recogerla dentro de treinta segundos. Mostrar ejecución/intentos, nueva corrida, plan, faltantes y pedidos. No reutilizar la #4 completada como si fuera una ejecución nueva.
9. En [Planificación](http://localhost:3100/planificacion), mostrar stock por fecha objetivo, receta/versiones y aportes a los ingredientes. Los lotes que vencen el 04 no cuentan para el 05. Crear un plan o pedido no aumenta inventario.
10. En [Compras](http://localhost:3100/compras), mostrar primero #13/#14 ENVIADO y sus recibos. Los pedidos de la nueva ejecución esperan aprobación. Aprobarlos produce **otros mensajes reales** al chat revisado; la prueba repetible lo permite expresamente. Ante PENDIENTE_VERIFICACION revisar el chat antes de conciliar; no reenviar a ciegas.

## Reentrenamiento repetible de esta jornada

Desde la raíz:

```powershell
node scripts/preparar-demo-noviembre.cjs --reentrenar
```

Crea una versión nueva con partición manual temporal y una programación pausada que la utiliza. No vuelve a cargar ventas, ajustar insumos, abrir lotes ni enviar Telegram. El modelo aparece en Pronósticos y la tarea de preparación queda registrada. Se comprobó creando #4 y programación #5. Repetirlo cambia esos identificadores; usar los de `.tmp/demo-2026-11-04/escenario.json`.

**El botón estándar «Entrenar modelo» mantiene la política histórica original**, con validación/prueba por meses completos: no confundir su horizonte con el del escenario manual para mañana. El comando anterior es la herramienta de reentrenamiento de esta demo; no implementa cierre diario/entrenamiento rolling en la interfaz.

Otros comandos:

```powershell
node scripts/preparar-demo-noviembre.cjs --respaldo
node scripts/preparar-demo-noviembre.cjs
node scripts/preparar-demo-noviembre.cjs --verificar
```

Respaldo verificado en `.tmp/demo-2026-11-04/antes-demo.dump`, modelos anteriores en `modelos-antes.tar`. El comando sin flag reutiliza la jornada ya preparada sin reiniciar sus avances; --verificar ensaya inferencia/plan/pedidos y revierte su transacción. Los comandos no envían mensajes ni inician pagos. Usan Compose y volúmenes existentes; guardas explícitas de fecha/base y PYTHONPATH=/code. Respaldos/evidencias son privados y quedan fuera de Git. Restaurar datos exige parar productores y revisar el estado: restaurar una base no borra mensajes ya enviados a Telegram.

## Otras pruebas importantes

- **Recepción parcial y completa:** un envío no significa mercancía recibida. Probar el registro administrativo del pedido de prueba con motivo, cantidad, lote y caducidad, y mostrar el movimiento y saldo. La recepción asistida exige además respuesta de aceptación del proveedor. El enlace local del proveedor no será accesible desde un teléfono externo sin conectividad publicada; no se habilitó un túnel en esta entrega.
- **Producción por tandas:** tras recibir insumos, usar un plan de la fecha operativa, consumir ingredientes una vez y generar lote de producto. El plan del 05 no puede producirse con operación fechada 04; cambiar la fecha operativa conscientemente o ejecutar en su jornada. No registrar fabricación ficticia como producción observada.
- **Caja/anulación:** cotizar, confirmar, repetir la misma clave y anular dentro del alcance admitido. Mostrar que el stock cambia una vez y que la compensación es un movimiento, no borrado del ticket.
- **Promoción agotada/vencida y último stock concurrente:** deben dejar de ofertarse/venderse; los casos de reglas, idempotencia y concurrencia pasaron en PostgreSQL. La consulta visual de stock no sustituye la reserva del checkout.
- **Roles y avisos:** Operador no modifica configuración ni aprueba promociones/pedidos. Leer un aviso no equivale a resolverlo; resolver conserva motivo/actor.
- **Dashboard/reportes:** mostrar filtros, versiones y ausencias sin convertirlas a cero. No calcular impacto comercial real con esta continuidad sintética.
- **Payme:** únicamente preproducción y cuatro botones independientes. Esta preparación comprobó cotización y publicación; **no ejecutó un pago nuevo ni certifica la habilitación externa de Yape/QR**.

## Verificación y conservación

18 pruebas SQLite correctas y dos omitidas de concurrencia; 20 correctas en esquemas temporales PostgreSQL. Incluyen configuración/permisos, monitor, aprobación/finalización, producción/recepción, caja y consumidor comercial. Typecheck y build de 25 rutas correctos. Migración 0025 aplicada y servicios actuales arrancados. Flujo real por Beat completado (#13, programación #4), dos envíos Telegram confirmados, promoción automática por Beat y manual recibidas/cotizadas por la API independiente. Preparación repetida sin duplicar datos; reentrenamiento repetible y ensayo con rollback correctos.

Doce conjuntos de filas previas conservaron huella: ventas/revisiones, catálogo, recetas/líneas, ingredientes, proveedores/ofertas, movimientos, modelos y tickets/líneas. **Los saldos de lotes previos sí cambian por las ventas FEFO:** 42 movimientos nuevos, 102 unidades retiradas de lotes anteriores; no se promete conservar sus saldos mientras se venden. Los otros retiros se aplican a lotes nuevos. Ajustes de insumos son explícitos y auditados. Ambos .env conservan sus huellas. Sin commit/push ni pruebas de precisión real/otro PC/CI remoto.

Evidencias privadas: escenario.json, ejecucion-real.json, telegram-resultados.json, verificacion-flujo.json y verificacion-final.json. No publicar destinos, capacidades de checkout, credenciales ni respaldos.
