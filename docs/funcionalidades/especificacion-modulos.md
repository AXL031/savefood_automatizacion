# Especificación funcional de la demo

Qué muestra y permite hacer cada pantalla del prototipo. Fórmulas y reglas: [guía de alcance](../guia-inicio-desarrollo.md). Cuerpos de API: [contratos](../api/contratos.md). Responsables: [responsabilidades](../equipo/responsabilidades.md). Funciones posteriores: [visión futura](../vision-futura.md).

## Navegación

Usuario único por instalación con rol **Administrador** u **Operador**. El Operador consulta; el Administrador además carga, edita, programa y aprueba. La cabecera muestra negocio y rol.

| Grupo | Pantallas (ruta) |
|---|---|
| Datos | Primera carga (`/inicializacion`), CSV piloto (`/inicializacion/piloto`), Productos, Ventas |
| Producción | Ingredientes, Recetas, Inventario, Planificación* |
| Abastecimiento | Proveedores*, Pedidos* |
| Pronósticos | Pronósticos, Panel histórico (`/panel`) |
| Sistema | Automatizaciones, Promociones sugeridas*, Configuración |

\* Pendiente de implementar. Notificaciones, Excedentes, Informes y Producción real no forman parte de la demo.

## Reglas comunes

- Ausencia de dato no es cero: se muestra «sin dato».
- Toda cifra lleva unidad y, si cambia de significado, periodo o fecha.
- Fecha histórica del escenario (reloj simulado) y hora real de ejecución se muestran por separado.
- «Enviado» no significa «confirmado por el proveedor».
- Cada pantalla tiene estados de carga, vacío, error y sin permiso.

## Pantallas

| Pantalla | Responsable | Muestra | Permite | Estado |
|---|---|---|---|---|
| Iniciar sesión | Axel | Formulario de correo y contraseña | Entrar; al vencer el token (30 min) vuelve aquí | Hecha |
| Primera carga | Edu | Estado durable de la instalación; asistente Archivos → Validación → Vista previa → Confirmar; errores ubicados por hoja/fila/columna | Subir 2 XLSX o 5 CSV, ver vista previa sin guardar, confirmar carga atómica (repetir no duplica) | Hecha |
| CSV piloto | Edu | Ejecución de preparación del modelo | Subir el CSV bakery y reintentar el entrenamiento sin volver a subir | Hecha |
| Productos | Edu | Catálogo con código, nombre, SKU externo, estado y marca de demo | Consultar | Hecha |
| Ventas | Edu | Ventas diarias por producto y fecha; historial de revisiones | Filtrar por rango y producto; corregir con motivo (crea revisión) | Hecha |
| Ingredientes | Max | Código, nombre, unidad base, uso en recetas y lotes, estado | Crear; editar nombre, unidad (bloqueada si está en uso) y estado (no se desactiva si está en receta activa) | Hecha |
| Recetas | Max | Productos con receta activa o «sin receta»; líneas con cantidad por unidad en unidad base; historial de versiones con motivo | Crear nueva versión con motivo; la misma composición no crea versión | Hecha |
| Inventario | Vera | Stock disponible por fecha y lote, caducidad, vida útil; movimientos | Ajuste con delta, motivo, clave y hora efectiva simulada; saldo nunca negativo | Hecha |
| Planificación | Max | Corrida usada, por producto: pronóstico, stock, cantidad a producir, versión de receta; necesidades por ingrediente: requerido, disponible, faltante; estados `HISTORIAL_INSUFICIENTE` y `PRODUCTO_NO_CUBIERTO` | Ver la traza de cada cifra; ir a los pedidos generados. Un recálculo crea plan nuevo y conserva el anterior | Pendiente (M02–M04) |
| Proveedores | Aguirre | Proveedor, estado, chat de Telegram vinculado; ofertas por ingrediente con unidad de compra, factor, mínimo, múltiplo y preferida | Crear, activar/desactivar, vincular chat, registrar oferta, marcar preferida | API hecha; pantalla pendiente |
| Pedidos | Aguirre | Pedidos por proveedor y plan, líneas convertidas, modo de aprobación, estado e intentos de envío; necesidades sin proveedor | Aprobar envío (modo `REQUIERE_APROBACION`); conciliar un envío incierto con evidencia | Pendiente (L02–L04) |
| Pronósticos | Kevin | Modelo, partición y versión; corridas persistidas y cobertura por producto | Preparar nueva versión del modelo | Hecha |
| Panel histórico | Kevin | Serie del tramo de prueba; para un día evaluado: pronóstico vs. real por producto, MAE, WAPE, % dentro de ±20 % y cobertura | Elegir día y versión | Hecha |
| Automatizaciones | Axel | Programaciones, ejecuciones e intentos con hora real, reloj simulado, estado y error | Programar `GENERAR_PROPUESTA` para una hora futura; abrir el detalle de una ejecución | Hecha (sin manejadores de plan/pedido) |
| Detalle de ejecución | Axel | Línea de tiempo de intentos (`1 de 3`…), entrada, resultado y error | Consultar | Hecha |
| Promociones sugeridas | Vera | Por lote: sugerencia con descuento y motivo, o rechazo razonado | Consultar; no activa descuentos | Pendiente (V03–V04) |
| Configuración | Axel | Nombre, zona horaria, moneda, modo de envío de pedidos, estado de la instalación | Guardar datos del comercio y modo de envío | Hecha |

## Cálculo del plan (M02–M03)

`producir = max(0, pronóstico − stock elegible del producto)` con margen de seguridad **0**. `requerido = Σ producir × cantidad_por_unidad` por ingrediente en unidad base, redondeado a 3 decimales al final. `faltante = max(0, requerido − stock elegible del ingrediente)`. Un pronóstico ausente o receta faltante produce un estado explicativo, nunca un cero.
