# Operaciones compatibles con Cueva · 28-10-2026

Integración selectiva solicitada por Axel desde origin/bohorquez en 4c2a2715c4887dae205ec96240681bc4a202fc88, principalmente 1462b8c, 4239c1d y ba76bbb. Implementación original registrada como Codex en esa rama; adaptación de Codex para Axel. Cueva coordina; inventario/promociones Vera, compras Aguirre, planes/recetas Rojas y ventas/UI Sanchez conservan su responsabilidad.

Prevalecen [ADR-010](../arquitectura/decisiones/ADR-010-tienda-independiente-payme.md), [caja presencial](contrato-caja-presencial.md) y [entradas de productos](contrato-entradas-productos.md). Tienda continúa en tienda/, independiente por API HTTP; Payme sobre catálogo de ejemplo no mueve inventario real.

## API disponible

Base /api/v1, sobre {datos:...}, errores estándar 401/403/404/409/410/422. Admin/Operador registran/consultan producción y recepción. Configuración, decisiones, enlaces y avisos requieren Admin. Proveedor usa únicamente su token temporal.

| Método y ruta | Comportamiento |
|---|---|
| GET /operaciones/resumen | Últimos 100 planes, pedidos, registros y sugerencias; productos activos, configuración y fecha operativa. Solo lectura; no crea configuración. |
| POST /operaciones/producciones | Tanda del plan de la fecha operativa: receta congelada, ingredientes FEFO y nuevo lote de producto con ingreso fechado, en una transacción. |
| PUT /operaciones/configuracion | Reloj ACTUAL/ESCENARIO, fecha/hora, productos vigilados y habilitación. No cambia el reloj de Caja ni la programación de automatizaciones. |
| POST /operaciones/revisar | Revisión manual de avisos/promociones, sin envío externo. |
| POST /operaciones/promociones/{id}/decision | Aprobar/rechazar pendiente vigente con saldo e ingreso elegibles. Registra decisión; no publica en tienda ni aplica descuento en caja. |
| GET /operaciones/avisos | Últimos 200 avisos persistidos. |
| PATCH /operaciones/avisos/{id} | Lectura y resolución opcional de 5–1000 caracteres, actor e historial. Leer no equivale a resolver. |
| POST /operaciones/pedidos/{id}/enlace | Token aleatorio, hash persistido, una hora real; regenerar revoca el pendiente. No envía el enlace. |
| GET/POST /proveedor/pedidos/{token} | Pedido limitado / aceptar o rechazar, nombre y compromiso futuro con zona. Repetición idéntica recupera; contradictoria 409, vencido/revocado 410. No acredita identidad del proveedor. |
| POST /operaciones/recepciones/{id} | Pedido aceptado y enviado; todas las líneas una vez, cantidad 0..pendiente, descripción de diferencias. Usa recepción pública de Compras para positivos; cero no mueve stock. Incidencia y recepción atómicas. |

Ejemplo ficticio de tanda, con IDs/fecha de un plan existente:

```json
{"clave_idempotencia":"tanda-001","plan_id":1,"fecha":"2026-10-28","lineas":[{"producto_id":1,"cantidad":2,"fecha_caducidad":"2026-10-30"}]}
```

1–100 productos únicos, cantidades enteras 1–100000, caducidad entre producción y cuatro días después. Tandas acumuladas hasta pendiente del plan. Misma clave, actor y contenido recuperan; distinto contenido 409. Servicios no hacen commit. Los ingredientes se consumen al producir; la venta posterior usa nuestra caja, cotización y precios existentes, sin volver a consumir ingredientes ni escribir histórico/ML. Los lotes no se ven/venden antes del ingreso.

## Migración y ejecución

0023_operaciones_compatibles después de 0022: cinco tablas operativas e índices; PRODUCCION con control de signos, conservando ENTRADA/VENTA/ANULA_VENTA y sus restricciones. No se copia ni reescribe 0020_operacion_integrada remota: pertenece a otra cadena e incluye tienda y una restricción incompatible. No usar stamp. Una base de Bohorquez ya en su 0020 requiere conversión específica; no aplicar esta cadena sobre ella. Downgrade se detiene ante evidencia operativa.

Beat registra foodsave.control_operativo cada 30 s; promociones tienen ventana durable de 600 s. Avisos de proveedor usan tiempo real. Monitor deshabilitado y sin productos por defecto. Revisión manual disponible; no depende de visitas a la web. No hay red externa en el monitor. Workers/Beat se deben iniciar expresamente en la instalación; no se arrancan ni envían mensajes como efecto de esta verificación.

PUBLIC_BASE_URL opcional configura URL web; fallback FRONTEND_ORIGIN. HABILITAR_ENLACES_PROVEEDOR=1 agrega enlace al preparar un envío ya autorizado y ajusta su plazo al iniciarlo; apagado por defecto. Mantiene aprobación/destino/recuperación Telegram. El enlace es una credencial temporal: compartir solo con destinatario. Ningún envío externo se ejecuta al integrar.

## Selección y límites

Se incorporan Operación diaria, portal de proveedor, bandeja/campana y jerarquía del menú. BPMN F02/F05 son referencias de diseño, no certificación de integración futura. Se conservan Ventas como módulo aparte, entradas múltiples, flujo visual de automatizaciones, compras compactas, precios PEN, datos y credenciales.

Se excluyen segunda caja /operaciones/ventas, escritura inmediata de venta_diaria, fichas/precios paralelos, checkout unido a FoodSave, cuentas mock, semillas y lanzadores/túneles. Originales conservados en la rama de origen. Es un backport adaptado, no un merge completo de historia Git. Publicación HTTP de catálogo/promociones, simuladores, cierre y entrenamiento con tickets siguen pendientes. [Pruebas y despliegue](../equipo/avances/cueva.md).

## Evidencia del corte

0023 aplicada;45 tablas anteriores idénticas, cinco nuevas vacías y ambos.env sin cambios. Suite general352 correctas/35 omitidas/6 subtests; corte final11 casos PostgreSQL correctos. UI con respuesta incierta conserva solicitud/clave por usuario antes de POST y bloquea otra hasta recuperarla, incluso al recargar; error del resumen posterior no repite una operación confirmada. [Detalle de validación y límites](../equipo/avances/cueva.md).

## Integración comercial · 28-10-2026

La integración HTTP de catálogo/promociones, cotización/reserva y ticket TIENDA ya se amplió en contrato-integracion-tienda.md. La aprobación interna alimenta la publicación de los productos seleccionados; conserva la caja canónica y no modifica venta_diaria/ML.
