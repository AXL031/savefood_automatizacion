# ADR-003: PostgreSQL para persistencia

**Estado:** Propuesto en el README principal.

## Decisión

Usar PostgreSQL para los datos operativos y de automatización. Los cambios de esquema se aplicarán con migraciones Alembic.

## Consecuencias

Las entidades del [diagrama entidad-relación](../../base_de_datos/diagrama-entidad-relacion.md) deben traducirse a tablas y restricciones concretas durante la implementación. Toda consulta de datos de un negocio debe respetar `negocio_id`.
