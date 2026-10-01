# Dashboard y reportes de lectura · 01-10-2026

Ampliación solicitada expresamente por Axel: gráficos en Inicio y módulo Reportes. Kevin conserva la responsabilidad del dashboard/informes; Edu entrega lecturas de ventas, Aguirre las de pedidos y Axel coordina integración. No incluye informes económicos, pagos ni impacto estimado.

## API y fuentes

`GET /api/v1/informes/resumen`, autenticado para Administrador y Operador. Parámetros opcionales: `desde`, `hasta` (fechas inclusivas), `modelo_id` positivo e `incluir_evaluacion` (true por defecto). Rango máximo: 366 días. Sin fechas, últimos 30 días terminados en la última venta conocida; sin ventas, última fecha de propuesta; sin ninguna fuente, fecha actual. El período aplicado y los límites disponibles se devuelven explícitamente.

Sobre `datos`: `generado_en` UTC, `periodo`, `fuentes`, `ventas` (unidades, registros producto/día, días observados, productos, serie diaria y ranking completo), `pedidos` (total, distribución de los nueve estados, propuestas y propuestas sin pedidos), `evaluacion` nullable y `aviso_evaluacion`. Ventas refleja revisiones actuales. Pedidos usa fecha objetivo del escenario y su estado actual, cuenta cada pedido una vez independientemente de los intentos de envío. Incluye propuestas canceladas, sin faltantes y bloqueadas en sus propios contadores.

Lecturas públicas: `ventas.servicio.resumen_ventas`/`periodo_ventas`, `compras.servicio.resumen_pedidos`/`periodo_propuestas`, y `pronosticos.evaluacion.resumen_evaluacion(..., desde=..., hasta=...)`. Informes no consulta tablas privadas ni confirma transacciones. Evaluación reutiliza métricas y revisiones vigentes de K03, solo corridas BACKTEST del modelo seleccionado; no entrena ni genera evaluaciones. Modelo ausente produce evaluación null con aviso; otros errores se propagan.

## Presentación y exportación

Inicio muestra ventas diarias, ocho productos principales y estados de pedidos del período visible. No rellena días ausentes con cero. Una venta explícita de cero sí es observada. Reportes permite rango y versión del modelo; tablas paginadas y gráficos usan el mismo resumen. Las fechas históricas y la cobertura permanecen visibles.

`GET /api/v1/informes/exportar?tipo=ventas|pronosticos|pedidos` admite los mismos filtros y devuelve CSV UTF-8 con BOM, delimitador punto y coma, nombre fijo por tipo/fechas y `Cache-Control: no-store`. Exporta el período completo, no la página visible. Ventas: registros agregados por fecha y por producto; pronósticos: pares por fecha/producto, con reales desconocidos vacíos y motivo de exclusión; pedidos: distribución completa por estado y contadores de propuestas. Incluye fuentes, fecha de generación y filtros. Textos potencialmente interpretables como fórmulas se neutralizan; nunca exporta token, chat, credenciales ni mensajes.

Los reportes no mueven stock, envían mensajes ni calculan dinero/ahorro ficticio. Rangos inválidos, mayores de 366 días y modelos inexistentes se rechazan. Un período sin registros se presenta como vacío; fallo de consulta no se presenta como cero.
