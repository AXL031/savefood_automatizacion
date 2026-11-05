# Operación diaria · 28-10-2026

05-11-2026 · Promociones usa `PromocionesOperacion`: producto/lote, filtro Activas/Programadas/Pendientes, búsqueda, fecha y modo de cada reserva. Diálogo Dentro de dos minutos, retirada advertida si estaba activa, cancelación a pendiente y cuenta atrás. La solicitud/clave se conserva en sessionStorage para recuperar respuesta incierta como producción/recepción. Solo Admin; requiere API/migración 0026. No cambia entrenamiento/planes ni envía mensajes. [Contrato](../../../../docs/api/contrato-operacion-integrada.md).

Interfaz original de Bohorquez 4c2a271 adaptada por Codex para Axel; coordinación Cueva, UI Sanchez y dominios Rojas/Vera/Aguirre. Leer guías padre y [contrato](../../../../docs/api/contrato-operacion-integrada.md).

Tandas, recepción asistida, aprobación y configuración del monitor; enlaces a Caja e Inventario existentes. Sin segunda venta interna ni ficha/checkout de tienda. Planes por fecha operativa; servidor valida permisos/stock. Formularios bloqueados al enviar y clave estable al reintentar. Resumen cada 30 s y cancelación al salir. Aprobación todavía sin publicación HTTP en tienda. Avisos /notificaciones y proveedor sin sesión administrativa /proveedor/pedido/[token].

Producción/recepción guardan ruta, cuerpo y clave en sessionStorage por usuario antes del POST. Ante respuesta incierta se bloquean nuevas operaciones; Recuperar reenvía el mismo cuerpo/clave aun después de recargar. Respuesta confirmada limpia el registro y reinicia el formulario. Errores de validación permiten corregir; un fallo del resumen después de confirmar no se presenta como fallo de registro. Regresión `scripts/verificar-operaciones.cjs`.

## Integración comercial · 28-10-2026

Las promociones aprobadas/vigentes se publican por el módulo Comercio para productos explícitamente publicados. La pestaña enlaza /tienda-admin; no usa el checkout acoplado de la rama remota.
