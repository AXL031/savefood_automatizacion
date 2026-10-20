# Dashboard y reportes de lectura · 01-10-2026

## Actualización K03/K04 · 20-10-2026

Inicio, Pronósticos, Evaluación y Reportes comparten navegación, identidad hoja/yema e indicadores. Gráfico de líneas con selección de fecha, teclado y separación ante ausencia de pares/fechas; fechas visibles y cifras con formato es-PE. Reportes presenta la hora de generación en la zona del negocio. Filtros y CSV mantienen el período completo y las fuentes reales. Los selectores recorren todas las páginas de modelos; el límite visual anterior de 50 versiones queda sustituido.

El resumen y detalle de evaluación añaden `pares_pendientes_evaluacion`; una revisión actual aún no evaluada se excluye con motivo `EVALUACION_PENDIENTE`, distinguible de una venta ausente. Corrección→reserva y consumo exacto de revisiones quedan definidos en [contratos](contratos.md#k03k04-y-frontera-e01--20-10-2026). No se recalculan planes/pedidos. Las advertencias de datos pendientes no acreditan por sí solas que un worker esté ejecutándose.

Ampliación solicitada expresamente por Axel: gráficos en Inicio y módulo Reportes. Kevin conserva la responsabilidad del dashboard/informes; Edu entrega lecturas de ventas, Aguirre las de pedidos y Axel coordina integración. No incluye informes económicos, pagos ni impacto estimado.

## API y fuentes

`GET /api/v1/informes/resumen`, autenticado para Administrador y Operador. Parámetros opcionales: `desde`, `hasta` (fechas inclusivas), `modelo_id` positivo e `incluir_evaluacion` (true por defecto). Rango máximo: 366 días. Sin fechas, últimos 30 días terminados en la última venta conocida; sin ventas, última fecha de propuesta; sin ninguna fuente, fecha actual. El período aplicado y los límites disponibles se devuelven explícitamente.

Sobre `datos`: `generado_en` UTC, `periodo`, `fuentes`, `ventas` (unidades, registros producto/día, días observados, productos, serie diaria y ranking completo), `pedidos` (total, distribución de los nueve estados, propuestas y propuestas sin pedidos), `evaluacion` nullable y `aviso_evaluacion`. Ventas refleja revisiones actuales. Pedidos usa fecha objetivo del escenario y su estado actual, cuenta cada pedido una vez independientemente de los intentos de envío. Incluye propuestas canceladas, sin faltantes y bloqueadas en sus propios contadores.

Lecturas públicas: `ventas.servicio.resumen_ventas`/`periodo_ventas`, `compras.servicio.resumen_pedidos`/`periodo_propuestas`, y `pronosticos.evaluacion.resumen_evaluacion(..., desde=..., hasta=...)`. Informes no consulta tablas privadas ni confirma transacciones. Evaluación reutiliza métricas y revisiones vigentes de K03, solo corridas BACKTEST del modelo seleccionado; no entrena ni genera evaluaciones. Modelo ausente produce evaluación null con aviso; otros errores se propagan.

## Presentación y exportación

Inicio muestra ventas diarias, ocho productos principales y estados de pedidos del período visible. No rellena días ausentes con cero. Una venta explícita de cero sí es observada. Reportes permite rango y versión del modelo; tablas paginadas y gráficos usan el mismo resumen. Las fechas históricas y la cobertura permanecen visibles.

`GET /api/v1/informes/exportar?tipo=ventas|pronosticos|pedidos` admite los mismos filtros y devuelve CSV UTF-8 con BOM, delimitador punto y coma, nombre fijo por tipo/fechas y `Cache-Control: no-store`. Exporta el período completo, no la página visible. Ventas: registros agregados por fecha y por producto; pronósticos: pares por fecha/producto, con reales desconocidos vacíos y motivo de exclusión; pedidos: distribución completa por estado y contadores de propuestas. Incluye fuentes, fecha de generación y filtros. Textos potencialmente interpretables como fórmulas se neutralizan; nunca exporta token, chat, credenciales ni mensajes.

Los reportes no mueven stock, envían mensajes ni calculan dinero/ahorro ficticio. Rangos inválidos, mayores de 366 días y modelos inexistentes se rechazan. Un período sin registros se presenta como vacío; fallo de consulta no se presenta como cero.
