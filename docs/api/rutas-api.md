# Rutas propuestas de la API

Base:
```text
/api/v1
```

## Autenticación
```http
POST /autenticacion/iniciar-sesion
POST /autenticacion/renovar
GET  /autenticacion/mi-perfil
```

## Negocios
```http
GET   /negocios/actual
PATCH /negocios/actual
```

## Productos
```http
GET    /productos
GET    /productos/{id}
POST   /productos
PUT    /productos/{id}
DELETE /productos/{id}
```

## Ingredientes
```http
GET    /ingredientes
GET    /ingredientes/{id}
POST   /ingredientes
PUT    /ingredientes/{id}
DELETE /ingredientes/{id}
```

## Recetas
```http
GET  /productos/{producto_id}/receta
POST /productos/{producto_id}/receta
PUT  /productos/{producto_id}/receta
```

## Ventas
```http
GET  /ventas
POST /ventas
POST /ventas/importar
GET  /ventas/resumen
```

## Producción
```http
GET  /produccion
POST /produccion
PUT  /produccion/{id}
```

## Inventario
```http
GET  /inventario
GET  /inventario/{ingrediente_id}
POST /inventario/movimientos
GET  /inventario/movimientos
GET  /inventario/existencias-bajas
```

## Pronósticos
```http
GET  /pronosticos
GET  /pronosticos/{fecha}
POST /pronosticos/ejecutar
```

## Planificación
```http
GET  /planes
GET  /planes/{id}
POST /planes/generar
GET  /planes/{id}/ingredientes
```

## Proveedores
```http
GET    /proveedores
GET    /proveedores/{id}
POST   /proveedores
PUT    /proveedores/{id}
DELETE /proveedores/{id}
POST   /proveedores/{id}/ingredientes
```

## Compras
```http
GET  /pedidos-compra
GET  /pedidos-compra/{id}
POST /pedidos-compra/generar
POST /pedidos-compra/{id}/enviar
POST /pedidos-compra/{id}/reintentar
```

## Excedentes
```http
GET  /excedentes
GET  /excedentes/actual
POST /excedentes/ejecutar
```

## Promociones
```http
GET  /promociones
GET  /promociones/{id}
POST /promociones/generar
POST /promociones/{id}/activar
POST /promociones/{id}/detener
```

## Automatizaciones
```http
GET  /automatizaciones
GET  /automatizaciones/{id}
PUT  /automatizaciones/{id}
GET  /ejecuciones-automatizacion
GET  /ejecuciones-automatizacion/{id}
POST /automatizaciones/{id}/ejecutar
POST /ejecuciones-automatizacion/{id}/reintentar
```

## Informes
```http
GET /informes/panel
GET /informes/operacion
GET /informes/desperdicio
GET /informes/pronosticos
GET /informes/automatizaciones
```
