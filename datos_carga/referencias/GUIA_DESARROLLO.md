# Guía de desarrollo — Referencias de los CSV

**26-10-2026 · Precios de caja solicitados por Axel:** [CSV de 139 estimaciones PEN](precios_estimados_ventas_pen.csv) y [fuentes, presentaciones y carga](precios_estimados_ventas_pen.md). Complemento independiente de los cinco archivos de inicialización. No alterar nombres/códigos ni interpretar euros de SKU como soles. Se aplican por el servicio público de precios con administrador activo y una transacción; el script conserva precios existentes y no modifica stock/histórico. Son estimaciones editables, no precios comerciales confirmados. Aplicación y evidencia en Cueva.

**Responsable:** Axel Cueva, coordinación. Leer la [guía de datos](../GUIA_DESARROLLO.md) y la [guía raíz](../../GUIA_DESARROLLO.md).

`supuestos_recetas.csv` es una copia intacta del archivo suministrado por Axel. Explica el origen y los supuestos de las recetas: 5 originales y 134 estimadas. Sirve para revisar el conjunto con Rojas; no acredita recetas comerciales verificadas ni forma parte de los cinco archivos aceptados por primera carga.

La [guía para otra PC](replicar_proveedores_otra_pc.md), añadida el 20-10-2026, reproduce mediante ofertas la asignación vigente 28/27/0 y enlaza el bot/API Telegram. No es un importador ni un respaldo de PostgreSQL; preservar la separación entre clasificación portable, estado aplicado y procedimiento. Los códigos internos del proveedor pueden variar por instalación. Mantener fuera de Git token, chat privado y secretos de instalación.

Conservar esta procedencia y los campos originales. No seleccionar este CSV en el asistente. Documentar una eventual sustitución por recetas verificadas en el contrato y registro del bloque correspondiente.

## Agrupación de abastecimiento · 14-10-2026

Por solicitud de Axel, agrupacion_insumos.md y agrupacion_insumos.json proponen tres rubros para cubrir los 55 ingredientes activos: panadería/repostería (27), frescos/refrigerados (18) y abarrotes/bebidas/empaques (10). Clasificación contrastada con la API vigente y el CSV de ingredientes, sin códigos repetidos ni faltantes. JSON conserva códigos, nombres y unidades para una asignación posterior; no incorpora IDs ni destinatarios de proveedores. Estos archivos son referencias, no se importan ni crean categorías/ofertas en la aplicación. Mantener separado grupo propuesto de proveedor efectivo. Agua exige definir si se compra o se abastece internamente antes de crear su oferta. Evidencia y siguiente paso en Cueva.

Asignación posterior autorizada el 14-10-2026: asignacion_proveedores.md registra el estado real de la base local. PROV-001 cubre G03 (10), PROV-002 G01 (27), con destinos ya verificados. G02 (18) sigue pendiente. Para probar, ofertas de 1 kg/1 L/una unidad, mínimo 0/múltiplo 1; arroz corregido expresamente y oferta anterior inactiva. Conservar la clasificación base y este registro de aplicación separados. No incluir chats/tokens en referencias ni tratar la documentación como importador automático.


Actualización expresa 15-10-2026: G02 (18 frescos) pasa temporalmente a PROV-001, que cubre G02+G03 (28); PROV-002 conserva G01 (27), PROV-003 queda sin ofertas. Cobertura 55/55. Las 18 ofertas se aplican mediante servicio público en una transacción y sin cambios operativos. El estado vigente está en asignacion_proveedores.md; el corte 37/55 anterior permanece como historial del registro.
