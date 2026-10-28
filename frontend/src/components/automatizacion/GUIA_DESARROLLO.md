# Guía de desarrollo — Presentación de ejecución

**Carpeta:** `frontend/src/components/automatizacion`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/automatizacion/programacion.md](../../../../docs/automatizacion/programacion.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](../../../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

**Disponible desde 21-10-2026:** `FlujoEjecucion` y `estadoFlujo` presentan cuatro etapas confirmadas por el estado de ejecución, tiempo transcurrido, reintento, desconexión y resultados. Las tres tarjetas de dominio explican pronóstico/plan/compras: no indican cuál está calculándose. Los IDs se validan antes de enlazar y COMPLETADA no acredita envío ni evaluación posterior. Diseño adaptable a móvil y movimiento reducido; la desconexión detiene la animación. Pruebas: `node scripts/verificar-flujo-automatizacion.cjs` (SSR y estados, sin APIs); no equivale a revisión visual del navegador.

1. Mostrar estado, intento, hora programada/disparada y reloj histórico.
2. Enlazar IDs de resultados y renderizar error sin secretos.
3. Distinguir espera/reintento/fallo de envío incierto, cuyo dueño es Compras.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Una ejecución fallida puede rastrearse hasta el intento y el efecto alcanzado.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.


## Pruebas repetibles autorizadas · 21-10-2026

FlujoEjecucion identifica la modalidad Prueba repetible desde parametros.prueba_repetible de la ejecución; no la deduce del número de pedidos. Consulta y pasos generales sin cambios. Las salidas continúan enlazando IDs reales.
