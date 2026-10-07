# ADR-002: FastAPI para la API

**Estado:** Aceptado e implementado.

## Decisión

Usar Python y FastAPI para las rutas HTTP; Pydantic para validación, SQLAlchemy para persistencia y Alembic para migraciones. Las funciones de las rutas delegarán las reglas de negocio a los servicios.

## Consecuencias

Los contratos HTTP podrán documentarse con OpenAPI. La autorización es por rol (Administrador/Operador) sobre el único negocio de la instalación ([ADR-005](ADR-005-instalacion-local-mvp.md)), con el sobre de error acordado.
