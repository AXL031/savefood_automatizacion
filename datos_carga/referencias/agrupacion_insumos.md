# Agrupación de insumos para tres proveedores

Pastelería Maria Juanita. Propuesta del 14-10-2026 basada en los 55 ingredientes activos de la instalación.

Cada grupo corresponde al rubro de un proveedor. Los grupos cubren todo el catálogo una sola vez. La distribución sigue afinidad comercial, por lo que sus tamaños son distintos.

| Grupo | Rubro del proveedor | Insumos |
|---|---|---:|
| G01 | Panadería y repostería | 27 |
| G02 | Frescos y refrigerados | 18 |
| G03 | Abarrotes, bebidas y empaques | 10 |
| **Total** | **Tres proveedores** | **55** |

## Detalle por grupo

### G01. Panadería y repostería (27)

Perfil: Distribuidor de materias primas de panadería y repostería.

| Familia | Insumos |
|---|---|
| Harinas, cereales y semillas | Harina de trigo; Harina de trigo integral; Harina de centeno; Almidón de maíz; Copos de avena; Mezcla de semillas (sésamo, girasol, lino) |
| Azúcares y endulzantes | Azúcar; Azúcar glas; Azúcar moreno; Jarabe de glucosa; Miel |
| Frutos secos y fruta deshidratada | Almendra molida; Almendra laminada; Nueces; Avellanas; Pistachos; Pasas |
| Chocolates y preparados dulces | Chocolate; Chocolate blanco; Cacao en polvo; Caramelo preparado |
| Leudantes, aromas y complementos | Levadura panadera; Polvo de hornear; Extracto de vainilla; Aroma frutal; Gelatina; Sal |

### G02. Frescos y refrigerados (18)

Perfil: Distribuidor de alimentos frescos, lácteos, huevos y carnes.

| Familia | Insumos |
|---|---|
| Lácteos y huevos | Mantequilla; Leche; Nata para montar / crema de leche; Huevo; Queso emmental |
| Frutas | Manzana; Pera; Fresa; Frambuesa; Albaricoque; Frutas variadas; Mango; Limón |
| Verduras | Lechuga; Tomate fresco; Mezcla de verduras |
| Carnes y fiambres | Pollo; Jamón cocido |

### G03. Abarrotes, bebidas y empaques (10)

Perfil: Distribuidor general de abarrotes, bebidas y empaques.

| Familia | Insumos |
|---|---|
| Abarrotes y salsas | Pasta seca; Arroz crudo; Aceite vegetal; Mayonesa; Salsa de tomate |
| Bebidas e infusiones | Agua; Café molido; Bolsa de té; Bebida envasada 330 ml |
| Empaques | Bolsa / empaque |

## Aplicación posterior

- La propuesta está preparada para asignar un proveedor a cada grupo. Los nombres y códigos G01–G03 identifican grupos, no proveedores ya registrados.
- Confirmar que cada proveedor pueda suministrar todos los insumos de su rubro. Todavía no se verificó su catálogo comercial.
- Al configurar las ofertas, definir presentación, contenido, mínimo y múltiplo por insumo. La unidad base se conserva y no determina por sí sola la presentación de compra.
- Agua queda en G03 para cubrir el catálogo completo. Antes de configurar su oferta, definir si se compra o se abastece internamente.
- Bolsa / empaque se mantiene en G03 porque forma parte del catálogo actual.
- Esta entrega no modifica proveedores, ofertas existentes, stock, recetas ni automatizaciones y no envía mensajes.

## Referencia estructurada

[agrupacion_insumos.json](agrupacion_insumos.json) conserva los códigos, nombres y unidades base de los 55 insumos, separados por grupo y familia. Es una propuesta auxiliar: no se selecciona en la primera carga y todavía no es una categoría persistida en la aplicación.

Validación: 55 de 55 activos cubiertos, ningún código repetido ni ajeno al catálogo; nombres y unidades coinciden con la API y el CSV original.
