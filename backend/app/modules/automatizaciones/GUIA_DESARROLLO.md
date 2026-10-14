# Guía de desarrollo — Programaciones, ejecuciones e intentos

**Carpeta:** `backend/app/modules/automatizaciones`.

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

**Paso 1 · 30-09-2026:** consultar_ejecucion y consultar_ejecucion_por_clave son fronteras públicas de lectura para E03/ML; no confirman sesiones.

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](../../../../docs/equipo/avances/cueva.md) para el último estado.

## Integración E03/K01

`obtener_ejecucion(sesion, id)` es la consulta pública de los consumidores que enlazan progreso, sin commit. E03 usa esa consulta y la reserva idempotente en la transacción de primera carga.

## Trabajo en esta carpeta

**14-10-2026 · Catálogo completo, solicitud de Axel:** ProgramarPropuesta/ConfigurarFlujo y programar_propuesta aceptan uno o más IDs positivos y únicos sin máximo de cinco. Se mantiene orden/idempotencia y validación de requisitos por producto. Asistente consulta todos los activos; selección heredada no restringe la planificación. Contrato de flujo y pruebas de persistencia de 139 IDs actualizados; coordinación en el registro de Cueva.

**A02 y A03 disponibles:** `modelos.py`, `esquemas.py`, `servicio.py` y `rutas.py` reservan programación más ejecución pendiente en una transacción, exponen lecturas y permiten iniciar/finalizar intentos con sesión del consumidor sin commit. `programar_ejecucion` permite a servicios internos reservar `GENERAR_PROPUESTA` o `EVALUAR_PROMOCION` con fecha UTC, fecha simulada, parámetros y clave idempotente. `0001b_automatizaciones` crea las tres tablas y `0001c_motor` agrega token y lease a la ejecución. Beat reclama y recupera trabajos; el cálculo de cada dominio espera su adaptador público. Ver [contratos A02 y A03](../../../../docs/api/contratos.md).

1. Crear consultas/acciones de programación y detalle con clave y huella de entrada.
2. Reclamar trabajos mediante transición atómica y lease recuperable.
3. Persistir intentos, tiempos, salidas y errores; encargar cálculo a cada módulo público.
4. Separar reintentos internos de la política especial de envíos de Aguirre.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `programacion_demo`, `ejecucion_automatizacion`, `intento_automatizacion`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

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

## Claridad y flujo completo · 30-09-2026

programar_propuesta admite modo_envio_pedidos opcional y lo conserva en parámetros/huella. Omitir conserva comportamiento previo; null no añade snapshot de modo. Validar literal manual/automático. La UI administra una ejecución única para el objetivo histórico.

## Corte vigente · 11-10-2026 · Flujo y promociones

Codex para Axel implementó configuración reutilizable, comprobación de requisitos por interfaces públicas, calendario histórico diario de 1–31 días, modelo/modo conservados y pausa/cancelación/reprogramación de tareas sin despacho. Promociones tienen regla inmutable versionada, reserva transaccional después de cada ajuste nuevo de producto y evaluación idempotente con snapshot/motivo; API y pantalla reales. Se conserva la propiedad de cada dominio.

[Contrato vigente, APIs y límites](../../../../docs/api/contrato-flujo-promociones.md). Aplicar `0015_flujo_promociones` antes de actualizar API/worker/Beat. El diagnóstico no ejecuta inferencia ni envía mensajes; guardar configuración no agenda. Consultas de tareas/evaluaciones admiten paginación real con total. La pausa no recupera horas perdidas: reprogramar antes de reanudar. Deshabilitar promociones afecta ajustes nuevos; tareas ya reservadas conservan su versión. Hora simulada de evaluación avanza por el tiempo real transcurrido desde el ajuste para comprobar frescura.

Las notas fechadas de cortes anteriores son historial; no usar sus pendientes como estado actual. Pruebas y límites finales en los registros Cueva/Vera/Sanchez, incluyendo PostgreSQL/Redis y Telegram real solo si fueron ejecutados. No confundir fixtures QA con datos de operación.

## Corte solicitado · 14-10-2026

Codex para Axel. Gestionar admite EJECUTAR_AHORA con motivo administrativo: adelanta una tarea pendiente/pausada, conserva entrada/clave/modelo/modo y la recoge Beat. No modifica tareas iniciadas. Contrato: docs/api/contrato-flujo-promociones.md; pruebas test_flujo_promociones.py.
