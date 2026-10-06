# C4 · Componentes

Módulos del servidor en la demo (`backend/app/modules/`) y quién orquesta las automatizaciones. Los módulos marcados con * aún no tienen código.

```mermaid
flowchart LR
    api[API FastAPI]
    autenticacion[Autenticación]
    negocios[Negocios]
    inicializacion[Inicialización]
    productos[Productos]
    ventas[Ventas]
    ingredientes[Ingredientes]
    recetas[Recetas]
    inventario[Inventario]
    pronosticos[Pronósticos]
    planificacion[Planificación*]
    proveedores[Proveedores]
    compras[Compras*]
    promociones[Promociones sugeridas*]
    automatizaciones[Motor de automatización]
    telegram[Adaptador Telegram*]

    api --> autenticacion & negocios & inicializacion & productos & ventas
    api --> ingredientes & recetas & inventario & pronosticos & planificacion
    api --> proveedores & compras & promociones & automatizaciones

    inicializacion --> productos & ventas & recetas & inventario
    recetas --> ingredientes
    automatizaciones --> pronosticos & planificacion & compras & promociones
    planificacion --> pronosticos & recetas & inventario
    compras --> planificacion & proveedores & telegram
    promociones --> inventario
```

Producción, excedentes, desperdicio, notificaciones e informes son [visión futura](../../vision-futura.md).
