# Repetir la configuración de proveedores en otra PC

**Pastelería Maria Juanita · corte 20-10-2026.** Procedimiento para reproducir la agrupación aplicada el 15-10-2026. Se configura desde la aplicación; copiar los CSV o clonar Git no crea proveedores ni ofertas. Esta guía no contiene credenciales, chats privados ni un volcado de la base.

## 1. Resultado que se quiere reproducir

| Referencia de la PC original | Nombre registrado | Grupo asignado actualmente | Ofertas preferidas activas |
|---|---|---|---:|
| PROV-001 | Proveedor de harina | G02 Frescos y refrigerados + G03 Abarrotes, bebidas y empaques | 28 |
| PROV-002 | Proveedor de harina | G01 Panadería y repostería | 27 |
| PROV-003 | Proveedor de cereales | Sin grupo; Telegram pendiente | 0 |
| **Total** | | **55 ingredientes cubiertos una vez** | **55** |

Inicialmente se pensó en tres proveedores, uno por grupo. Después Axel pidió asignar **temporalmente G02 al primer proveedor**, porque los otros dos ya estaban vinculados y verificados en Telegram. Esa es la configuración vigente que se reproduce aquí. El tercero puede permanecer sin ofertas; no es necesario asignarle ingredientes para completar esta prueba.

Los dos primeros tienen el mismo nombre en la PC original: distinguirlos por **código**, no solo por nombre. Los códigos se generan al crear cada proveedor y pueden ser diferentes si la otra base ya tiene registros. Anotar la equivalencia «proveedor que cubre G02+G03» y «proveedor que cubre G01» en esa PC; no dar por hecho que sus IDs internos sean 1 y 2. La identidad portable del ingrediente es su **código** (`harina_trigo`, `arroz`, etc.), no su ID numérico de base.

**Qué es un grupo en esta versión:** organización documental para repartir abastecimiento. No existe una categoría de proveedor que asigne automáticamente todos sus ingredientes. La relación real se guarda mediante **una oferta por ingrediente**, marcada preferida. Un mismo proveedor puede tener muchas ofertas.

## 2. Preparar la instalación

1. Obtener una versión que incluya estos cambios: al corte están en `cueva`, [PR #16](https://github.com/AXL031/savefood_automatizacion/pull/16). Si ya fue integrada, usar la rama acordada por el equipo que la contenga. Seguir el [arranque del proyecto](../../README.md#arranque-local-de-desarrollo) para crear `.env` privado, construir y crear el Administrador de esta instalación. No reutilizar contraseñas de ejemplo.
2. En Windows, `iniciar-foodsave.cmd -Build` actualiza las imágenes y aplica migraciones mediante Compose. La cabeza de este corte es `0018_recepcion_compras`; el lanzador espera a la API y abre la web. Sin override local, el puerto es **3000**; el **3100** de la PC original provenía de configuración local no versionada. Usar la dirección que abra el lanzador.
3. **Solo si la base está vacía**, hacer [primera carga completa](../README.md#cómo-cargar) con los cinco CSV de `datos_carga`: productos, ingredientes, recetas, stock inicial y ventas. Objetivo **2026-09-30**, referencia de stock **2026-09-29**. Son 139 productos, 55 ingredientes, 998 líneas de recetas, 194 aperturas y 88 543 ventas. Esperar al modelo. No importar `supuestos_recetas.csv` ni los JSON de referencia.
4. Si la instalación ya tiene catálogo/datos, comprobar sus ingredientes antes de asignar. No volver a importar para configurar proveedores. Los CSV, el modelo, la configuración del bot y los datos de PostgreSQL son componentes diferentes; una copia del repositorio no restaura los volúmenes de otra PC.

## 3. Crear o identificar los proveedores

1. Entrar como Administrador y abrir **Proveedores**. La tabla muestra los proveedores e ingredientes que suministran.
2. Con **Crear proveedor**, crear los registros necesarios. El código se genera al guardar; no se introduce a mano. En una base limpia se pueden crear en el orden de la tabla anterior. Con registros existentes, elegir los equivalentes y conservar su historial.
3. Dejar activos los dos que recibirán los grupos. Registrar qué código de esta PC corresponde a cada rol. El nombre es editable al crear; conservar los nombres de la tabla si se busca reproducir exactamente el escenario anterior.
4. Para Telegram, seguir la [guía del bot y su API](../../docs/api/configurar-telegram.md). El bot público es [@foodsave_proveedor_bot](https://t.me/foodsave_proveedor_bot); el token se guarda privadamente desde **Conexión de Telegram → Configurar Telegram**.
5. Vincular y **verificar** el chat propio de pruebas en cada uno de los dos proveedores. Se puede usar el mismo chat propio para ambos al probar. La verificación comprueba acceso, pero no envía mensajes. **Enviar mensaje de prueba** es una acción adicional que sí transmite a Telegram; ejecutarla deliberadamente desde cada proveedor si se quiere acreditar entrega. El tercer proveedor puede quedar sin vincular.

## 4. Registrar las ofertas de cada grupo

Abrir la gestión del proveedor correcto → **Ingredientes que suministra → Añadir ingrediente**. Para cada ingrediente de sus grupos, elegirlo por nombre contrastando el código con el [detalle completo de los 55 ingredientes](agrupacion_insumos.md) o la [referencia JSON](agrupacion_insumos.json).

| Grupo | Proveedor equivalente de esta PC | Ingredientes | Qué repetir |
|---|---|---:|---|
| G01 Panadería y repostería | Referencia PROV-002 | 27 | Todas las familias de harinas/semillas, azúcares, frutos secos, chocolates y auxiliares de G01 |
| G02 Frescos y refrigerados | Referencia PROV-001 | 18 | Todos los lácteos/huevos, frutas, vegetales y carnes de G02 |
| G03 Abarrotes, bebidas y empaques | Referencia PROV-001 | 10 | Todos los ingredientes de G03, incluido `arroz` |

Usar estas **presentaciones iniciales de prueba**, pendientes de validar con el catálogo comercial de cada proveedor:

| Unidad base del ingrediente | Presentación que compras | Contenido de una presentación, en el formulario | Unidad del contenido que se debe elegir | Factor que guarda la API |
|---|---|---:|---|---:|
| `g` | `kg` | `1` | Kilogramos (`kg`) | `1000` g |
| `ml` | `L` | `1` | Litros (`l`) | `1000` ml |
| `unidad` | `unidad` | `1` | Unidades | `1` unidad |

Para todas: **Cantidad mínima de presentaciones = 0**, **Comprar en grupos de = 1** y oferta **preferida**. Poner un nombre descriptivo, por ejemplo «Harina de trigo, 1 kg». El formulario crea la oferta activa y la opción preferida viene seleccionada; comprobarlo en la tabla al guardar. Repetir hasta cubrir **28 ingredientes en el primer proveedor y 27 en el segundo**.

**Conversión:** escribir `1` y seleccionar `kg` ya equivale a `1000 g`. También se puede escribir `1000` con unidad del contenido `g`; no escribir `1000` y elegir `kg`, porque eso representaría mil kilos. `factor_conversion` de la API siempre expresa unidades base por presentación. Mínimo y múltiplo expresan cantidades de presentaciones, no gramos ni litros.

**Arroz:** crear preferida con presentación `kg`, contenido `1 kg` (=1000 g), mínimo 0 y múltiplo 1. En la PC original se conservó inactiva la oferta rápida anterior con presentación «5», mínimo 1 y múltiplo 3. En una base nueva no hay que crear esa oferta incorrecta. Si ya existe, crear la correcta, marcarla preferida y desactivar la anterior conservando su historial.

**Agua:** en este escenario se prueba su compra por litro. Su abastecimiento comercial real todavía debe confirmarse. No se han fijado precios ni condiciones comerciales reales con esta configuración.

## 5. Comprobar antes de programar

- La tabla de Proveedores debe mostrar los 55 ingredientes repartidos **28 / 27 / 0**. En la gestión de ofertas, comprobar que cada ingrediente tiene su oferta activa y preferida en el proveedor previsto; no contar ofertas antiguas inactivas.
- Los dos proveedores asignados deben estar activos y tener destino Telegram verificado. Un tercero sin ofertas no obliga a vincularlo para cubrir estos grupos.
- Abrir **Automatización**, elegir el catálogo deseado y **Comprobar requisitos**. No deben quedar avisos de oferta/destino para estos ingredientes. Otros requisitos —modelo, recetas, stock y fecha— se resuelven por separado; tener proveedores listos no garantiza que exista un faltante o que la fecha esté libre para comprar.
- Con el conjunto actual, usar un objetivo dentro de la prueba reservada del modelo; para la primera prueba preparada es **2026-09-30**. No reemplazarlo por la fecha real del equipo. La hora real solo indica cuándo ejecutar.
- Antes de programar, revisar si ya hay una compra activa/enviada para esa fecha. El sistema protege contra recompras; ejecutar otra vez no libera la fecha.
- Para revisar el cálculo antes de enviar, usar **requiere aprobación**. El modo automático necesita su autorización expresa y puede enviar pedidos reales al chat configurado cuando se ejecute. Guardar ofertas o comprobar requisitos por sí solo no envía nada.

### Si una propuesta anterior sigue diciendo «falta una oferta»

Las propuestas conservan el cálculo de su creación. Añadir las ofertas no reescribe ese historial. Para un borrador bloqueado sin decisiones ni envíos, **Preparar propuesta corregida** crea un reemplazo con plan recalculado y aprobación manual, conservando el original cancelado y su enlace. Solo procede si cumple las validaciones; no reintentar a ciegas un pedido enviado o incierto. La actualización del destino de un pedido es otra acción y no completa ofertas faltantes.

## 6. Cuando se habilite el tercer proveedor

La distribución prevista con tres proveedores sería **G01 → segundo (27), G02 → tercero (18), G03 → primero (10)**. Ese traslado todavía no se ha aplicado en este corte. Primero vincular/verificar el destino del tercero y acordar sus presentaciones; después registrar sus 18 ofertas y cambiar las preferidas para cálculos nuevos, conservando el historial anterior. Cambiar la oferta preferida no cambia pedidos ya creados ni sus factores congelados.

## Referencias y alcance de la reproducción

- [Clasificación completa](agrupacion_insumos.md), [códigos/unidades en JSON](agrupacion_insumos.json) y [estado aplicado en la PC original](asignacion_proveedores.md). El JSON conserva la clasificación inicial `PROPUESTA_SIN_ASIGNAR`; la asignación efectiva posterior se documenta en el estado aplicado y esta guía.
- [Contrato de pedidos, ofertas y Telegram](../../docs/api/contrato-pedidos.md), [interfaz del formulario](../../frontend/src/app/proveedores/page.tsx) y [flujos para diagramar](../../docs/automatizacion/flujos-implementados.md).
- Esta guía se contrastó con las referencias versionadas y el código. Documenta una reproducción manual; **no acredita haber configurado ni probado otra PC**. No incluye script que asigne grupos automáticamente.
