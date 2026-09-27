# Después de la demostración universitaria

Esta página es **hoja de ruta**, no contrato de la migración `0002` ni compromiso de funciones disponibles. El [prototipo](guia-inicio-desarrollo.md) termina al mostrar plan y sugerencias de insumos; conserva ventas diarias y stock por lotes en PostgreSQL.

| Etapa posterior | Qué se añade | Decisión previa necesaria |
|---|---|---|
| Operación diaria | Carga o registro continuo de ventas, producción real, descuentos de stock por ventas/consumo y política de devoluciones. | Elegir sistema de origen y cómo evitar aplicar dos veces cada movimiento. |
| Compras reales | Proveedores, órdenes, aprobación, envío, confirmación y recepción parcial. La recepción física crea movimientos de ingreso, no la sola aprobación. | Canal, evidencia de entrega y reglas de conciliación. |
| Automatización operativa | El prototipo ya demuestra Beat, ejecución durable y reintentos con un escenario histórico. Después se añade cierre diario real, evaluación periódica intradía e idempotencia de efectos externos. | Hora local de cierre, datos actuales, fallos recuperables y método de reconciliación por canal. |
| Fuentes externas | Adaptadores para Excel recurrente, POS o Google Sheets. PostgreSQL sigue siendo la fuente operativa del prototipo; una sincronización futura debe definir quién es autoridad para cada dato. | Dirección de sincronización, conflictos, permisos y verificación de escrituras. |
| Prevención | El prototipo guarda sugerencias de promoción por regla de stock y caducidad. Después se añaden activación real, medición y excedentes intradía. | Datos intradía y modelo/regla propios; el CatBoost diario no predice venta restante del día. |
| Comercialización | Seguridad, pruebas integradas, despliegue y evaluación prospectiva del modelo. | Datos reales nuevos, criterios de calidad por comercio y operación soportada. |

Estas etapas se diseñarán en ADR y migraciones nuevas. `0002` sí incluye la programación y el registro de ejecuciones de **simulación**; no anticipa tablas de pedidos reales solo porque aparezcan en maquetas históricas.
