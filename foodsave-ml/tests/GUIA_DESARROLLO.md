# Guía de desarrollo — Pruebas ML y normalizador

**Carpeta:** `foodsave-ml/tests`.

**Responsable:** Kevin Bohorquez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Modelo predictivo, evaluación histórica y dashboard.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../docs/guia-inicio-desarrollo.md).
- [foodsave-ml/POLITICA_EVALUACION.md](../POLITICA_EVALUACION.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `test_normalizar_ventas.py`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Kevin Bohorquez](../../docs/equipo/avances/bohorquez.md) para el último estado.

## Trabajo en esta carpeta

1. Kevin prueba ventanas temporales, ausencias, cobertura, artefacto y métricas.
2. Edu mantiene test_normalizar_ventas.py y casos de entrada a la frontera canónica.
3. Probar que modificar la venta objetivo no altera su vector de inferencia.
4. Evitar entrenamientos largos en cada prueba unitaria; reservar la verificación completa para el gate pertinente.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Los casos detectan fuga temporal y confusión entre ausencia y cero.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../docs/equipo/avances/bohorquez.md) siguiendo [la plantilla](../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
