# Responsabilidades del equipo — reparto vigente

Esta es la fuente única de asignación para los seis integrantes. Sustituye el reparto anterior. Se aplica al [alcance del prototipo](../guia-inicio-desarrollo.md), incluyendo pedidos y Telegram real a un chat de pruebas con aprobación configurable. Cada persona entrega su bloque completo: interfaz, backend, API, datos, pruebas e integración.

## Reparto y equilibrio de complejidad

La distribución considera el trabajo pendiente y la dificultad de integración, no solo el número de módulos. Los puntos de partida ya existentes se reutilizan. La igualdad de horas no se puede garantizar sin conocer disponibilidad y experiencia: revisar carga al completar el primer corte y reasignar tareas concretas si aparece una diferencia sostenida.

| Responsable | Bloque | Complejidad dominante | Rama |
|---|---|---|---|
| Axel Cueva | Acceso, configuración y motor de automatizaciones | Concurrencia, programación durable y recuperación de tareas. | `cueva` |
| Edu Sanchez | Inicialización, productos, ventas y estructura visual compartida | Validación de archivos, consistencia entre dominios y carga atómica. | `sanchez` |
| Kevin Bohorquez | Modelo predictivo, evaluación histórica y dashboard | Reproducibilidad, ventanas temporales, cobertura y ausencia de fuga de datos. | `bohorquez` |
| Leonardo Vera | Inventario por lotes y promociones sugeridas | Atomicidad de saldos, concurrencia, caducidad y reloj simulado. | `vera` |
| Leonardo Aguirre | Proveedores, pedidos y Telegram | Efectos externos, estados de compra y duplicados entre planes. | `aguirre` |
| Max Rojas | Ingredientes, recetas y planificación | Versiones de recetas, cálculos decimales e integración pronóstico/stock/compras. | `rojas` |

## Qué entrega cada integrante

### Axel Cueva — Acceso, configuración y motor de automatizaciones

**Entidades propias:** `usuario`, `negocio`, `programacion_demo`, `ejecucion_automatizacion`, `intento_automatizacion`.

**Carpetas principales:** [backend/app/core](../../backend/app/core/GUIA_DESARROLLO.md), [backend/app/modules/autenticacion](../../backend/app/modules/autenticacion/GUIA_DESARROLLO.md), [backend/app/modules/negocios](../../backend/app/modules/negocios/GUIA_DESARROLLO.md), [backend/app/modules/automatizaciones](../../backend/app/modules/automatizaciones/GUIA_DESARROLLO.md), [backend/app/workers](../../backend/app/workers/GUIA_DESARROLLO.md), [frontend/src/app/automatizaciones](../../frontend/src/app/automatizaciones/GUIA_DESARROLLO.md). El [mapa completo](mapa-carpetas.md) incluye rutas, componentes, pruebas y documentación.

| Tarea | Trabajo concreto | Evidencia de terminado |
|---|---|---|
| A01 · Completar identidad, roles y configuración | Validar zona horaria y moneda; exponer modo de aprobación; uniformar errores y mantener acceso/sesión en UI. | Una operación administrativa falla con 403 para Operador; valores inválidos no se guardan. |
| A02 · Construir programaciones y ejecuciones durables | Modelos, rutas, pantallas, estados, clave idempotente, intentos y consulta de resultados. | Programar para una hora próxima produce una ejecución trazable con horas real y simulada. |
| A03 · Implementar Beat y recuperación | Despachador, lease, reentregas, reintentos de tareas internas y publicación recuperable tras commit. | Reiniciar entre persistir y encolar no pierde la acción; dos entregas no duplican el efecto local. |
| A04 · Preparar infraestructura común | Compose, imágenes, volúmenes y variables; integrar requisitos ML de Kevin y canal de Aguirre; CI y migraciones. | Otra persona reproduce el arranque; CI ejecuta comprobaciones de núcleo y pruebas aportadas por los dueños. |

### Edu Sanchez — Inicialización, productos, ventas y estructura visual compartida

**Entidades propias:** `configuracion_inicial`, `producto`, `sku_producto`, `importacion_venta`, `venta_diaria`, `revision_venta`.

**Carpetas principales:** [backend/app/modules/inicializacion](../../backend/app/modules/inicializacion/GUIA_DESARROLLO.md), [backend/app/modules/productos](../../backend/app/modules/productos/GUIA_DESARROLLO.md), [backend/app/modules/ventas](../../backend/app/modules/ventas/GUIA_DESARROLLO.md), [frontend/src/app/inicializacion](../../frontend/src/app/inicializacion/GUIA_DESARROLLO.md), [frontend/src/features/ventas](../../frontend/src/features/ventas/GUIA_DESARROLLO.md), [frontend/src/components/layout](../../frontend/src/components/layout/GUIA_DESARROLLO.md). El [mapa completo](mapa-carpetas.md) incluye rutas, componentes, pruebas y documentación.

| Tarea | Trabajo concreto | Evidencia de terminado |
|---|---|---|
| E01 · Definir y cargar productos y ventas | Mapear SKU externos, persistir ventas agregadas, conservar revisiones y distinguir ausencia de cero. | SKU desconocido y sucursal ajena rechazan el lote; una corrección conserva el valor anterior. |
| E02 · Construir asistente XLSX/CSV | Lectores, validación, vista previa, huellas y confirmación; orquestar servicios de Max y Vera en una transacción. | Un error en stock o receta revierte toda la carga; repetir clave y contenido no duplica. |
| E03 · Preparar primera inicialización | Estado durable, datos de ejemplo, archivos y aviso de preparación ML; pedir ejecución a Axel y entrada a Kevin. | Desde base vacía se carga un escenario completo; fallo ML permite reintentar sin importar nuevamente. |
| E04 · Entregar pantallas y piezas comunes | Productos, ventas y asistente; navegación, formularios y estados reutilizables; contratos del cliente HTTP con Axel. | Cada pantalla propia usa API real; los demás pueden reutilizar layout y componentes sin copiar fetch o estilos. |

### Kevin Bohorquez — Modelo predictivo, evaluación histórica y dashboard

**Entidades propias:** `artefacto_modelo`, `corrida_pronostico`, `pronostico`, `evaluacion_pronostico`.

**Carpetas principales:** [foodsave-ml](../../foodsave-ml/GUIA_DESARROLLO.md), [backend/app/modules/pronosticos](../../backend/app/modules/pronosticos/GUIA_DESARROLLO.md), [frontend/src/features/pronosticos](../../frontend/src/features/pronosticos/GUIA_DESARROLLO.md), [frontend/src/app/pronosticos](../../frontend/src/app/pronosticos/GUIA_DESARROLLO.md), [frontend/src/app/panel](../../frontend/src/app/panel/GUIA_DESARROLLO.md), [frontend/src/components/charts](../../frontend/src/components/charts/GUIA_DESARROLLO.md). El [mapa completo](mapa-carpetas.md) incluye rutas, componentes, pruebas y documentación.

| Tarea | Trabajo concreto | Evidencia de terminado |
|---|---|---|
| K01 · Extraer entrenamiento reutilizable | Llevar la lógica del notebook a funciones ejecutables en worker; partición temporal y validaciones del artefacto. | Entrenar sin abrir Colab produce CBM y metadatos compatibles con versión, huella y partición. |
| K02 · Implementar inferencia y persistencia | Construir las 13 características por calendario, validar modelo y cobertura, guardar corrida y pronósticos. | Cambiar la venta del día objetivo no cambia sus características; historial insuficiente produce null con motivo. |
| K03 · Implementar evaluación histórica | Backtest por fecha y comparación posterior con revisión de venta; MAE, WAPE, ±20% y cobertura. | Reentregar no duplica evaluación; venta ausente se excluye y WAPE con real total cero queda indefinido. |
| K04 · Construir dashboard y vistas de pronóstico | API de métricas, serie histórica, comparación por producto, fecha y versión; gráficos con componentes de Edu. Ampliación solicitada 01-10-2026: Inicio con gráficos y Reportes de lectura según [contrato](../api/contrato-informes.md). | Los totales previsto/real usan los mismos pares evaluables y permiten rastrear la corrida; reportes conservan fechas, fuentes y cobertura. |

### Leonardo Vera — Inventario por lotes y promociones sugeridas

**Entidades propias:** `lote_producto`, `lote_ingrediente`, `movimiento_inventario`, `regla_promocion_demo`, `evaluacion_promocion`.

**Carpetas principales:** [backend/app/modules/inventario](../../backend/app/modules/inventario/GUIA_DESARROLLO.md), [backend/app/modules/promociones](../../backend/app/modules/promociones/GUIA_DESARROLLO.md), [frontend/src/features/inventario](../../frontend/src/features/inventario/GUIA_DESARROLLO.md), [frontend/src/features/promociones](../../frontend/src/features/promociones/GUIA_DESARROLLO.md), [frontend/src/app/inventario](../../frontend/src/app/inventario/GUIA_DESARROLLO.md), [frontend/src/app/promociones](../../frontend/src/app/promociones/GUIA_DESARROLLO.md). El [mapa completo](mapa-carpetas.md) incluye rutas, componentes, pruebas y documentación.

| Tarea | Trabajo concreto | Evidencia de terminado |
|---|---|---|
| V01 · Implementar lotes y apertura | Persistir lote, unidad, caducidad, saldo y procedencia; servicio de apertura para el importador de Edu. | Cero explícito registra saldo conocido; una apertura positiva genera movimiento único. |
| V02 · Implementar ajustes y disponibilidad | Bloqueo/transacción, delta, motivo, clave y hora efectiva; agregación de stock elegible por fecha para Max. | Dos ajustes concurrentes no generan saldo negativo; repetir una operación no cambia saldo otra vez. |
| V03 · Integrar regla de promoción | Versionar regla y persistir aceptación/rechazo; programar evaluación mediante Axel tras el ajuste. | Dato vencido, falta de fecha o lectura antigua producen rechazo explicado sin publicar descuentos. |
| V04 · Entregar inventario y promoción en UI | Saldos, filtros por lote, movimientos, formulario de ajuste y detalle de evaluación. | Cada cifra muestra unidad y fecha; resultado conecta movimiento, regla y ejecución. |

### Leonardo Aguirre — Proveedores, pedidos y Telegram

**Entidades propias:** `proveedor`, `oferta_ingrediente`, `pedido_compra`, `linea_pedido`, `envio_pedido`.

**Carpetas principales:** [backend/app/modules/proveedores](../../backend/app/modules/proveedores/GUIA_DESARROLLO.md), [backend/app/modules/compras](../../backend/app/modules/compras/GUIA_DESARROLLO.md), [backend/app/integrations/proveedores](../../backend/app/integrations/proveedores/GUIA_DESARROLLO.md), [frontend/src/features/proveedores](../../frontend/src/features/proveedores/GUIA_DESARROLLO.md), [frontend/src/features/compras](../../frontend/src/features/compras/GUIA_DESARROLLO.md), [frontend/src/app/compras](../../frontend/src/app/compras/GUIA_DESARROLLO.md). El [mapa completo](mapa-carpetas.md) incluye rutas, componentes, pruebas y documentación.

| Tarea | Trabajo concreto | Evidencia de terminado |
|---|---|---|
| L01 · Implementar proveedores y ofertas | Proveedor activo, chat de prueba, ingrediente, unidad de compra, factor, mínimo y múltiplo. | Conversión inválida se rechaza; cada ingrediente tiene como máximo una oferta preferida activa. |
| L02 · Generar pedidos desde necesidades | Agrupar por proveedor y preservar cálculo; cerrar con Max la prevención de recompra entre planes de la misma fecha. | Repetir plan no duplica; recalcular la misma fecha no provoca segundo envío sin aplicar la política acordada. |
| L03 · Implementar aprobación y canal | Estados de compra, snapshot de modo, aprobación administrativa, bot y mensaje real al chat propio. | Funciona modo manual y automático; guardar message_id acredita envío sin fingir confirmación comercial. |
| L04 · Resolver fallos y entregar UI | Pantallas de proveedor/pedido/envío, destino bloqueado, timeout incierto y conciliación con evidencia. | Una caída después del envío no causa reenvío ciego; tokens no aparecen en UI, base de negocio ni registros. |

### Max Rojas — Ingredientes, recetas y planificación

**Entidades propias:** `ingrediente`, `receta`, `receta_ingrediente`, `plan_produccion`, `elemento_plan`, `necesidad_ingrediente`.

**Carpetas principales:** [backend/app/modules/ingredientes](../../backend/app/modules/ingredientes/GUIA_DESARROLLO.md), [backend/app/modules/recetas](../../backend/app/modules/recetas/GUIA_DESARROLLO.md), [backend/app/modules/planificacion](../../backend/app/modules/planificacion/GUIA_DESARROLLO.md), [frontend/src/features/ingredientes](../../frontend/src/features/ingredientes/GUIA_DESARROLLO.md), [frontend/src/features/recetas](../../frontend/src/features/recetas/GUIA_DESARROLLO.md), [frontend/src/features/planificacion](../../frontend/src/features/planificacion/GUIA_DESARROLLO.md). El [mapa completo](mapa-carpetas.md) incluye rutas, componentes, pruebas y documentación.

| Tarea | Trabajo concreto | Evidencia de terminado |
|---|---|---|
| M01 · Implementar ingredientes y recetas | Unidades base, relaciones, versiones y servicios para primera carga; formularios de consulta/edición acordados. | Una receta usada permanece reproducible; cambio crea versión, no altera planes anteriores. |
| M02 · Calcular plan de producción | Consumir corrida de Kevin y stock de Vera; aplicar max(0, pronóstico-stock) y guardar snapshots. | Un pronóstico no disponible no se convierte en cero; generar el plan no mueve stock. |
| M03 · Calcular necesidades y faltantes | Agregar ingredientes de todos los productos, redondear al final, guardar requerido/disponible/faltante y entregar a Aguirre. | Dos productos que usan harina generan una necesidad agregada correcta en la unidad base. |
| M04 · Entregar pantalla y contrato del plan | Detalle, trazas de receta/stock/pronóstico, avisos y enlace a pedidos; versiones y respuesta API. | Cada cantidad puede explicarse; plan repetido recupera resultado y un recálculo conserva el anterior. |

## Fronteras que evitan duplicar trabajo

| Frontera | Quién entrega | Quién consume | Acuerdo requerido |
|---|---|---|---|
| Sesión, permisos y error HTTP | Axel | Todos | Identidad pública, códigos estables y sobre JSON. Edu integra el cliente común. |
| Historial de ventas y SKU | Edu | Kevin | IDs, fechas locales, cantidades, revisiones y ausencia distinta de cero. |
| Primera carga de recetas y lotes | Max y Vera exponen servicios; Edu orquesta | Inicialización | Misma sesión/transacción; los servicios participantes no hacen commit independiente. |
| Estado de primera carga/modelo | Edu mantiene configuracion_inicial | Kevin y Axel | Servicios de transición para DATOS_CARGADOS, ENTRENANDO y MODELO_LISTO; fallo no recarga datos. |
| Artefacto, pronóstico y métricas | Kevin | Max, Axel y dashboard de Kevin | Versión, fecha, estado y cobertura; nunca inferir con venta real del objetivo. |
| Stock disponible por fecha | Vera | Max y promociones de Vera | Unidad, lote, vigencia y lectura reproducible, sin modificar saldo al consultar. |
| Receta y necesidades del plan | Max | Aguirre | Plan y receta versionados, cantidades decimales y fecha del escenario. |
| Pedidos y envío | Aguirre | Axel y pantalla de compras | El dominio de compras decide estados/reenvío; el worker común no reintenta ciegamente Telegram. |
| Motor de tareas | Axel | Edu, Kevin, Vera, Aguirre y Max | Envoltorio de ejecución, claves, intentos y eventos. Cada dueño escribe la función de su dominio. |
| Componentes visuales | Edu coordina | Todos | Layout, formularios, tablas, estados y cliente común. Kevin mantiene gráficos/métricas; Axel los componentes de ejecución. |

Edu conserva el normalizador de archivos de entrada; Kevin conserva características, entrenamiento, inferencia y evaluación. Si se modifica `foodsave-ml/normalizar_ventas.py`, Edu coordina el contrato con Kevin y aporta sus pruebas. El dashboard histórico pertenece a Kevin, aunque use la estructura visual de Edu.

## Trabajo compartido con responsabilidad explícita

- **Migraciones:** cada dueño aporta columnas, restricciones, modelos y pruebas de sus tablas. Axel coordina el orden y una única cabeza de Alembic; no escribe todas las migraciones por los demás.
- **CI y contenedores:** Axel mantiene el flujo común; Kevin entrega requisitos de ML y persistencia del artefacto; Aguirre entrega configuración del canal. Cada persona corrige los fallos de su bloque.
- **Pruebas integradas:** el proveedor de un servicio y su consumidor preparan juntos el caso de frontera. Las pruebas no se delegan todas a Edu ni a Axel.
- **Diseño:** Edu mantiene convenciones compartidas. Cada dueño implementa sus pantallas, accesibilidad y estados vacíos/error/carga.
- **Documentación:** cada dueño actualiza su GUIA_DESARROLLO.md y contrato cuando cambia el comportamiento. Axel coordina consistencia, sin convertirse en autor de todos los documentos.
- **Revisión:** usar una persona consumidora del contrato como revisora: Edu↔Kevin para ventas, Kevin↔Max para pronóstico, Max↔Vera para stock, Max↔Aguirre para compras, Axel↔dueño de tarea para ejecución.

## Secuencia de entregas

1. **Contratos antes de código en paralelo:** cada dueño publica solicitudes/respuestas, restricciones SQL, estados, errores y ejemplos de su bloque. Se revisan con quien los consume; cualquier ruta nueva se añade al catálogo API antes de conectarla.
2. **Primer corte por persona:** Axel deja identidad/ejecución; Edu valida archivos y catálogo; Kevin hace inferencia reproducible con fixture; Vera mueve un lote atómicamente; Aguirre prepara proveedor/oferta/pedido con adaptador falso; Max calcula un plan con entradas de contrato. Los fixtures no se presentan como datos reales en UI.
3. **Integración de datos:** importar un escenario completo de 3–5 productos, recetas y stock. Entrenar con la tarea real y persistir el artefacto.
4. **Integración principal:** Beat → inferencia → plan → necesidades → pedido → aprobación opcional → Telegram de pruebas. Evaluación histórica y dashboard consultan resultados persistidos.
5. **Recuperación:** ajustes y promoción; reinicio de worker, entrega duplicada, fallo transitorio y envío incierto. Cada dueño demuestra su parte y otra persona reproduce el recorrido.

Antes de conectar compras, Aguirre y Max deben cerrar la regla de recompra entre planes de la misma fecha; la unicidad por plan no evita por sí sola una segunda compra. Antes de escribir una migración, su dueño cierra tipos/FK/CHECK en el esquema con los consumidores. Antes de conectar una pantalla, su dueño entrega el cuerpo exacto de la API. Estos son pendientes de definición asignados, no funciones ya implementadas.

## Criterio común de terminado

- Código, interfaz y API conectados; estado persistido y errores visibles.
- Esquemas y migraciones coherentes con el contrato del módulo.
- Caso normal y caso de fallo propio del dominio verificados; idempotencia/concurrencia cuando aplique.
- Permisos aplicados en servidor; secretos y datos personales fuera de Git y registros.
- Prueba de frontera con al menos un consumidor, documentación y forma de reproducir el resultado.
- Otra persona revisa el cambio antes de integrarlo según el [flujo Git](flujo-git.md).

## Carpetas de evolución posterior

Producción física, excedentes intradía y desperdicio: Leonardo Vera es custodio documental. Informes operativos/económicos: Kevin Bohorquez. Notificaciones y canales externos de avisos: Axel Cueva. Activación de descuentos en canales de venta: Leonardo Vera. Recepción física/pagos: Leonardo Aguirre. Son referencias para mantener las carpetas; no son entregables adicionales de este reparto. Su implementación exige ampliar el alcance y reevaluar la carga.

## Cómo trabajar con una IA

Consultar también [dependencias y entregas](dependencias.md) y el [registro de avances](avances/README.md). Cada avance significativo debe actualizar el registro del responsable antes del traspaso; el siguiente integrante parte del resumen vigente, contrato y ejemplo enlazados.

Leer primero el [AGENTS.md raíz](../../AGENTS.md), este reparto y la GUIA_DESARROLLO.md de la carpeta a editar. Indicar a la IA el integrante y un ID de tarea (por ejemplo, M02). La guía local define qué construir y a quién entrega datos; no otorga permiso para ampliar funciones futuras. El nombre del responsable expresa propiedad técnica, no bloquea cambios de integración ya autorizados.
