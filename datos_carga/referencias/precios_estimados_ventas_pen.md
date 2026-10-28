# Precios estimados para la caja de FoodSave

**Solicitud de Axel · 26-10-2026.** Codex preparó [139 precios en PEN](precios_estimados_ventas_pen.csv), uno por código del catálogo activo. Son estimaciones para probar Ventas, editables por Administrador; no son una lista de precios confirmada del comercio ni una recomendación de rentabilidad. No se convirtieron importes antiguos en euros presentes en nombres de SKU.

## Fuentes consultadas

Precios publicados en webs de los propios comercios, consultados el 26-10-2026. Los ejemplos observados sirven de referencia local; el CSV expresa nuestra estimación por analogía y los supuestos de presentación, sin atribuir cada SKU francés a una oferta peruana exacta.

| Código | Referencia oficial | Ejemplos observados en soles |
|---|---|---|
| S1 | [Panes, San Antonio](https://pasteleriasanantonio.com/programados/?product_cat=panes) | Baguette 5.90; croissant de mantequilla 5.90; molde blanco/integral 600 g 13.90 |
| S2 | [Carta San Antonio](https://carta.pasteleriasanantonio.com/) | Porción de cheesecake 13.90; sándwiches alrededor de 16–20; bebidas e infusiones |
| P1 | [Catálogo Panea](https://www.paneaperu.com/pedir?categoria=bolleria) | Baguette 7; croissant 8; almendras 12; brownie 8; pain suisse 9; macaron 7 y caja de 12 a 70 |
| P2 | [Carta Pastipan, PDF vigente al consultar](https://pastipan.com.pe/menu/MenuSalon.pdf) | Mixto en pan campesino/croissant 15.90; sándwich de asado 21.90 y platos/combinaciones de cafetería |
| C1 | [Tienda La Crème de la Crème](https://lacremedelacreme.com.pe/es/shop) | Pastelería individual y macaron a 6; referencia de categoría, no equivalencia exacta |
| D1 | [Tienda Dolce Capriccio](https://dolcecapriccio.pe/) | Tortas chicas alrededor de 60–85; otras presentaciones 110–140; tamaño y tipo influyen |
| SUPUESTO | Estimación propia, sin equivalente comercial verificado | SKU ambiguos como COUPE se documentan expresamente |

## Criterio y presentaciones

- Precio por **una unidad del SKU**: una pieza/porción individual salvo que el nombre indique paquete, personas, bandeja o kilogramo. Cantidad 1 de `special_bread_kg` representa una pieza comercial de 1 kg; no añade venta por peso fraccionario a la caja.
- Panes, bollería y porciones se estimaron dentro o cerca de las referencias locales; variantes sin equivalente se ajustaron por relleno, semillas o tamaño. Baguette y croissant quedan en S/ 5.50; brownie S/ 8.00; macaron individual S/ 5.00 y caja de doce S/ 54.00.
- Piezas de 4/6/8 personas conservan un precio por pieza completa, con escala creciente. `plaque_tarte_25p` se interpreta como plancha de 25 porciones a S/ 250.00, no porción individual. Las bandejas pequeñas/grandes se suponen de 12/24 bocaditos.
- `reduction_sucrees_12/24` se interpreta como cajas de mini pastelería, no un descuento ni dinero negativo. Los códigos históricos `plat_6_50e` y similares son identidades, no precios en PEN ni tipo de cambio.
- `coupe`, `chocolat`, `cafe_ou_eau`, bolsas y nombres sin presentación precisa tienen un supuesto explícito en su fila. `coupe` se conserva con S/ 0.50 por posible servicio de corte: revisar su naturaleza antes de uso comercial. No se renombra ni elimina ningún producto.
- La caja registra el importe final declarado; esta carga no añade impuestos, descuentos o cobros automáticos. Rango del catálogo: S/ 0.50–250.00 según presentación.

## Aplicación y conservación

El CSV es una referencia adicional; **no** se selecciona como uno de los cinco archivos de primera carga. `scripts/cargar-precios-estimados.py` valida cobertura exacta, moneda, identidad y formato; necesita un administrador activo indicado explícitamente. Sin `--aplicar` solo informa. Con `--aplicar` consume `ventas.caja.guardar_precio` dentro de una sola transacción, con claves derivadas de la huella del archivo. Conserva cualquier precio ya configurado, incluso al repetir la carga; no reemplaza ediciones manuales.

Ejecutar en el entorno backend con su `DATABASE_URL`, sin incluir secretos en argumentos ni documentos:

```text
python scripts/cargar-precios-estimados.py --archivo datos_carga/referencias/precios_estimados_ventas_pen.csv --usuario-id ID_ADMIN
python scripts/cargar-precios-estimados.py --archivo datos_carga/referencias/precios_estimados_ventas_pen.csv --usuario-id ID_ADMIN --aplicar
```

En Docker, montar ambos archivos de solo lectura y usar sus rutas dentro del contenedor. Aplicación habitual con respaldo y comprobación de datos registrada en [Cueva](../../docs/equipo/avances/cueva.md). No modifica productos, recetas, ofertas, inventario, ventas históricas ni tickets. **Asignar precio no vuelve vendible un lote vencido:** siguen haciendo falta unidades con fecha límite de venta vigente.
