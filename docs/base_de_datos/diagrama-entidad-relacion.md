# Diagrama entidad-relación

El archivo [diagrama-entidad-relacion.mmd](diagrama-entidad-relacion.mmd) es la única fuente del ER conceptual del prototipo. Sigue [ADR-005](../arquitectura/decisiones/ADR-005-instalacion-local-mvp.md) y [ADR-006](../arquitectura/decisiones/ADR-006-identidades-lotes-pronosticos.md): una instalación local, ventas diarias y stock administrados en PostgreSQL, lotes con movimientos y corridas de pronóstico. Las dos relaciones hacia `MOVIMIENTO_INVENTARIO` son excluyentes por fila: cada movimiento afecta exactamente un lote de ingrediente o uno de producto.

Solo `negocio` y `usuario` existen en `0001_nucleo`. Las demás entidades del diagrama son diseño objetivo de la futura migración `0002`, detalladas en el [diccionario](diccionario-de-datos.md) y el [esquema objetivo](esquema-objetivo-mvp.md).
