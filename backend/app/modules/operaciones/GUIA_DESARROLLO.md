# Operaciones compatibles · 28-10-2026

Coordinación Cueva; producción/planes Rojas, inventario/promociones Vera, compras Aguirre, ventas/UI Sanchez. Backport adaptado de Bohorquez 4c2a271, por Codex para Axel. Leer guías padre, responsabilidades/dependencias y [contrato vigente](../../../../docs/api/contrato-operacion-integrada.md).

servicio.py: tandas con receta congelada y pendiente bajo bloqueo de plan. inventario/operacion.py expone consumo/alta de lote con ingreso fechado. proveedores.py: enlace, respuesta e incidencia mediante Compras. monitoreo.py: revisión durable, avisos y sugerencias; rutas.py confirma la transacción completa. Servicios sin commit ni red; resumen GET solo lectura. Configuración serializada en PostgreSQL; catálogo bloqueado en orden.

Migración nueva 0023 sobre 0022, sin cambiar revisiones aplicadas ni 0020 remota. Conserva caja/entradas y añade PRODUCCION con signos. No añadir segunda caja, precios paralelos, semillas ni checkout: tienda/ es independiente por HTTP/ADR-010. Aprobar promoción no publica ni aplica descuento en caja. Pruebas test_operacion_integrada.py y test_migracion_operaciones.py; concurrencia requiere PostgreSQL. Actualizar contrato, guías y registro Cueva con evidencia real.
