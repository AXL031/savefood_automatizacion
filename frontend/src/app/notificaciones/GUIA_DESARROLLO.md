# Guía de desarrollo — Notificaciones externas futuras

**Carpeta:** `frontend/src/app/notificaciones`.

**Responsable:** Axel Cueva. Custodia documental de una función posterior.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `page.tsx`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../../../docs/equipo/avances/cueva.md) para el último estado.

## Alcance de esta carpeta

Las ejecuciones muestran estado/error dentro de FoodSave. Un centro genérico de avisos queda para otra etapa.

## Trabajo permitido en esta etapa

1. Mantener referencia y guía alineadas con el alcance.
2. No crear rutas, tablas o acciones operativas por la sola existencia de este directorio.
3. Si se amplía el alcance, actualizar contrato, reparto y dependencias antes de implementar.

## Contrato necesario al ampliar

Definir destinatarios, canales y deduplicación. Los pedidos Telegram actuales pertenecen a Compras/Aguirre, no a este módulo. Dependencias previstas: Eventos de automatización y preferencias futuras.

## Criterio de entrega actual

La función se presenta como futura/no implementada y no altera datos ni expone un éxito ficticio. El trabajo futuro no se suma a la carga de la demo.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
