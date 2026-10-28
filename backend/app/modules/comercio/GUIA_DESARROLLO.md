# Comercio por API · integración de tienda

Solicitud de Axel, 28-10-2026. Coordinación Cueva; tienda Rojas, Ventas/UI Sanchez e Inventario/Promociones Vera. Leer guías padre, responsabilidades/dependencias y [contrato](../../../../docs/api/contrato-integracion-tienda.md). No importar código de tienda ni abrir su base.

Publicación comercial versionada hacia la API de tienda; cotización/reserva y consumo sobre el inventario canónico. Ticket TIENDA en Ventas, sin usuarios ficticios ni escritura en venta_diaria/ML. Solo Payme de preproducción verificado por el backend de tienda. Bearer de integración limitado, separado del administrativo y de Payme. Servicios no confirman; HTTP externo siempre fuera de transacciones de negocio. Reservas, presencial y ajustes comparten el bloqueo de lotes. No reescribir migraciones anteriores; nueva 0024. Worker de publicación independiente de Telegram. Pruebas aisladas, sin seeds sobre la base habitual.
