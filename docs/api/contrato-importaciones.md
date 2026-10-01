# Contrato de primera inicialización

**Estado:** asistente completo implementado: XLSX/CSV, vista previa, carga atómica de catálogos/ventas/recetas/lotes y preparación ML automática. PostgreSQL es la fuente después de aceptar. Ver contrato E03 de este corte y registros de Edu/Kevin/Axel; plan/pedidos/promociones no se declaran completos.

## Acceso rápido del piloto implementado

`POST /api/v1/inicializacion/piloto-bakery` requiere Bearer de Administrador y `multipart/form-data` con el campo `archivo` (`.csv`, máximo 25 MB). Acepta las columnas originales `date,article,Quantity`; toma el catálogo de `lista_productos_precios_limpia.md` incluido en la aplicación. Tras validar, carga productos y ventas agregadas en una sola sesión, calcula la huella SHA-256 del archivo y reserva `PREPARAR_MODELO` en el mismo commit. Responde `202` con `datos = {importacion_id, repetida, productos, filas_aceptadas, filas_negativas_excluidas, ventas_diarias_creadas, version_modelo, ejecucion_id, estado_ejecucion}`. Repetir el mismo archivo recupera la importación y la ejecución sin duplicarlas; un error revierte todo. La UI `/inicializacion/piloto` muestra la carga, el estado de ejecución y un reintento de preparación si falla, sin volver a subir el CSV.

El CSV no se guarda en tablas ni se copia a la imagen Docker; se usa un archivo temporal que se borra al terminar la solicitud. Este acceso es solo para el dataset bakery y no establece el estado de primera inicialización completa.

`version_modelo` incorpora la política de entrenamiento (`piloto-q65v2-<huella>`). Una nueva política puede reservar otra preparación para el mismo archivo sin repetir las ventas; la idempotencia de ejecución aplica dentro de cada versión. Las versiones y evaluaciones anteriores se conservan.

## E03 disponible: carga completa y preparación automática de ML

### Completar una instalación que ya cargó el piloto (30-09-2026)

Mientras la primera carga siga `PENDIENTE` y sin huella aceptada, confirmar los cinco archivos puede completar el piloto existente sin reinicializar. Deben contener exactamente los mismos SKU bakery, activos y con correspondencia uno a uno. Se reconocen los códigos técnicos `bakery-<hash del SKU>` del piloto; se adoptan los códigos legibles, nombres y selección `demostrar` de `productos.csv`, conservando `producto.id` y `sku_producto`. Un catálogo ordinario debe coincidir también en código→SKU; no se intercambian identidades ni se fusionan catálogos distintos.

Las ventas ya cargadas del periodo entregado deben aparecer con el mismo valor. Se conservan su ID, importación y revisiones; solo se insertan los pares nuevos explícitos del archivo y su revisión inicial. Cambiar u omitir un par conocido devuelve `409 HISTORIAL_DIFERENTE`; catálogo incompatible devuelve `409 CATALOGO_DIFERENTE`. No se generan ceros por ausencia: un cero nuevo solo se acepta cuando el archivo lo declara. La nueva importación conserva su propia clave/huella; `ventas_diarias` cuenta filas creadas, no las reutilizadas. La carga rápida del piloto sigue rechazando periodos superpuestos bajo otra clave.

Los servicios públicos `registrar_catalogo(..., completar_piloto=True)` y `registrar_ventas_diarias(..., reutilizar_identicas=True)` son opciones explícitas del coordinador de primera carga. Ninguno confirma la sesión. Catálogo, filas nuevas, recetas, apertura y reserva ML siguen en una sola transacción: un conflicto o fallo de stock revierte también el cambio de códigos y selección. No se eliminan modelos/evaluaciones anteriores ni se modifica una inicialización completa aceptada; la carga completa reserva su propia versión ML. Repetir la misma entrega aceptada no duplica importaciones, movimientos ni preparación.

La confirmación completa reserva PREPARAR_MODELO en la misma sesión que catálogo, ventas, recetas, apertura y estado DATOS_CARGADOS. No publica a Redis antes del commit: Beat reclama la ejecución durable. Repetir los mismos archivos recupera la carga y no crea otra preparación. El piloto mantiene su contrato separado y no modifica la fila de inicialización.

`GET /api/v1/inicializacion/estado` (Bearer) añade `preparacion_numero`, `modelo_id`, `preparacion` y `evaluacion`. Los dos últimos son null o `{id, estado, mensaje_error}`; sus estados son PENDIENTE, EN_EJECUCION, REINTENTANDO, COMPLETADA o FALLIDA. `modelo_id` referencia el artefacto persistido; MODELO_LISTO significa artefacto disponible, no evaluación terminada. El dashboard debe consultar ese modelo y comprobar `evaluacion.estado`.

`POST /api/v1/inicializacion/reintentar-preparacion` requiere Administrador, no recibe archivos ni cuerpo y responde 202 con el mismo estado ampliado. Sin carga completa devuelve 409 DATOS_NO_CARGADOS. Si la preparación/evaluación está activa o completada correctamente, recupera la reserva actual. Tras fallo definitivo reserva una generación nueva bajo bloqueo de la fila única; dos solicitudes simultáneas recuperan la misma nueva ejecución. Un backtest fallido reutiliza el modelo ya entrenado y reserva otra evaluación, sin importar ni entrenar nuevamente.

La versión del modelo es `inicial-q65v2-<24 caracteres de huella_solicitud>`; cada generación conserva su ejecución anterior e intentos. El motor confirma ENTRENANDO junto con el inicio durable del intento, antes del cálculo largo. El handler confirma MODELO_LISTO, modelo y reserva del backtest junto con su resultado; fallo o recuperación por lease conserva la carga y vuelve a DATOS_CARGADOS con mensaje. Los reintentos automáticos permanecen visibles en REINTENTANDO. Error por menos de seis meses completos se explica sin marcar un modelo listo.

Servicios públicos: `inicializacion.servicio.solicitar_preparacion`, `iniciar_preparacion`, `completar_preparacion` y `fallar_preparacion`; `automatizaciones.servicio.consultar_ejecucion`/`consultar_ejecucion_por_clave`. No hacen commit/rollback. Los callbacks AL_INICIAR y AL_FALLAR reciben `(sesion, contexto)` y `(sesion, contexto, mensaje)`; el motor los invoca en sus transacciones de inicio/fallo y recuperación. Solo el adaptador PREPARAR_MODELO con huella_inicializacion enlaza el estado E03; preparaciones manuales/piloto mantienen su comportamiento.

Migración aditiva `0008_e03_preparacion_ml` sobre 0007: preparacion_ejecucion_id y modelo_id nullable con FK RESTRICT, preparacion_numero no negativo con default 0. Conserva cargas previas; una carga completa anterior sin reserva puede usar el endpoint de preparación sin subir archivos. UI `/inicializacion` refresca estado cada tres segundos, muestra ejecución/evaluación, ofrece reintento y enlace al panel, y oculta la carga cuando ya está aceptada.

Prueba real del corte: PostgreSQL/Redis/CatBoost y Beat con seis meses de ventas de fixture; entrenamiento, fallo controlado de evaluación, reintento que conserva un único modelo y dashboard con pares persistidos. No acredita calidad comercial ni implementa plan, pedidos o promociones.

## Entrega

- Preferida: `ventas.xlsx` con hoja `ventas` y `catalogo.xlsx` con hojas `productos`, `ingredientes`, `recetas`, `stock_inicial`.
- Equivalente CSV UTF-8: `ventas.csv`, `productos.csv`, `ingredientes.csv`, `recetas.csv`, `stock_inicial.csv`. Un CSV no puede contener varias hojas. Encabezados exactos y fechas `YYYY-MM-DD`.
- El sistema muestra vista previa, cantidad de filas, productos mapeados, fechas cubiertas, errores por archivo/hoja/fila y huellas. Solo una aceptación explícita inicia la carga. Si falla una validación, no se marca inicializado ni se entrena.
- El asistente pide `fecha_objetivo_demo` y `fecha_referencia_stock` local. Para el caso del dataset se propone `2022-08-24` y stock simulado al cierre de `2022-08-23`. Se rechaza una referencia de stock igual o posterior al objetivo. Son supuestos visibles, no una fotografía histórica real del comercio.
- `clave_importacion` estable y SHA-256 canónico evitan duplicar la carga al reintentar. Los dos archivos se conservan como referencia de auditoría; ninguna ruta absoluta de la computadora del usuario entra en las tablas de negocio. `configuracion_inicial` pasa por `PENDIENTE → DATOS_CARGADOS → ENTRENANDO → MODELO_LISTO`.

## Ventas históricas

La hoja `ventas` usa `fecha_local`, `sku_externo`, `unidades_vendidas` (entero `>= 0`). Es una fila por fecha y SKU, incluido cero explícito; fila ausente significa desconocido. El CSV real del piloto tiene columnas `date`, `article`, `Quantity` y líneas de ticket: el adaptador `bakery` las valida y agrega a la misma forma diaria, conservando el archivo original y reportando filas negativas excluidas. `article` es texto externo; `sku_producto(origen, sku_externo)` lo resuelve a `producto.id`. El par `comercio_id`/`sucursal_id` canónico se toma del único negocio local cuando el archivo carece de él; si está presente debe ser un único par coincidente. No se mezclan dos sucursales.

```csv
fecha_local,sku_externo,unidades_vendidas
2022-08-23,BAGUETTE,12
2022-08-23,CROISSANT,0
```

Todos los SKU de ventas deben aparecer en `productos`; no se crean productos a escondidas ni se descartan filas desconocidas. El archivo puede contener todo el historial de productos; solo los 3–5 productos con receta seleccionados participan en el plan de la demostración. El entrenamiento usa únicamente días anteriores a la fecha objetivo. Las ventas históricas no descuentan stock inicial, que representa un escenario simulado posterior a esas ventas.

## Catálogo y recetas

| Hoja | Columnas obligatorias | Regla |
|---|---|---|
| `productos` | `codigo`, `nombre`, `sku_externo`, `demostrar` | `codigo` y `sku_externo` únicos, texto no vacío; `demostrar` es `si` o `no`. Elegir 3–5 `si` con historial y receta. |
| `ingredientes` | `codigo`, `nombre`, `unidad_base` | Código único; unidades permitidas en la plantilla: `g`, `kg`, `ml`, `l`, `unidad`. No se convierten unidades implícitamente. |
| `recetas` | `codigo_producto`, `codigo_ingrediente`, `cantidad_por_unidad` | Una línea por pareja; cantidad decimal positiva en la **unidad base** del ingrediente. Cada producto con `demostrar=si` necesita al menos una línea. La primera carga crea versión de receta `1`. |

El catálogo inicial no incluye precios ni proveedores; después de cargarlo, el administrador configura el proveedor de prueba, sus ofertas por ingrediente y el chat de Telegram según el [contrato de pedidos](contrato-pedidos.md). No hay fórmulas de costo ni cambios automáticos de receta. Códigos repetidos, referencias inexistentes y cantidades inválidas rechazan el catálogo completo. Una receta posterior se versiona; no edita la versión usada por un plan.

## Stock inicial

La hoja `stock_inicial` usa `tipo` (`producto`/`ingrediente`), `codigo` interno del catálogo, `cantidad` no negativa, `codigo_lote` opcional, `fecha_caducidad` opcional y `fecha_limite_venta` opcional solo para producto. Para cada producto seleccionado y cada ingrediente de sus recetas se exige una fila o una fila explícita de cantidad `0`: la ausencia significa **stock desconocido**, no cero. La cantidad de producto es entera; la de ingrediente usa su unidad base y hasta tres decimales. No se permite un mismo lote dos veces para el mismo ítem. Si lote no se conoce, el importador asigna un código técnico único y marca procedencia «lote no informado»; la caducidad permanece desconocida.

```csv
tipo,codigo,cantidad,codigo_lote,fecha_caducidad,fecha_limite_venta
producto,baguette,4,PT-001,2022-08-25,2022-08-24
ingrediente,harina,12.000,ING-001,2022-12-31,
```

El stock positivo se inserta mediante movimientos `APERTURA` idempotentes y saldo por lote en la misma transacción. Una fila explícita de cero registra stock conocido sin crear un movimiento de delta cero. Después se ajusta **en FoodSave** mediante movimientos `AJUSTE`; no hace falta volver a subir los archivos. La carga inicial no ejecuta ventas ni producción física y no descuenta stock por el historial importado. Lotes vencidos antes de la fecha objetivo no aportan disponibilidad; fecha desconocida produce advertencia en el plan.

## Entrenamiento y disponibilidad

Tras aceptar datos, la preparación separa entrenamiento, validación y prueba por la [regla de duración y meses completos](../../foodsave-ml/POLITICA_EVALUACION.md), entrena CatBoost **una vez** sin usar la prueba para ajustar/seleccionar y guarda `.cbm` y metadatos (`version_modelo`, SHA-256, variables ordenadas, productos cubiertos y partición). Para el CSV piloto, validación es abril–junio de 2022 y prueba julio–septiembre de 2022; `2022-08-24` cae en prueba. La fecha elegida para demo debe estar en la prueba reservada. Tras preparar el modelo, `EVALUAR_MODELO` realiza un backtest cronológico sobre esa prueba. Puede tardar; un fallo de entrenamiento deja el sistema en `DATOS_CARGADOS` y permite reintentar sin recargar ventas o stock. La acción programada solo carga el artefacto listo y hace inferencia; las ventas reales del objetivo solo aparecen después como comparación. Las métricas históricas no certifican uso comercial.


## Integración de puertos M01/V01 (30-09-2026)

La ruta de confirmación usa `ServicioRecetasM01` y `ServicioInventarioV01` con la sesión compartida. Una carga completa devuelve DATOS_CARGADOS y pendiente_de vacío. Cero de stock crea lote sin movimiento; caducidad de pastelería mayor que referencia+4 días provoca 422 VIDA_UTIL_EXCEDIDA en confirmación y revierte toda la transacción. La comprobación de esa regla en vista previa sigue pendiente. El entrenamiento automático desde el asistente completo no se declara conectado.
