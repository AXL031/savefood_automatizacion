# C4 · Contexto

Muestra el alcance del prototipo. El destinatario de Telegram es un chat de pruebas que simula al proveedor; la publicación de promociones y las notificaciones externas quedan para después.

```mermaid
flowchart LR
    administrador[Administrador del negocio] -->|Usa| foodsave[FoodSave]
    foodsave -->|Envía pedido de demostración| telegram[Telegram Bot API]
    telegram -->|Entrega mensaje| proveedor[Chat de pruebas del proveedor]
```
