# Guía de desarrollo — Producción física

**Carpeta:** `frontend/src/app/produccion`.

**Responsable:** Leonardo Vera. Custodia documental de una función posterior.

**Bloque:** Inventario por lotes y promociones sugeridas.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Leonardo Vera](../../../../docs/equipo/avances/vera.md) para el último estado.

## Alcance de esta carpeta

La demo guarda un plan sugerido, pero no ejecuta producción ni consumo de insumos.

## Trabajo permitido en esta etapa

1. Mantener referencia y guía alineadas con el alcance.
2. No crear rutas, tablas o acciones operativas por la sola existencia de este directorio.
3. Si se amplía el alcance, actualizar contrato, reparto y dependencias antes de implementar.

## Contrato necesario al ampliar

Definir órdenes/lotes producidos, cantidades reales, consumo de receta, desperdicio y operación atómica antes de crear rutas o tablas. Dependencias previstas: Planificación de Max y movimientos de Inventario de Vera.

## Criterio de entrega actual

La función se presenta como futura/no implementada y no altera datos ni expone un éxito ficticio. El trabajo futuro no se suma a la carga de la demo.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/vera.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
