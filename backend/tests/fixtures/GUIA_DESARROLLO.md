# Guía de desarrollo — Datos de ejemplo para integración

**Carpeta:** `backend/tests/fixtures`.

**Responsable:** Edu Sanchez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-importaciones.md](../../../docs/api/contrato-importaciones.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Edu Sanchez](../../../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

1. Preparar CSV/XLSX de ventas, productos, ingredientes, recetas y stock con claves coherentes.
2. Max aporta recetas/cantidades, Vera lotes, Kevin ventanas de historial, Aguirre ofertas y chat ficticio.
3. Agregar variantes inválidas: SKU ajeno, duplicado, stock negativo, unidad incorrecta y archivo con error tardío.
4. Usar datos sintéticos y evitar números, tokens o chat_id reales.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

El fixture válido permite recorrer la demo; cada inválido provoca el error esperado sin persistencia parcial.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
