# Contratos entre módulos

## Planning → Forecasting

```python
forecast_service.get_forecast(product_id, date)
```

Respuesta:
```json
{
  "product_id": 1,
  "date": "2026-09-24",
  "predicted_quantity": 60,
  "confidence": 0.93
}
```

## Planning → Inventory

```python
inventory_service.get_stock(ingredient_id)
```

Respuesta:
```json
{
  "ingredient_id": 5,
  "stock": 2,
  "unit": "kg"
}
```

## Planning → Purchasing

```json
{
  "ingredient_id": 5,
  "required": 5.8,
  "available": 2,
  "shortage": 3.8
}
```

## Purchasing → Suppliers

```python
supplier_service.find_preferred_supplier(ingredient_id)
```

## Surplus → Promotions

```json
{
  "product_id": 1,
  "current_stock": 24,
  "expected_sales": 9,
  "expected_surplus": 15,
  "risk": "HIGH"
}
```
