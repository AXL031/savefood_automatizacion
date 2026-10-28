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

## Integración E03/K01

E03/K01: el motor notifica inicio antes del cálculo y fallo tras rollback del savepoint o recuperación de lease. Los callbacks no hacen commit. El dominio mantiene su estado sin perder intentos ni duplicar datos.

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

## Despacho L03 del paso 6 · 30-09-2026

celery_app registra foodsave.despachar_envios_pedidos cada 30s y foodsave.enviar_pedido; ambas delegan a compras.envios. Broker lleva solo ID/token de despacho, nunca token Telegram ni mensaje. Publicación después del commit con lease recuperable solo antes de ENVIANDO; envío externo usa transacciones separadas y nunca el retry del motor común. API/worker comparten configuración cifrada; worker lee volumen y conserva evidencia en PostgreSQL. Reiniciar API/worker/Beat tras actualizar imágenes y aplicar 0013. Revisión manual y fallos mínimos disponibles; automático/conciliación pendiente del paso 7. Ver contrato-pedidos y avance de Aguirre.

## Conciliación de cueva

Conciliación 06-10-2026: se conservan callbacks y recuperación remotos. Las comparaciones de fechas persistidas normalizan UTC también en SQLite de pruebas; la política de despacho PostgreSQL no cambia.

## Corte vigente · 11-10-2026 · Flujo y promociones

Codex para Axel implementó configuración reutilizable, comprobación de requisitos por interfaces públicas, calendario histórico diario de 1–31 días, modelo/modo conservados y pausa/cancelación/reprogramación de tareas sin despacho. Promociones tienen regla inmutable versionada, reserva transaccional después de cada ajuste nuevo de producto y evaluación idempotente con snapshot/motivo; API y pantalla reales. Se conserva la propiedad de cada dominio.

[Contrato vigente, APIs y límites](../../../docs/api/contrato-flujo-promociones.md). Aplicar `0015_flujo_promociones` antes de actualizar API/worker/Beat. El diagnóstico no ejecuta inferencia ni envía mensajes; guardar configuración no agenda. Consultas de tareas/evaluaciones admiten paginación real con total. La pausa no recupera horas perdidas: reprogramar antes de reanudar. Deshabilitar promociones afecta ajustes nuevos; tareas ya reservadas conservan su versión. Hora simulada de evaluación avanza por el tiempo real transcurrido desde el ajuste para comprobar frescura.

Las notas fechadas de cortes anteriores son historial; no usar sus pendientes como estado actual. Pruebas y límites finales en los registros Cueva/Vera/Sanchez, incluyendo PostgreSQL/Redis y Telegram real solo si fueron ejecutados. No confundir fixtures QA con datos de operación.

## Acoplamiento de Bohorquez · 28-10-2026

Backport adaptado 4c2a271: [contrato de operaciones](../../../docs/api/contrato-operacion-integrada.md). Conserva tienda independiente por HTTP, caja y entradas múltiples de Cueva. Nueva migración 0023 sobre 0022; producción explícita, recepción asistida, avisos/monitor. No publica en tienda ni altera histórico/ML. Evidencia y límites en el registro de Cueva.
