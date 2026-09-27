# Guía de desarrollo — Worker y Celery Beat

**Carpeta:** `backend/app/workers`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../docs/guia-inicio-desarrollo.md).
- [docs/automatizacion/programacion.md](../../../docs/automatizacion/programacion.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `__init__.py`, `celery_app.py`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Configurar broker, registro de tareas, scheduler y recuperación.
2. Pasar IDs y claves a servicios públicos; no copiar algoritmos del dominio aquí.
3. Integrar dependencias/volúmenes de ML con Kevin y credencial de Telegram con Aguirre.
4. Mantener la prueba existente y agregar tareas reales según contratos.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Worker reiniciado retoma trabajo durable y UI conserva intentos.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
