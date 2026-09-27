# Guía de desarrollo — Recursos públicos de interfaz

**Carpeta:** `frontend/public`.

**Responsable:** Edu Sanchez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../docs/guia-inicio-desarrollo.md).
- [docs/diseno/especificacion-visual.md](../../docs/diseno/especificacion-visual.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Edu Sanchez](../../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

1. Guardar iconos, logos e imágenes estáticas con nombres descriptivos y procedencia conocida.
2. No guardar exportaciones privadas, modelos ML ni archivos de ventas aquí.
3. Optimizar tamaño y definir texto alternativo en el componente que consume el recurso.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Un recurso público no expone datos de negocio ni secretos.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
