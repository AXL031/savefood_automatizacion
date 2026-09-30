# Guía de desarrollo — Envoltorios de tareas por dominio

**Carpeta:** `backend/app/workers/tasks`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/automatizacion/flujos.md](../../../../docs/automatizacion/flujos.md).

## Punto de partida

`manejadores.py` define `ContextoEjecucion` y el registro explícito `MANEJADORES`. Los adaptadores de Kevin para `PREPARAR_MODELO`, `EVALUAR_MODELO` y `EVALUAR_PRONOSTICO` están registrados; plan y promoción continúan sin manejador y terminan con error visible. Cada dueño registra su función pública `(sesion, contexto) -> dict`, sin commit ni rollback propios. Consultar el resumen vigente de [Axel Cueva](../../../../docs/equipo/avances/cueva.md) y [Kevin Bohorquez](../../../../docs/equipo/avances/bohorquez.md).

Axel mantiene infraestructura; cada dueño implementa la función de su dominio y sus pruebas.

## Trabajo en esta carpeta

1. Crear envoltorios finos de PREPARAR_MODELO, EVALUAR_MODELO, GENERAR_PROPUESTA y EVALUAR_PROMOCION.
2. Kevin implementa entrenamiento/inferencia/evaluación; Max plan; Vera promoción; Aguirre pedido y envío.
3. Usar claves durables y persistir salida/error a través del motor.
4. Separar generación de pedido de intento externo para no reejecutar envío al repetir el plan.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Reentrega usa el resultado persistido y no repite el efecto de dominio.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
