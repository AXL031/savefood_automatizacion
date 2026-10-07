# Contrato de primera inicialización

**Estado:** asistente completo implementado con recetas y apertura reales. La integración E03/K01 reserva entrenamiento durable al confirmar la carga completa. Los archivos se solicitan **solo la primera vez** y PostgreSQL queda como fuente de ventas y stock. El CSV piloto conserva su flujo independiente.

## Preparación automática E03/K01

`POST /inicializacion/confirmar` conserva HTTP 201 y añade `datos.ejecucion_id` nullable. Una carga completa reserva `PREPARAR_MODELO` en la misma transacción que catálogo, ventas, recetas, apertura y estado; una carga parcial no reserva entrenamiento. La revisión `0008_e03_modelo` añade `configuracion_inicial.preparacion_ejecucion_id`, FK nullable a ejecución con `ON DELETE RESTRICT`. Las revisiones anteriores se conservan.

`GET /inicializacion/estado` añade `preparacion_modelo`, null o `{ejecucion_id, estado, version_modelo, modelo_id, mensaje_error}`. Tras la carga queda `DATOS_CARGADOS` con ejecución `PENDIENTE`. El motor guarda `ENTRENANDO` al iniciar un intento, antes del cálculo largo. Éxito confirma artefacto, reserva de `EVALUAR_MODELO`, resultado y `MODELO_LISTO` juntos. El backtest tiene su ejecución independiente: modelo listo no significa evaluación terminada. Fallo o interrupción recuperada devuelve la instalación a `DATOS_CARGADOS` con mensaje, sin borrar ni cargar otra vez ventas o lotes.

`POST /inicializacion/reintentar-modelo` (Administrador) recibe `{ "clave_idempotencia": "reintento-1" }`, 1–64 caracteres `[A-Za-z0-9._:-]`, y responde 202 con el resumen de preparación. Sin carga completa devuelve `409 INICIALIZACION_NO_PREPARADA`. Una ejecución pendiente/activa/en reintento o un modelo listo se recupera sin reservar otra tarea. Tras un fallo definitivo, una clave nueva crea una ejecución y versión nuevas; repetir esa clave recupera su resultado. La instalación se bloquea al confirmar/reservar para serializar solicitudes concurrentes. Los callbacks comprueban ID de ejecución y huella de inicialización antes de cambiar estado; el piloto no cambia esta fila.

El asistente consulta el progreso periódicamente, enlaza la ejecución y ofrece reintento sin archivos cuando la preparación falla. Las cinco muestras CSV de `backend/tests/fixtures/primera_carga/` son sintéticas y cubren enero–septiembre de 2022; no acreditan calidad comercial del modelo.

## Acceso rápido del piloto implementado

`POST /api/v1/inicializacion/piloto-bakery` requiere Bearer de Administrador y `multipart/form-data` con el campo `archivo` (`.csv`, máximo 25 MB). Acepta las columnas originales `date,article,Quantity`; toma el catálogo de `lista_productos_precios_limpia.md` incluido en la aplicación. Tras validar, carga productos y ventas agregadas en una sola sesión, calcula la huella SHA-256 del archivo y reserva `PREPARAR_MODELO` en el mismo commit. Responde `202` con `datos = {importacion_id, repetida, productos, filas_aceptadas, filas_negativas_excluidas, ventas_diarias_creadas, version_modelo, ejecucion_id, estado_ejecucion}`. Repetir el mismo archivo recupera la importación y la ejecución sin duplicarlas; un error revierte todo. La UI `/inicializacion/piloto` muestra la carga, el estado de ejecución y un reintento de preparación si falla, sin volver a subir el CSV.

El CSV no se guarda en tablas ni se copia a la imagen Docker; se usa un archivo temporal que se borra al terminar la solicitud. Este acceso es solo para el dataset bakery y no establece el estado de primera inicialización completa.

`version_modelo` incorpora la política de entrenamiento (`piloto-q65v2-<huella>`). Una nueva política puede reservar otra preparación para el mismo archivo sin repetir las ventas; la idempotencia de ejecución aplica dentro de cada versión. Las versiones y evaluaciones anteriores se conservan.

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

La ruta de confirmación usa `ServicioRecetasM01` y `ServicioInventarioV01` con la sesión compartida. Una carga completa devuelve DATOS_CARGADOS y pendiente_de vacío. Cero de stock crea lote sin movimiento; caducidad de pastelería mayor que referencia+4 días provoca 422 VIDA_UTIL_EXCEDIDA en confirmación y revierte toda la transacción. La comprobación de esa regla en vista previa sigue pendiente. El disparador automático se conecta en la entrega E03/K01 descrita al inicio de este contrato.
