# ADR-003: PostgreSQL para persistencia

**Estado:** Propuesto en el README principal.

## Decisión

Usar PostgreSQL para los datos operativos y de automatización. Los cambios de esquema se aplicarán con migraciones Alembic.

## Consecuencias

Las entidades del [diagrama entidad-relación](../../base_de_datos/diagrama-entidad-relacion.md) deben traducirse a tablas y restricciones concretas durante la implementación. Para el MVP, [ADR-005](ADR-005-instalacion-local-mvp.md) sustituye la separación por `negocio_id`: cada comercio tiene su propia instalación y base de datos.
