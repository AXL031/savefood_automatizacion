# ADR-006: ventas diarias, lotes locales e identidad de pronósticos

**Estado:** aceptada para el prototipo universitario. Especificación, todavía sin migración ni rutas de dominio.

## Contexto

El dataset usa `article` textual; la base usa `producto.id` entero. El diseño anterior no alineaba nombres de ER y diccionario ni identificaba corridas repetidas. La decisión de importar cortes de Excel como fuente permanente de stock fue reemplazada por la elección posterior del equipo: **FoodSave mantiene ventas diarias y stock en su propia PostgreSQL**. El dataset y un archivo estático sirven para preparar la demostración, no son fuentes de verdad posteriores a la carga.

## Decisión

1. Sigue [ADR-005](ADR-005-instalacion-local-mvp.md): una instalación, comercio y sucursal; `negocio.id = 1`, sin `negocio_id` en tablas operativas. `sku_producto(origen, sku_externo, producto_id)` resuelve `article` a un producto interno. El mapeo es único y no crea productos silenciosamente.
2. `venta_diaria` guarda unidades no negativas por producto y fecha local. Es la serie que consume ML; no hay tickets, pagos, facturas ni devoluciones neteadas. La carga inicial del dataset se registra con clave y huella para no duplicarse. Las correcciones manuales son auditables. Una fecha ausente es desconocida, no cero.
3. `lote_ingrediente` y `lote_producto` son los saldos físicos de la instalación, con caducidad opcional. `movimiento_inventario` registra toda alta o ajuste y cambia el saldo del lote en la **misma transacción**, con clave idempotente única. `INVENTARIO`, `inventario_ingrediente` y `existencia_producto` son lecturas agregadas, no tablas físicas. `fecha_limite_venta` de producto es distinta de `fecha_caducidad`.
4. El prototipo inicia stock con un archivo estático de demostración o carga manual que produce movimientos de apertura. Las ventas históricas importadas **no descuentan ese stock**: representan un período anterior al escenario simulado. Durante la demo, solo un ajuste explícito modifica existencias. Esto evita aplicar ventas dos veces.
5. Cada ejecución de inferencia persiste `corrida_pronostico` con `fecha_objetivo`, `version_modelo`, huella de entradas y clave de idempotencia. `pronostico` es único por corrida/producto. `elemento_plan` es el nombre canónico; cada plan fija corrida y lectura de stock utilizada. Una nueva corrección genera una versión nueva, sin sobrescribir la anterior.
6. El cálculo de abastecimiento produce necesidades desde receta y stock. La decisión posterior [ADR-008](ADR-008-pedidos-desde-el-plan.md) convierte necesidades positivas en pedidos por proveedor y permite enviarlos a un chat de pruebas mediante Telegram; no confirma recepción ni altera inventario. La demo añade ejecución programada y sugerencias de promoción según [ADR-007](ADR-007-automatizaciones-demo.md), sin activar descuentos. Integración recurrente con Excel/Google Sheets queda para una etapa posterior.

## Consecuencias

La futura migración de dominio debe proteger cantidades no negativas, una sola venta diaria por producto/fecha, identidad externa única y movimiento/saldo atómicos. El plan no descuenta stock; producir, vender o recibir físicamente requeriría una operación explícita de inventario, fuera de la demo. El [esquema objetivo](../../base_de_datos/esquema-objetivo-mvp.md) fija tablas y restricciones del prototipo; la [guía de alcance](../../guia-inicio-desarrollo.md) distingue la demo de la visión futura.
