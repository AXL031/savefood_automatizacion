# Guía de desarrollo — Integración continua

**Carpeta:** `.github/workflows`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../docs/guia-inicio-desarrollo.md).
- [docs/equipo/arranque-modulos.md](../../docs/equipo/arranque-modulos.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `base-ci.yml`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Mantener base-ci.yml con instalación reproducible y validación de Compose.
2. Integrar pruebas unitarias y de frontera que aporta cada responsable.
3. Comprobar migraciones, API y cola; incorporar Beat cuando exista su implementación.
4. Sustituir Telegram por un adaptador falso en CI y mostrar registros de fallo sin secretos.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

El flujo falla ante una regresión significativa y detiene servicios al terminar; documentar lo no cubierto.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
