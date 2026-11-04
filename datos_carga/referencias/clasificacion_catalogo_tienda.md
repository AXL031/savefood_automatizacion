# Clasificación comercial del catálogo de tienda · 04-11-2026

Autor: Codex para Axel. Coordinación Cueva; productos/UI de Sanchez y tienda de Rojas. Solicitud: analizar y clasificar los 139 productos existentes. [Asignación por código y fuentes](clasificacion_catalogo_tienda.json).

## Dónde se guarda

La tabla `producto` contiene identidad, código, nombre, activo y marcas técnicas; **no tiene columna de categoría**. La clasificación comercial vigente se guarda en FoodSave, en el JSON **`publicacion_producto.datos.categoria`**. Comercio controla la versión de cada ficha y la publica por HTTP a la base propia de tienda. No se añaden columnas, categorías de ML ni acceso cruzado a bases. Se puede editar en Ventas → Publicar en tienda.

## Distribución aplicada

| Categoría | Código | Productos | Ejemplos/criterio |
|---|---|---:|---|
| Panes y hojaldres | panes | 45 | Baguettes, panes especiales, brioche, croissant, pain au chocolat y bolsas de viennoiserie |
| Postres personales | postres-personales | 42 | Éclair, flan, tartelette, macaron, brownie, galletas y porciones individuales |
| Postres para compartir | postres-enteros | 18 | Tartas/galettes familiares, formatos grandes y cajas de dulces |
| Comidas preparadas | comidas | 12 | Pasta, platos preparados y fórmulas/combos individuales |
| Kekes | kekes | 6 | Cake, financier y nantais en sus presentaciones |
| Bocados salados | bocados | 6 | Sándwiches, triángulos y bandejas saladas |
| Tortas clásicas | tortas | 5 | Bûches de 4/6/8 personas y Royal de 4/6 personas |
| Bebidas | bebidas | 4 | BOISSON 33CL, CAFE OU EAU, THE y CHOCOLAT provisional |
| Otros productos | otros | 1 | COUPE: identidad insuficiente |
| **Total** | | **139** | Códigos únicos y cobertura completa |

## Criterios y límites

Clasificación inferida de código/nombre, familia de producto y presentación de la [referencia de precios existente](precios_estimados_ventas_pen.csv). Aquella referencia contiene supuestos, por lo que esta clasificación no acredita recetas, ingredientes, tamaño real, alérgenos ni fabricación. Un mismo tipo de postre se separa por formato cuando el SKU lo expresa: ROYAL individual frente a ROYAL 4P/6P; TARTELETTE frente a TARTE FRUITS 4P/6P. Las cajas de dulces se agrupan como para compartir; no se convierten en tortas por tener varias unidades.

Para contrastar nombres franceses se consultaron fuentes de fabricantes/pastelerías: [Banette identifica Moisson como pan](https://www.banette.fr/nos-produits/pains/banette-moisson), [Deherripon reúne pain au chocolat, chausson y brioche suisse como viennoiseries](https://www.boulangerie-deherripon.fr/272-viennoiseries), [Gavet identifica Armoricain como pastelería](https://www.patisserie-gavet.fr/produit/larmoricain/) y [Maison Chavanne clasifica Noix Japonaise como pâtisserie/entremets](https://maison-chavanne.com/product/noix-japonaise/). Estas fuentes apoyan familias genéricas; no prueban la composición exacta del SKU local.

## Casos que requieren confirmación del comercio

| Código | Categoría asignada | Motivo de revisión |
|---|---|---|
| coupe | otros | Podría ser corte/rebanado; no se identifica con certeza como alimento |
| chocolat | bebidas | Se conserva la hipótesis previa de bebida; podría ser chocolatería |
| caramel_noix | postres-personales | Nombre de sabor; falta ficha específica |
| delicetropical | postres-personales | Nombre comercial; presentación individual asumida |
| douceur_d_hiver | postres-personales | Nombre comercial; presentación individual asumida |
| nid_de_poule | postres-personales | Nombre ambiguo; familia/formato provisionales |
| tulipe | postres-personales | Forma/nombre comercial; familia/formato provisionales |

Los siete casos quedan marcados `requiere_revision` en la referencia, sin inventar atributos técnicos ni añadirlos a la API como si fueran datos verificados. COUPE conserva su publicación y stock actuales porque esta tarea solo solicita clasificación; su aptitud como artículo vendible necesita confirmación.

## Aplicación

Reclasificar únicamente mediante `comercio.catalogo.guardar_ficha` con versión actual, conservando publicado, descripción, presentación e imagen, y preparar un snapshot durable. Respaldo previo y comprobación de que precios, stock, lotes, ventas y demás tablas quedan idénticos. Bebidas y Comidas preparadas amplían el esquema y el selector administrativo sin migración SQL; se publican sin imagen de categoría hasta disponer de un archivo propio. Evidencia de ejecución y versión recibida en [Cueva](../../docs/equipo/avances/cueva.md).

Aplicado el 04-11-2026: 126 fichas cambiaron de categoría y 13 conservaron la anterior. Snapshot **versión 8 CONFIRMADO**, recibido por la API real de tienda con los 139 códigos y esta misma distribución. Las otras 53 tablas comparadas quedaron idénticas; los demás metadatos de las fichas y las 1390 unidades de prueba se conservaron. Respaldo y evidencia privados en `.tmp/clasificacion-20261104/`. Los siete casos provisionales de la tabla anterior mantienen su marca de revisión en la referencia.
