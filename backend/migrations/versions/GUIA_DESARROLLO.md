# Guía de desarrollo — Revisiones Alembic

**Carpeta:** `backend/migrations/versions`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../docs/guia-inicio-desarrollo.md).
- [docs/base_de_datos/esquema-objetivo-mvp.md](../../../docs/base_de_datos/esquema-objetivo-mvp.md).

## Punto de partida

**Integración 30-09-2026:** Nuevas revisiones 0005_m01_ingredientes_recetas → 0006_v01_inventario → 0007_l01_proveedores sobre 0004. Las revisiones previamente aplicadas no se reescriben. Delta reversible probado en SQLite; cadena completa PostgreSQL se verifica en CI.

Archivos técnicos observados al preparar esta guía: `0001_nucleo.py`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../../docs/equipo/avances/cueva.md) para el último estado.

Axel coordina integración de revisiones; no asume las tablas de los seis.

**Cadena tras Kevin:** `0001_nucleo → 0001a_configuracion → 0001b_automatizaciones → 0001c_motor → 0002_e01_ventas → 0003_pronosticos`. `0002` agrega catálogo y ventas; `0003` agrega persistencia ML. Las siguientes revisiones de dominio dependen de `0003_pronosticos` o de su sucesora, sin modificar migraciones ya aplicadas. Coordinar tipos, FK y CHECK restantes con sus dueños.

## Integración E03/K01

`0008_e03_modelo` sucede a `0007_l01_proveedores` y añade la FK nullable `configuracion_inicial.preparacion_ejecucion_id`. No altera las revisiones anteriores ni recarga datos.

## Trabajo en esta carpeta

1. Coordinar una sola cadena de revisiones; cada dueño entrega sus tablas/restricciones.
2. Comparar modelos, esquema objetivo y migración antes de integrar.
3. No reescribir 0001 ni revisiones aplicadas por compañeros.
4. Probar upgrade en base vacía y restricciones de unicidad/FK/CHECK; documentar rollback de desarrollo.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Una base nueva llega a head y rechaza cantidades/identidades inválidas según contrato.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Corte M02–M04 · 06-10-2026

`0009_m02_planes` añade plan, elementos y necesidades; FK RESTRICT, unicidad y CHECK de cantidades. Necesidades NUMERIC(18,3); stock desconocido exige disponible/faltante NULL. Solo estado PROPUESTO. Delta reversible y comparación de modelos verificados por las pruebas.
