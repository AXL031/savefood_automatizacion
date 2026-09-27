# Guía de desarrollo — Decisiones arquitectónicas

**Carpeta:** `docs/arquitectura/decisiones`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../equipo/dependencias.md).
- [Alcance de la demo](../../guia-inicio-desarrollo.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](../../equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Registrar motivo, decisión, consecuencias y estado cuando cambie un contrato fundamental.
2. Respetar ADR-008 para pedido/Telegram y documentar ampliaciones explícitas.
3. Cada dueño aporta decisiones de su dominio; enlazar ADR reemplazado si aplica.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Una decisión puede rastrearse a su impacto y al contrato afectado.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../equipo/avances/cueva.md) siguiendo [la plantilla](../../equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
