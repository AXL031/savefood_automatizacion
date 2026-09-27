# Guía de desarrollo — Raíz y coordinación del repositorio

**Carpeta:** `.`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](AGENTS.md).
- [Reparto vigente y criterios de entrega](docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](docs/equipo/dependencias.md).
- [Alcance de la demo](docs/guia-inicio-desarrollo.md).
- [docs/base-para-desarrollo.md](docs/base-para-desarrollo.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `.env.example`, `.gitignore`, `compose.yaml`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](docs/equipo/avances/cueva.md) para el último estado.

Axel coordina la raíz; los seis responden por su propio bloque. La revisión documental no declara implementados los módulos.

## Trabajo en esta carpeta

1. Mantener README como entrada al alcance y reparto vigente; enlazar el mapa de carpetas.
2. Integrar manifiestos, Compose y variables de entorno con los requisitos aportados por cada bloque.
3. Mantener una revisión por cambio y evidencia de integración por cada frontera.
4. Preservar datos históricos, cambios locales y secretos fuera de Git.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

README, reparto, diccionario y guías atribuyen el mismo dueño; un compañero puede ubicar su tarea y reproducir el núcleo.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](docs/equipo/avances/cueva.md) siguiendo [la plantilla](docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
