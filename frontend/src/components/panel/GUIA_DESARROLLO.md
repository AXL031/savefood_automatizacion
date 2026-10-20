# Guía de desarrollo — Composición del dashboard histórico

**Carpeta:** `frontend/src/components/panel`.

**Responsable:** Kevin Bohorquez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Modelo predictivo, evaluación histórica y dashboard.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [foodsave-ml/POLITICA_EVALUACION.md](../../../../foodsave-ml/POLITICA_EVALUACION.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Kevin Bohorquez](../../../../docs/equipo/avances/bohorquez.md) para el último estado.

## Trabajo en esta carpeta

1. Componer tarjetas, filtros, serie y detalle del día evaluado.
2. Consumir métricas de Pronósticos y enlazar corrida/plan/ejecución.
3. Mostrar alcance histórico y cobertura; no inventar ahorros o impacto económico.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Total previsto y real usan exactamente los mismos productos evaluables.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/bohorquez.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.


## Avance K03/K04 y E01/E02 · 20-10-2026

Codex a solicitud del usuario; se conserva la responsabilidad de los dominios. Analitica.tsx publica NavegacionAnalitica, IndicadoresEvaluacion, ParticionModelo, IconoAnalitica y numeroAnalitica. Consumidos por Inicio, Pronósticos, Evaluación y Reportes. Props tipadas del contrato vigente, null como Sin dato y cifras sin precisión comercial inventada.

[Contrato y ejemplos vigentes](../../../../docs/api/contratos.md#k03k04-y-frontera-e01--20-10-2026). [Pruebas, consumidores y límites del corte](../../../../docs/equipo/avances/bohorquez.md). Sin migraciones nuevas; no se acredita PostgreSQL/Redis, CI remoto ni envío real por la QA visual.
