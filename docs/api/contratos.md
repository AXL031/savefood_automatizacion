# Contratos entre módulos

## Alcance y convenciones del MVP

Estos contratos usan una instalación local para un comercio y una sucursal, según [ADR-005](../arquitectura/decisiones/ADR-005-instalacion-local-mvp.md). Los `id` son internos a esa instalación. Toda ruta de negocio requiere autenticación salvo `POST /autenticacion/iniciar-sesion` y `/salud`. Las respuestas de éxito llevan `datos`; las de error usan el formato documentado en el README principal. Los servicios intercambian objetos tipados, no acceden al repositorio SQL de otro módulo.

Antes de implementar un consumidor y su proveedor, ambos responsables acuerdan: nombres y unidades de los campos, ausencia frente a cero, qué error devuelve, si la llamada puede repetirse y quién guarda el resultado. Los ejemplos siguientes son contratos iniciales; el esquema exacto se actualiza junto con la primera implementación de cada dominio.

### Ventas → Pronósticos

Entrada: `producto_id`, `fecha_local` y `unidades_vendidas` enteras no negativas, con identificador de origen para deduplicar importaciones. Un día sin fila permanece desconocido. El pronóstico para el día siguiente utiliza solo ventas anteriores al momento de ejecución. El adaptador de CSV debe rechazar archivos con más de un par `comercio_id`/`sucursal_id` en el MVP.

### Pronósticos → Planificación

Entrada: `producto_id`, `fecha_objetivo`, `cantidad_pronosticada` y `version_modelo`. `cantidad_pronosticada` representa unidades, no un porcentaje; si falta historial, se comunica `HISTORIAL_INSUFICIENTE`. El artefacto CatBoost queda en almacenamiento local y su versión se conserva con cada pronóstico.

### Planificación → Inventario → Compras

El plan consulta unidades disponibles de producto terminado y cantidades disponibles de ingredientes con su unidad. Entrega a compras `plan_id`, `ingrediente_id`, `cantidad_requerida`, `cantidad_disponible`, `cantidad_faltante` y `unidad`. Compras no vuelve a calcular el faltante; valida que no sea negativo y crea pedidos sin duplicarlos para el mismo plan e ingrediente.

### Compras → Canal de envío

Compras construye el pedido y llama a un adaptador con `pedido_id`, destinatario y texto. El adaptador devuelve `canal`, `identificador_externo`, `enviado_en` y `estado_envio`, o un error recuperable. Enviar con éxito significa que Telegram aceptó el mensaje; solo una respuesta explícita del proveedor cambia el pedido a `CONFIRMADO`. La repetición usa la misma clave de operación para evitar dos pedidos por un reintento.

### Automatizaciones → Módulos

Axel coordina servicios públicos de cada módulo mediante una clave de idempotencia, guarda ejecución e intentos, y registra el error o resultado. Cada módulo conserva la lógica de su dominio. Un fallo de red en Telegram deja el pedido pendiente y la ejecución programada para reintento; no se marca como confirmado.

## Planificación → Pronósticos

```python
servicio_pronosticos.obtener_pronostico(producto_id, fecha)
```

Respuesta:

Devuelve `datos = {id, tipo, estado, ejecutar_desde_utc, fecha_hora_simulada_local, parametros, clave_idempotencia, despachada_en, lease_hasta, creado_por, creado_en, ejecucion_id}`. `parametros` conserva `fecha_objetivo_demo` y `producto_ids` ordenados. Al crearla, `estado = PROGRAMADA` y se reserva una ejecución `PENDIENTE` con la misma clave y huella. **A02 solo guarda y consulta**: `despachada_en`, intentos y salida quedan vacíos hasta que A03 conecte Beat y los servicios de dominio. Repetir clave con entrada equivalente recupera el mismo ID, incluso si ya pasó la hora programada; cambiar la entrada devuelve `409 CLAVE_REUTILIZADA`. `GET /programaciones-demo` y `GET /ejecuciones-automatizacion` devuelven `datos` como listas recientes (máximo 50); las variantes `/{id}` devuelven un objeto o `404 PROGRAMACION_NO_ENCONTRADA` / `404 EJECUCION_NO_ENCONTRADA`. Todas las lecturas requieren Bearer.

`GET /ejecuciones-automatizacion/{id}` devuelve `id`, `programacion_id` nullable, `tipo`, `clave_idempotencia`, `huella_entrada`, `datos_entrada`, `estado`, `inicio_en`, `fin_en`, `proximo_intento_en`, `datos_salida`, `mensaje_error` e `intentos`. Cada intento incluye `id`, `numero_intento` (1–3), `inicio_en`, `fin_en`, `estado` y `mensaje_error`. Los estados de ejecución son `PENDIENTE`, `EN_EJECUCION`, `REINTENTANDO`, `COMPLETADA`, `FALLIDA`; los de programación `PROGRAMADA`, `DESPACHADA`, `CANCELADA`. Las funciones públicas `crear_o_recuperar_ejecucion(sesion, tipo, clave_idempotencia, datos_entrada, programacion_id=None)`, `iniciar_intento(sesion, ejecucion_id)` y `finalizar_intento(sesion, intento_id, estado, datos_salida=None, mensaje_error=None, proximo_intento_en=None)` **no hacen commit**: Edu, Kevin, Vera, Max y Aguirre pasan su sesión y confirman su propio caso de uso atómico. La tarea de dominio conserva la unicidad de sus efectos; el motor solo conserva el sobre. Los reintentos automáticos y el despacho recuperable pertenecen a A03. No se ofrece reintento manual de ejecución en A02.

## Contrato A03: despacho recuperable y servicios consumidores

La API A02 conserva las mismas rutas y agrega `despachada_en` y `lease_hasta` a cada ejecución; son instantes UTC o `null`. Los estados ya definidos en A02 reflejan ahora trabajo real del motor. `programacion_demo.estado=DESPACHADA` confirma que se reclamó la programación; no afirma que el cálculo de dominio haya terminado. `lease_hasta` puede quedar vacío después de completar, fallar o programar otro intento. El detalle debe mostrar el motivo de un servicio aún no conectado sin inventar corrida o plan.

El servicio `programar_ejecucion(sesion, *, tipo, ejecutar_desde_utc, fecha_hora_simulada_local, parametros, clave_idempotencia, creado_por=None)` admite `GENERAR_PROPUESTA` y `EVALUAR_PROMOCION`; crea programación y ejecución pendiente en la **sesión del consumidor, sin commit**.

Ejemplo de Vera tras un ajuste confirmado en la misma transacción:

```python
programar_ejecucion(
    sesion,
    tipo="EVALUAR_PROMOCION",
    ejecutar_desde_utc=hora_real_utc,
    fecha_hora_simulada_local=reloj_local,
    parametros={"lote_producto_id": lote_id},
    clave_idempotencia=f"promocion-ajuste-{movimiento_id}",
)
```

Edu puede llamar `crear_o_recuperar_ejecucion` desde la primera carga con su misma sesión. El despachador lee ambas clases de ejecución **después** del commit, por lo que el productor no publica un mensaje antes de persistir.

Cada dueño aporta un manejador `Callable[[Session, ContextoEjecucion], dict]` en `app.workers.tasks.manejadores.MANEJADORES`, enlazando su servicio público mediante una importación explícita y probada. `ContextoEjecucion` lleva `id`, `tipo`, `clave_idempotencia` y `datos_entrada`. El manejador recibe la sesión ya bloqueada, **no hace commit/rollback**, guarda su efecto local idempotente con esa clave y devuelve un objeto JSON con IDs reales. El motor confirma el efecto y `finalizar_intento` juntos. Un `ErrorDatos` registra fallo definitivo legible; `ErrorTransitorioInterno` permite hasta tres intentos totales. Un timeout genérico y cualquier efecto externo incierto no se reintentan automáticamente. Envío y conciliación de Telegram quedan bajo el contrato de Aguirre. El registro contiene los tres adaptadores de Kevin (`PREPARAR_MODELO`, `EVALUAR_MODELO`, `EVALUAR_PRONOSTICO`); plan y promoción siguen sin manejador.

Beat revisa cada 30 segundos. El motor confirma un lease y token en PostgreSQL antes de publicar en Redis; el vencimiento permite reenviar la **misma ejecución**, girando el token para descartar mensajes anteriores. Un worker que ya ejecuta mantiene bloqueo de fila durante su efecto local. Una interrupción posterior al inicio deja el intento visible y, al vencer su lease, el motor registra fallo transitorio y agenda el siguiente intento. Las esperas son 60–65 y 120–125 segundos. La demostración con un manejador de prueba se realiza en un esquema PostgreSQL aislado y una cola Redis separada; no acredita todavía los cálculos del resto del equipo.

## Inicialización → Ventas y catálogo

**E01 parcial disponible para K02/K03 (29-09-2026):** las funciones públicas `app.modules.productos.servicio.cargar_catalogo_bakery(sesion, lista)` y `resolver_sku(sesion, origen, sku_externo)` registran/resuelven el catálogo explícito.

`app.modules.ventas.servicio.importar_bakery(sesion, csv_path, clave_importacion)` agrega las líneas del CSV piloto por SKU y fecha, conserva una revisión inicial y devuelve cantidades de líneas aceptadas y negativas excluidas.

`leer_historial(sesion, producto_ids, inicio, fin_exclusivo)` devuelve una lista de `VentaHistorica(producto_id, sku_externo, fecha_local, unidades_vendidas, revision_venta_id)`.

Un día ausente no produce objeto; un cero explícito sí. `corregir_venta` crea revisión nueva sin borrar la anterior.

`listar_skus_bakery(sesion)` entrega el mapa de productos activos a SKU externo; `nombres_productos(sesion, ids)` entrega nombres para las vistas, y `limites_historial(sesion, ids)` devuelve primera y última fecha observada.

Todas reciben la misma `Session`, hacen `flush` cuando necesitan IDs y **no hacen commit**.

Ejemplo:

```python
leer_historial(
    sesion,
    [1],
    date(2022, 8, 1),
    date(2022, 8, 24),
)
```

Excluye la venta objetivo del 24.

El proveedor no crea SKU implícitos (`422 SKU_DESCONOCIDO`); una clave de importación repetida con otro archivo devuelve `409 CLAVE_REUTILIZADA`. Requiere migración `0002_e01_ventas`.

Se comprobó el consumo E01→K01–K03 con el CSV piloto en SQLite local; el upgrade y la operación en PostgreSQL siguen sin verificar.

**E02/E03 disponibles (29-09-2026):** el asistente de primera carga lee los dos libros XLSX o los cinco CSV. Si el archivo de ventas es el CSV de tickets del piloto, el adaptador `bakery` valida cada artículo contra `lista_productos_precios_limpia.md`, excluye las líneas negativas informando cuántas y agrega por fecha y artículo antes de validar.

* `POST /inicializacion/vista-previa` (Administrador, multipart con `archivos`, `fecha_objetivo_demo` y `fecha_referencia_stock`) **no escribe nada**. Devuelve `aceptable`, `total_errores`, `errores[]` con `campo` en forma `archivo:fila/columna`, `filas_por_hoja`, el resumen de ventas y catálogo, las tres huellas y, si aplicó, `adaptador_bakery`. Se reúnen todos los problemas en una sola respuesta, no solo el primero.

* `POST /inicializacion/confirmar` añade `clave_importacion` y persiste todo en una transacción: `409 YA_INICIALIZADA` si la instalación ya tiene otra carga aceptada, `422 CARGA_INVALIDA` si la validación falla, y la misma solicitud repetida devuelve `ya_estaba_cargada` sin duplicar. La respuesta trae `estado` y `pendiente_de[]`.

* `GET /inicializacion/estado` (Bearer) devuelve la fila única `configuracion_inicial` con estado, huellas y fechas del escenario.

* Transiciones para Kevin y Axel: `hay_datos_cargados(sesion)`, `marcar_entrenando`, `marcar_modelo_listo` y `marcar_fallo_entrenamiento`. Un fallo de entrenamiento vuelve a `DATOS_CARGADOS` y **no** obliga a recargar ventas ni stock.

* La carga invoca los puertos `ServicioRecetas` (Max, M01) y `ServicioInventario` (Vera, V01) de `backend/app/modules/inicializacion/puertos.py` con la **misma** sesión; los servicios participantes no confirman por separado. Mientras no existan, la carga persiste catálogo y ventas y deja el estado en `PENDIENTE` con `mensaje_error` indicando qué falta: la instalación **no** se declara inicializada por una carga parcial.

Desde el 30-09-2026 la ruta pasa `ServicioRecetasM01` y `ServicioInventarioV01`; una carga válida termina en `DATOS_CARGADOS`.

**Rutas de catálogo y ventas (E01/E04):** `GET /productos` (con `solo_demo`), `GET /ventas` (filtros `producto_id`, `desde`, `hasta`, `limite`; `422 RANGO_INVALIDO` si la fecha inicial es posterior a la final), `GET /ventas/{id}/revisiones` y `PATCH /ventas/{id}` (Administrador, exige `motivo`).

Una fecha sin fila no se devuelve ni se rellena con cero; un cero explícito sí aparece. Requiere `0004_e03_inicializacion`, que sucede a `0003_pronosticos`.

La primera carga recibe los dos libros Excel o cinco CSV del [contrato de primera inicialización](contrato-importaciones.md). Guarda `venta_diaria`, `producto`, `sku_producto`, `ingrediente`, `receta`, lotes y movimientos `APERTURA`.

El archivo de ventas `bakery` transforma `article` textual a `(origen, sku_externo)` y luego `producto.id` interno.

La misma `clave_importacion` y huella recupera el resultado; distinto archivo con la misma clave devuelve `409 CLAVE_REUTILIZADA`.

SKU no mapeado, dos sucursales, receta rota, stock negativo o unidad incompatible rechazan el lote completo.

Una fecha sin venta queda desconocida; cero explícito queda almacenado.

La venta histórica no descuenta el stock de apertura. Tras la inicialización, ventas diarias y stock se consultan y corrigen en PostgreSQL; los archivos no se vuelven a leer en cada plan. Una corrección de `venta_diaria` conserva revisión y obliga a nueva corrida si afecta entradas previas.

El período de evaluación se fija en la primera carga con la [política temporal](../../foodsave-ml/POLITICA_EVALUACION.md): los últimos 6 meses completos de prueba si hay al menos 24 meses, 3 si hay de 12 a menos de 24, o 1 si hay de 6 a menos de 12; se reserva validación anterior de 3, 3 o 1 mes, respectivamente. Menos de 6 meses no habilita métricas de demo.

La fecha objetivo demostrativa debe caer en la prueba reservada. `particion` y `version_modelo` quedan en los metadatos del artefacto; el test no se usa para seleccionar ni ajustar el modelo.

## Ventas → Pronósticos

La carga rápida del piloto se mantiene en `POST /api/v1/inicializacion/piloto-bakery` (Administrador, multipart `archivo` CSV, límite 25 MB).

Responde `202` con `datos.importacion_id`, `repetida`, `productos`, `filas_aceptadas`, `filas_negativas_excluidas`, `ventas_diarias_creadas`, `version_modelo`, `ejecucion_id` y `estado_ejecucion`.

Repetir el mismo archivo conserva la importación y la ejecución; el catálogo, las ventas y la reserva `PREPARAR_MODELO` se confirman juntos. Este atajo para el piloto existente es independiente del asistente completo y no marca `configuracion_inicial` como completa.

**Servicio K02 implementado:** `generar_corrida(sesion, ejecucion_id=..., clave_ejecucion=..., fecha_objetivo=..., producto_ids=..., tipo="DEMO_PROGRAMADA")` lee la interfaz pública de ventas de Edu con rango `[objetivo-28 días, objetivo)`, verifica el CBM y persiste una corrida y un pronóstico por producto sin confirmar la sesión.

`obtener_pronosticos(sesion, corrida_id)` entrega a Max `producto_id`, `estado` y `cantidad_pronosticada` nullable.

Producto fuera del artefacto produce `PRODUCTO_NO_CUBIERTO`; menos de siete observaciones conocidas en 28 días produce `HISTORIAL_INSUFICIENTE`.

Misma clave con mismo modelo, productos, historial y revisiones recupera la corrida; otra huella devuelve `409 CLAVE_REUTILIZADA`.

La fecha debe estar en la prueba reservada y ser posterior al corte del modelo.

**Preparación K01:** `POST /pronosticos/preparar-modelo` (Administrador) recibe:

```json
{
  "version_modelo": "demo-catboost-1",
  "clave_idempotencia": "modelo-demo-catboost-1"
}
```

Reserva una ejecución y responde `202` con `ejecucion_id`.

El worker lee ventas confirmadas en PostgreSQL, entrena sin Colab, publica un directorio versionado bajo `MODEL_ARTIFACT_DIR`, registra huella/partición en `artefacto_modelo` y reserva `EVALUAR_MODELO`.

La identidad externa del piloto se configura mediante `ML_COMERCIO_ID`/`ML_SUCURSAL_ID` (valores de demo `piloto`/`principal`) hasta que Edu entregue el estado de primera inicialización.

El disparador automático desde E03 sigue pendiente.

**Evaluación K03:** `solicitar_evaluacion_corrida(sesion, corrida_id)` reserva `EVALUAR_PRONOSTICO` con las revisiones actuales y puede llamarse desde el plan de Max.

`evaluar_corrida` conserva cada evaluación por `corrida_id`, producto y `revision_venta_id`; una corrección crea otra comparación sin borrar la anterior.

`EVALUAR_MODELO` crea corridas `BACKTEST` por fecha de la prueba con clave `backtest-{modelo_id}-{fecha}` y calcula métricas únicamente sobre pronósticos disponibles y ventas conocidas.

El resumen usa esas corridas canónicas, los mismos pares para ambos totales y no promedia WAPE diario.

**Lecturas K04:** `GET /pronosticos/modelos` devuelve hasta 50 versiones; `GET /pronosticos/corridas?modelo_id=...` lista hasta 50 corridas; `GET /pronosticos/corridas/{id}` agrega pronósticos y motivos.

`GET /pronosticos/evaluacion?modelo_id=...` devuelve versión, partición, métricas globales, serie diaria y `corrida_id` por fecha.

`GET /pronosticos/corridas/{id}/evaluacion` devuelve comparación por producto (ID y nombre) usando solo la revisión de venta vigente.

Todas requieren Bearer y el sobre `datos`.

`0003_pronosticos` depende de `0002_e01_ventas`.

La inferencia de la demo la inicia `GENERAR_PROPUESTA` a la hora programada. Su entrada interna es `fecha_objetivo` local, lista de `producto_id` seleccionados y `clave_ejecucion` derivada de la programación.

Solo se leen `venta_diaria` con `fecha_local < fecha_objetivo`.

Se valida el vector y la huella del `.cbm` según [contrato ML](../../foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md).

Resultado durable por producto:

```json
{
  "producto_id": 1,
  "fecha": "2026-09-24",
  "cantidad_pronosticada": 60,
  "confianza": 0.93
}
```

## Planificación → Inventario

```python
servicio_inventario.obtener_existencias(ingrediente_id)
```

Respuesta:

```json
{
  "ingrediente_id": 5,
  "existencias": 2,
  "unidad": "kg"
}
```

## Planificación → Compras

Las necesidades con faltante positivo alimentan [pedidos por proveedor](contrato-pedidos.md). Una corrida nueva o un ajuste de stock produce otro plan y conserva el anterior. Repetir la misma operación con igual entrada no duplica plan ni pedido.

## Inventario propio

Una apertura o ajuste identifica un lote de producto **o** ingrediente, `delta`, `motivo` y `clave_operacion`. Se bloquea el lote, se valida saldo final `>= 0` y se persisten movimiento y saldo en la misma transacción.

La misma clave con idénticos parámetros devuelve el movimiento existente; con parámetros distintos, `409 CLAVE_REUTILIZADA`.

El plan no es una operación de inventario. Las ventas históricas importadas tampoco lo son.

### M01 disponible: ingredientes y recetas versionadas (30-09-2026)

Funciones públicas; reciben la `Session` del llamador, hacen `flush` y **no** confirman:

* `app.modules.recetas.servicio.ServicioRecetasM01` implementa el puerto `ServicioRecetas` de la primera carga. Ya está conectado en `POST /inicializacion/confirmar`.

* `obtener_receta(sesion, receta_id) -> RecetaLeida` lee una versión concreta, activa o no; es la que el plan guarda para ser reproducible.

* `recetas_activas(sesion, producto_ids) -> dict[producto_id, RecetaLeida]` y `obtener_receta_activa(sesion, producto_id)`. Un producto sin receta no aparece en el diccionario (no es receta vacía).

* `RecetaLeida(receta_id, producto_id, version, activo, motivo, creado_en, lineas)`; cada línea trae `ingrediente_id`, `codigo`, `nombre`, `unidad_base` y `cantidad_por_unidad: Decimal` con 3 decimales, en la unidad base.

* `crear_version(sesion, producto_id, lineas, motivo, usuario_id)` es el único camino para cambiar una receta: crea la versión siguiente y desactiva la anterior. La misma composición que la activa no crea versión (`creada=False`).

* `app.modules.ingredientes.servicio.obtener_ingredientes(sesion, ids)` entrega el catálogo a inventario y compras.

Rutas: `GET /ingredientes`, `POST /ingredientes` y `PATCH /ingredientes/{id}` (Administrador); `GET /recetas` (productos activos con su receta activa o `null`), `GET /recetas/{receta_id}`, `GET /recetas/productos/{producto_id}/versiones` y `POST /recetas/productos/{producto_id}/versiones` (Administrador; 201 si crea, 200 si la composición no cambió).

Las cantidades viajan como texto con tres decimales.

```json
POST /recetas/productos/3/versiones

{
  "motivo": "Ajuste de hidratación",
  "lineas": [
    {
      "ingrediente_id": 1,
      "cantidad_por_unidad": "260"
    }
  ]
}

→ 201 {
  "datos": {
    "receta_id": 9,
    "version": 2,
    "activo": true,
    "creada": true,
    "lineas": [
      {
        "ingrediente_id": 1,
        "codigo": "harina",
        "unidad_base": "g",
        "cantidad_por_unidad": "260.000"
      }
    ]
  }
}
```

Errores propios: `422 UNIDAD_NO_PERMITIDA`, `409 CODIGO_DUPLICADO`, `409 UNIDAD_EN_USO` (una receta o un lote usa la unidad), `409 INGREDIENTE_EN_RECETA_ACTIVA` (al desactivar), `422 CANTIDAD_INVALIDA` (≤ 0 o más de 3 decimales), `422 PAREJA_DUPLICADA`, `422 REFERENCIA_ROTA`, `409 RECETA_DIFERENTE` (primera carga repetida con otra receta).

Migración `0005_m01_ingredientes_recetas`.

### V01/V02 disponibles: apertura, ajustes y stock por fecha (30-09-2026)

Implementado por Max Rojas por encargo de las tareas de Leonardo Vera.

* `app.modules.inventario.servicio.ServicioInventarioV01` implementa el puerto `ServicioInventario`, ya conectado en la primera carga. Cantidad `0` crea el lote con saldo cero y sin movimiento; cantidad positiva crea un único `APERTURA` con `efectivo_en_demo = fecha_referencia_stock 23:59` y clave derivada de `clave_operacion_base`, ítem y lote. Un lote no informado recibe código técnico estable `SIN-LOTE-…` y `lote_informado=false`.

* `registrar_ajuste(sesion, SolicitudAjuste(tipo_item, lote_id, delta, motivo, clave_operacion, efectivo_en_demo), usuario_id)` bloquea el lote con `SELECT … FOR UPDATE`, valida saldo final `>= 0` y guarda movimiento y saldo juntos. Producto: delta entero; ingrediente: hasta 3 decimales. `efectivo_en_demo` es hora local sin zona.

* `consultar_disponibilidad(sesion, fecha, tipo=None, producto_ids=None, ingrediente_ids=None) -> Disponibilidad` solo lee. Cada ítem trae `unidad`, `stock_conocido`, `cantidad_disponible` (`None` si no hay ningún lote: desconocido, no cero), `cantidad_prioridad`, `cantidad_excluida`, `vigencia_desconocida` y el detalle de lotes. `Disponibilidad.huella` resume lotes, saldos y fechas para que el plan detecte si el stock cambió; `leido_en` es el instante UTC de la lectura.

**Vida útil (acuerdo del equipo).** Producto de pastelería: máximo 5 días y `fecha_caducidad` es el día 5. Día de vida en la fecha consultada = `5 - (fecha_caducidad - fecha)`.

Días 1–3 `OPTIMO` (cuenta), 4–5 `PRIORIDAD` (cuenta y se vende primero), 6 en adelante `MERMA` (no cuenta); pasar `fecha_limite_venta` también es `MERMA`.

Ingrediente: `VIGENTE` hasta su caducidad inclusive, luego `VENCIDO`.

Sin caducidad: `DESCONOCIDO`, cuenta y activa `vigencia_desconocida`.

En la apertura, un producto con caducidad o límite de venta posterior a `fecha_referencia_stock + 4 días` se rechaza con `422 VIDA_UTIL_EXCEDIDA` (hoy aparece al confirmar, no en la vista previa).

Rutas:

* `GET /inventario/disponibilidad?fecha=YYYY-MM-DD[&tipo=producto|ingrediente]`
* `GET /inventario/movimientos?[tipo][&lote_id][&limite]`
* `POST /inventario/ajustes` (Administrador; 201 si es nuevo, 200 con `repetido=true` si la clave ya se aplicó igual).

```json
POST /inventario/ajustes

{
  "tipo": "producto",
  "lote_id": 1,
  "delta": "-1",
  "motivo": "Una baguette quemada",
  "clave_operacion": "ajuste-3f2a…",
  "efectivo_en_demo": "2022-08-24T17:45:00"
}

→ 201 {
  "datos": {
    "movimiento_id": 6,
    "tipo_movimiento": "AJUSTE",
    "delta": "-1",
    "saldo_resultante": "3",
    "repetido": false
  }
}
```

Errores propios: `404 LOTE_NO_ENCONTRADO`, `409 SALDO_INSUFICIENTE`, `409 CLAVE_REUTILIZADA`, `409 LOTE_EXISTENTE` (apertura repetida con otros datos), `422 VIDA_UTIL_EXCEDIDA`, `422 CANTIDAD_INVALIDA`, `422 MOTIVO_OBLIGATORIO`.

Migración `0006_v01_inventario`.

Pendiente de V03: agendar `EVALUAR_PROMOCION` después de un ajuste de producto.

## Automatizaciones de la exposición

`POST /programaciones-demo` recibe `tipo = GENERAR_PROPUESTA`, `ejecutar_desde_utc` (hora real futura), `fecha_hora_simulada_local` (fecha/hora histórica mostrada), `clave_idempotencia` y productos del escenario.

Devuelve `programacion_id`, `estado = PROGRAMADA` y `ejecutar_desde_utc`.

El reloj real inicia el trabajo; el reloj simulado determina los datos.

Beat consulta programaciones vencidas cada 30 segundos y el worker registra una ejecución durable con intentos. Puede haber un pequeño retraso de cola; la UI no promete disparo exacto al segundo.

Misma clave/entrada recupera la programación; otra entrada devuelve `409 CLAVE_REUTILIZADA`.

La carga inicial encola `PREPARAR_MODELO` por evento.

`POST /inventario/ajustes` registra un movimiento de producto con `efectivo_en_demo` local y agenda `EVALUAR_PROMOCION` para una hora real próxima.

La evaluación recibe el reloj simulado, lote, stock, fecha límite de venta y versión de la regla.

Usa `evaluar_promocion` y guarda por lote:

```json
{
  "ingrediente_id": 5,
  "requerido": 5.8,
  "disponible": 2,
  "faltante": 3.8
}
```

## Compras → Proveedores

```python
servicio_proveedores.buscar_proveedor_preferido(ingrediente_id)
```

## Excedentes → Promociones

```json
{
  "producto_id": 1,
  "existencias_actuales": 24,
  "ventas_estimadas": 9,
  "excedente_estimado": 15,
  "riesgo": "ALTO"
}
```
