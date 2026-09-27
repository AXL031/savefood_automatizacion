# Base de desarrollo del prototipo FoodSave

**Corte de revisión: 26-09-2026.** Este documento distingue decisiones de producto ya tomadas, código existente y trabajo necesario para iniciar el desarrollo integrado. La [guía de alcance](guia-inicio-desarrollo.md) y sus contratos enlazados son la fuente normativa del prototipo. El [README extenso](../README.md), el cronograma original y las maquetas describen también una visión posterior. La decisión posterior del usuario [incorporó pedidos y Telegram](arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md) al prototipo.

## Resultado de la revisión

| Área | Existe hoy | Falta para el recorrido de la demo |
|---|---|---|
| Entorno | Compose con PostgreSQL, Redis, API, worker y frontend; migración `0001`; CI de arranque | Celery Beat, dependencias ML dentro de la imagen del worker, almacenamiento persistente del `.cbm` y comprobación del arranque en otra computadora |
| Acceso | Inicio de sesión JWT, perfil, negocio único y roles Administrador/Operador | Validar zona horaria y moneda, homologar errores HTTP y probar autorización de las rutas nuevas |
| Datos | Contrato de importación, ER y esquema objetivo escritos | Migración `0002`, modelos, lector XLSX/CSV, vista previa, carga atómica, revisiones de venta y saldos por lote |
| Modelo | Notebook experimental, normalizador y política temporal documentados | Entrenador reproducible fuera del notebook, artefacto con metadatos/huella, inferencia con las 13 variables y backtest durable |
| Compras y Telegram | Carpetas vacías y descripción de producto amplio | Proveedor mínimo, oferta y conversión de unidad, pedido por plan, aprobación configurable, envío real y auditoría del mensaje |
| Automatización | Celery ejecuta una tarea de prueba; hay regla pura de promoción | Programaciones durables, despachador Beat, ejecuciones/intentos, reintentos, idempotencia y tareas reales |
| Interfaz | Acceso, configuración y pantallas preliminares; compila con TypeScript | Asistente de carga, plan, dashboard de evaluación y sugerencia; adaptar tipos/estados de automatización al contrato de la demo |
| Verificación | Pruebas unitarias de normalización y regla de promoción; CI del núcleo | Pruebas integradas con PostgreSQL/Redis/Beat, fixture de catálogo y escenario completo repetible |

**Conclusión:** el alcance y la arquitectura de la demo están definidos, pero la base ejecutable de sus módulos de dominio no está terminada. No se debe anunciar el producto como implementado ni interpretar que pasar el CI actual valida el recorrido final.

## Decisiones cerradas para implementar

1. **Producto:** una instalación local, un comercio y una sucursal. El prototipo es una simulación histórica de planificación y promoción sugerida; sí crea pedidos desde el plan y envía mensajes reales a un chat de pruebas por Telegram. No activa descuentos.
2. **Fuente de datos:** dos libros XLSX o cinco CSV en la primera carga. Después, PostgreSQL es fuente de ventas y stock. Fecha sin venta es desconocida; cero explícito sí es dato.
3. **Identidad y unidades:** `negocio.id = 1`; SKU externo se resuelve a `producto.id`. Producto y ventas en enteros, ingrediente en `numeric(14,3)` y su unidad base. Lotes y movimientos conservan el historial.
4. **Modelo:** CatBoost diario de un día adelante. Separación temporal por meses completos; la prueba queda fuera del ajuste. Inferencia solo con observaciones anteriores a la fecha objetivo. El backtest y el dashboard se rotulan como evaluación histórica exploratoria.
5. **Plan y compra:** `max(0, pronóstico - stock elegible)`, margen de seguridad cero y faltantes por receta versionada. El plan genera pedidos borrador por proveedor. Crear o enviar un pedido no modifica inventario.
6. **Automatización:** carga aceptada → preparar modelo → evaluar modelo; Beat despacha propuesta programada y evaluación de promoción. La hora UTC real dispara y la fecha/hora histórica local selecciona el escenario. Hasta tres intentos totales; cada efecto es idempotente y auditable.
7. **Promoción:** la regla existente solo crea sugerencia o rechazo razonado por lote. No usa CatBoost para estimar ventas intradía ni modifica precios.
8. **API:** base `/api/v1`, sobre exitoso `datos`, error estable `error.codigo`, Bearer para dominio y Administrador para escrituras sensibles. Las rutas objetivo están en [rutas-api.md](api/rutas-api.md); hoy solo existen autenticación y negocio.
9. **Envío:** modo inicial `REQUIERE_APROBACION`, configurable a `AUTOMATICO`. El envío real usa un bot de Telegram y un chat de pruebas vinculado; aceptación por Telegram no significa confirmación del proveedor. El escenario histórico se marca «demostración, no surtir».

## Orden de integración y puertas de aceptación

| Puerta | Entrega verificable | Responsable principal según la distribución actual |
|---|---|---|
| 0. Núcleo coherente | Validación de configuración, error uniforme, tipos de interfaz acordes a los estados del prototipo, CI verde y Compose reproducido en otra PC | Axel; Edu coordina componentes compartidos |
| 1. Persistencia | `0002` con FK, `CHECK`, unicidad y modelos de datos, incluido proveedor, oferta, pedido, líneas y envíos; migración arriba/abajo probada con base nueva | Axel coordina; cada dueño aporta su esquema según el [diccionario](base_de_datos/diccionario-de-datos.md) |
| 2. Primera carga | Archivos de ejemplo versionados sin datos personales, validación/vista previa, carga atómica, segunda carga idéntica sin duplicados y rechazo completo de SKU desconocido | Edu (asistente, estado, productos y ventas); Max (ingredientes/recetas); Vera (apertura de stock) |
| 3. Modelo | Entrenamiento fuera de HTTP y del notebook, `.cbm` persistido con huella y partición, vector de inferencia validado, backtest sin fuga del día objetivo | Kevin; Axel integra ejecución durable |
| 4. Plan y evaluación | Programación próxima ejecutada por Beat, una corrida y un plan por clave/entrada, faltantes con unidad, comparación posterior con ventas reales y cobertura visible | Kevin (pronóstico, evaluación y panel); Max (plan/necesidades); Vera (stock); Axel (Beat) |
| 5. Pedidos y canal | Un pedido por plan/proveedor con líneas trazables; aprobación manual y modo automático probados; mensaje real al chat de pruebas con `message_id` y fallo incierto sin reenvío ciego | Leonardo Aguirre (compras y Telegram); Axel (configuración y worker) |
| 6. Promoción | Ajuste atómico de lote, programación próxima, sugerencia o rechazo guardado con regla/version/horas y entrega repetida sin segundo efecto | Leonardo Vera (stock, regla y resultado); Axel (orquestación) |
| 7. Demo reproducible | Desde base vacía: migrar, cargar, entrenar, programar, comparar, pedir, enviar al chat de pruebas, ajustar y observar trazas. Probar caída transitoria, reintento y reentrega de Beat | Todo el equipo; Axel coordina la integración |

Ninguna puerta se declara terminada por documentación o maqueta. La evidencia mínima es una prueba o demostración reproducible con IDs persistidos, y la ruta de interfaz consulta la API real.

## Riesgos concretos que hay que resolver antes de repartir trabajo en paralelo

- **Migración compartida:** `0002` debe incorporar las entidades de compras de [ADR-008](arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md) junto a las demás claves cruzadas. Acordar nombres, tipos y orden de creación en una sola revisión antes de que cada rama escriba migraciones divergentes. Las migraciones aplicadas por otros no se reescriben.
- **ML en contenedores:** `backend/pyproject.toml` no declara CatBoost, pandas ni NumPy; el `backend/Dockerfile` instala solo ese proyecto. `compose.yaml` no tiene Beat ni volumen para artefactos. Las tareas ML no pueden ejecutarse en el worker actual.
- **Contrato UI/API:** `frontend/src/types/automatizacion.ts` usa estados y tipos de la visión amplia (`COMPLETADO`, `FALLIDO`, pedidos), mientras que el esquema de demo define `COMPLETADA`, `FALLIDA` y tareas `PREPARAR_MODELO`, `GENERAR_PROPUESTA`, etc. Se debe fijar el esquema de respuesta antes de conectar esas pantallas.
- **Importación real:** solo está versionado el CSV de ventas `bakery`. Falta el catálogo/recetas/stock del escenario y faltan plantillas XLSX o cinco CSV de prueba para demostrar la carga desde cero.
- **Pruebas insuficientes:** las pruebas actuales no ejercitan base, cola, Beat, migración `0002` ni API de dominio. El CI verifica el núcleo, no la idempotencia ni la ausencia de fuga de datos.
- **Documentos históricos:** [cronograma](equipo/cronograma.md), [especificación funcional amplia](funcionalidades/especificacion-modulos.md) contienen trabajo posterior; [responsabilidades](equipo/responsabilidades.md) define el reparto actual; para esta entrega se usa la columna de puertas y el [alcance congelado](guia-inicio-desarrollo.md).

## Regla para cambiar esta base

Si un requisito nuevo altera alcance, tabla, ruta, evento o métrica, actualizar primero el contrato dueño y el criterio de aceptación afectado; luego implementar código, migración, interfaz y una prueba que recorra la frontera. Registrar una decisión arquitectónica cuando cambie una de las decisiones cerradas. Así cada responsable puede desarrollar en paralelo contra un contrato explícito.
