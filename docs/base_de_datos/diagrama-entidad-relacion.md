# Diagrama entidad-relación

El archivo [diagrama-entidad-relacion.mmd](diagrama-entidad-relacion.mmd) es la única fuente del ER de FoodSave. Corte **21-10-2026**: contiene las **38 tablas, 357 columnas y 67 FK** de los modelos SQLAlchemy del código local, con tipos PostgreSQL, PK, FK, UK individuales, nulabilidad y referencias. Las claves únicas compuestas se identifican en los comentarios como `UQ(nombre)`; no se marca cada participante como único individualmente.

La [estructura física completa](estructura-fisica.md) detalla todas las columnas, tipos con precisión/escala, defaults de servidor/Python, FK y sus acciones ON DELETE, restricciones UNIQUE/CHECK e índices explícitos, incluidos los parciales y funcionales.

## Alcance y estado

Sigue [ADR-005](../arquitectura/decisiones/ADR-005-instalacion-local-mvp.md), [ADR-006](../arquitectura/decisiones/ADR-006-identidades-lotes-pronosticos.md), [ADR-008](../arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md) y [ADR-010](../arquitectura/decisiones/ADR-010-tienda-independiente-payme.md): instalación local, ventas y stock en PostgreSQL, lotes con movimientos, pronósticos y compras por proveedor. Cada movimiento afecta exactamente un lote de ingrediente **o** uno de producto, nunca ambos; el CHECK de exclusión complementa las dos relaciones opcionales del ER.

El dibujo corresponde al **esquema implementado en código hasta `0019_tienda_clientes`**. Incluye `cliente`, incorporada por esa migración al API de identidad de FoodSave; no acredita que 0019 esté aplicada en la instalación habitual ni que catálogo, stock y compras de tienda estén conectados. No se consultó ni modificó la base habitual para producir el ER. La tabla técnica `alembic_version` queda fuera del modelo de dominio.

La tienda independiente mantiene su almacenamiento SQLite de pagos fuera de este ER. No existe FK ni acceso compartido a la base de FoodSave. `negocio` es configuración de instalación única: no se añaden relaciones `negocio_id` inexistentes.

## Uso en la presentación

Copiar todo el contenido del `.mmd` en un editor Mermaid y exportar en SVG para conservar legibilidad al ampliar. El ER completo sirve de respaldo; para la diapositiva, seleccionar un recorrido o ampliar un bloque sin retirar columnas del archivo canónico. Los códigos de tipos `timestamptz` y `jsonb` representan sus tipos PostgreSQL; `numeric` conserva precisión/escala en su comentario.

Definiciones de negocio y dueños: [diccionario](diccionario-de-datos.md). Evolución y migraciones: [esquema](esquema-objetivo-mvp.md). Los cortes históricos de esos documentos no sustituyen el inventario de columnas actual de [estructura física](estructura-fisica.md).
