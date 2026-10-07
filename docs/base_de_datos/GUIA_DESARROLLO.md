# Guía de desarrollo — Modelo de datos compartido

**Carpeta:** `docs/base_de_datos`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../equipo/responsabilidades.md).
- [Dependencias entre integrantes](../equipo/dependencias.md).
- [Alcance de la demo](../guia-inicio-desarrollo.md).
- [docs/base_de_datos/esquema-objetivo-mvp.md](esquema-objetivo-mvp.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `diagrama-entidad-relacion.mmd`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Cada dueño define columnas, nulabilidad, precisión, FK, CHECK e índices de sus entidades.
2. Axel coordina consistencia ER/diccionario/esquema y orden de migración.
3. Edu posee producto/venta/inicialización; Max receta/plan; Kevin ML; Vera stock/promoción; Aguirre compra.
4. Cada tabla nueva va en una revisión al final de la cadena; no se reescriben migraciones aplicadas.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

La tabla de propiedad coincide con reparto; SQL objetivo y API usan las mismas identidades.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../equipo/avances/cueva.md) siguiendo [la plantilla](../equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
