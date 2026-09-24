# Responsabilidades del equipo

El equipo se organiza en **seis módulos de trabajo integrales**, uno por persona. Cada módulo agrupa los dominios funcionales relacionados que se indican a continuación. **Cada responsable desarrolla el frontend, el backend y las APIs de su módulo**, y entrega su funcionalidad integrada de extremo a extremo.

| Persona | Módulo a cargo | Dominios incluidos |
|---|---|---|
| Axel Cueva | Automatización y control | Automations + Notifications |
| Edu Sanchez | Dashboard y reportes | Dashboard + Reports |
| Kevin Bohorquez | Predicción y planificación | Forecasting + Planning |
| Leonardo Vera | Operación e inventario | Sales + Production + Inventory |
| Leonardo Aguirre | Proveedores y compras | Suppliers + Purchasing |
| Max Rojas | Excedentes, promociones y desperdicio | Surplus + Promotions + Waste |

## Responsabilidades comunes de cada persona

- **Frontend:** desarrollar las pantallas, componentes, formularios y visualizaciones de su módulo, incluyendo validaciones y estados de carga, error y datos vacíos.
- **Backend:** implementar las reglas de negocio, servicios, persistencia, modelos y migraciones correspondientes a su módulo.
- **APIs:** diseñar, implementar y documentar sus endpoints, y conectarlos con su frontend; coordinar los contratos e integraciones con otros módulos.
- **Calidad:** probar el funcionamiento de su módulo y su integración, aplicar los permisos por negocio y documentar su uso.
- **Entrega:** presentar un módulo funcional desde la interfaz hasta la base de datos, incluyendo sus automatizaciones e integraciones cuando correspondan.

## Axel Cueva — Automatización y control

- **Frontend:** pantallas de configuración de automatizaciones, historial y detalle de ejecuciones, intentos, errores, reintentos y notificaciones.
- **Backend:** Automation, AutomationExecution, AutomationAttempt, scheduler, motor de control y reintentos, logs y notificaciones; configuración de Redis, Celery y Celery Beat.
- **APIs:** consulta y configuración de automatizaciones, ejecución manual, seguimiento de ejecuciones, reintentos y gestión de notificaciones.
- **Integración:** orquestar los servicios de los demás módulos mediante los contratos acordados.

## Edu Sanchez — Dashboard y reportes

- **Frontend:** dashboard, reportes, filtros, indicadores, tablas y gráficos.
- **Backend:** servicios de consulta y agregación de datos para métricas operativas, predicción, automatización, impacto económico y desperdicio.
- **APIs:** endpoints de dashboard y reportes, con filtros y respuestas adecuadas para las visualizaciones.
- **Integración:** consumir los datos y servicios de los demás módulos para presentar resultados consolidados.

## Kevin Bohorquez — Predicción y planificación

- **Frontend:** pantallas de pronósticos, métricas de predicción, planes de producción y necesidades de ingredientes.
- **Backend:** preparación de datos, algoritmo de predicción, Forecast, ProductionPlan, ProductionPlanItem, IngredientRequirement y cálculos por receta.
- **APIs:** consulta y ejecución de predicciones, generación y consulta de planes y cálculo de necesidades de ingredientes.
- **Integración:** utilizar ventas, recetas e inventario y entregar los faltantes al módulo de compras; exponer los servicios necesarios para la planificación automática.

## Leonardo Vera — Operación e inventario

- **Frontend:** pantallas de ventas, importación CSV, registro de producción, stock y movimientos de inventario.
- **Backend:** Sales, Production, Inventory, InventoryMovement, importación de ventas, control de stock y stock mínimo.
- **APIs:** registro y consulta de ventas y producción, importación CSV, consulta de inventario y gestión de movimientos.
- **Integración:** proporcionar datos operativos a predicción, planificación, excedentes y reportes.

## Leonardo Aguirre — Proveedores y compras

- **Frontend:** pantallas de proveedores, insumos suministrados, precios, pedidos, detalle de compra y seguimiento de estados y envíos.
- **Backend:** Suppliers, SupplierIngredient, PurchaseOrder, PurchaseOrderItem, selección de proveedor, generación y envío de pedidos y gestión de estados.
- **APIs:** gestión de proveedores y sus insumos, generación y consulta de pedidos, envío y reintento de pedidos.
- **Integración:** recibir faltantes de planificación y conectar el abastecimiento con el motor de automatización.

## Max Rojas — Excedentes, promociones y desperdicio

- **Frontend:** pantallas de excedentes, niveles de riesgo, promociones, seguimiento de resultados y registro de desperdicio.
- **Backend:** SurplusDetection, reglas de excedente, Promotion, activación y seguimiento de promociones, registro de desperdicio y métricas del módulo.
- **APIs:** detección y consulta de excedentes, generación, activación y finalización de promociones y registro y consulta de desperdicio.
- **Integración:** utilizar ventas y producción, conectar las acciones preventivas con automatización y proporcionar resultados a reportes.

## Coordinación de elementos compartidos

- Axel coordina la arquitectura, los contratos, la infraestructura base y la integración general; cada persona implementa y verifica la integración de su propio módulo.
- Edu coordina el AppShell, Sidebar, Header y los componentes visuales compartidos; cada persona construye las pantallas de su módulo con esa base.
- Los componentes transversales Auth, Businesses, Products, Recipes e Ingredients requieren una asignación explícita antes de su implementación; esta distribución conserva los dominios principales existentes sin asignarles responsables adicionales de forma implícita.
- La responsabilidad integral definida en este punto prevalece sobre cualquier reparto por capas mencionado en las secciones de dependencias, entregables o resumen de responsabilidades.
