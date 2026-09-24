# ADR-002: FastAPI para la API

**Estado:** Propuesto en el README principal.

## Decisión

Usar Python y FastAPI para las rutas HTTP; Pydantic para validación, SQLAlchemy para persistencia y Alembic para migraciones. Las funciones de las rutas delegarán las reglas de negocio a los servicios.

## Consecuencias

Los contratos HTTP podrán documentarse con OpenAPI. La implementación debe mantener la autorización por negocio y las respuestas de error acordadas.
