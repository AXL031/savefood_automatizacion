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

**Paso 1 · 30-09-2026:** El motor invoca callbacks públicos AL_INICIAR/AL_FALLAR: inicio se confirma con intento durable antes del handler largo; fallo después del rollback del efecto y recuperación por lease se confirman con su estado. E03 mantiene ENTRENANDO visible y conserva datos ante caída.

**A03 implementado:** `celery_app.py` registra el despacho de Beat cada 30 segundos y la tarea de ejecución; `motor.py` reclama con `SKIP LOCKED`, confirma el token y lease antes de publicar, registra intentos y recupera leases vencidos. El efecto local y la finalización se confirman en una misma transacción. Consultar el resumen vigente de [Axel Cueva](../../../docs/equipo/avances/cueva.md) para el último estado.

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
