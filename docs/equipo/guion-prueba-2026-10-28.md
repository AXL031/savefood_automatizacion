# Jornada de prueba del 28 de octubre en la aplicación actual

Preparación solicitada por Axel, por Codex para Cueva, con interfaces de Sanchez (Ventas), Vera (Inventario/promociones), Bohorquez (ML), Rojas (recetas/planes/tienda) y Aguirre (Compras/Telegram). La aclaración final exige usar **FoodSave 3100, tienda 3101 y Telegram ya configurado**. La preparación separada anterior quedó detenida y su código de despliegue/receptor ficticio se retiró. Esta entrega no agrega otro módulo de simulación ni cambia la arquitectura HTTP de la tienda.

## Datos que están listos

| Parte | Preparación inicial |
|---|---|
| Ventas del 27/10 | Cuatro tickets presenciales, 171 unidades de 12 productos; coinciden con los agregados sintéticos del histórico. |
| Continuidad para inferencia | 216 observaciones sintéticas del 10 al 27 de octubre para esos productos, identificadas como ESCENARIO_DEMO y con motivo explícito. La carga original de 88 543 observaciones se conserva. |
| Stock de productos | 98 unidades vendibles iniciales, con remanentes del 27 y entradas frescas del 28; 15 lotes nuevos. Los lotes anteriores siguen registrados. |
| Insumos | Ajustes auditados sobre lotes vigentes de los ingredientes seleccionados y nueva apertura pequeña/conocida para provocar faltantes. No se borraron recepciones ni movimientos anteriores. |
| Modelo | Modelo #2, prueba-jornada-2026-10-28-particion-manual; modelo #1 conservado. |
| Automatización | Programación #3 PAUSADA, objetivo 28/10, 12 productos, modelo #2, prueba repetible y REQUIERE_APROBACION. |
| Pronóstico/insumos/pedidos ensayados | 12 pronósticos, 154 unidades previstas, dos pedidos y diez líneas de insumos. El ensayo revierte su transacción para dejar listo el recorrido en vivo. |
| Promociones | Regla habilitada: revisar cada diez minutos, ventana de prueba 00:00–23:59, umbral cinco unidades y descuento 25 % (máximo 30 %). Tres lotes con stock y límite de venta hoy; croissant aprobado para comprobar publicación y otros pendientes para mostrar la aprobación. |
| Tienda | Doce productos publicados por API. Croissant con 25 %: dos unidades cotizan S/ 8,26. No se inició ningún pago externo. |
| Telegram | Destinos existentes de los dos proveedores usados vigentes/verificados, con el bot y credenciales originales. Dos mensajes construidos por el servicio real de Compras; no se enviaron durante la preparación. |

Los valores corresponden a la apertura del escenario; ventas, ajustes y nuevas ejecuciones posteriores pueden cambiarlos. No hay ventas observadas del 28: ausencia no equivale a cero.

## Recorrido para mostrarlo en vivo

1. Entrar a [FoodSave habitual](http://localhost:3100) con la cuenta administrativa existente. En [Ventas](http://localhost:3100/ventas), filtrar 27/10/2026 para mostrar los cuatro tickets; el histórico importado contiene las doce cantidades sintéticas de ese día.
2. En [Inventario](http://localhost:3100/inventario), mostrar la apertura de productos del 27/28, stock vigente y lotes próximos al límite de venta. Los códigos DEMO identifican los lotes del escenario; los ajustes tienen motivo de simulación.
3. Abrir [Automatizaciones](http://localhost:3100/automatizaciones). Localizar la programación #3 y elegir **Gestionar → Ejecutar ahora**. Su estado inicial es PAUSADA para evitar que consuma el recorrido antes de la exposición. Beat recoge el despacho en su siguiente ciclo, hasta unos treinta segundos; la UI permite seguir ejecución y resultado.
4. Desde el resultado, mostrar [Pronósticos](http://localhost:3100/pronosticos), el plan y [necesidades de insumos](http://localhost:3100/planificacion). El cálculo utiliza la historia anterior al 28 y descuenta el stock vendible, conservando las versiones de receta/modelo.
5. Abrir [Compras](http://localhost:3100/compras), revisar los dos pedidos, presentación/cantidad y mensaje preparado. **Aprobar y enviar** usa el Telegram real y el destino ya verificado mostrado en pantalla. Esperar ENVIADO/message_id y mostrar el mensaje en el chat configurado. Esto es un efecto real cuando se aprueba; no hay receptor ficticio en el flujo actual. No reenviar a ciegas si aparece PENDIENTE_VERIFICACION.
6. En [Operación diaria](http://localhost:3100/operaciones), pestaña Promociones, mostrar las sugerencias con stock, fecha y descuento. Aprobar otra pendiente para mostrar el paso administrativo. La regla sigue revisando automáticamente; **Revisar ahora** permite la prueba inmediata.
7. Abrir [Publicar en tienda](http://localhost:3100/tienda-admin) para comprobar la entrega/versiones y [tienda habitual](http://localhost:3101/tienda/menu) para ver la promoción. La publicación se entrega cada diez segundos y el stock visible se consulta cada cinco segundos. La cotización de canasta verifica cantidades promocionadas por lote.
8. Se puede registrar una venta presencial y observar disponibilidad, o probar Payme preproducción como invitado en la tienda. Solo el backend verificado confirma la venta y consume su reserva. La habilitación efectiva de Yape/QR sigue dependiendo de Payme; esta preparación no certifica esos métodos externos.

Para repetir la planificación del mismo día, la opción Prueba repetible ya está habilitada. Crear una nueva programación desde el asistente; una ejecución ya completada conserva su resultado y no se reutiliza como otro pedido. Una aprobación nueva produce otro mensaje real.

## Modelo y límites

El modelo de la jornada se entrenó con 7 092 filas entrenables y se validó con 360. Entrenamiento hasta agosto, validación septiembre y octubre reservado, incluyendo el objetivo 28. La partición es **ESCENARIO_MANUAL_JORNADA_v1**, explícita para la exposición; no modifica POLITICA_EVALUACION_v1 ni el artefacto anterior. Las observaciones sintéticas de octubre permiten construir las variables previas, no se presentan como mediciones ni prueba de precisión comercial. No se fabrican ventas futuras del 28.

Esta preparación recorre los módulos existentes. El reloj acelerado, los dos generadores automáticos de ventas y el cierre diario con consolidación/reentrenamiento siguen pendientes de implementación; no se sustituyen por escribir tickets automáticamente al histórico.

## Preparación y verificación reproducibles

Desde la raíz, con la carga original y Compose actuales:

```powershell
node scripts/preparar-jornada-actual.cjs
```

La herramienta conserva el primer respaldo .tmp/jornada-actual/antes-jornada-20261028.dump, valida su índice, pausa brevemente worker/Beat, agrega los datos en una transacción, comprueba coherencia de tickets/historia y ensaya plan/pedidos con rollback. Reejecutar conserva el marcador y los avances existentes; no reinicia la jornada. Los Python requieren PREPARAR_JORNADA_AUTORIZADA=2026-10-28 y base foodsave. La selección de cuenta usa un administrador existente, sin crear cuentas ni cambiar contraseñas. Los .env no se modifican.

scripts/aprobar-promocion-jornada.py es la prueba puntual ya ejecutada: aprueba la sugerencia de croissant por el controlador existente y prepara su snapshot; requiere las mismas guardas y /evidencia. No inicia Payme ni manda Telegram. Los respaldos y evidencias contienen información local y están ignorados por Git.

Verificación: quince conjuntos previos, incluidos ventas/revisiones, catálogo, recetas, proveedores/ofertas, movimientos, lotes originales de producto y modelo anterior, conservaron sus recuentos/huellas. Las modificaciones esperadas de insumos son movimientos AJUSTE auditados; datos/modelo/configuración nuevos se identifican por la jornada. Ambos .env conservaron su hash. Evidencias privadas: escenario.json, verificacion-flujo.json, mensajes-previstos.txt, promocion-en-tienda.json y preservacion.json dentro de .tmp/jornada-actual/.
