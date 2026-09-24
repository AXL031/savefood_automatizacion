# C4 · Contexto

Muestra las personas y los sistemas externos que interactúan con FoodSave.

```mermaid
flowchart LR
    administrador[Administrador del negocio] -->|Usa| foodsave[FoodSave]
    foodsave -->|Envía pedidos| proveedor[Proveedor]
    foodsave -->|Publica promociones| canal[Canal de venta]
    foodsave -->|Envía alertas| avisos[Servicio de notificaciones]
```
