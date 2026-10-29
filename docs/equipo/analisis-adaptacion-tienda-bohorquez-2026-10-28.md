# Análisis previo de adaptación de la tienda de Bohorquez

> **Actualización 28-10-2026:** la implementación de catálogo, promociones aprobadas, reservas y ventas TIENDA por HTTP se documenta en [el contrato vigente](../api/contrato-integracion-tienda.md). Sustituye las menciones históricas de integración pendiente de este documento para esas capacidades. El modo ejemplo sigue sin afectar inventario; Payme continúa solo en preproducción. Cierre diario, simuladores y ML siguen pendientes.

**28-10-2026 · Solo análisis, sin implementación.** Solicitud de Axel: revisar antes de trasladar cambios a nuestra tienda independiente. Comparación estática del código local en cueva con origin/bohorquez **4c2a2715c4887dae205ec96240681bc4a202fc88**; fetch confirma esa cabeza y main39723b4. Autor: Codex para Axel. No cambia contratos vigentes, configuración, datos ni ejecutables; no habilita conexión de tienda, pagos reales o simuladores.

Coordinación Cueva; dominio de tienda Rojas, Ventas/UI Sanchez e Inventario/Promociones Vera. Se conserva la procedencia del código de la rama de Bohorquez, sin atribuir nueva implementación a integrantes. Rigen [ADR-010](../arquitectura/decisiones/ADR-010-tienda-independiente-payme.md), [Payme de pruebas](../api/contrato-payme-pruebas.md), [caja implementada](../api/contrato-caja-presencial.md) y [bases de integración futura](bases-modulo-ventas.md).

## Resultado

La adaptación es viable conservando el proyecto independiente y el checkout invitado de Payme. El avance de Bohorquez aporta principalmente backend y datos operativos; no contiene un rediseño general nuevo de la tienda. Copiar su checkout o activar solamente TIENDA_MODO=api rompería la coherencia de nuestra solución. Se propone reutilizar conceptos de catálogo, disponibilidad y promociones, implementando la integración sobre nuestras reglas de ventas e inventario mediante HTTP.

## Qué cambió realmente en la rama de origen

- Frontend: cuatro archivos de ejecución de tienda cambian respecto de HEAD: carrito, ModalLogin, DetallePedido y servicios. Sustituye Google obligatorio por una cuenta local de demostración cuando procede; conserva cuenta obligatoria para comprar. Hace explícitos los rótulos de pago simulado y SIM-, y activa consumo de API por defecto. CSS propio de tienda, contexto, tarjetas y recursos gráficos no cambian en ese corte. La composición visual principal ya procede del prototipo de Rojas que tenemos.
- Backend: operaciones/tienda.py publica fichas con precios/categorías/imágenes, calcula estados de stock, cotiza descuentos por lote y crea pedidos con pago simulado. Consume servicios/modelos de FoodSave dentro de su backend. Sus páginas ya consultan HTTP; el problema para nosotros es la titularidad de datos/pagos y el flujo de confirmación, no que sea imposible conservar una interfaz web separada.
- Compra: cliente autenticado, bloqueo de productos/lotes, validación de precio/stock y descuento FEFO. Al confirmar inserta RegistroOperacion de tipo VENTA_TIENDA y construye de inmediato pago APROBADO con referencia SIM-. No integra un proveedor financiero ni usa nuestra caja; deja compras de tienda fuera de Ventas/ML.
- Administración: fichas/precios paralelos en FichaTienda, publicación y aprobación de promociones. En Cueva solo se incorporaron monitor/decisión internos, no las fichas, cuentas locales ni el checkout remoto.
- Demo: semilla de12 productos/seis categorías, recetas/insumos/historia artificial y estados de stock variados. Nuestra tienda ya tiene21 productos de ejemplo y seis categorías; no es una ampliación automática de nuestro catálogo. Los139 precios de caja del comercio pertenecen a otra fuente y no deben sustituirse por esa semilla.

## Comparación y decisión propuesta

| Área | Bohorquez | Nuestra tienda | Adaptación propuesta |
|---|---|---|---|
| Presentación | Mismo diseño base; ajustes de textos y acceso | Diseño separado con componentes Payme | Conservar maquetación; mejorar mensajes de estado y consulta de compras sin introducir una cuenta obligatoria. |
| Catálogo | FichaTienda en PostgreSQL FoodSave | Ejemplo en frontend y JSON de cotización en API propia | FoodSave envía publicaciones versionadas a API de tienda; copia comercial propia, sin compartir tablas. |
| Precio | Precio/versiones propios de FichaTienda | Payme calcula con JSON propio; caja FoodSave tiene precios versionados | Una autoridad comercial FoodSave, basada en precios vigentes de caja o regla de canal acordada; no crear otro precio independiente sin contrato. |
| Stock | Lectura de lotes reales y tres niveles | Estados de ejemplo y adaptador HTTP preparado | Reutilizar el formato público, pero calcular con reglas actuales de Inventario y respetar fecha_ingreso. |
| Promociones | Aprobadas y aplicadas a unidades del lote | Ejemplo con unidades promocionadas; caja sin descuentos comerciales | Publicación versionada por API y cotización autoritativa que conserve cantidades con/sin promoción. |
| Acceso | Cliente Google/local obligatorio | Invitado para pagar; cuenta opcional heredada | Mantener invitado. Consulta con capacidad privada/enlace del pedido; cuenta opcional sería otra fase. |
| Pago | Tarjeta/Yape/Plin simulados; aprobación inmediata | Payme sandbox, CARD/YAPE/QR/PAGOEFECTIVO por botón | Conservar Payme, cambio de método y verificación backend. No copiar formulario propio ni aprobaciones SIM-. |
| Pedido e inventario | Un POST local hace ambas cosas, sin espera financiera | Pago durable separado; no genera ticket/stock FoodSave | Reserva previa y evento de venta confirmado por API, con acuse y recuperación. No compartir transacción SQL. |
| Ventas | Compra guardada fuera del módulo Ventas | Caja actual solo PRESENCIAL; canal tienda diseñado para fase futura | Ampliar servicio canónico para TIENDA mediante migración aditiva; no copiar un segundo registro de ventas. |
| Historia/demostración | Datos sintéticos sembrados en instalación demo | Datos existentes y pagos sandbox propios | Conservarlos; cualquier escenario enriquecido se prepara aparte y explícitamente. |

## Incompatibilidades que deben resolverse antes de conectar compras

1. **Dos fuentes de cotización.** servicios.ts permite catálogo/stock de FoodSave en modo api, pero cotizarCarrito siempre llama a la API propia /pagos/cotizar. pagos.py lee catalogo_prueba.json y crear_pago vuelve a cotizar con ese archivo. Cambiar una variable no conecta importes/versiones: se podría mostrar un producto/precio y preparar otro importe. El backend de tienda deberá obtener o validar una cotización FoodSave identificada y conservar su snapshot para Payme.
2. **Identidad de productos.** IDs numéricos de datos de ejemplo, semilla remota y catálogo cargado se crean por separado. No mapearlos por coincidencia numérica ni por nombres parecidos. Publicación con identificador de origen estable y versión, conservando relación con producto FoodSave. Una futura migración de carrito debe validar versión/origen y explicar los productos retirados, no reutilizar carritos antiguos a ciegas.
3. **Stock disponible durante el pago.** El POST simulado remoto descuenta al confirmar sin esperar servicios externos. Payme admite estados pendientes: no mantener locks SQL abiertos mientras el cliente paga ni cobrar primero confiando en stock posterior. Diseñar reserva con vencimiento, consumo/liberación y control de pagos tardíos. También la caja presencial y ajustes deben respetar reservas activas para no vender dos veces la última unidad. Liberar la reserva no equivale a cancelar una transacción Payme.
4. **Estado de pago separado de estado comercial.** Pago aprobado verificado, pedido confirmado y ticket registrado son hechos distintos. La tienda necesita estados persistidos, por ejemplo pago pendiente, venta pendiente de sincronizar y venta registrada, más revisión por excepción. Un timeout de FoodSave debe reintentar el mismo evento y recuperar el mismo ticket; no iniciar otro pago. Un pago tardío tras expirar la reserva no se etiqueta automáticamente como compra entregable.
5. **Cuenta obligatoria incompatible.** El carrito remoto bloquea compra sin sesión y su endpoint depende de cliente_actual; el login local requiere cuenta/contraseña guardada en FoodSave. No reintroducir esos requisitos: el navegador compra como invitado y el backend de tienda se identifica ante FoodSave con credencial de integración limitada. No usar el token de Administrador ni enviar secretos Payme a FoodSave.
6. **Precios y promociones por lote.** La caja actual conserva una versión de precio y exige subtotal=cantidad*precio. El remoto puede mezclar unidades con/sin descuento en una línea. Hace falta ampliar el contrato de línea/segmentos y su evidencia, sin editar tickets anteriores ni aplicar descuento a todas las unidades porque la tarjeta del producto muestre una promoción. Aprobación interna ya disponible no equivale a publicación ni a soporte comercial completo.
7. **Criterio de lote vendible.** El selector remoto no filtra fecha_ingreso y exige fecha_caducidad conocida; nuestra venta actual excluye ingresos futuros y permite caducidad desconocida con aviso si existe límite vigente. No copiar ese selector como segunda regla. Debe acordarse la política publicada y consumir la interfaz canónica, conservando los lotes y fechas actuales.
8. **Canal de ventas pendiente.** TicketVenta impone canal=PRESENCIAL y sus rutas esperan un usuario de caja. Habilitar TIENDA implica identidad de integración, clave por evento/pedido externo, precio/reserva validada y ampliaciones de datos/servicio; no basta llamar a registrar_ticket con un usuario ficticio. Registrar una venta online no inserta venta_diaria ni ejecuta cierre/entrenamiento.
9. **Contrato de disponibilidad e imágenes.** Los tres estados de stock no garantizan cantidad al pagar: la reserva debe validarla en FoodSave. El snapshot comercial de tienda no es autoridad del saldo. Las rutas /tienda/productos/*.jpg pueden seguir siendo assets propios ya presentes, con asociación por producto o marcador neutral. Nunca montar el directorio FoodSave ni sustituir imágenes arbitrariamente para139 SKU.
10. **Migraciones y datos.** La0020 remota añade tablas/estados incompatibles con nuestra cadena0023; no aplicarla ni copiar el servidor/semilla remotos a esta instalación. Nuevas tablas de publicación, integración o reservas requieren migraciones aditivas separadas y respaldo. No cambiar .env, precios, stock, usuarios ni el catálogo cargado como parte de una adaptación visual.

## Arquitectura propuesta, aún sin implementar

Se mantiene la dirección pedida por Axel en las bases de Ventas:

1. FoodSave publica **productos y promociones aprobadas** a la API propia de tienda. Evento/recurso/versiones y acuse; conservar reintentos durables, orden por versión y retirada de publicación sin borrar historia. La tienda conserva su copia comercial y assets propios.
2. Tienda muestra esa copia. Para comprar, su backend solicita a FoodSave **cotización y reserva** con productos de origen, cantidad, canal y clave estable. FoodSave valida publicación, precio, promoción, fechas y saldo; devuelve snapshot/versiones/vencimiento. El navegador no fija importes ni movimientos.
3. Backend de tienda prepara Payme sandbox con el importe congelado de esa cotización. Conserva cuatro botones y capacidad privada; solo Consulta/S2S firmado verifica el pago como ahora. No se comparte credencial Payme con FoodSave.
4. Después de verificar, tienda envía **evento de venta** por HTTP: identificadores de integración/evento/pedido, reserva/cotización, referencia y resultado verificado del pago. Datos comerciales mínimos y autenticación de integración; nunca datos de tarjeta ni permiso administrativo.
5. FoodSave valida idempotencia/estado y confirma **ticket TIENDA + consumo de reserva + salida de lotes** en una transacción propia. Devuelve el mismo ticket ante reintentos. Tienda guarda el acuse y lo muestra en Mis compras; sin doble descuento desde frontend o Payme.
6. Si hay caída o respuesta perdida, tienda conserva el evento y consulta/reintenta con la misma identidad. Con reserva vencida, importe distinto o conflicto posterior al pago, persiste estado de revisión. No declarar éxito comercial ni hacer reembolso automático que todavía no existe. Cierre diario y ML se mantienen como ampliación futura.

Son capacidades propuestas, no endpoints publicados ni integración disponible. Las dos bases permanecen separadas. Habrá que concretar campos, errores, autenticación, plazos y reconciliación antes de implementar consumidor/proveedor.

## Orden recomendado para una implementación posterior

**Etapa1 · Presentación compatible.** Conservar nuestro checkout invitado, Payme y diseño. Ajustar Mis pedidos/pagos para distinguir simulaciones históricas, pago Payme y pedido confirmado, sin mensajes que afirmen entrega/stock inexistentes. No importar cuenta obligatoria ni datos mock. Esta etapa puede hacerse sin conectar inventario real.

**Etapa2 · Catálogo/promociones por API, todavía sin compras conectadas.** Completar ficha/publicación versionada con precios existentes, identidad estable, recepción en tienda, fotos/marcador y actualización visible de stock/promoción. Mientras no haya cotización/reserva completas, el checkout de catálogo real no se mezcla con el de ejemplo. El modo sandbox actual puede mantenerse separado.

**Etapa3 · Compra completa con Payme sandbox.** Ampliar Ventas/Inventario para canal tienda y reservas, cotización común y eventos persistidos con acuse; probar ambos canales, pendientes/expirados y recuperación. Solo entonces asociar esos pagos de prueba a tickets/stock de una instalación de demostración expresamente preparada. No alterar la instalación comercial por el mero cambio de un flag.

**Etapa4 · Demostración/simuladores y cierre.** Los escenarios enriquecidos de Bohorquez pueden servir como referencias de datos en una base aislada, sin sobrescribir nuestra carga. Los simuladores, cierre, cobertura diaria y entrenamiento siguen sus propuestas existentes y no son requisito de un cambio visual.

## Criterios de aceptación para esa adaptación futura

- Tienda compila y arranca fuera del repositorio FoodSave; ningún import, volumen o SQL cruzado.
- Pago invitado; cuatro botones; cambio de método y recuperación actuales conservados, sin volver a pago simulado al pulsar confirmar.
- Lo mostrado, cotizado, reservado y preparado en Payme usa el mismo origen, moneda, versión e importe; ejemplos y catálogo real no se mezclan.
- Promoción aprobada/publicada llega una sola vez por versión; la retirada y agotamiento se reflejan y una promoción de pocas unidades no rebaja todo el carrito.
- La última unidad concurrente entre presencial/tienda y dos tiendas no se vende dos veces; reenvío de venta/pago no duplica ticket ni saldo.
- Payme pendiente, pago tardío, corte de FoodSave y respuesta perdida conservan estados y recuperación sin cobrar otra vez. Una devolución/anulación de mercancía no se presenta como un reembolso financiero ya implementado.
- Invitado consulta solo su compra con capacidad privada; integración sin permisos de Administrador. Credenciales existentes fuera del código/frontend.
- Precios, tickets, lotes, carga histórica y automatizaciones actuales conservados. No se escribe ML ni se entrena por recibir un ticket.

## Evidencia revisada y límites

- Remoto, mediante git show/diff: frontend/src/app/tienda/carrito/page.tsx; frontend/src/tienda/{servicios.ts,componentes/ModalLogin.tsx,componentes/DetallePedido.tsx}; backend/app/modules/operaciones/{tienda.py,rutas.py,esquemas.py,modelos.py,semilla_catalogo.py}; inventario/operacion.py.
- Local: [servicios de tienda](../../tienda/frontend/src/tienda/servicios.ts), [carrito Payme](../../tienda/frontend/src/app/tienda/carrito/page.tsx), [componente Payme](../../tienda/frontend/src/tienda/componentes/PagoPayme.tsx), [detalle de pagos](../../tienda/frontend/src/tienda/componentes/DetallePagoPayme.tsx), [cotización/persistencia](../../tienda/backend/checkout/pagos.py), [rutas de pago](../../tienda/backend/checkout/rutas_pagos.py), [caja](../../backend/app/modules/ventas/modelos_caja.py) y [stock canónico](../../backend/app/modules/inventario/ventas.py).
- Se distingue código disponible de diseño pendiente. No se ejecutaron tests funcionales, pagos, Google, seeds, migraciones ni llamadas a datos de operación: es análisis estático y documental. Las pruebas de la integración anterior siguen siendo evidencia de aquel corte, no de una tienda conectada.
- Solo se crean este informe y referencias de coordinación/bitácora. No hay cambios de comportamiento, despliegue, credenciales, rama, commit o push por este análisis.
