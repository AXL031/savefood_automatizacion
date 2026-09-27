# Guía de desarrollo — Reparto, coordinación y traspasos

**Carpeta:** `docs/equipo`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](responsabilidades.md).
- [Dependencias entre integrantes](dependencias.md).
- [Alcance de la demo](../guia-inicio-desarrollo.md).
- [docs/equipo/dependencias.md](dependencias.md).
- [docs/equipo/avances/README.md](avances/README.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](avances/cueva.md) para el último estado.

Axel coordina documentos de equipo; cada autor es responsable de su avance.

## Trabajo en esta carpeta

1. Mantener responsabilidades como fuente única y mapa por carpeta.
2. Actualizar dependencias indicando qué se puede adelantar y qué bloquea integración.
3. Cada integrante mantiene su registro de avances y entrega contrato/prueba al consumidor.
4. Revisar equilibrio al primer corte sin ampliar artificialmente alcance.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

El siguiente responsable consulta registro y contrato para continuar sin inspeccionar todo el repositorio.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](avances/cueva.md) siguiendo [la plantilla](avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
