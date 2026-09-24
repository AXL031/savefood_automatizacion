# Diccionario de datos del MVP — propuesta para revisión del equipo

Este diccionario sigue la [decisión de instalación local](../arquitectura/decisiones/ADR-005-instalacion-local-mvp.md): una base por comercio, una sucursal por instalación. Es el contrato de diseño antes de las migraciones de cada módulo. La migración inicial solo crea `negocio` y `usuario`; cada responsable implementa y revisa las tablas de su dominio. Los campos pendientes de negocio no se deben inventar en una migración sin actualizar este documento.

## Convenciones compartidas

| Regla | Decisión |
|---|---|
| Claves internas | `id` entero autogenerado; claves foráneas del mismo tipo e índices en relaciones consultadas. |
| Tiempo | `creado_en` y `actualizado_en` como instante UTC con zona horaria; fechas de venta, plan y pronóstico como `date` local según `negocio.zona_horaria`. |
| Cantidades | Unidades de producto enteras no negativas; ingredientes como `numeric(14,3)` no negativo. Se registra la unidad de medida del ingrediente. |
| Dinero | `numeric(14,2)` no negativo y moneda definida en `negocio`; no usar coma flotante. |
| Borrado | Desactivar catálogos con `activo`; no borrar operaciones históricas por cascada. |
| Auditoría | Toda operación automática y envío externo tiene estado, instante y referencia a su origen. |
| Datos desconocidos | La ausencia de una venta diaria no equivale a cero ventas. Un cero explícito sí es cero conocido. |

## Núcleo inicial — Axel

| Tabla | Campos y restricciones principales | Relaciones |
|---|---|---|
| `negocio` | `id` con valor único `1`, `nombre` texto obligatorio, `zona_horaria` texto obligatorio, `moneda` código de 3 caracteres, `hora_apertura` y `hora_cierre` opcionales, `creado_en`, `actualizado_en`. | Registro único por instalación. |
| `usuario` | `id`, `correo` obligatorio y único sin distinguir mayúsculas, `hash_contrasena`, `nombre`, `rol` (`ADMINISTRADOR`, `OPERADOR`), `activo`, `creado_en`, `actualizado_en`. | Usuarios de la instalación. |

## Catálogos y operación

| Dueño | Tablas previstas | Restricciones que deben conservarse |
|---|---|---|
| Leonardo Vera | `producto`, `venta`, `registro_produccion`, `inventario_ingrediente`, `movimiento_inventario`, `existencia_producto` | Producto con código estable y nombre; venta con producto, fecha local, cantidad, origen y referencia externa opcional; referencia externa única por origen si existe; producción y movimientos con cantidad positiva y tipo; existencias de ingredientes y productos terminados separadas. |
| Kevin Bohorquez | `ingrediente`, `receta`, `receta_ingrediente`, `pronostico`, `plan_produccion`, `elemento_plan`, `necesidad_ingrediente` | Ingrediente con unidad fija; receta ligada a producto y componentes únicos por ingrediente; pronóstico único por producto, fecha y versión/corrida; plan con elementos únicos por producto; necesidades únicas por ingrediente dentro del plan. |
| Leonardo Aguirre | `proveedor`, `proveedor_ingrediente`, `pedido_compra`, `elemento_pedido`, `envio_pedido` | Pedido ligado a proveedor y opcionalmente a plan; elementos únicos por ingrediente; `envio_pedido` conserva canal, identificador externo, instante, resultado e intento; confirmar el pedido requiere evidencia independiente de la aceptación de Telegram. |
| Max Rojas | `deteccion_excedente`, `promocion`, `registro_desperdicio` | Detección ligada a producto y medición temporal; promoción ligada a detección y producto; desperdicio real separado de excedente estimado. |
| Axel Cueva | `automatizacion`, `ejecucion_automatizacion`, `intento_automatizacion`, `notificacion` | Ejecución con clave de idempotencia única por acción de negocio; intentos numerados y únicos dentro de cada ejecución; envío y error trazables. |

`existencia_producto` se incluye porque el plan resta productos terminados disponibles. Las existencias pueden derivarse de movimientos, pero si se guarda un saldo materializado debe actualizarse en la misma transacción que el movimiento.

## Puertas antes de cada migración de dominio

El dueño del módulo completa para sus tablas: columna, tipo SQL, nulabilidad, valor por defecto, `CHECK`, claves únicas, índices, claves foráneas y política de actualización/borrado. Otro dueño revisa las relaciones compartidas antes de unir la migración. Una migración aplicada no se reescribe; los cambios posteriores usan una migración nueva.

Quedan por acordar con datos reales: unidad y conversión de cada ingrediente, política de devoluciones de ventas, momento de cierre del día, stock de producto terminado al inicio del día, y qué respuesta exacta constituye confirmación del proveedor. Estas decisiones afectan reglas de negocio y deben cerrarse antes de migrar las tablas correspondientes.
