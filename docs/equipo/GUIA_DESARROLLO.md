# Guía de desarrollo — Reparto, coordinación y traspasos

## Plan de ampliación · 15-10-2026

**26-10-2026 · Ampliación de propuesta:** el [plan vigente de dos simuladores](plan-ventas-vivo-simulacion.md#propuesta-vigente--26-10-2026--dos-simuladores-para-la-exposición) añade controles desde Ventas y desde tienda, ejecución individual/conjunta, reloj por API, tablas en vivo y cierre D → evaluación del pronóstico previo → nuevo modelo con D → pronóstico D+1. Datos/modelos/colas aislados; simuladores y ciclo ML siguen sin implementar. Jornada acelerada y tiempo real de cierre/entrenamiento se muestran separados. Prevalece esta ampliación sobre las decisiones preliminares de la simulación única del 15-10.

[plan-ventas-vivo-simulacion.md](plan-ventas-vivo-simulacion.md) describe tickets, reloj, escenario aislado y jornada de 300 s. Solo diseño; no declara ventas en vivo, producción ni simulador implementados. Recepción se implementa por petición expresa distinta y se registra transversalmente en avances/cueva.md.

## Revisión transversal · 20-10-2026

[Revisión del proyecto](revision-proyecto-2026-10-20.md): estado observado sobre `a19a294`, hallazgos R01–R03, pendientes por responsable y criterios de cierre. Distingue implementación existente, defectos, evidencia pendiente y ampliaciones fuera del prototipo. El informe no modifica contratos ni acredita envíos o pruebas de infraestructura que no se hayan ejecutado.

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

**26-10-2026 · Definición de Ventas solicitada por Axel:** [bases-modulo-ventas.md](bases-modulo-ventas.md), con [contrato propuesto](../api/contrato-ventas-operativas.md), separa venta presencial, publicación hacia tienda y recepción de sus ventas por HTTP. El módulo operativo aún es planteamiento. Precios, stock, promociones, identidad y cierre/ML tienen responsables y criterios de aceptación; simulador y conexión Payme no se implementan en esta entrega. Registro transversal en Cueva sin atribuir autoría a los demás integrantes.

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


## Plan de cierre vigente · 30-09-2026

Consultar [plan-cierre-prototipo.md](plan-cierre-prototipo.md): base disponible 1–7, corte de interfaz solicitado y pasos 7–10 pendientes con criterios de aceptación. Detenerse al concluir el corte UI; recurrencia diaria se planifica como ampliación posterior con fuente de datos actuales.

## Análisis previo de tienda · 28-10-2026

[Adaptación de la tienda de Bohorquez](analisis-adaptacion-tienda-bohorquez-2026-10-28.md): comparación estática con tienda independiente/Payme y propuestas por fases. Solo análisis; no modifica contratos vigentes ni declara conexión de inventario, canal tienda o simuladores implementados.

## Preparación de jornada · 28-10-2026

Guion de prueba del 28 en guion-prueba-2026-10-28.md. Por aclaración posterior de Axel se prepara la aplicación actual, con respaldo y efectos reales de Telegram al aprobar, conservando la tienda independiente. No declara implementados reloj acelerado ni cierre diario.
