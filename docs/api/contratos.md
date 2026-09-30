# Contratos del recorrido demostrable

**Estado:** A01–A03 implementan acceso, programación y motor. El corte K01–K04 de pronósticos tiene rutas y servicios propios; la primera carga de Edu y el plan de Max todavía no lo consumen de extremo a extremo. Las demás rutas de dominio son especificación de desarrollo. [Alcance del prototipo](../guia-inicio-desarrollo.md). Una instalación local tiene un comercio/sucursal (`negocio.id = 1`); no se envía `negocio_id` en cada solicitud. Las rutas de negocio requieren Bearer y los cambios de carga/stock requieren Administrador. Los servicios de un módulo exponen interfaces públicas; ningún módulo importa modelos privados de otro.

## Convenciones HTTP

Respuesta exitosa: `{"datos": {...}, "metadatos": {...}}`; `metadatos` puede omitirse. Error implementado: `{"error":{"codigo":"CODIGO_ESTABLE","mensaje":"Texto legible","detalles":[]}}`. `detalles` se omite salvo en errores 422 y cada elemento indica `campo` y `mensaje`. HTTP `400` archivo o parámetro inválido, `401` sin sesión, `403` sin permiso, `404` ID inexistente, `409` duplicado/clave reutilizada, `422` esquema inválido, `503` configuración o artefacto no listo. Las rutas implementadas ya responden con este sobre para errores HTTP y de validación; cada dominio nuevo debe elegir un código estable específico cuando el genérico no baste. Las fechas son `YYYY-MM-DD`, instantes ISO 8601 UTC, unidades de producto enteras y cantidades de ingrediente decimales en unidad base.

### Contrato A01 disponible: acceso y configuración

`POST /autenticacion/iniciar-sesion` recibe `{"correo":"admin@example.com","contrasena":"..."}` y devuelve `datos.token_acceso`, `datos.tipo = bearer` y `datos.expira_en` UTC. `GET /autenticacion/mi-perfil` devuelve `datos = {id, correo, nombre, rol}`. Ambas rutas usan los roles `ADMINISTRADOR`/`OPERADOR`. Toda ruta protegida usa `app.core.identidad.identidad_actual`; las escrituras administrativas usan `requiere_administrador`. Falta de Bearer devuelve `401 AUTENTICACION_REQUERIDA`, credencial inválida `401 CREDENCIAL_INVALIDA`, usuario inactivo `401 USUARIO_NO_DISPONIBLE` y rol Operador en escritura administrativa `403 PERMISO_DENEGADO`. Credenciales incorrectas en inicio devuelven `401 CREDENCIALES_INVALIDAS` sin revelar cuál dato falló. No hay renovación: el cliente vuelve al inicio al recibir 401 en una ruta protegida.

`GET /negocios/actual` (Bearer) devuelve, por ejemplo, `{"datos":{"id":1,"nombre":"Comercio de demostración","zona_horaria":"America/Lima","moneda":"PEN","modo_envio_pedidos":"REQUIERE_APROBACION"}}`. `PATCH /negocios/actual` (Administrador) acepta cualquier subconjunto no vacío de `nombre`, `zona_horaria`, `moneda` y `modo_envio_pedidos`, y devuelve el mismo cuerpo actualizado. `null`, campos desconocidos y cuerpo vacío producen `422 DATOS_INVALIDOS`. Zona horaria debe existir en IANA; moneda son tres letras ASCII mayúsculas; modo es `REQUIERE_APROBACION` o `AUTOMATICO`. La respuesta 422 incluye detalles de campo y no guarda cambios parciales. El valor inicial del modo es `REQUIERE_APROBACION`. La función pública `app.modules.negocios.servicio.obtener_modo_envio_pedidos(sesion)` lee el modo vigente dentro de la sesión del consumidor, sin hacer commit; Aguirre debe copiarlo al crear cada pedido, de modo que un cambio posterior no altere pedidos ya creados. La revisión `0001a_configuracion` agrega y restringe la columna de modo; la futura `0002` de los demás dominios debe depender de `0001c_motor`.

## Contrato A02: programación y trazas persistidas

`POST /programaciones-demo` (Administrador) recibe `tipo = GENERAR_PROPUESTA`, `ejecutar_desde_utc` con zona UTC y hora futura, `fecha_hora_simulada_local` sin zona, `fecha_objetivo_demo` del mismo día simulado, `producto_ids` positivos y únicos (1–5) y `clave_idempotencia` de 1–128 caracteres `[A-Za-z0-9._:-]`. Ejemplo:

```json
{"tipo":"GENERAR_PROPUESTA","ejecutar_desde_utc":"2027-09-27T16:05:00Z","fecha_hora_simulada_local":"2022-08-24T10:00:00","fecha_objetivo_demo":"2022-08-24","producto_ids":[1,2,3],"clave_idempotencia":"demo-propuesta-2022-08-24-v1"}
```

Devuelve `datos = {id, tipo, estado, ejecutar_desde_utc, fecha_hora_simulada_local, parametros, clave_idempotencia, despachada_en, lease_hasta, creado_por, creado_en, ejecucion_id}`. `parametros` conserva `fecha_objetivo_demo` y `producto_ids` ordenados. Al crearla, `estado = PROGRAMADA` y se reserva una ejecución `PENDIENTE` con la misma clave y huella. **A02 solo guarda y consulta**: `despachada_en`, intentos y salida quedan vacíos hasta que A03 conecte Beat y los servicios de dominio. Repetir clave con entrada equivalente recupera el mismo ID, incluso si ya pasó la hora programada; cambiar la entrada devuelve `409 CLAVE_REUTILIZADA`. `GET /programaciones-demo` y `GET /ejecuciones-automatizacion` devuelven `datos` como listas recientes (máximo 50); las variantes `/{id}` devuelven un objeto o `404 PROGRAMACION_NO_ENCONTRADA` / `404 EJECUCION_NO_ENCONTRADA`. Todas las lecturas requieren Bearer.

`GET /ejecuciones-automatizacion/{id}` devuelve `id`, `programacion_id` nullable, `tipo`, `clave_idempotencia`, `huella_entrada`, `datos_entrada`, `estado`, `inicio_en`, `fin_en`, `proximo_intento_en`, `datos_salida`, `mensaje_error` e `intentos`. Cada intento incluye `id`, `numero_intento` (1–3), `inicio_en`, `fin_en`, `estado` y `mensaje_error`. Los estados de ejecución son `PENDIENTE`, `EN_EJECUCION`, `REINTENTANDO`, `COMPLETADA`, `FALLIDA`; los de programación `PROGRAMADA`, `DESPACHADA`, `CANCELADA`. Las funciones públicas `crear_o_recuperar_ejecucion(sesion, tipo, clave_idempotencia, datos_entrada, programacion_id=None)`, `iniciar_intento(sesion, ejecucion_id)` y `finalizar_intento(sesion, intento_id, estado, datos_salida=None, mensaje_error=None, proximo_intento_en=None)` **no hacen commit**: Edu, Kevin, Vera, Max y Aguirre pasan su sesión y confirman su propio caso de uso atómico. La tarea de dominio conserva la unicidad de sus efectos; el motor solo conserva el sobre. Los reintentos automáticos y el despacho recuperable pertenecen a A03. No se ofrece reintento manual de ejecución en A02.

## Contrato A03: despacho recuperable y servicios consumidores

La API A02 conserva las mismas rutas y agrega `despachada_en` y `lease_hasta` a cada ejecución; son instantes UTC o `null`. Los estados ya definidos en A02 reflejan ahora trabajo real del motor. `programacion_demo.estado=DESPACHADA` confirma que se reclamó la programación; no afirma que el cálculo de dominio haya terminado. `lease_hasta` puede quedar vacío después de completar, fallar o programar otro intento. El detalle debe mostrar el motivo de un servicio aún no conectado sin inventar corrida o plan.

El servicio `programar_ejecucion(sesion, *, tipo, ejecutar_desde_utc, fecha_hora_simulada_local, parametros, clave_idempotencia, creado_por=None)` admite `GENERAR_PROPUESTA` y `EVALUAR_PROMOCION`; crea programación y ejecución pendiente en la **sesión del consumidor, sin commit**. Ejemplo de Vera tras un ajuste confirmado en la misma transacción: `programar_ejecucion(sesion, tipo="EVALUAR_PROMOCION", ejecutar_desde_utc=hora_real_utc, fecha_hora_simulada_local=reloj_local, parametros={"lote_producto_id": lote_id}, clave_idempotencia=f"promocion-ajuste-{movimiento_id}")`. Edu puede llamar `crear_o_recuperar_ejecucion` desde la primera carga con su misma sesión. El despachador lee ambas clases de ejecución **después** del commit, por lo que el productor no publica un mensaje antes de persistir.

Cada dueño aporta un manejador `Callable[[Session, ContextoEjecucion], dict]` en `app.workers.tasks.manejadores.MANEJADORES`, enlazando su servicio público mediante una importación explícita y probada. `ContextoEjecucion` lleva `id`, `tipo`, `clave_idempotencia` y `datos_entrada`. El manejador recibe la sesión ya bloqueada, **no hace commit/rollback**, guarda su efecto local idempotente con esa clave y devuelve un objeto JSON con IDs reales. El motor confirma el efecto y `finalizar_intento` juntos. Un `ErrorDatos` registra fallo definitivo legible; `ErrorTransitorioInterno` permite hasta tres intentos totales. Un timeout genérico y cualquier efecto externo incierto no se reintentan automáticamente. Envío y conciliación de Telegram quedan bajo el contrato de Aguirre. El registro contiene los tres adaptadores de Kevin (`PREPARAR_MODELO`, `EVALUAR_MODELO`, `EVALUAR_PRONOSTICO`); plan y promoción siguen sin manejador.

Beat revisa cada 30 segundos. El motor confirma un lease y token en PostgreSQL antes de publicar en Redis; el vencimiento permite reenviar la **misma ejecución**, girando el token para descartar mensajes anteriores. Un worker que ya ejecuta mantiene bloqueo de fila durante su efecto local. Una interrupción posterior al inicio deja el intento visible y, al vencer su lease, el motor registra fallo transitorio y agenda el siguiente intento. Las esperas son 60–65 y 120–125 segundos. La demostración con un manejador de prueba se realiza en un esquema PostgreSQL aislado y una cola Redis separada; no acredita todavía los cálculos del resto del equipo.

## Inicialización → Ventas y catálogo

**E01 parcial disponible para K02/K03 (29-09-2026):** las funciones públicas
`app.modules.productos.servicio.cargar_catalogo_bakery(sesion, lista)` y
`resolver_sku(sesion, origen, sku_externo)` registran/resuelven el catálogo
explícito. `app.modules.ventas.servicio.importar_bakery(sesion, csv_path,
clave_importacion)` agrega las líneas del CSV piloto por SKU y fecha, conserva
una revisión inicial y devuelve cantidades de líneas aceptadas y negativas
excluidas. `leer_historial(sesion, producto_ids, inicio, fin_exclusivo)` devuelve
una lista de `VentaHistorica(producto_id, sku_externo, fecha_local,
unidades_vendidas, revision_venta_id)`. Un día ausente no produce objeto; un
cero explícito sí. `corregir_venta` crea revisión nueva sin borrar la anterior.
`listar_skus_bakery(sesion)` entrega el mapa de productos activos a SKU externo;
`nombres_productos(sesion, ids)` entrega nombres para las vistas, y
`limites_historial(sesion, ids)` devuelve primera y última fecha observada.
Todas reciben la misma `Session`, hacen `flush` cuando necesitan IDs y **no
hacen commit**. Ejemplo: `leer_historial(sesion, [1], date(2022, 8, 1),
date(2022, 8, 24))` excluye la venta objetivo del 24. El proveedor no crea
SKU implícitos (`422 SKU_DESCONOCIDO`); una clave de importación repetida con
otro archivo devuelve `409 CLAVE_REUTILIZADA`. Requiere migración
`0002_e01_ventas`. Se comprobó el consumo E01→K01–K03 con el CSV piloto en
SQLite local; el upgrade y la operación en PostgreSQL siguen sin verificar.

**E02/E03 disponibles (29-09-2026):** el asistente de primera carga lee los dos
libros XLSX o los cinco CSV. Si el archivo de ventas es el CSV de tickets del
piloto, el adaptador `bakery` valida cada artículo contra
`lista_productos_precios_limpia.md`, excluye las líneas negativas informando
cuántas y agrega por fecha y artículo antes de validar.

- `POST /inicializacion/vista-previa` (Administrador, multipart con `archivos`,
  `fecha_objetivo_demo` y `fecha_referencia_stock`) **no escribe nada**. Devuelve
  `aceptable`, `total_errores`, `errores[]` con `campo` en forma
  `archivo:fila/columna`, `filas_por_hoja`, el resumen de ventas y catálogo, las
  tres huellas y, si aplicó, `adaptador_bakery`. Se reúnen todos los problemas en
  una sola respuesta, no solo el primero.
- `POST /inicializacion/confirmar` añade `clave_importacion` y persiste todo en
  una transacción: `409 YA_INICIALIZADA` si la instalación ya tiene otra carga
  aceptada, `422 CARGA_INVALIDA` si la validación falla, y la misma solicitud
  repetida devuelve `ya_estaba_cargada` sin duplicar. La respuesta trae
  `estado` y `pendiente_de[]`.
- `GET /inicializacion/estado` (Bearer) devuelve la fila única
  `configuracion_inicial` con estado, huellas y fechas del escenario.
- Transiciones para Kevin y Axel: `hay_datos_cargados(sesion)`,
  `marcar_entrenando`, `marcar_modelo_listo` y `marcar_fallo_entrenamiento`. Un
  fallo de entrenamiento vuelve a `DATOS_CARGADOS` y **no** obliga a recargar
  ventas ni stock.
- La carga invoca los puertos `ServicioRecetas` (Max, M01) y
  `ServicioInventario` (Vera, V01) de
  `backend/app/modules/inicializacion/puertos.py` con la **misma** sesión; los
  servicios participantes no confirman por separado. Mientras no existan, la
  carga persiste catálogo y ventas y deja el estado en `PENDIENTE` con
  `mensaje_error` indicando qué falta: la instalación **no** se declara
  inicializada por una carga parcial.

**Rutas de catálogo y ventas (E01/E04):** `GET /productos` (con `solo_demo`),
`GET /ventas` (filtros `producto_id`, `desde`, `hasta`, `limite`; `422
RANGO_INVALIDO` si la fecha inicial es posterior a la final),
`GET /ventas/{id}/revisiones` y `PATCH /ventas/{id}` (Administrador, exige
`motivo`). Una fecha sin fila no se devuelve ni se rellena con cero; un cero
explícito sí aparece. Requiere `0004_e03_inicializacion`, que sucede a
`0003_pronosticos`.


La primera carga recibe los dos libros Excel o cinco CSV del [contrato de primera inicialización](contrato-importaciones.md). Guarda `venta_diaria`, `producto`, `sku_producto`, `ingrediente`, `receta`, lotes y movimientos `APERTURA`. El archivo de ventas `bakery` transforma `article` textual a `(origen, sku_externo)` y luego `producto.id` interno. La misma `clave_importacion` y huella recupera el resultado; distinto archivo con la misma clave devuelve `409 CLAVE_REUTILIZADA`. SKU no mapeado, dos sucursales, receta rota, stock negativo o unidad incompatible rechazan el lote completo. Una fecha sin venta queda desconocida; cero explícito queda almacenado.

La venta histórica no descuenta el stock de apertura. Tras la inicialización, ventas diarias y stock se consultan y corrigen en PostgreSQL; los archivos no se vuelven a leer en cada plan. Una corrección de `venta_diaria` conserva revisión y obliga a nueva corrida si afecta entradas previas.

El período de evaluación se fija en la primera carga con la [política temporal](../../foodsave-ml/POLITICA_EVALUACION.md): los últimos 6 meses completos de prueba si hay al menos 24 meses, 3 si hay de 12 a menos de 24, o 1 si hay de 6 a menos de 12; se reserva validación anterior de 3, 3 o 1 mes, respectivamente. Menos de 6 meses no habilita métricas de demo. La fecha objetivo demostrativa debe caer en la prueba reservada. `particion` y `version_modelo` quedan en los metadatos del artefacto; el test no se usa para seleccionar ni ajustar el modelo.

## Ventas → Pronósticos

La carga rápida del piloto se mantiene en `POST /api/v1/inicializacion/piloto-bakery` (Administrador, multipart `archivo` CSV, límite 25 MB). Responde `202` con `datos.importacion_id`, `repetida`, `productos`, `filas_aceptadas`, `filas_negativas_excluidas`, `ventas_diarias_creadas`, `version_modelo`, `ejecucion_id` y `estado_ejecucion`. Repetir el mismo archivo conserva la importación y la ejecución; el catálogo, las ventas y la reserva `PREPARAR_MODELO` se confirman juntos. Este atajo para el piloto existente es independiente del asistente completo y no marca `configuracion_inicial` como completa.

**Servicio K02 implementado:** `generar_corrida(sesion, ejecucion_id=..., clave_ejecucion=..., fecha_objetivo=..., producto_ids=..., tipo="DEMO_PROGRAMADA")` lee la interfaz pública de ventas de Edu con rango `[objetivo-28 días, objetivo)`, verifica el CBM y persiste una corrida y un pronóstico por producto sin confirmar la sesión. `obtener_pronosticos(sesion, corrida_id)` entrega a Max `producto_id`, `estado` y `cantidad_pronosticada` nullable. Producto fuera del artefacto produce `PRODUCTO_NO_CUBIERTO`; menos de siete observaciones conocidas en 28 días produce `HISTORIAL_INSUFICIENTE`. Misma clave con mismo modelo, productos, historial y revisiones recupera la corrida; otra huella devuelve `409 CLAVE_REUTILIZADA`. La fecha debe estar en la prueba reservada y ser posterior al corte del modelo.

**Preparación K01:** `POST /pronosticos/preparar-modelo` (Administrador) recibe `{"version_modelo":"demo-catboost-1","clave_idempotencia":"modelo-demo-catboost-1"}`, reserva una ejecución y responde `202` con `ejecucion_id`. El worker lee ventas confirmadas en PostgreSQL, entrena sin Colab, publica un directorio versionado bajo `MODEL_ARTIFACT_DIR`, registra huella/partición en `artefacto_modelo` y reserva `EVALUAR_MODELO`. La identidad externa del piloto se configura mediante `ML_COMERCIO_ID`/`ML_SUCURSAL_ID` (valores de demo `piloto`/`principal`) hasta que Edu entregue el estado de primera inicialización. El disparador automático desde E03 sigue pendiente.

**Evaluación K03:** `solicitar_evaluacion_corrida(sesion, corrida_id)` reserva `EVALUAR_PRONOSTICO` con las revisiones actuales y puede llamarse desde el plan de Max. `evaluar_corrida` conserva cada evaluación por `corrida_id`, producto y `revision_venta_id`; una corrección crea otra comparación sin borrar la anterior. `EVALUAR_MODELO` crea corridas `BACKTEST` por fecha de la prueba con clave `backtest-{modelo_id}-{fecha}` y calcula métricas únicamente sobre pronósticos disponibles y ventas conocidas. El resumen usa esas corridas canónicas, los mismos pares para ambos totales y no promedia WAPE diario.

**Lecturas K04:** `GET /pronosticos/modelos` devuelve hasta 50 versiones; `GET /pronosticos/corridas?modelo_id=...` lista hasta 50 corridas; `GET /pronosticos/corridas/{id}` agrega pronósticos y motivos. `GET /pronosticos/evaluacion?modelo_id=...` devuelve versión, partición, métricas globales, serie diaria y `corrida_id` por fecha. `GET /pronosticos/corridas/{id}/evaluacion` devuelve comparación por producto (ID y nombre) usando solo la revisión de venta vigente. Todas requieren Bearer y el sobre `datos`. `0003_pronosticos` depende de `0002_e01_ventas`.

La inferencia de la demo la inicia `GENERAR_PROPUESTA` a la hora programada. Su entrada interna es `fecha_objetivo` local, lista de `producto_id` seleccionados y `clave_ejecucion` derivada de la programación. Solo se leen `venta_diaria` con `fecha_local < fecha_objetivo`. Se valida el vector y la huella del `.cbm` según [contrato ML](../../foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md). Resultado durable por producto:

```json
{
  "corrida_id": 12,
  "producto_id": 1,
  "fecha_objetivo": "2022-08-24",
  "cantidad_pronosticada": 60,
  "version_modelo": "demo-catboost-1",
  "estado": "DISPONIBLE"
}
```

`cantidad_pronosticada` es `null` con `HISTORIAL_INSUFICIENTE` o `PRODUCTO_NO_CUBIERTO`. Una fecha futura sin observaciones necesarias no se rellena con cero. Misma clave y misma huella recupera la corrida; contenido distinto produce `409 CLAVE_REUTILIZADA`. Una versión nueva no borra corridas anteriores.

Al quedar listo el artefacto se encola `EVALUAR_MODELO`: backtest idempotente de un día adelante por fecha del tramo de prueba, con entradas fechadas antes del objetivo. Cada corrida `BACKTEST` guarda pronósticos y después se enlaza con la revisión de `venta_diaria` que sirvió como valor real. Al persistir una propuesta programada, `EVALUAR_PRONOSTICO` hace la misma comparación para esa corrida `DEMO_PROGRAMADA`; no vuelve a entrenar. Una corrección posterior de venta marca la evaluación anterior como histórica y requiere evaluación nueva vinculada a la revisión nueva, sin borrar el resultado anterior.

`GET /pronosticos/evaluacion` presenta el intervalo reservado, versión, serie por fecha con total previsto y total real conocido, `MAE`, `WAPE`, porcentaje dentro de ±20% y cobertura. `GET /pronosticos/corridas/{id}/evaluacion` detalla valores previsto/real, error absoluto y estado por producto. Solo cuentan filas con pronóstico disponible y venta real conocida; ausente no equivale a cero. `WAPE` queda «no definido» si la suma real es cero. El porcentaje ±20% sigue `|real-previsto| / max(real,1) <= 0,20`. Las métricas y la cobertura se rotulan como comprobación histórica exploratoria, con fecha concreta; no se muestra `100-WAPE` como «acierto».

## Pronósticos + Inventario → Plan

Entrada interna tras la inferencia: `corrida_id` y `clave_ejecucion`. El plan solo toma pronósticos disponibles con receta activa. Lee lotes para `fecha_objetivo` y guarda cifras de stock y versión de receta en `elemento_plan`/`necesidad_ingrediente`. No modifica saldos. Fórmulas del prototipo:

```text
cantidad_producir = max(0, cantidad_pronosticada - stock_producto_disponible)
cantidad_requerida_ingrediente = suma(cantidad_producir × cantidad_por_unidad)
cantidad_faltante = max(0, cantidad_requerida - stock_ingrediente_disponible)
```

La suma de ingredientes se redondea al final a tres decimales hacia arriba. `unidad` es `ingrediente.unidad_base`. Stock con vigencia desconocida se señala y requiere lectura cuidadosa de la propuesta; stock vencido no cuenta. La sugerencia de compra es cada `necesidad_ingrediente` con faltante positivo:

```json
{
  "plan_id": 7,
  "ingrediente_id": 5,
  "cantidad_requerida": "5.800",
  "cantidad_disponible": "2.000",
  "cantidad_faltante": "3.800",
  "unidad": "kg",
  "vigencia_stock_desconocida": false
}
```

Las necesidades con faltante positivo alimentan [pedidos por proveedor](contrato-pedidos.md). Una corrida nueva o un ajuste de stock produce otro plan y conserva el anterior. Repetir la misma operación con igual entrada no duplica plan ni pedido.

## Inventario propio

Una apertura o ajuste identifica un lote de producto **o** ingrediente, `delta`, `motivo` y `clave_operacion`. Se bloquea el lote, se valida saldo final `>= 0` y se persisten movimiento y saldo en la misma transacción. La misma clave con idénticos parámetros devuelve el movimiento existente; con parámetros distintos, `409 CLAVE_REUTILIZADA`. El plan no es una operación de inventario. Las ventas históricas importadas tampoco lo son.

## Automatizaciones de la exposición

`POST /programaciones-demo` recibe `tipo = GENERAR_PROPUESTA`, `ejecutar_desde_utc` (hora real futura), `fecha_hora_simulada_local` (fecha/hora histórica mostrada), `clave_idempotencia` y productos del escenario. Devuelve `programacion_id`, `estado = PROGRAMADA` y `ejecutar_desde_utc`. El reloj real inicia el trabajo; el reloj simulado determina los datos. Beat consulta programaciones vencidas cada 30 segundos y el worker registra una ejecución durable con intentos. Puede haber un pequeño retraso de cola; la UI no promete disparo exacto al segundo. Misma clave/entrada recupera la programación; otra entrada devuelve `409 CLAVE_REUTILIZADA`.

La carga inicial encola `PREPARAR_MODELO` por evento. `POST /inventario/ajustes` registra un movimiento de producto con `efectivo_en_demo` local y agenda `EVALUAR_PROMOCION` para una hora real próxima. La evaluación recibe el reloj simulado, lote, stock, fecha límite de venta y versión de la regla. Usa `evaluar_promocion` y guarda por lote:

```json
{
  "ejecucion_id": 19,
  "lote_producto_id": 3,
  "fecha_hora_simulada_local": "2022-08-24T18:00:00",
  "stock_leido": 15,
  "proponer": true,
  "descuento_pct": 20,
  "motivo": "Vence hoy y supera el umbral de stock"
}
```

Una evaluación negativa se persiste con `proponer=false`, `descuento_pct=null` y motivo concreto. La sugerencia no activa descuentos ni altera precios o stock. Un lote sin `fecha_limite_venta` o con lectura demasiado antigua nunca se presenta como promoción válida. La tarea no reutiliza el CatBoost diario para predecir venta restante del día.

`GET /ejecuciones-automatizacion/{id}` muestra programación, horas reales, hora simulada, estado, intentos `1/3` a `3/3`, salida o error y los IDs de corrida/plan/evaluaciones creados. El worker y Beat usan claves únicas en PostgreSQL: reentrega idéntica recupera efectos y no crea otra propuesta. Reintentos solo para fallos transitorios, según [política](../automatizacion/politica-de-reintentos.md).

## Evolución posterior

Recepción física, pago, **activación** de promociones, cierre diario real y conectores Excel/Google Sheets quedan fuera del primer recorrido. Proveedor mínimo, pedido y Telegram forman parte de este prototipo según [contrato-pedidos.md](contrato-pedidos.md). Las rutas de [rutas-api.md](rutas-api.md) están clasificadas como existentes o propuestas.

## Entrega M01 y V01/V02 integrada desde rojas

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

## L01 integrado: proveedores y ofertas (30-09-2026)

Migración `0007_l01_proveedores` sobre `0006_v01_inventario`. Código recibido de Aguirre y adaptado por coordinación de Axel: Base/sesión comunes, FK a ingrediente, permisos y sobre `datos`. `ServicioProveedores` hace flush, nunca commit; el llamador controla rollback/commit. `oferta_preferida_para_compras` es la consulta pública para Compras (consumidor L02 todavía pendiente).

Lecturas con Bearer: GET `/proveedores`, GET `/proveedores/{id}/ofertas` y GET `/proveedores/ofertas/preferida/{ingrediente_id}`. Administrador: POST `/proveedores`, PATCH `/{id}/estado?activo=false`, PUT `/{id}/chat?chat_id=...`, POST `/{id}/verificar-destino`, POST `/{id}/ofertas`, POST `/ofertas/{id}/preferida` y PATCH `/ofertas/{id}/desactivar`, todas bajo `/proveedores` y `/api/v1`.

Ejemplo de oferta: `{"ingrediente_id": 1, "descripcion": "Saco", "unidad_compra": "saco", "factor_conversion": "25000", "minimo": "0", "multiplo": "1", "preferida": true}`. Factor/múltiplo positivos y mínimo no negativo, hasta 14 dígitos y 4 decimales; ingrediente debe existir y estar activo. Una preferida activa por ingrediente está protegida por índice único parcial. Los nombres implementados `factor_conversion`, `minimo`, `multiplo`, `activa`, `chat_id_pruebas` corresponden respectivamente a los conceptos de diseño `factor_a_unidad_base`, `minimo_compra`, `multiplo_compra`, `activo`, `telegram_chat_id`; los consumidores usan los nombres del servicio publicado.

Errores: 404 `REFERENCIA_NO_ENCONTRADA`/`OFERTA_NO_ENCONTRADA`, 409 `CONFLICTO_PROVEEDORES`, 422 validación común, 401 sin sesión y 403 Operador en escritura. La respuesta de consulta expone `compra_automatica_habilitada` y `motivo_bloqueo`; no crea ni envía pedidos. Sin adaptador Telegram la verificación retorna `verificado=false` y detalle explícito. L01 sigue parcial por canal/UI; L02–L04 no implementados por esta integración.
