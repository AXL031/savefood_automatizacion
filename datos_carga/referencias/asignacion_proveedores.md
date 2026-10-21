# Asignación de grupos a proveedores

Pastelería Maria Juanita. Configuración aplicada a la instalación local el 15-10-2026, America/Lima.

| Proveedor | Nombre registrado | Grupo | Insumos | Estado |
|---|---|---|---:|---|
| PROV-001 | Proveedor de harina | G02. Frescos y refrigerados + G03. Abarrotes, bebidas y empaques | 28 | Asignado mediante ofertas preferidas; Telegram verificado |
| PROV-002 | Proveedor de harina | G01. Panadería y repostería | 27 | Asignado mediante ofertas preferidas; Telegram verificado |
| PROV-003 | Proveedor de cereales | Sin grupo temporalmente | 0 | Pendiente de vincular/verificar Telegram |

La asignación cubre **55 de los 55 insumos**. Los dos proveedores con el mismo nombre se distinguen por su código. PROV-001 recibe G03 porque ya tenía el arroz; los nombres de los proveedores se conservaron.

## Presentaciones iniciales para la prueba

Cada insumo asignado tiene una oferta activa y preferida, con estas condiciones elegidas para probar el sistema:

| Unidad base del insumo | Presentación de compra | Contenido en unidad base | Mínimo | Múltiplo |
|---|---|---:|---:|---:|
| g | 1 kg | 1000 g | 0 | 1 |
| ml | 1 L | 1000 ml | 0 | 1 |
| unidad | Una unidad | 1 unidad | 0 | 1 |

Estas presentaciones son la configuración inicial de la prueba, pendiente de contrastar con el catálogo comercial de cada proveedor. No se infieren precios ni condiciones comerciales reales.

Agua queda configurada por litro para esta prueba del grupo G03; su abastecimiento comercial real sigue por confirmar.

## Corrección del arroz

El arroz de PROV-001 queda con unidad de compra **kg**, factor **1000 g**, mínimo **0** y múltiplo **1**. Se pueden pedir presentaciones de un kilo, una a una.

La oferta rápida anterior tenía unidad de compra «5», mínimo 1 y múltiplo 3. Se conserva inactiva y sin preferencia como historial; la nueva es la que consulta Compras.

## Alcance

La configuración se guardó en una sola transacción mediante los servicios de Proveedores. Conserva chats, verificaciones, nombres, códigos, recetas, ventas, stock, modelos y tareas. Este paso no genera pedidos ni envía mensajes.

Por respuesta expresa de Axel del 15-10-2026, G02 se asigna temporalmente a PROV-001. Se conserva PROV-003 sin ofertas; trasladar G02 requerirá una configuración posterior explícita. El detalle de los 55 insumos permanece en [agrupacion_insumos.md](agrupacion_insumos.md) y [agrupacion_insumos.json](agrupacion_insumos.json). El grupo describe la organización propuesta; la asignación efectiva de la aplicación se resuelve mediante una oferta preferida por ingrediente.

Esta configuración pertenece a la base local. Copiar estos archivos a otra instalación no aplica las ofertas automáticamente.

Para reproducirla desde la interfaz en otra PC, seguir [replicar_proveedores_otra_pc.md](replicar_proveedores_otra_pc.md): instalación, equivalencia de proveedores, 55 ofertas, conversiones y verificación de Telegram. Los IDs/códigos de la nueva base pueden diferir; no confundir los proveedores de igual nombre.

## Verificación

La transacción adicional crea exactamente 18 ofertas preferidas para G02 en PROV-001. Los consumidores públicos de Compras confirman 55 insumos cubiertos, proveedor activo y compra automática habilitada por destino verificado. Recuentos operativos y saldos se contrastaron antes/después y no cambiaron. Respaldo privado previo conservado. Las propuestas existentes guardan su cálculo anterior y requieren preparar una corrección; asignar ofertas por sí solo no altera su historial ni envía mensajes.
