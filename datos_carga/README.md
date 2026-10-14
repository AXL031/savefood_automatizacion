# Archivos de carga — Pastelería Maria Juanita

Copias preparadas el 14-10-2026 a partir de los seis CSV proporcionados por Axel. Los originales de Downloads se conservan. Esta entrega permite probar la primera carga completa con la base de Rojas y los ajustes de `cueva`.

**Actualización: todo el catálogo habilitado.** Se marcaron los 139 productos en el archivo de carga y se retiró el máximo de cinco del sistema. Si ya cargaste la versión anterior, usa **Automatización → Seleccionar todos**; no vuelvas a importar ni entrenar. Estas instrucciones de carga se aplican a una instalación pendiente.

## Cómo cargar

1. Iniciar FoodSave con `iniciar-foodsave.cmd` y entrar como Administrador.
2. Abrir **Datos iniciales → Primera carga completa** en `http://localhost:3100/inicializacion`.
3. Elegir los **cinco CSV de esta carpeta** juntos. Mantener sus nombres exactos:

   | Archivo | Filas de datos |
   |---|---:|
   | `productos.csv` | 139 |
   | `ingredientes.csv` | 55 |
   | `recetas.csv` | 998 |
   | `stock_inicial.csv` | 194 |
   | `ventas.csv` | 88 543 |

4. Indicar **fecha de planificación: 2026-09-30** y **fecha de referencia del stock: 2026-09-29**.
5. Revisar la vista previa y confirmar una sola vez. Esperar a que la preparación del modelo termine; la evaluación histórica puede continuar después. No volver a subir archivos para reintentar el entrenamiento.
6. Para probar la automatización, mantener el objetivo **2026-09-30**, pulsar **Seleccionar todos** y usar **Probar en un minuto**. Una configuración nueva incluye los 139 activos por defecto; también puedes elegir un subconjunto. **Gestionar → Ejecutar ahora** permite adelantar una tarea pendiente. Los horarios de ejecución son reales; el objetivo corresponde a esta prueba histórica.

`referencias/supuestos_recetas.csv` es documentación auxiliar: **no se selecciona en la carga**. El importador acepta los cinco archivos indicados arriba.

## Qué se corrigió

- Se retiró el sufijo ` (1)` de los nombres, para cumplir el contrato del importador.
- Ingredientes, recetas y ventas se copian sin cambios de contenido. Se conservan cantidades, códigos, SKU, ceros explícitos y fechas de venta (2025-01-11 a 2026-10-09). En productos solo se cambió la columna técnica `demostrar` a `si` para los 139; sigue siendo obligatoria por compatibilidad, y la selección de cada programación se hace en Automatización.
- En el stock se trasladaron ambas columnas de fechas **14 días hacia atrás** para usar una referencia del 29 de septiembre. En los lotes de producto, toda fecha posterior a **2026-10-03** se limitó a ese día: la regla vigente admite cinco días de vida desde la referencia, contando ambos extremos. Esto afecta a 52 lotes de producto además del traslado de fechas; cantidades, códigos y números de lote se conservan. Los campos vacíos siguen vacíos.
- Estos vencimientos son un escenario de prueba; no establecen la vida útil real de los alimentos. El archivo de supuestos documenta las recetas estimadas del conjunto original y se conserva sin alteraciones.

## Por qué se usa el 30 de septiembre

El modelo actual calcula su partición usando meses completos. Este historial contiene 20 meses completos (febrero de 2025 a septiembre de 2026); la prueba reservada abarca **2026-07-01 a 2026-09-30**. Octubre está incompleto. La inferencia de la rama actual exige que el objetivo esté dentro de esa prueba reservada; elegir 2026-10-14 fallaría aunque la vista previa acepte los archivos. Se conserva el historial entregado, sin inventar ventas futuras.

## Alcance

Axel ya confirmó los archivos anteriores y la instalación habitual tiene los 139 productos y un modelo listo. La ampliación permite usarlos sin volver a cargar. Los archivos no configuran proveedores, ofertas, destinos ni WhatsApp; para generar y enviar pedidos deben completarse esos datos después de la carga. Consultar [configuración de WhatsApp](../docs/api/configurar-whatsapp.md).

**Validación ejecutada:** PostgreSQL aislado con todas las migraciones. Vista previa sin errores; confirmación de 139 productos, 55 ingredientes, 88 543 ventas y 194 aperturas; reintento sin duplicados; CatBoost real para los 139 y motor GENERAR_PROPUESTA real con 139 pronósticos/elementos y 55 necesidades CALCULADAS, incluso conservando solo cinco flags heredados. Reentrega ignorada, stock intacto y cero envíos. Corte de cinco suites: 42 pruebas correctas en 161,12 s; la prueba concurrente omitida inicialmente se habilitó y pasó después (1 en 3,07 s). Esquemas y artefactos temporales retirados. La aplicación habitual conserva sus datos y modelo; su evaluación histórica ya estaba completada antes de actualizar. Detalles en el [registro de Cueva](../docs/equipo/avances/cueva.md).
