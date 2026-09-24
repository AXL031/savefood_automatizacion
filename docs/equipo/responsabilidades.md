# Responsabilidades del equipo

Los módulos funcionales se reparten entre las seis personas. Una persona puede encargarse de varios módulos relacionados; **cada módulo tiene un único responsable de interfaz, servidor, API, pruebas e integración**. Los componentes compartidos tienen una persona coordinadora, pero los cambios de cada dominio siguen siendo responsabilidad de su dueño.

| Responsable | Módulos asignados | Alcance integrado |
|---|---|---|
| Axel Cueva | Autenticación; Negocios y configuración; Automatizaciones y control; Notificaciones | Acceso por negocio, preferencias, programación, ejecuciones, reintentos y avisos |
| Edu Sanchez | Panel principal; Informes | Indicadores, consultas agregadas, visualizaciones y componentes de interfaz compartidos |
| Kevin Bohorquez | Ingredientes; Recetas; Pronósticos; Planificación | Catálogo de ingredientes, composición de productos, demanda prevista, planes y faltantes |
| Leonardo Vera | Productos; Ventas; Producción; Inventario | Catálogo de productos, datos operativos, existencias y movimientos |
| Leonardo Aguirre | Proveedores; Compras | Oferta de insumos, selección de proveedor, pedidos, envíos y confirmaciones |
| Max Rojas | Excedentes; Promociones; Desperdicio | Detección de riesgo, acciones preventivas, medición y merma real |

Esta tabla cubre todos los módulos de la sección 7 y los módulos de automatización, notificaciones e informes. **Configuración** forma parte de Negocios y configuración; **ejecuciones y recuperación** forman parte de Automatizaciones y control. Las dependencias entre responsables se coordinan mediante contratos, sin trasladar la propiedad de un módulo.

## Responsabilidades comunes

- **Interfaz:** crear las pantallas, formularios y visualizaciones de su módulo, con validaciones y estados de carga, error y ausencia de datos.
- **Servidor:** implementar reglas de negocio, persistencia, modelos y migraciones de su módulo.
- **API:** diseñar, implementar y documentar las rutas de su módulo y conectarlas con su interfaz.
- **Calidad:** probar el módulo, aplicar los permisos por negocio y documentar su uso.
- **Integración:** acordar contratos con los demás responsables y entregar su funcionalidad completa, desde la interfaz hasta la base de datos.

## Axel Cueva — Autenticación, negocios, automatización y notificaciones

- **Interfaz:** acceso, configuración del negocio, automatizaciones, historial de ejecuciones, errores, reintentos y notificaciones.
- **Servidor:** autenticación, permisos por negocio, reglas de configuración, programación y ejecución de tareas, verificación, reintentos, eventos y avisos; configuración de Redis, Celery y Celery Beat.
- **API:** autenticación, negocios y configuración, automatizaciones, ejecuciones, reintentos y notificaciones.
- **Integración:** orquestar los servicios de los demás módulos mediante contratos acordados y coordinar la arquitectura general.

## Edu Sanchez — Panel principal e informes

- **Interfaz:** panel de control, filtros, indicadores, tablas y gráficos; coordinación de la estructura visual y los componentes compartidos.
- **Servidor:** consultas y agregaciones para métricas operativas, de predicción, automatización, impacto económico y desperdicio.
- **API:** rutas del panel y los informes, con filtros y respuestas adecuadas para las visualizaciones.
- **Integración:** obtener datos de los demás módulos y presentar resultados consolidados.

## Kevin Bohorquez — Ingredientes, recetas, predicción y planificación

- **Interfaz:** ingredientes, recetas, pronósticos, métricas de predicción, planes de producción y necesidades de insumos.
- **Servidor:** catálogo de ingredientes, composición de recetas, preparación de datos, predicción de demanda, planes y cálculo de ingredientes.
- **API:** ingredientes, recetas, pronósticos, planes y necesidades de insumos.
- **Integración:** utilizar ventas, recetas e inventario; entregar faltantes al módulo de compras y permitir la planificación automática.

## Leonardo Vera — Productos, ventas, producción e inventario

- **Interfaz:** productos, ventas, importación de archivos CSV, producción, existencias y movimientos de inventario.
- **Servidor:** catálogo de productos, registro de ventas y producción, importación de datos, existencias y movimientos.
- **API:** productos, ventas, producción e inventario; importación CSV y movimientos.
- **Integración:** proporcionar datos operativos a predicción, planificación, excedentes e informes.

## Leonardo Aguirre — Proveedores y compras

- **Interfaz:** proveedores, insumos suministrados, precios, pedidos y seguimiento de estados y envíos.
- **Servidor:** selección de proveedores, generación y envío de pedidos, precios y gestión de estados.
- **API:** gestión de proveedores e insumos, generación y consulta de pedidos, envío y reintento de pedidos.
- **Integración:** recibir faltantes de planificación y conectar el abastecimiento con las automatizaciones.

## Max Rojas — Excedentes, promociones y desperdicio

- **Interfaz:** excedentes, niveles de riesgo, promociones, seguimiento de resultados y registro de desperdicio.
- **Servidor:** detección y clasificación de excedentes, reglas de promoción, activación, seguimiento, desperdicio y métricas del módulo.
- **API:** consulta de excedentes, generación y gestión de promociones, registro y consulta de desperdicio.
- **Integración:** utilizar ventas y producción, conectar las acciones preventivas con las automatizaciones y proporcionar resultados a informes.

## Coordinación de elementos compartidos

- Axel coordina arquitectura, contratos, infraestructura base e integración general; cada persona implementa y verifica la integración de sus módulos.
- Edu coordina la estructura visual y los componentes compartidos; cada persona construye las pantallas de sus módulos con esa base.
- Autenticación y negocios pertenecen a Axel; productos, a Leonardo Vera; ingredientes y recetas, a Kevin. Se consulta al dueño antes de cambiar contratos compartidos.
- La responsabilidad integral definida aquí prevalece sobre las listas antiguas de entregables por capas de otras secciones.
