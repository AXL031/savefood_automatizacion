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

**Integración 30-09-2026:** CI comprueba alembic check después del upgrade y ejecuta A03/V02 en PostgreSQL/Redis con flags explícitos. Las pruebas V02 crean y eliminan solo sus esquemas aislados.

Archivos técnicos observados al preparar esta guía: `base-ci.yml`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

**A01:** `base-ci.yml` incluye la prueba de contrato HTTP y configuración de Axel con SQLite aislado. El paso de Compose aplica también `0001a_configuracion` en PostgreSQL. Esta prueba no sustituye las futuras pruebas de Beat, Compras o consumidores.

**A02:** el paso Python incluye `test_programaciones_a02.py` y el upgrade de Compose alcanza `0001b_automatizaciones`. El CI remoto todavía debe ejecutarse al publicar los cambios.

**A03:** el paso Python incluye toda la suite `backend/tests/integration`; el paso Docker aplica `0001c_motor` al iniciar Compose y ejecuta la prueba A03 aislada con PostgreSQL y Redis. La validación remota sigue pendiente hasta publicar estos cambios.

**A04:** el flujo se dispara en push de cualquier rama y PR, instala el extra `ml`, exige `alembic current --check-heads` y prueba que worker puede escribir y API leer el mismo volumen de artefactos. El token Telegram permanece vacío en CI; ningún paso envía mensajes externos. Confirmar la ejecución remota antes de declararla validada.

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
