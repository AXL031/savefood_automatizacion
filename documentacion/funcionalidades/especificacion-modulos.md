# Especificación funcional integral de FoodSave

## Objetivo del producto

FoodSave presenta y coordina la operación de un negocio que produce alimentos perecibles. Permite consultar demanda y producción, preparar abastecimiento, anticipar excedentes, activar promociones, vigilar automatizaciones y revisar su impacto. El flujo operativo es **detectar → decidir → actuar → verificar → corregir → notificar**. Las acciones y cifras pertenecen al negocio activo; cada resultado muestra fecha u hora, estado y unidad cuando corresponda.

Esta especificación define las funciones que debe ofrecer la experiencia descrita aquí. Los importes, productos, horarios y porcentajes incluidos como ejemplos de interfaz no son reglas universales. Cada módulo tiene una persona responsable de su interfaz, servidor, API, pruebas e integración.

## Actores y navegación

La cabecera identifica el **negocio activo** y el rol **Administrador**. Las pantallas se agrupan en:

| Grupo | Secciones |
|---|---|
| Inicio | Panel principal |
| Operación | Producción, Predicciones, Inventario |
| Abastecimiento | Compras, Proveedores |
| Prevención | Excedentes, Promociones |
| Sistema | Automatizaciones, Informes, Configuración |

Cada sección conserva la misma navegación, encabezado y contexto de negocio.

## Responsables de todos los módulos

| Módulo | Responsable |
|---|---|
| Autenticación | Axel Cueva |
| Negocios y configuración | Axel Cueva |
| Automatizaciones y control | Axel Cueva |
| Notificaciones | Axel Cueva |
| Panel principal | Edu Sanchez |
| Informes | Edu Sanchez |
| Ingredientes | Kevin Bohorquez |
| Recetas | Kevin Bohorquez |
| Pronósticos | Kevin Bohorquez |
| Planificación | Kevin Bohorquez |
| Productos | Leonardo Vera |
| Ventas | Leonardo Vera |
| Producción | Leonardo Vera |
| Inventario | Leonardo Vera |
| Proveedores | Leonardo Aguirre |
| Compras | Leonardo Aguirre |
| Excedentes | Max Rojas |
| Promociones | Max Rojas |
| Desperdicio | Max Rojas |

Las funciones de acceso, catálogos, recetas, ventas, notificaciones y desperdicio aparecen en esta matriz para que ningún módulo quede sin dueño. Las secciones siguientes desarrollan el comportamiento del producto y señalan quién responde por cada una. Cuando una vista reúne datos de varios módulos, cada responsable entrega sus datos mediante un contrato compartido.

## 1. Panel principal

**Responsable:** Edu Sanchez. Los indicadores de otros dominios proceden de sus respectivos responsables.

**Finalidad.** Dar una lectura rápida del día y permitir entrar a la causa o el detalle de los cambios relevantes.

**Información.** Demanda prevista en unidades, producción planificada, unidades con riesgo de excedente y pérdida evitada con periodo. Producción del día por producto con cantidad hecha frente a cantidad prevista; actividad automática reciente con hora y estado; pedidos a proveedores con insumo, importe y estado; impacto acumulado en alimentos salvados, unidades recuperadas, reducción del desperdicio y pérdida económica evitada.

**Acciones.** Abrir automatizaciones desde la cabecera; entrar al detalle de pedidos, riesgos o actividad desde sus bloques. Una alerta preventiva explica el producto en riesgo, la acción programada y cuándo se medirá el resultado.

**Criterio funcional.** Las tarjetas deben distinguir indicadores del día de métricas semanales o acumuladas. Un estado «pendiente» no se presenta como confirmado. La ausencia de datos debe indicarse sin mostrar ceros ficticios.

## 2. Planificación de producción

**Responsable:** Kevin Bohorquez. El registro de producción real y las existencias corresponden a Leonardo Vera.

**Finalidad.** Revisar y aprobar una propuesta de producción y conocer sus necesidades de abastecimiento.

**Información.** Precisión reciente, demanda prevista, margen de seguridad, número de insumos faltantes y plan por producto con demanda, stock, cantidad a producir y confianza. El sistema explica los factores usados para calcular el plan. Un panel lista insumo faltante, proveedor asociado y cantidad; otro anticipa los siguientes pasos y horarios.

**Acciones.** «Aprobar plan» confirma la propuesta vigente. «Generar pedidos automáticos» toma los faltantes mostrados y abre o inicia el proceso de compras. La interfaz debe informar qué versión del plan fue aprobada y si ya se generaron pedidos para evitar duplicidad visible.

**Estados.** Plan generado, pendiente de aprobación y aprobado; falta de insumos que requiere compra. La pantalla debe separar claramente una **recomendación** de una decisión ya aprobada.

**Cálculo.** La explicación visible relaciona ventas históricas, stock actual y margen de seguridad. La fórmula exacta, redondeo y tratamiento del stock no quedan definidos por esta interfaz y deben cerrarse antes de implementar el motor de cálculo.

## 3. Predicciones

**Responsable:** Kevin Bohorquez.

**Finalidad visible.** Entregar la demanda prevista y una medida de precisión o confianza que alimenta la planificación y el panel.

**Información exigida por las otras secciones.** Estimación de demanda por producto y periodo; precisión reciente y confianza por producto cuando estén disponibles. Debe distinguirse la demanda estimada de ventas observadas.

## 4. Inventario

**Responsable:** Leonardo Vera.

**Finalidad visible.** Proporcionar existencias actuales que se comparan con demanda y venta estimada.

**Información exigida por las otras secciones.** Stock de producto para el plan y para el cálculo de excedente; insumos disponibles para identificar faltantes. Cada cifra incluye unidad y momento de actualización.

## 5. Compras y abastecimiento

**Responsable:** Leonardo Aguirre.

**Finalidad.** Cubrir faltantes del plan y comprobar que los pedidos llegan al proveedor.

**Información.** Pedidos generados hoy, enviados, pendientes y total estimado. Cada pedido muestra número, proveedor, hora, importe, insumos con cantidades, plan de origen, regla aplicada y estado. El detalle incluye una línea de control con creación, envío, confirmación y resultado. Una alerta indica pedidos sin confirmar y la próxima medida de control.

**Acciones.** «Nuevo pedido» permite iniciar un pedido. Al seleccionar uno se abre su detalle. Un pedido con problema ofrece acceso a la ejecución correspondiente para reintentar, cambiar proveedor o registrar un pedido manual.

**Estados.** Generado, enviado, confirmado, pendiente y fallido. La emisión de un mensaje no equivale a una confirmación recibida. Las acciones posteriores actualizan el historial sin borrar pasos previos.

**Reglas visibles.** Puede existir un proveedor habitual y un límite de monto para pedidos automáticos. La cifra concreta del límite se configura por negocio.

## 6. Proveedores

**Responsable:** Leonardo Aguirre.

**Finalidad visible.** Identificar quién suministra cada insumo y a quién se dirige un pedido.

**Información exigida por compras.** Nombre de proveedor, insumos asociados, condición de habitual y estado de confirmación del pedido. En una recuperación de fallo debe poder elegirse otro proveedor para el pedido afectado.

## 7. Excedentes

**Responsable:** Max Rojas.

**Finalidad.** Detectar productos que podrían quedar sin vender antes del cierre y proponer una acción preventiva.

**Información.** Productos y unidades en riesgo, valor potencial perdido y número de acciones activas. La tabla muestra producto, stock, venta estimada, excedente, nivel de riesgo y acción. El detalle de un producto presenta situación inicial, acción con descuento y duración, y resultado medido después de un intervalo.

**Acciones.** «Revisar ahora» ejecuta o solicita una nueva evaluación. Tras medir una acción se puede mantener la promoción o recalcular la respuesta. El ciclo visible es detectar, decidir, actuar, verificar y corregir.

**Estados.** Riesgo alto, medio o bajo; acción programada, activa o en control; resultado suficiente o que requiere recálculo. El valor «potencial perdido» es una estimación, no una pérdida realizada.

## 8. Promociones

**Responsable:** Max Rojas.

**Finalidad.** Aplicar descuentos de forma manual o como respuesta al riesgo de excedente y comprobar su efecto.

**Información.** Promociones activas, unidades recuperadas, descuento promedio y pérdida evitada. La lista presenta producto, descuento, inicio, fin, origen y estado. El detalle muestra producto, duración, motivo de la decisión y si la promoción se aplicó correctamente en el punto de venta. El resultado medido compara excedente inicial, unidades vendidas durante el control, excedente posterior estimado y pérdida evitada.

**Acciones.** «Nueva promoción» permite iniciar una promoción; las generadas por el control de excedentes aparecen con su origen. La persona puede consultar una promoción y su medición posterior.

**Estados.** Programada, activa y finalizada. La activación interna y la confirmación de aplicación en el punto de venta deben presentarse como hechos distintos. El descuento máximo se toma de Configuración.

## 9. Automatizaciones

**Responsable:** Axel Cueva.

**Finalidad.** Configurar reglas automáticas y seguir cada ejecución hasta su resultado.

**Reglas visibles.** Planificación nocturna con ventas históricas e inventario como entrada; pedidos a proveedores después del plan usando insumos faltantes; control periódico de excedentes usando stock y ventas del día. Configuración también presenta promociones automáticas e informe semanal de impacto. Cada regla expone horario o frecuencia, entrada, acción y si está activa.

**Información de control.** Número de ejecuciones recientes, completadas, en control y fallidas. Una lista de últimas ejecuciones muestra hora, nombre, duración cuando se conoce y estado. El ciclo de control recorre detectar, decidir, actuar, verificar, corregir y notificar.

**Acciones.** «Nueva automatización» inicia una regla; los interruptores activan o desactivan las existentes. Seleccionar una ejecución abre sus pasos y resultado. Una regla desactivada deja de producir ejecuciones futuras, pero su historial permanece consultable.

## 10. Ejecución y recuperación

**Responsable:** Axel Cueva. Las acciones sobre pedidos conservan a Leonardo Aguirre como dueño de Compras.

**Finalidad.** Explicar una decisión automática, el fallo y las opciones para resolverlo.

**Información.** Aviso de fallo con causa y hora de notificación; estado, intentos usados, duración e impacto operativo. La trazabilidad ordena detección, decisión, acción, envío, verificación, corrección y notificación con marcas de tiempo. Un panel muestra la notificación remitida al administrador, otro el impacto en la producción y otro las reglas aplicadas.

**Acciones.** Reintentar el envío ahora, cambiar proveedor o registrar el pedido manualmente. Cada acción debe registrar un nuevo evento y actualizar estado e impacto; no debe presentar como exitosa una operación que no recibió confirmación.

**Decisión pendiente.** El contador de ejecución indica «2 de 2» intentos, mientras el ajuste «Intentos de reenvío» también muestra el valor 2. La redacción debe aclarar si el límite cuenta intentos totales o reenvíos posteriores al primero. Hasta resolverlo, el valor no debe usarse para inferir silenciosamente el número total de envíos.

## 11. Configuración y avisos

**Responsable:** Axel Cueva.

**Finalidad.** Adaptar operación y control al negocio activo.

**Datos del negocio.** Nombre, hora de cierre y zona horaria. El encabezado identifica al negocio y el rol que administra estas opciones.

**Automatizaciones configurables.** Planificación nocturna, pedidos automáticos, control de excedentes, promociones automáticas e informe semanal de impacto, cada uno con interruptor y explicación breve.

**Límites.** Pedido automático máximo, margen de seguridad, descuento máximo e intentos de reenvío. El valor guardado debe verse reflejado en las decisiones posteriores y en la explicación de reglas de cada ejecución.

**Notificaciones.** Interruptores para fallo de automatización, pedido no confirmado, riesgo alto de excedente y resumen diario. La notificación de un fallo informa causa, pedido afectado y siguiente paso; su envío queda registrado.

**Estado del sistema.** Automatizaciones activas respecto del total, conexión del punto de venta, tiempo desde la última sincronización y proveedores habilitados para pedido automático. Estos indicadores describen el estado actual, no una opción editable.

**Acción.** «Guardar cambios» valida y persiste la configuración. Si un campo es inválido, debe explicarse cuál es y no debe aparentarse que el guardado se completó.

## 12. Informes e impacto

**Responsable:** Edu Sanchez.

**Finalidad visible.** Presentar resultados de producción, automatización y reducción de desperdicio para un periodo.

**Información ya mostrada en el producto.** Alimentos salvados, unidades recuperadas, variación del desperdicio y pérdida económica evitada; además de precisión reciente y estados de ejecuciones. Cada indicador debe indicar periodo, unidad y si es medido o estimado.

## Requisitos compartidos de funcionamiento

- Cada vista usa datos del negocio activo y muestra cuándo se generó o actualizó una decisión automática.
- Las cifras conservan unidad y periodo; un importe potencial no se comunica como ahorro ya verificado.
- La acción principal tiene una respuesta visible: progreso, éxito, error o pendiente de confirmación.
- Los estados vacíos, de carga y de fallo explican la situación y el siguiente paso cuando corresponde.
- Pedido, promoción y ejecución conservan su origen, regla aplicada y línea de tiempo para poder explicar el resultado.
- Los controles manuales no borran evidencia de intentos o acciones automáticas anteriores.
