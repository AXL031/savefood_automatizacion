# ADR-003: PostgreSQL para persistencia

**Estado:** Aceptado e implementado.

## Decisión

Usar PostgreSQL para los datos operativos y de automatización. Los cambios de esquema se aplicarán con migraciones Alembic.

## Consecuencias

Las entidades del [diagrama entidad-relación](../../base_de_datos/diagrama-entidad-relacion.md) se traducen a tablas y restricciones en el [esquema](../../base_de_datos/esquema-objetivo-mvp.md). Por [ADR-005](ADR-005-instalacion-local-mvp.md) no hay `negocio_id`: cada comercio tiene su propia instalación y base de datos.
