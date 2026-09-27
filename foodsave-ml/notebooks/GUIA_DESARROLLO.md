# Guía de desarrollo — Notebook experimental

**Carpeta:** `foodsave-ml/notebooks`.

**Responsable:** Kevin Bohorquez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Modelo predictivo, evaluación histórica y dashboard.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../docs/guia-inicio-desarrollo.md).
- [foodsave-ml/EXPERIMENTOS_CATBOOST.md](../EXPERIMENTOS_CATBOOST.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `foodsave_colab.ipynb`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Kevin Bohorquez](../../docs/equipo/avances/bohorquez.md) para el último estado.

## Trabajo en esta carpeta

1. Conservar pasos reproducibles, semilla, datos/partición y resultados interpretables.
2. Comparar implementación extraída con el notebook y documentar divergencias.
3. No exportar un artefacto como listo_demo sin versión, huella y contrato completo.
4. Conservar test fuera del ajuste y rotular evaluación histórica exploratoria.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Notebook verificable y artefacto recargado dan resultados consistentes dentro del contrato.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../docs/equipo/avances/bohorquez.md) siguiendo [la plantilla](../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
