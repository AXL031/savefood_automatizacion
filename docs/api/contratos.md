# Contratos del recorrido demostrable

**Estado:** A01–A03 implementan acceso, programación y motor; las demás rutas de dominio son especificación de desarrollo. [Alcance del prototipo](../guia-inicio-desarrollo.md). Una instalación local tiene un comercio/sucursal (`negocio.id = 1`); no se envía `negocio_id` en cada solicitud. Las rutas de negocio requieren Bearer y los cambios de carga/stock requieren Administrador. Los servicios de un módulo exponen interfaces públicas; ningún módulo importa modelos privados de otro.

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

Cada dueño aporta un manejador `Callable[[Session, ContextoEjecucion], dict]` en `app.workers.tasks.manejadores.MANEJADORES`, enlazando su servicio público mediante una importación explícita y probada. `ContextoEjecucion` lleva `id`, `tipo`, `clave_idempotencia` y `datos_entrada`. El manejador recibe la sesión ya bloqueada, **no hace commit/rollback**, guarda su efecto local idempotente con esa clave y devuelve un objeto JSON con IDs reales. El motor confirma el efecto y `finalizar_intento` juntos. Un `ErrorDatos` registra fallo definitivo legible; `ErrorTransitorioInterno` permite hasta tres intentos totales. Un timeout genérico y cualquier efecto externo incierto no se reintentan automáticamente. Envío y conciliación de Telegram quedan bajo el contrato de Aguirre. La conexión de un manejador requiere que el dueño entregue contrato, idempotencia y prueba de su efecto; el registro base está vacío mientras esos servicios no existen.

Beat revisa cada 30 segundos. El motor confirma un lease y token en PostgreSQL antes de publicar en Redis; el vencimiento permite reenviar la **misma ejecución**, girando el token para descartar mensajes anteriores. Un worker que ya ejecuta mantiene bloqueo de fila durante su efecto local. Una interrupción posterior al inicio deja el intento visible y, al vencer su lease, el motor registra fallo transitorio y agenda el siguiente intento. Las esperas son 60–65 y 120–125 segundos. La demostración con un manejador de prueba se realiza en un esquema PostgreSQL aislado y una cola Redis separada; no acredita todavía los cálculos del resto del equipo.

## Inicialización → Ventas y catálogo


La primera carga recibe los dos libros Excel o cinco CSV del [contrato de primera inicialización](contrato-importaciones.md). Guarda `venta_diaria`, `producto`, `sku_producto`, `ingrediente`, `receta`, lotes y movimientos `APERTURA`. El archivo de ventas `bakery` transforma `article` textual a `(origen, sku_externo)` y luego `producto.id` interno. La misma `clave_importacion` y huella recupera el resultado; distinto archivo con la misma clave devuelve `409 CLAVE_REUTILIZADA`. SKU no mapeado, dos sucursales, receta rota, stock negativo o unidad incompatible rechazan el lote completo. Una fecha sin venta queda desconocida; cero explícito queda almacenado.

La venta histórica no descuenta el stock de apertura. Tras la inicialización, ventas diarias y stock se consultan y corrigen en PostgreSQL; los archivos no se vuelven a leer en cada plan. Una corrección de `venta_diaria` conserva revisión y obliga a nueva corrida si afecta entradas previas.

El período de evaluación se fija en la primera carga con la [política temporal](../../foodsave-ml/POLITICA_EVALUACION.md): los últimos 6 meses completos de prueba si hay al menos 24 meses, 3 si hay de 12 a menos de 24, o 1 si hay de 6 a menos de 12; se reserva validación anterior de 3, 3 o 1 mes, respectivamente. Menos de 6 meses no habilita métricas de demo. La fecha objetivo demostrativa debe caer en la prueba reservada. `particion` y `version_modelo` quedan en los metadatos del artefacto; el test no se usa para seleccionar ni ajustar el modelo.

## Ventas → Pronósticos

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
