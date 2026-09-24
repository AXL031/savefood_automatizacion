# FoodSave

FoodSave es una plataforma SaaS para planificar producción y abastecimiento y prevenir desperdicio de alimentos perecibles. Este repositorio contiene el **esqueleto de trabajo** basado en el [documento técnico maestro](FoodSave_documento_tecnico_maestro.md). Las carpetas de código están preparadas para el desarrollo; todavía no hay una aplicación ejecutable.

## Por dónde empezar

1. Lee la [visión de arquitectura](docs/architecture/overview.md) y las [responsabilidades por módulo](docs/team/responsibilities.md).
2. Abre el [índice de diagramas](docs/architecture/diagrams/README.md), donde están el contexto, los contenedores, los componentes y el [modelo entidad-relación](docs/database/erd.md).
3. Consulta los [endpoints propuestos](docs/api/endpoints.md) y los [contratos entre módulos](docs/api/contracts.md) antes de implementar integraciones.
4. Trabaja en `frontend/src` y `backend/app/modules` según el módulo asignado. Cada carpeta tiene un `README.md` con su propósito.

## Organización

| Carpeta | Contenido |
|---|---|
| [`docs/`](docs/README.md) | Arquitectura, API, base de datos, automatización y equipo |
| [`frontend/`](frontend/README.md) | Interfaz Next.js y funciones por dominio |
| [`backend/`](backend/README.md) | API FastAPI, módulos, workers y pruebas |
| [`scripts/`](scripts/README.md) | Futuros scripts de apoyo |
| [`.github/workflows/`](.github/workflows/README.md) | Futuros pipelines de CI |

La distribución es por **módulo completo**: cada responsable implementa frontend, backend y APIs de su dominio. Consulta [la sección 16](docs/team/responsibilities.md) para los límites de cada módulo. Los elementos transversales `Auth`, `Businesses`, `Products`, `Recipes` e `Ingredients` siguen pendientes de asignación explícita.

## Estado actual

Es un repositorio documental y estructural. Los manifiestos de dependencias, Dockerfiles, migraciones, pipelines y archivos de código se crearán al iniciar la implementación de cada fase. No se han añadido archivos vacíos que aparenten una aplicación funcional.
