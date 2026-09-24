# Diagramas

Abre estos archivos Markdown en GitHub para ver sus bloques Mermaid como gráficos:

| Vista | Archivo | Qué muestra |
|---|---|---|
| Arquitectura general | [vision_general.md](../vision_general.md) | Flujo entre web, API, base de datos y trabajadores |
| Contexto C4 | [contexto.md](../c4/contexto.md) | Administrador y sistemas externos |
| Contenedores C4 | [contenedores.md](../c4/contenedores.md) | Aplicación web, API, trabajador, PostgreSQL y Redis |
| Componentes C4 | [componentes.md](../c4/componentes.md) | Módulos principales y orquestación |
| Entidad-relación | [diagrama-entidad-relacion.md](../../base_de_datos/diagrama-entidad-relacion.md) | Entidades y cardinalidades conceptuales |

Para el **diagrama entidad-relación**, abre [`documentacion/base_de_datos/diagrama-entidad-relacion.md`](../../base_de_datos/diagrama-entidad-relacion.md) en GitHub. También puedes abrir el código fuente [`diagrama-entidad-relacion.mmd`](../../base_de_datos/diagrama-entidad-relacion.mmd) en GitHub o pegarlo en el [editor interactivo de Mermaid](https://mermaid.live/). Si ves texto en lugar del dibujo, usa una vista previa de Markdown compatible con Mermaid.

Las vistas C4 de contexto y contenedores se adaptaron a diagramas de flujo Mermaid para facilitar su visualización; la vista de componentes conserva el flujo descrito en el [README principal](../../../README.md). El diagrama entidad-relación es conceptual: no sustituye al esquema real de PostgreSQL.
