# ADR-002: FastAPI para la API

**Estado:** Propuesto en el documento maestro.

## Decisión

Usar Python y FastAPI para los endpoints HTTP; Pydantic para validación, SQLAlchemy para persistencia y Alembic para migraciones. Los routers delegarán las reglas de negocio a los servicios.

## Consecuencias

Los contratos HTTP podrán documentarse con OpenAPI. La implementación debe mantener la autorización por negocio y las respuestas de error acordadas.
