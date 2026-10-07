# Compras

> Guía vigente: [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md). Responsable: **Leonardo Aguirre**. Tareas, dependencias y avances se detallan en la guía local.

Pedidos, selección de proveedor, envío y estados.

Esta carpeta forma parte del esqueleto del proyecto. El código se agregará al implementar su funcionalidad.

**Responsable del módulo:** Leonardo Aguirre. La responsabilidad incluye interfaz, servidor y APIs según [la división del equipo](../../../../docs/equipo/responsabilidades.md).

**Estructura prevista:** `rutas.py`, `servicio.py`, `repositorio.py`, `modelos.py`, `esquemas.py`, `dependencias.py`, `errores.py` y `tests/`. Crear estos archivos con su implementación, sin acceder directamente al repositorio de otro módulo.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.

## Paso 6 local · L03 · 30-09-2026

Aprobación/rechazo administrativos con clave idempotente, responsable, nombre y fecha; rechazo motivado de pendiente/bloqueado sin exigir canal. Aprobar exige modo manual, propuesta válida y chat revisado/verificado con credencial vigente. Congela texto/chat/huella y reserva envio_pedido en la misma transacción. Consultas/UI incluyen decisión, destino actual separado de snapshots, mensaje DEMOSTRACIÓN — NO SURTIR e intento/evidencia de Telegram. Aprobar no confirma envío; Beat/worker lo ejecutan y guardan message_id/fecha solo con respuesta válida.

Outbox con lease y token de despacho: revalida antes de transmitir y confirma ENVIANDO antes del efecto externo. Reentrega no vuelve a enviar; timeout, respuesta inválida o worker interrumpido quedan PENDIENTE_VERIFICACION sin retry. Cambiar destino/credencial bloquea antes de red. Ninguna acción mueve stock ni libera por sí sola la reserva de fecha. AUTOMATICO, conciliación y nuevos intentos humanos siguen en paso 7. Migración aditiva 0013; downgrade bloqueado si existen decisiones para no borrar evidencia. Contrato vigente: docs/api/contrato-pedidos.md; prueba test_aprobacion_envio_l03.py. Implementación local por Codex para Axel, responsabilidad de Aguirre, sin commit ni remoto; bot real pendiente del usuario.
