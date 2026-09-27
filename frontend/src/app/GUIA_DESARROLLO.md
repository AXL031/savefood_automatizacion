# Guía de desarrollo — Rutas y navegación

**Carpeta:** `frontend/src/app`.

**Responsable:** Edu Sanchez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../docs/guia-inicio-desarrollo.md).
- [docs/api/rutas-api.md](../../../docs/api/rutas-api.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `layout.tsx`, `page.tsx`, `styles.css`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Edu Sanchez](../../../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

1. Mantener layout, estilos y entrada raíz según estado de sesión/inicialización.
2. Cada dueño implementa page.tsx de su dominio usando ProtectedShell y componentes comunes.
3. Mostrar carga, vacío, error y falta de backend; proteger escrituras también en servidor.
4. Las carpetas nuevas de rutas documentales no son páginas disponibles hasta añadir implementación.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Navegación identifica correctamente funciones disponibles y estado de la demo.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
