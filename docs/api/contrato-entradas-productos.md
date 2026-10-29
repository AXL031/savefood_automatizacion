# Registro de entradas de productos

**28-10-2026 · Implementación solicitada por Axel.** Autor: Codex para Axel; dominio Inventario de Vera, Productos/UI compartida de Sanchez y coordinación Cueva. [Evidencia](../equipo/avances/cueva.md). Amplía la apertura inicial con entradas administrativas posteriores de productos terminados. No crea nuevos SKU, calcula producción ni consume ingredientes. La tienda sigue independiente y pendiente de integración.

## Flujo disponible

En Inventario, **Registrar entrada** permite seleccionar varios productos activos del catálogo y registrar hasta 100 lotes juntos. Un producto puede aparecer en varias filas con códigos de lote distintos. Fecha de entrada y motivo comunes; cada fila tiene producto, código de lote, cantidad entera, elaboración, límite de venta y caducidad. La UI propone un código editable por lote y fechas de hasta cinco días de vida, incluyendo elaboración.

La revisión muestra todos los lotes antes de confirmar. Si falla una fila, se revierte la entrada entera. Se conservan los lotes anteriores y se crean movimiento/saldo/nuevo lote en una única transacción. Historial paginado y detalle guardan responsable, momento, motivo, cantidades originales y referencias de movimiento. Cantidad ingresada y saldo actual son datos diferentes.

Inventario consulta **hoy en la zona del negocio** al abrirse, igual que Ventas; mantiene el filtro histórico y el botón Ver stock de hoy. Tras confirmar/recuperar una entrada muestra productos en su fecha de entrada y actualiza movimientos. No modifica la fecha histórica configurada para automatizaciones ni el entrenamiento.

## API

Base `/api/v1`, Bearer habitual. Administrador registra; Administrador/Operador consultan. Sobres `{"datos":...}` y errores estándar.

| Método y ruta | Resultado |
|---|---|
| GET `/inventario/entradas-productos/contexto` | Fecha actual del servidor, zona horaria, vida máxima en días y productos activos `{id,codigo,nombre,activo}` |
| POST `/inventario/entradas-productos` | 201 con detalle; repetición idéntica 200 |
| GET `/inventario/entradas-productos` | Historial con filtros opcionales `desde`, `hasta` inclusivos, `limite` 1–100 y `desplazamiento` >= 0 |
| GET `/inventario/entradas-productos/{id}` | Detalle y referencias de lotes/movimientos |
| GET `/inventario/entradas-productos/por-clave/{clave}` | Resultado por clave del usuario actual; 404 si aún no se confirmó |

Ejemplo ficticio (sustituir IDs por los del catálogo; no es una carga ya realizada):

```json
{
  "clave_operacion": "entrada-20261028-001",
  "fecha_entrada": "2026-10-28",
  "motivo": "Ingreso de productos del día",
  "lineas": [
    {"producto_id": 1, "codigo_lote": "CRO-2810-A", "cantidad": 30,
     "fecha_elaboracion": "2026-10-28", "fecha_limite_venta": "2026-10-29", "fecha_caducidad": "2026-10-30"},
    {"producto_id": 2, "codigo_lote": "BAG-2810-A", "cantidad": 20,
     "fecha_elaboracion": "2026-10-28", "fecha_limite_venta": "2026-10-28", "fecha_caducidad": "2026-10-29"}
  ]
}
```

## Validaciones e idempotencia

- IDs positivos y cantidades enteras estrictas de 1 a 1000000; se rechazan fracciones, booleanos, cero y negativos. De 1 a 100 filas. Campos adicionales rechazados.
- Código de lote obligatorio, no vacío tras trim, máximo 80 caracteres; identidad única por producto/código. Un código ya existente exige otro código o ajuste del lote original. No se reutilizan lotes vencidos ni se cambian sus fechas. El mismo código para productos diferentes sí es válido.
- Fechas ISO: `elaboración ≤ entrada ≤ límite de venta ≤ caducidad`. Caducidad como máximo elaboración + 4 días, vida útil total de cinco días. La fecha de entrada no puede ser futura respecto al servidor y zona del negocio. Se admite fecha anterior si todas las reglas del lote se cumplen; registrar una entrada antigua no vuelve vendible hoy un lote caducado.
- Motivo recortado de 3–300 caracteres. Clave de operación de 8–80 caracteres `[A-Za-z0-9._:-]`, por usuario. Huella de todo el contenido normalizado, con líneas ordenadas por producto/código. Cambiar el orden no duplica; reutilizar clave con otro contenido devuelve 409.
- PostgreSQL serializa misma clave con advisory lock transaccional y productos en orden de ID. Restricciones únicas protegen código/producto, entrada/clave y referencias de movimiento. Conflicto o fallo revierte todos los efectos.

401 sin sesión; 403 Operador intentando registrar; 404 entrada/clave inexistente; 409 clave reutilizada, producto inactivo/inexistente o lote repetido; 422 formatos, cantidades o fechas inválidos. Listar un rango invertido también devuelve 422.

## Respuestas y stock compartido

Detalle: `id`, `numero` (`E-00000001`), `fecha_entrada`, `motivo`, `usuario_id`, `nombre_usuario`, `creado_en` UTC y `lineas`. Cada línea conserva `id`, producto/código/nombre, código de lote, cantidad ingresada, elaboración/caducidad/límite, `lote_id` y `movimiento_id`. El listado añade `lotes` y `unidades` por entrada, y metadatos total/límite/desplazamiento.

Cada lote recibe `fecha_ingreso`. Los movimientos son tipo **ENTRADA**, positivos y solo de producto terminado; el instante de auditoría es real UTC, y el movimiento usa fecha de entrada con hora local de registro. No dispara automáticamente promociones, pagos o tareas. Ajustes/recepción de ingredientes mantienen sus propios contratos; ningún ajuste puede fecharse antes del ingreso conocido del lote.

`consultar_disponibilidad` excluye lotes de producto recibidos después de la fecha consultada; NULL mantiene comportamiento de lotes anteriores. Ventas verifica también fecha de ingreso y utiliza los mismos lotes para sus salidas FEFO. Sigue exigiendo precio y fechas vendibles; entrada no asigna precio. Estas consultas no reconstruyen saldos históricos anteriores a ajustes/ventas posteriores.

## Recuperación y persistencia

Antes de POST, la UI guarda solicitud completa en `sessionStorage`, por usuario. Doble clic bloqueado; red/5xx o sesión vencida conservan solicitud/clave. Al remontar, GET propio por clave recupera una confirmación ya hecha; reintentar usa la solicitud original. No cerrar/borrar la pestaña con una entrada pendiente. No es una cola offline ni sincronización entre dispositivos.

Migración aditiva **0022_entradas_productos** sobre 0021: tablas `entrada_productos` y `linea_entrada_productos`, columna nullable `lote_producto.fecha_ingreso` y CHECK de tipo/signo de ENTRADA. No reescribe migraciones anteriores. Los lotes previos reciben NULL sin alterar saldo ni caducidad. Downgrade bloqueado si hay entradas, movimientos ENTRADA o fechas de ingreso de producto conservadas.

Pruebas HTTP/stock/concurrencia en `test_entradas_productos.py`, DDL/preservación en `test_migracion_entradas.py`, cadena completa y metadatos en `test_migraciones_entregas.py`. Prueba React `node scripts/verificar-entradas.cjs`: varios productos, revisión, cantidades, hoy, doble clic, respuesta perdida/remontaje y permisos, con HTTP falso. QA y aplicación local se registran en Cueva; ejemplos y fixtures no son existencias reales.
