# Revisión del proyecto — 20-10-2026

**Seguimiento posterior de esta sesión:** el usuario autorizó avanzar los bloques, priorizando Bohorquez y el diseño. R01–R03 quedan corregidos localmente con seis regresiones permanentes, paginación completa de pronósticos y rediseño de analítica. Suite del avance: 271 passed, 26 skipped, 6 subtests passed. [Entrega vigente y límites](avances/bohorquez.md). Este informe conserva los hallazgos y pruebas de observación de la base `a19a294`; para verificar la corrección usar `backend/tests/integration/test_evaluacion_revisiones.py`, no los casos temporales que describían el defecto anterior.

Revisión transversal por Codex a solicitud del usuario. Coordinación documental A04 de Cueva; cada integrante conserva la responsabilidad de su dominio. Base local: rama `bohorquez`, commit `a19a294` (`Merge pull request #14 from AXL031/cueva`), árbol inicialmente limpio. No se cambia de rama, publica, integra ni modifica lógica de negocio.

## Dictamen

El prototipo tiene implementación de sus seis bloques y del recorrido carga → ML → plan → necesidades → compras, además de aprobación, recuperación de envíos, promociones y reportes. No corresponde volver a construir esos módulos ni deducir su ausencia de los README antiguos. Quedan defectos de evaluación, mejoras de robustez y evidencia de cierre. La operación diaria con datos actuales es una ampliación pendiente distinta del cierre del prototipo histórico.

Alcance de la revisión: contratos y registros de los seis responsables, rutas/servicios centrales, persistencia y migraciones, worker/Beat, adaptador Telegram, cliente/sesión/pantallas, configuración de contenedores y CI, y comprobaciones locales. Esta revisión no acredita la configuración actual de la base habitual ni el estado remoto de CI.

## Hallazgos que conviene corregir

### R01 · P2 · Corregir una venta retira su comparación sin programar la nueva

**Responsables:** Sanchez (E01) y Bohorquez (K03/K04).

`corregir_venta` conserva la revisión anterior y crea otra, pero ni el servicio ni su ruta reservan una evaluación. `detalle_evaluacion` muestra únicamente comparaciones que coinciden con la revisión vigente. Por tanto, después de corregir una venta ya evaluada, esa pareja deja de contribuir a las métricas hasta que otro proceso la evalúe. El usuario puede ver bajar la cobertura y cambiar los totales sin que haya una tarea nueva que complete la comparación.

**Evidencia:** [corrección](../../backend/app/modules/ventas/servicio.py), [ruta PATCH](../../backend/app/modules/ventas/rutas.py), [selección de evaluaciones vigentes](../../backend/app/modules/pronosticos/evaluacion.py). La prueba existente `test_inferencia_no_lee_real_objetivo_y_evaluacion_versiona_revision` llama a `evaluar_corrida` manualmente después de corregir; no comprueba esa conexión desde HTTP.

**Cierre propuesto:** acordar una interfaz pública para reservar las reevaluaciones afectadas en la misma transacción de la corrección, conservar versiones y mostrar estado pendiente. Añadir prueba PATCH → ejecución → métricas, sin depender de una llamada manual al evaluador. No regenerar planes ni pedidos como efecto de esa corrección.

**Reproducción aislada ejecutada:** pronóstico 5, venta real 10, una comparación guardada; corregir la venta a 12 deja `productos_evaluables=0`, conserva la evaluación anterior y no crea otra ejecución.

### R02 · P2 · La evaluación programada ignora las revisiones de su entrada

**Responsable:** Bohorquez (K03), consumidor del motor A03 de Cueva.

`solicitar_evaluacion_corrida` guarda los pares producto/revisión en `datos_entrada_json` y los incorpora a la clave de la tarea. Sin embargo, `evaluacion_programada` solo pasa `corrida_id` al evaluador, que consulta las ventas vigentes al ejecutarse. Una corrección entre reserva y ejecución hace que la tarea procese otra revisión distinta de la conservada en su entrada. La evaluación guarda la revisión realmente usada, pero la identidad de la solicitud deja de explicar su resultado.

**Evidencia:** [reserva y evaluador](../../backend/app/modules/pronosticos/evaluacion.py), [adaptador del worker](../../backend/app/modules/pronosticos/manejadores.py).

**Cierre propuesto:** consumir las revisiones conservadas mediante interfaz pública de Ventas, o detectar explícitamente que quedaron obsoletas y reservar otra ejecución. Probar una corrección entre encolado y ejecución, reentrega y coexistencia de ambas revisiones. Resolver junto con R01.

**Reproducción aislada ejecutada:** reservar evaluación con revisión 1/real 10, corregir a revisión 2/real 12 y ejecutar el manejador. La entrada sigue identificando la revisión 1 y la evaluación resultante usa la revisión 2.

### R03 · P2 · El límite de subida se comprueba después de cargar todo el archivo

**Responsable:** Sanchez (E02), coordinación de infraestructura A04.

El asistente declara 64 MiB por archivo, pero `_leer_archivos` ejecuta `await archivo.read()` sin tamaño y después comprueba `len`. El archivo completo ya se ha materializado en memoria antes de devolver 413; tampoco se limita el total de archivos de la entrega en ese punto. Un archivo accidentalmente grande o muchas entradas pueden agotar la API antes de que actúe el límite previsto. La ruta piloto sí lee en bloques y limita durante la lectura.

**Evidencia:** [asistente](../../backend/app/modules/inicializacion/rutas.py), [lectura acotada del piloto](../../backend/app/modules/inicializacion/piloto.py).

**Cierre propuesto:** lectura acotada a límite+1 o por bloques, presupuesto total y validación temprana de cantidad/nombres; comprobar 413 sin consumir todo el archivo. Mantener el formato de error y atomicidad de la carga.

**Reproducción aislada ejecutada:** un archivo instrumentado confirma que `_leer_archivos` solicita `read(-1)`; no se adjunta un archivo gigante ni se provoca agotamiento de memoria.

## Qué falta por bloque

| Bloque | Implementación encontrada | Pendiente concreto |
|---|---|---|
| Cueva · A01–A04 | Sesión/roles, usuarios, negocio, programaciones, gestión, intentos, recuperación por lease, Beat y CI. | Repetir infraestructura y migraciones con PostgreSQL/Redis en este corte; respaldo/restauración y reproducción por otro integrante. |
| Sanchez · E01–E04 | Catálogo/SKU, ventas y revisiones, XLSX/CSV, vista previa, carga atómica, estado inicial y estructura visual común. | R01 con Kevin y R03; automatizar pruebas de interfaz de los recorridos principales. La API de productos solo devuelve hasta 500 filas. |
| Bohorquez · K01–K04 | Entrenamiento ejecutable, artefacto, 13 características, inferencia persistida, backtest, métricas, panel y CSV. | R01/R02; conservar acceso a todo el historial de modelos/corridas; evaluar rendimiento con datos futuros independientes antes de uso comercial. |
| Vera · V01–V04 | Lotes, apertura/ajustes, disponibilidad y reglas/evaluaciones de promoción con motor y pantalla. | Demostración conjunta reproducible. La consulta por fecha aplica vigencia al saldo actual; no reconstruye un saldo histórico a partir de `efectivo_en_demo`. Acordar esa semántica antes de ampliar escenarios temporales. |
| Aguirre · L01–L04 | Proveedores/ofertas, conversiones, propuesta por fecha, aprobación, outbox, Telegram y conciliación/reintento explícito. | Completar proveedor/ofertas/chat según instalación; demostrar automático real autorizado y recuperación. WhatsApp tiene documentación preparatoria, sin adaptador implementado. |
| Rojas · M01–M04 | Ingredientes, versiones de recetas, plan, necesidades agregadas y trazas a pronóstico/stock/pedidos. | Participar en demo conjunta; ampliar historial consultable y verificar con Vera la semántica temporal si se amplía el prototipo. |

Los datos previos de la instalación —139 productos, 88 543 ventas y un modelo listo— aparecen en el registro del 14-10; **no fueron consultados de nuevo**. Tampoco se presume que proveedores, ofertas o Telegram estén configurados hoy.

## Cierre pendiente del prototipo

1. Corregir R01–R03 con sus pruebas de frontera y contratos actualizados.
2. Repetir desde base aislada: migraciones → carga → CatBoost → Beat → plan → faltantes → pedidos → evaluación/reportes → ajuste/promoción. Comprobar reinicios, reentrega, permisos y stock intacto. Hay suites para gran parte del recorrido; falta acreditar el cierre conjunto de esta entrega.
3. Bajo una tarea con autorización expresa de envío, comprobar el modo automático real a un chat propio y conservar evidencia del resultado. Una prueba con transporte falso no sustituye esta evidencia. Esta revisión no autoriza ni ejecuta mensajes externos.
4. Reproducir arranque y recorrido en otra PC. Preparar y probar restauración coherente de PostgreSQL, `model_artifacts`, `telegram_secrets` y secreto de instalación protegido; documentar versiones y parada/arranque. `scripts/` aún contiene solo documentación.
5. Añadir pruebas automáticas de navegador de login/permisos, carga, programación, detalle/recuperación y promoción. `frontend/package.json` solo define dev/build/start/typecheck; CI compila mediante Docker, pero no hay una suite de comportamiento del navegador.
6. Actualizar los resúmenes vigentes. El Git local ya contiene el merge del PR #14, mientras registros/dependencias todavía indican revisión e integración pendientes. `backend/README.md` afirma que los manejadores no están conectados y que faltan tablas; `backend/tests/README.md` presenta pruebas como esqueleto. No tomar esas frases como estado real. No se verificó el CI remoto actual.

## Mejoras posteriores y límites conocidos

- **Historial completo:** modelos/corridas, planes y propuestas de compra conservan cortes de 50 registros; la paginación visual no recupera filas anteriores. Automatizaciones/promociones y Ventas ya tienen paginación remota: reutilizar el patrón. Es un límite documentado del corte, no ausencia total de esas pantallas.
- **Reproducibilidad Python:** `backend/pyproject.toml` usa rangos de dependencias sin lockfile o constraints versionadas. Una instalación nueva puede resolver versiones distintas de la instalación aceptada. Fijar una combinación comprobada y revisar actualizaciones por separado.
- **Operación actual:** faltan un flujo diario general para cargar/registrar nuevas ventas, mantenimiento del catálogo desde API/UI, política de actualización/reentrenamiento y una inferencia fuera del tramo reservado de prueba. Ventas permite consultar/corregir registros existentes; la importación `piloto-bakery` es una vía específica del piloto, no ese flujo operativo general. Actualmente `generar_corrida` rechaza objetivos fuera del tramo reservado; un calendario histórico de 1–31 días no equivale a un servicio diario indefinido para hoy.
- **Datos de negocio:** las recetas estimadas y fechas de lotes de prueba requieren validación comercial. La precisión histórica no acredita demanda no atendida, ahorro, desperdicio real ni rendimiento futuro.
- **Fuera del alcance vigente:** producción física, recepción/pagos, descuento automático de stock por ventas/producción, POS y publicación real de promociones. No contarlos como tareas incumplidas del prototipo.

## Verificaciones de esta revisión

| Comprobación | Resultado |
|---|---|
| `npm run typecheck` | Correcto. |
| `npm ci --no-audit --no-fund` y `npm run build` | Correctos; 23 páginas generadas. El build inicial no encontraba las dos fuentes ya declaradas; reinstalar desde lockfile resolvió el entorno. |
| `python -m alembic heads` desde backend | Una sola cabeza: `0016_nombre_comercio`. No acredita la revisión aplicada en una base. |
| Reglas de promociones y normalización de ventas | 10 passed, 6 subtests passed, 23,19 s; selección incluida también en la suite general. |
| Casos adicionales de auditoría R01–R03 | 3 passed, 1 warning, 9,70 s. SQLite temporal, predicción controlada y archivo instrumentado; no provocan OOM ni mensajes reales. |
| `python -m pytest backend/tests/unit backend/tests/integration foodsave-ml/tests -q --tb=short -r fEs` | **265 passed, 26 skipped, 39 warnings, 6 subtests passed; 409,90 s. Sin fallos.** Las 26 omisiones requieren PostgreSQL y/o Redis (bloqueos, concurrencia, DDL transaccional y Beat/worker reales). Incluye entrenamiento/evaluación CatBoost con datos temporales en las pruebas locales habilitadas; no equivale al recorrido PostgreSQL/Redis. |

Entorno: Windows, Python 3.13, dependencias declaradas en `backend[test,ml]` instaladas únicamente en `.tmp/revision-deps`, TEMP/TMP dirigidos a `.tmp/revision-runtime`; PYTHONPATH incluye backend, esas dependencias, las pruebas de integración y foodsave-ml, con autodescubrimiento de plugins externos de pytest deshabilitado. Los casos adicionales están en `.tmp/test_revision_proyecto.py`; son comprobaciones de observación locales, no regresiones de una corrección ya implementada. El registro local de la suite está en `.tmp/revision-suite.log`; la selección de 10 pruebas está incluida en las 265 y no debe sumarse de nuevo. Los tres casos de auditoría son adicionales.

El primer intento general no ejecutó aserciones: 23 errores de colección por `cryptography`/`catboost` ausentes. La selección inicial de normalización tuvo errores de permisos en temporales del sandbox; se resolvieron usando el workspace. Las ejecuciones asíncronas dentro del sandbox se interrumpieron por bloqueo del entorno y se repitieron fuera de él con los mismos datos aislados. Advertencias finales: deprecación del cliente Starlette/httpx, reflexión SQLite de índices por expresión y unidades temporales genéricas de NumPy en features/ventanas. No causaron fallos; conviene atender las deprecaciones al fijar/actualizar dependencias.

Docker Desktop no está disponible: no se inicia la instalación habitual ni sus tareas pendientes. No se acreditan PostgreSQL/Redis/Beat en vivo, migraciones aplicadas en base, CI remoto, otro equipo ni nueva QA visual de navegador. El build no sustituye esos recorridos.

No se consultan secretos, envía Telegram, modifica stock/datos habituales ni cambia migraciones. Los casos adicionales de auditoría usan datos temporales y modelo falso; no acreditan inferencia CatBoost real por sí mismos.
