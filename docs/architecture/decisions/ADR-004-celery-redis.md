# ADR-004: Celery y Redis para automatizaciones

**Estado:** Propuesto en el documento maestro.

## Decisión

Usar Redis como broker, Celery para tareas asíncronas y Celery Beat para tareas programadas. Registrar ejecución, verificación, intentos y resultados.

## Consecuencias

Las acciones externas necesitarán una política de reintentos y protección frente a ejecuciones duplicadas. Los horarios deben usar la zona horaria configurada por negocio.
