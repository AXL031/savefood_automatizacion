# Guía de desarrollo — Adaptadores externos

**Carpeta:** `backend/app/integrations`.

**Responsable:** Leonardo Aguirre. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Proveedores, pedidos y Telegram.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-pedidos.md](../../../docs/api/contrato-pedidos.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Leonardo Aguirre](../../../docs/equipo/avances/aguirre.md) para el último estado.

Aguirre coordina la integración activa; canales de venta pertenecen a Vera y avisos futuros a Axel.

## Trabajo en esta carpeta

1. Separar protocolos externos de estados y reglas de negocio.
2. Implementar Telegram para compras dentro de proveedores.
3. Definir un adaptador falso para pruebas deterministas y uno real para el chat de la demo.
4. Normalizar éxito, fallo definitivo y resultado incierto sin ocultar errores.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Compras se prueba sin red y puede ejecutar el adaptador real sin exponer token.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../docs/equipo/avances/aguirre.md) siguiendo [la plantilla](../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
