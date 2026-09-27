# Guía de desarrollo — Herramientas de desarrollo y verificación

**Carpeta:** `scripts`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../AGENTS.md).
- [Reparto vigente y criterios de entrega](../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../docs/equipo/dependencias.md).
- [Alcance de la demo](../docs/guia-inicio-desarrollo.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Agregar solo scripts reproducibles que apoyen arranque, fixtures o verificación.
2. Edu aporta generación de plantillas, Kevin verificación ML; cada script identifica su dueño.
3. Usar rutas explícitas y no borrar volúmenes/datos por defecto.
4. Documentar requisitos, entradas, salida y código de error.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Otra persona ejecuta el script con instrucciones y obtiene un resultado verificable.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
