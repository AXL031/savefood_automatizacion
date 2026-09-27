# Guía de desarrollo — Informes operativos futuros

**Carpeta:** `frontend/src/app/informes`.

**Responsable:** Kevin Bohorquez. Custodia documental de una función posterior.

**Bloque:** Modelo predictivo, evaluación histórica y dashboard.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Kevin Bohorquez](../../../../docs/equipo/avances/bohorquez.md) para el último estado.

## Alcance de esta carpeta

El dashboard histórico de la demo vive en Pronósticos y /panel; aquí se reserva la evolución operativa.

## Trabajo permitido en esta etapa

1. Mantener referencia y guía alineadas con el alcance.
2. No crear rutas, tablas o acciones operativas por la sola existencia de este directorio.
3. Si se amplía el alcance, actualizar contrato, reparto y dependencias antes de implementar.

## Contrato necesario al ampliar

Definir indicadores, periodos y fuentes antes de crear informes económicos; no duplicar la evaluación histórica aquí. Dependencias previstas: Lecturas públicas de los dominios y métricas existentes de Pronósticos.

## Criterio de entrega actual

La función se presenta como futura/no implementada y no altera datos ni expone un éxito ficticio. El trabajo futuro no se suma a la carga de la demo.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/bohorquez.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
