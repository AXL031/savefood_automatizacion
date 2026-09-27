# Guía de desarrollo — Aplicación web común

**Carpeta:** `frontend`.

**Responsable:** Edu Sanchez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida.

## Leer antes de trabajar

- [Instrucciones para IA](../AGENTS.md).
- [Reparto vigente y criterios de entrega](../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../docs/equipo/dependencias.md).
- [Alcance de la demo](../docs/guia-inicio-desarrollo.md).
- [docs/diseno/especificacion-visual.md](../docs/diseno/especificacion-visual.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `.dockerignore`, `Dockerfile`, `next-env.d.ts`, `next.config.ts`, `package-lock.json`, `package.json`, `tsconfig.json`, `tsconfig.tsbuildinfo`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Edu Sanchez](../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

1. Mantener estructura Next.js/TypeScript, scripts y estilos compartidos.
2. Coordinar navegación y componentes; cada dueño construye sus pantallas completas.
3. Axel mantiene contrato de sesión; Kevin panel/gráficos; Max plan; Vera stock/promoción; Aguirre compras.
4. Verificar typecheck y build cuando cambie código de UI.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Las pantallas usan servicios comunes, no presentan una operación no implementada como completada.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
