# Visión posterior a la demo

Hoja de ruta, no contrato. Nada de esta página está implementado ni se construye para la entrega universitaria. El alcance vigente está en la [guía de alcance](guia-inicio-desarrollo.md).

| Etapa | Qué se añade | Decisión previa necesaria |
|---|---|---|
| Operación diaria | Registro continuo de ventas y producción real; descuento de stock por venta y consumo; devoluciones. | Sistema de origen y cómo evitar aplicar dos veces un movimiento. |
| Compras operativas | Confirmación comercial del proveedor, recepción parcial y conciliación. La recepción crea el ingreso de stock, no la aprobación. | Evidencia de aceptación y reglas de recepción. |
| Automatización operativa | Cierre diario real (p. ej. planificación nocturna fija), control intradía de excedentes, idempotencia de efectos externos por canal. | Hora local de cierre, datos actuales y método de reconciliación. |
| Prevención | Detección intradía de excedentes con nivel de riesgo, activación y publicación de promociones, medición posterior del efecto. | Datos intradía y modelo propio; el CatBoost diario no predice la venta restante del día. |
| Avisos | Notificaciones internas e historial de avisos; canales adicionales (correo, WhatsApp). | Canal, consentimiento y política de reintento. |
| Informes | Impacto económico (pérdida evitada), desperdicio en unidades y kg, métricas de automatización por periodo. | Definición de línea base y de valores medidos vs. estimados. |
| Fuentes externas | Excel recurrente, POS o Google Sheets. | Quién es autoridad de cada dato y cómo se resuelven conflictos. |
| Comercialización | Varias sucursales o comercios, SaaS, seguridad reforzada, despliegue y evaluación prospectiva del modelo. | Datos reales nuevos y operación soportada. |

Las pantallas de referencia de Excedentes y Promociones activas ([mockups 08 y 09](diseno/mockups/README.md)) pertenecen a esta visión. Cada etapa requiere su propio ADR y migraciones nuevas.
