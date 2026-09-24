# Diagramas de FoodSave

Abre estos archivos Markdown en GitHub para ver sus bloques Mermaid como gráficos:

| Vista | Archivo | Qué muestra |
|---|---|---|
| Arquitectura general | [overview.md](../overview.md) | Flujo entre web, API, base de datos y workers |
| Contexto C4 | [context.md](../c4/context.md) | Administrador y sistemas externos |
| Contenedores C4 | [containers.md](../c4/containers.md) | Aplicación web, API, worker, PostgreSQL y Redis |
| Componentes C4 | [components.md](../c4/components.md) | Módulos principales y orquestación |
| Entidad-relación | [erd.md](../../database/erd.md) | Entidades y cardinalidades conceptuales |

Para el **ERD**, abre [`docs/database/erd.md`](../../database/erd.md) en GitHub. También puedes abrir el código fuente [`foodsave-erd.mmd`](../../database/foodsave-erd.mmd) en GitHub o pegarlo en [Mermaid Live Editor](https://mermaid.live/). Si ves texto en lugar del dibujo, usa una vista previa de Markdown compatible con Mermaid.

Las vistas C4 de contexto y contenedores se adaptaron a diagramas de flujo Mermaid para facilitar su visualización; la vista de componentes conserva el flujo del documento maestro. El ERD es conceptual: no sustituye al esquema real de PostgreSQL.
