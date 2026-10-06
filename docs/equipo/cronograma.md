# Cronograma de FoodSave: semanas 1 a 16

Semanas académicas, sin fechas de calendario. Estado según la evidencia de los [registros de avance](avances/README.md) al **06-10-2026**. Una semana solo se marca «Realizado» con demostración, pruebas o cambios en el repositorio. El alcance es el de la [guía de alcance](../guia-inicio-desarrollo.md).

| Semana | Objetivo | Entregable / criterio | Estado |
|---|---|---|---|
| 1 | Presentar la idea | Problema, público y propuesta | Realizado |
| 2 | Presentar el flujo | Recorrido datos → predicción → plan → compra → prevención | Realizado |
| 3 | Presentar la interfaz | Sistema visual y mockups | Realizado |
| 4 | Consolidar alcance y reparto | Acuerdos técnicos y responsables | Por confirmar con el equipo |
| 5 | Presentar el repositorio | Estructura, README, especificaciones, cronograma y reparto | Realizado |
| 6 | Base ejecutable común | Compose, API, web, migraciones, acceso, configuración, motor (A01–A04) | Realizado (listo para integrar) |
| 7 | Primer corte por dominio | Productos, ventas, primera carga, ingredientes, recetas, lotes, proveedores con API; modelo entrenado y evaluado | En curso: todo hecho salvo pantalla de proveedores |
| **8** | **Versión preliminar integrada** | Carga → modelo → Beat genera pronóstico, plan y faltantes → pedido por proveedor; panel histórico con datos reales | **Pendiente:** plan (M02–M03) y pedidos (L02) |
| 9 | Plan y pedidos completos | Pantalla del plan con trazas (M04); aprobación y envío Telegram a chat de pruebas (L03) | Propuesto |
| 10 | Promoción sugerida | Ajuste de stock → `EVALUAR_PROMOCION` → sugerencia o rechazo visible (V03–V04) | Propuesto |
| 11 | Fallos y recuperación | Envío incierto, conciliación, reintentos visibles, reentregas sin duplicar (L04, A03) | Propuesto |
| 12 | Alinear interfaz | Tokens, navegación e íconos según la especificación visual; estados vacío/error en todas las pantallas | Propuesto |
| 13 | Pruebas de extremo a extremo | Recorrido completo de la guía en PostgreSQL/Redis; CI verde | Propuesto |
| 14 | Estabilizar | Corrección de defectos, accesibilidad, instalación en otra PC | Propuesto |
| 15 | Ensayo de demo | Guion, datos de demostración y caso de fallo recuperado | Propuesto |
| **16** | **Entrega final** | Criterio de demo completa de la guía de alcance, documentación al día y versión instalable | **Hito final** |

Una integración externa sin credenciales se demuestra con su adaptador y se declara como simulada.
