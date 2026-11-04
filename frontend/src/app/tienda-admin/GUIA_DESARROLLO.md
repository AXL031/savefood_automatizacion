# Catálogo publicado a tienda

04-11-2026 · Lighthouse Desktop: `.shop-catalog-links` subraya los enlaces a Ventas y Operación diaria dentro de la descripción del catálogo. No depender solo del color verde para distinguirlos del párrafo. Ajuste exclusivo de presentación; no cambia publicación, precios ni sincronización.

04-11-2026: selector de nueve categorías, incluidas Comidas preparadas (`comidas`) y Bebidas (`bebidas`). Categoría es metadato versionado de la ficha en `publicacion_producto.datos`, no columna de `producto`. La tienda independiente recibe la clasificación por HTTP y genera sus secciones desde el snapshot. No alterar precios/stock al reclasificar. Referencia y casos pendientes en `datos_carga/referencias/clasificacion_catalogo_tienda.json` desde la raíz.

Coordinación Cueva, dominio tienda Rojas, UI/Productos/Ventas Sanchez. Leer guías padre y docs/api/contrato-integracion-tienda.md. Administración de metadatos/publicación; precio canónico se edita en Ventas. Sesión administrativa solo dentro de FoodSave, ningún secreto de integrador en navegador. Resumen de entrega durable y reservas; stock reservado no equivale a salida física. No publicar automáticamente todos los SKU ni inventar fotos para productos. Actualizar registro Cueva y pruebas consumidor/proveedor.
