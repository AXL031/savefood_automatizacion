# Guía de desarrollo — Pruebas unitarias por dominio

**Carpeta:** `backend/tests/unit`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../docs/guia-inicio-desarrollo.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `test_reglas_promociones.py`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Max prueba fórmulas y redondeo; Vera vigencia/regla; Aguirre conversión y estados; Edu normalización; Kevin características/métricas; Axel permisos/reintentos.
2. Conservar pruebas existentes de promociones y ampliarlas solo por casos nuevos.
3. Fijar reloj/datos para obtener resultados deterministas.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Los casos incluyen límites del dominio y no solo copian la implementación.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
