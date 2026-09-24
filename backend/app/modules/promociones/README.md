# Promociones

Generación, activación y seguimiento de promociones.

## Primera regla configurable

`reglas.py` contiene una regla pura para **proponer** una promoción, sin un
segundo modelo de aprendizaje automático. El disparador se evalúa por producto
y sucursal con la hora local del comercio:

1. El producto tiene como fecha límite de venta el día de la evaluación.
2. La hora está entre `hora_revision` (incluida) y `hora_cierre` (excluida).
3. Hay una lectura de stock no más antigua que el límite configurado, por
   defecto 30 minutos, y no existe una promoción activa para ese producto.
4. `stock_actual > stock_umbral`. El umbral es el número de unidades que el
   comercio aún espera vender sin promoción o considera aceptable conservar.
5. El descuento propuesto no supera el máximo permitido por el comercio.

Ejemplo provisional: si el pan deja de venderse hoy al cierre, a las 18:00
quedan 15 unidades y el umbral es 10, se propone un descuento del 20 % si el
máximo configurado es al menos 20 %. Con 10 unidades o menos no se propone.
Por eso la condición es **más de 10**, no *menos de 10*: pocas existencias por
sí solas no indican riesgo de desperdicio. Cada producto puede tener su propio
umbral, horario y porcentaje; los números del ejemplo no son valores globales.

La función devuelve `proponer`, `motivo` y `descuento_pct`. La aplicación
deberá guardar el estado, evitar duplicados por producto/sucursal y fecha,
permitir aprobación o activación según la configuración y confirmar con el
punto de venta que el descuento realmente se aplicó. Una propuesta no cuenta
como promoción activa ni como alimento salvado. Al cierre se deberán registrar
las unidades vendidas bajo promoción y las desechadas para medir el resultado.
Con el CSV histórico de solo ventas no se puede ejecutar esta regla: faltan
stock actual, fecha límite de venta y descuentos.

Esta carpeta forma parte del esqueleto del proyecto. El código se agregará al implementar su funcionalidad.

**Responsable del módulo:** Max Rojas. La responsabilidad incluye interfaz, servidor y APIs según [la división del equipo](../../../../documentacion/equipo/responsabilidades.md).

**Estructura prevista:** `rutas.py`, `servicio.py`, `repositorio.py`, `modelos.py`, `esquemas.py`, `dependencias.py`, `errores.py` y `tests/`. Crear estos archivos con su implementación, sin acceder directamente al repositorio de otro módulo.
