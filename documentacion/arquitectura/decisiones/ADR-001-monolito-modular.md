# ADR-001: Monolito modular

**Estado:** Propuesto en el README principal.

## Contexto

FoodSave tiene varios dominios relacionados y un equipo que trabajará en paralelo. La integración y el despliegue deben mantenerse manejables durante la primera versión.

## Decisión

Usar un monolito modular. Cada dominio mantiene sus propias reglas de negocio, persistencia y API. Las llamadas entre dominios pasan por servicios o contratos, sin acceder directamente al repositorio de otro módulo.

## Consecuencias

Se facilita el desarrollo paralelo y un despliegue inicial sencillo. Hay que vigilar las dependencias entre módulos para conservar sus límites. La extracción de servicios independientes queda para una necesidad real posterior.
