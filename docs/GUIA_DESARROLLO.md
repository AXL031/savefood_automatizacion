# Guía de desarrollo — Documentación normativa e índice

**Carpeta:** `docs`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../AGENTS.md).
- [Reparto vigente y criterios de entrega](equipo/responsabilidades.md).
- [Dependencias entre integrantes](equipo/dependencias.md).
- [Alcance de la demo](guia-inicio-desarrollo.md).
- [docs/equipo/responsabilidades.md](equipo/responsabilidades.md).
- [docs/equipo/dependencias.md](equipo/dependencias.md).
- [docs/equipo/avances/README.md](equipo/avances/README.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

**26-10-2026 · Propuesta de dos simuladores:** [plan de exposición](equipo/plan-ventas-vivo-simulacion.md#propuesta-vigente--26-10-2026--dos-simuladores-para-la-exposición), uno desde Ventas y otro desde tienda, solos o coordinados por API. Cierre con ventas consolidadas, evaluación previa, nuevo entrenamiento y pronóstico siguiente, todo en instalación aislada. Definición documental; no es funcionalidad implementada ni modifica la política ML vigente.

**26-10-2026 · Bases de Ventas, solo definición:** [bases del módulo](equipo/bases-modulo-ventas.md) y [contrato propuesto](api/contrato-ventas-operativas.md). Registro presencial y futura integración HTTP bidireccional de tienda; no implementa caja, endpoints, migraciones, reservas o cierre ML. La carga/historial no se presenta como el módulo operativo. Actualización documental por Codex para Axel, con responsables de cada dominio conservados.

1. Mantener entradas a alcance, reparto, contratos, dependencias y avances.
2. Distinguir documentación de diseño de funcionalidad verificada.
3. Cada dueño mantiene la especificación de su dominio y enlaces del consumidor.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Un desarrollador encuentra dueño, contrato, estado y siguiente entrega sin revisar todo el código.

## Informe parcial académico V2

Entrega documental preparada el 22-10-2026 para el corte académico del 21-10-2026,
Grupo 1: [Word editable](../entregables/FoodSave-informe-parcial-V2.docx) y
[PDF](../entregables/FoodSave-informe-parcial-V2.pdf). Sigue la pauta del curso y la
portada Word proporcionadas por Axel. Distingue resultados previos registrados de
pruebas nuevas, diseño pendiente y ampliaciones de tienda. Las observaciones
académicas de V1 no se recibieron y su conciliación sigue pendiente. No modifica
contratos ni acredita otra ejecución funcional del sistema. Registro en
[Cueva](equipo/avances/cueva.md).

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](equipo/avances/cueva.md) siguiendo [la plantilla](equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
