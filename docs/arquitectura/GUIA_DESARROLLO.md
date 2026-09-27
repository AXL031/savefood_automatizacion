# Guía de desarrollo — Arquitectura e interfaces de módulos

**Carpeta:** `docs/arquitectura`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../equipo/responsabilidades.md).
- [Dependencias entre integrantes](../equipo/dependencias.md).
- [Alcance de la demo](../guia-inicio-desarrollo.md).
- [docs/arquitectura/vision_general.md](vision_general.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](../equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Mantener monolito modular, instalación local y separación API/worker/almacenamiento.
2. Incluir Telegram de pruebas y límites de simulación en las vistas.
3. Documentar cambios de frontera con participación de sus dueños.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Las vistas describen el alcance vigente y los documentos históricos están identificados.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../equipo/avances/cueva.md) siguiendo [la plantilla](../equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
