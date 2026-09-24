# Endpoints propuestos

Base:
```text
/api/v1
```

## Auth
```http
POST /auth/login
POST /auth/refresh
GET  /auth/me
```

## Businesses
```http
GET   /businesses/current
PATCH /businesses/current
```

## Products
```http
GET    /products
GET    /products/{id}
POST   /products
PUT    /products/{id}
DELETE /products/{id}
```

## Ingredients
```http
GET    /ingredients
GET    /ingredients/{id}
POST   /ingredients
PUT    /ingredients/{id}
DELETE /ingredients/{id}
```

## Recipes
```http
GET  /products/{product_id}/recipe
POST /products/{product_id}/recipe
PUT  /products/{product_id}/recipe
```

## Sales
```http
GET  /sales
POST /sales
POST /sales/import
GET  /sales/summary
```

## Production
```http
GET  /production
POST /production
PUT  /production/{id}
```

## Inventory
```http
GET  /inventory
GET  /inventory/{ingredient_id}
POST /inventory/movements
GET  /inventory/movements
GET  /inventory/low-stock
```

## Forecasting
```http
GET  /forecasts
GET  /forecasts/{date}
POST /forecasts/run
```

## Planning
```http
GET  /plans
GET  /plans/{id}
POST /plans/generate
GET  /plans/{id}/ingredients
```

## Suppliers
```http
GET    /suppliers
GET    /suppliers/{id}
POST   /suppliers
PUT    /suppliers/{id}
DELETE /suppliers/{id}
POST   /suppliers/{id}/ingredients
```

## Purchasing
```http
GET  /purchase-orders
GET  /purchase-orders/{id}
POST /purchase-orders/generate
POST /purchase-orders/{id}/send
POST /purchase-orders/{id}/retry
```

## Surplus
```http
GET  /surplus
GET  /surplus/current
POST /surplus/run
```

## Promotions
```http
GET  /promotions
GET  /promotions/{id}
POST /promotions/generate
POST /promotions/{id}/activate
POST /promotions/{id}/stop
```

## Automations
```http
GET  /automations
GET  /automations/{id}
PUT  /automations/{id}
GET  /automation-executions
GET  /automation-executions/{id}
POST /automations/{id}/run
POST /automation-executions/{id}/retry
```

## Reports
```http
GET /reports/dashboard
GET /reports/operations
GET /reports/waste
GET /reports/forecasting
GET /reports/automations
```
