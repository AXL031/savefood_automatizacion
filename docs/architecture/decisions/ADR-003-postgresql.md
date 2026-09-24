# ADR-003: PostgreSQL para persistencia

**Estado:** Propuesto en el documento maestro.

## Decisión

Usar PostgreSQL para los datos operativos y de automatización. Los cambios de esquema se aplicarán con migraciones Alembic.

## Consecuencias

Las entidades del [ERD](../../database/erd.md) deben traducirse a tablas y restricciones concretas durante la implementación. Toda consulta de datos de un negocio debe respetar `business_id`.
