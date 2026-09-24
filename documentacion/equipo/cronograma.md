# Cronograma de FoodSave: semanas 1 a 16

El plan usa semanas académicas y evita asignar fechas de calendario no confirmadas. Las semanas 1 a 3 son hitos comunicados por el equipo; la semana 5 es la semana actual y contempla presentar el avance. El contenido de la semana 4 debe validarse con el equipo. Las semanas 6 a 16 son objetivos propuestos para seis responsables que trabajan **en paralelo por módulos completos**: interfaz, servidor, API, pruebas e integración.

| Semana | Objetivo | Entregable o criterio de aceptación | Estado |
|---|---|---|---|
| 1 | Presentar la idea del proyecto | Problema, público objetivo y propuesta FoodSave explicados | Realizado según el equipo |
| 2 | Presentar el flujo del sistema | Secuencia desde datos y predicción hasta prevención y control | Realizado según el equipo |
| 3 | Presentar la propuesta de interfaz | Pantallas principales y sistema visual expuestos | Realizado según el equipo |
| 4 | Consolidar alcance, arquitectura y responsabilidades | Acuerdos técnicos y distribución de todos los módulos; confirmar qué se entregó realmente esa semana | Por confirmar |
| 5 | Presentar el avance del desarrollo | Repositorio organizado, documentación y demostración del código que esté funcionando en ese momento | Semana actual; presentación prevista |
| 6 | Crear la base ejecutable común | Interfaz y API arrancan localmente; PostgreSQL conectado; migración inicial; autenticación y negocio mínimos; contratos entre responsables acordados | Propuesto |
| 7 | Implementar el primer corte de cada dominio | Productos, ingredientes, recetas, ventas, inventario y proveedores tienen datos y API básicos; pronóstico, plan, pedido, riesgo, panel y ejecución cuentan con un primer recorrido conectado | Propuesto |
| **8** | **Presentar la versión preliminar integrada** | **Se puede recorrer con un negocio de demostración: registrar o cargar datos, generar demanda y plan, detectar faltantes, crear un pedido, visualizar riesgo y una acción preventiva, y ver el resultado en el panel. La interfaz usa rutas reales y persistencia; las integraciones externas aún pueden usar adaptadores de prueba claramente identificados.** | **Hito propuesto** |
| 9 | Completar la operación diaria | Validaciones e importación de ventas, registro de producción, movimientos de inventario, catálogo y recetas; pruebas de consistencia de existencias | Propuesto |
| 10 | Completar planificación y abastecimiento | Pronóstico evaluable, plan revisable y aprobable, cálculo de faltantes, selección de proveedor, envío de pedido y estados de confirmación | Propuesto |
| 11 | Completar prevención de desperdicio | Detección y clasificación de excedentes, promociones dentro de límites, medición posterior y registro de desperdicio real | Propuesto |
| 12 | Completar automatización y recuperación | Programación, disparadores, trazabilidad, verificación, reintentos, manejo de duplicados y notificaciones ante fallos | Propuesto |
| 13 | Consolidar panel, informes y configuración | Indicadores con periodos y origen, métricas de impacto, filtros necesarios, límites y preferencias editables, permisos por negocio | Propuesto |
| 14 | Integrar y probar el ciclo completo | Pruebas de extremo a extremo para planificación, compra, excedente y fallo; conexiones disponibles verificadas; registros y observabilidad funcional | Propuesto |
| 15 | Estabilizar la entrega | Corrección de defectos, pruebas de regresión y seguridad, revisión de accesibilidad, documentación de instalación y preparación de demostración | Propuesto |
| **16** | **Entregar el sistema completo** | **Todos los módulos asignados funcionan integrados, con interfaz, API, persistencia, permisos, automatizaciones, pruebas y documentación; se demuestra el flujo normal y al menos un fallo recuperado, y se entrega una versión instalable.** | **Hito final propuesto** |

## Seguimiento

La versión preliminar de la semana 8 no equivale al sistema final: demuestra el recorrido principal con datos persistidos y deja visibles las integraciones externas simuladas. Las semanas 9 a 15 completan reglas, excepciones, mediciones, seguridad y calidad sin detener el trabajo paralelo. El equipo debe registrar evidencia de cada entrega —demostración, pruebas y cambios en el repositorio— antes de marcarla como realizada. Si una integración externa exige credenciales o acceso de un tercero, se debe documentar su estado y conservar un adaptador verificable para la demostración; no se presentará como conexión real algo que esté simulado.
