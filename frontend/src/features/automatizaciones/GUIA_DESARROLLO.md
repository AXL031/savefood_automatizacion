# Guía de desarrollo — Programaciones, ejecuciones e intentos

**Carpeta:** `frontend/src/features/automatizaciones`.

**Responsable:** Axel Cueva. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Acceso, configuración y motor de automatizaciones. **Tareas:** A02, A03.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/automatizacion/programacion.md](../../../../docs/automatizacion/programacion.md).
- [docs/automatizacion/politica-de-reintentos.md](../../../../docs/automatizacion/politica-de-reintentos.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](../../../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

**14-10-2026 · Todo el catálogo:** AsistenteFlujo consulta todos los productos activos, selecciona todos por defecto en una configuración nueva y conserva configuraciones existentes. Seleccionar todos incluye todos los activos aunque haya búsqueda; Quitar selección permite empezar de nuevo. Búsqueda por nombre/código y contador del tamaño real. Eliminada la restricción de cinco checkboxes; API y manejador tienen el mismo contrato ampliado.

1. Listar programaciones/ejecuciones con filtros y estados canónicos de demo.
2. Programar hora real y mostrar escenario histórico por separado.
3. Mostrar intentos, errores y enlaces a resultado sin simular éxito cuando falta API.

## Organización de implementación

Agrupar aquí formularios, hooks y vistas específicos del dominio. Consumir `src/services` y `src/types`; reutilizar layout y componentes de Edu. Las fórmulas y decisiones definitivas viven en el backend, no se duplican en el navegador.

## Dependencias y contrato de entrega

- **Recibe:** Eventos de carga, planes, ajustes y horarios reales con escenario histórico.
- **Entrega:** Ejecuciones trazables y despacho recuperable para los servicios de dominio.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Reentrega no duplica efectos locales.
- Caída tras commit y antes de publicar no pierde la acción.
- UI muestra intentos y ambas referencias temporales.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Corte vigente · 11-10-2026 · Flujo y promociones

Codex para Axel implementó configuración reutilizable, comprobación de requisitos por interfaces públicas, calendario histórico diario de 1–31 días, modelo/modo conservados y pausa/cancelación/reprogramación de tareas sin despacho. Promociones tienen regla inmutable versionada, reserva transaccional después de cada ajuste nuevo de producto y evaluación idempotente con snapshot/motivo; API y pantalla reales. Se conserva la propiedad de cada dominio.

[Contrato vigente, APIs y límites](../../../../docs/api/contrato-flujo-promociones.md). Aplicar `0015_flujo_promociones` antes de actualizar API/worker/Beat. El diagnóstico no ejecuta inferencia ni envía mensajes; guardar configuración no agenda. Consultas de tareas/evaluaciones admiten paginación real con total. La pausa no recupera horas perdidas: reprogramar antes de reanudar. Deshabilitar promociones afecta ajustes nuevos; tareas ya reservadas conservan su versión. Hora simulada de evaluación avanza por el tiempo real transcurrido desde el ajuste para comprobar frescura.

Las notas fechadas de cortes anteriores son historial; no usar sus pendientes como estado actual. Pruebas y límites finales en los registros Cueva/Vera/Sanchez, incluyendo PostgreSQL/Redis y Telegram real solo si fueron ejecutados. No confundir fixtures QA con datos de operación.

## Corte solicitado · 14-10-2026

Codex para Axel. Probar en un minuto prepara una ejecución próxima de un día, con revisión y confirmación final. Fecha inicial desde primera carga/modelo, sin fecha 2022 fija. El calendario avanza desde la fecha elegida; no se confunde con mañana real. Conserva las validaciones del servidor.


## Gestión y avisos · 14-10-2026 · Codex para Axel

Selector de productos en tabla paginada con búsqueda, Solo seleccionados y contador global; seleccionar todos incluye todo el catálogo, independiente de página/filtro. Resumen de nombres desplegable. Proveedores/ofertas/destinos pendientes aparecen como avisos con recomendación y enlace por ingrediente/proveedor; no bloquean el plan. Compras conserva bloqueos de envío.
