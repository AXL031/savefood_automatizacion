# Guía de desarrollo — Aplicación backend y dependencias

**Carpeta:** `backend`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../AGENTS.md).
- [Reparto vigente y criterios de entrega](../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../docs/equipo/dependencias.md).
- [Alcance de la demo](../docs/guia-inicio-desarrollo.md).
- [docs/arquitectura/vision_general.md](../docs/arquitectura/vision_general.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `.dockerignore`, `Dockerfile`, `alembic.ini`, `pyproject.toml`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Mantener pyproject.toml y Dockerfile consistentes y reproducibles.
2. Incorporar dependencias ML propuestas por Kevin y lector de archivos de Edu.
3. Acordar configuración y acceso a artefactos entre API y worker.
4. Cada dueño implementa y prueba su módulo completo bajo app/modules.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

La imagen arranca y los módulos registrados respetan las mismas convenciones.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
