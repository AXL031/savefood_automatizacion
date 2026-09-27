# Guía de desarrollo — Tipos de contratos

**Carpeta:** `frontend/src/types`.

**Responsable:** Edu Sanchez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contratos.md](../../../docs/api/contratos.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `api.ts`, `autenticacion.ts`, `automatizacion.ts`, `notificacion.ts`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Edu Sanchez](../../../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

1. Cada dueño mantiene request/response de su dominio; Edu coordina organización.
2. Axel alinea estados de ejecución con esquema de demo y Aguirre los de pedido.
3. Representar null, decimales, fechas y paginación como en API.
4. Distinguir contratos propuestos de implementados; no agregar campos por lo que muestra una maqueta.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Typecheck y ejemplos de API coinciden en campos y estados.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
