# Guía de desarrollo — Canales de venta futuros

**Carpeta:** `backend/app/integrations/canales_venta`.

**Responsable:** Leonardo Vera. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Inventario por lotes y promociones sugeridas.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/vision-futura.md](../../../../docs/vision-futura.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Leonardo Vera](../../../../docs/equipo/avances/vera.md) para el último estado.

Fuera de la implementación actual; responsable es custodio documental.

## Trabajo en esta carpeta

1. Mantener esta carpeta como reserva del diseño futuro.
2. Antes de implementar, acordar publicación/reversión de precio, identidad de producto y confirmación externa.
3. Conservar promoción sugerida dentro del módulo actual sin simular publicación.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

La demo no llama un POS ni presenta descuentos como activos.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/vera.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
