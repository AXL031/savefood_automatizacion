# Operaciones compatibles · 28-10-2026

05-11-2026 · `promociones_programadas.py`: programación puntual por Admin sobre sugerencia pendiente/aprobada. Retirada temporal PROGRAMADA, motor EVALUAR_PROMOCION, revalidación de lote/regla/fecha al ejecutar, modo conservado y cancelación antes de reclamo dejando pendiente. Resumen identifica producto/lote, programación y actividad comercial. Migración 0026; [contrato](../../../../docs/api/contrato-operacion-integrada.md). La vigilancia no adelanta lotes programados; servicios sin commit ni red.

04-11-2026 · monitor consume `negocios.servicio.obtener_modo_publicacion_promociones`; modo conservado por evaluación nueva, aprobación automática sin actor humano y aviso explicativo. Pendientes/rechazos anteriores no cambian por cambiar Configuración. Resumen expone modo_publicacion; comercio entrega las aprobadas/vigentes. Migración 0025 y prueba `test_modo_promociones.py`.

Coordinación Cueva; producción/planes Rojas, inventario/promociones Vera, compras Aguirre, ventas/UI Sanchez. Backport adaptado de Bohorquez 4c2a271, por Codex para Axel. Leer guías padre, responsabilidades/dependencias y [contrato vigente](../../../../docs/api/contrato-operacion-integrada.md).

servicio.py: tandas con receta congelada y pendiente bajo bloqueo de plan. inventario/operacion.py expone consumo/alta de lote con ingreso fechado. proveedores.py: enlace, respuesta e incidencia mediante Compras. monitoreo.py: revisión durable, avisos y sugerencias; rutas.py confirma la transacción completa. Servicios sin commit ni red; resumen GET solo lectura. Configuración serializada en PostgreSQL; catálogo bloqueado en orden.

Migración nueva 0023 sobre 0022, sin cambiar revisiones aplicadas ni 0020 remota. Conserva caja/entradas y añade PRODUCCION con signos. No añadir segunda caja, precios paralelos, semillas ni checkout: tienda/ es independiente por HTTP/ADR-010. Aprobar promoción no publica ni aplica descuento en caja. Pruebas test_operacion_integrada.py y test_migracion_operaciones.py; concurrencia requiere PostgreSQL. Actualizar contrato, guías y registro Cueva con evidencia real.
