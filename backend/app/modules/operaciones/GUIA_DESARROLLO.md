# Operación integrada

Cueva coordina; producción/tienda Rojas, inventario/promociones Vera, ventas Sanchez y compras Aguirre. Implementación por Codex para el usuario, sin atribuir autoría a integrantes.

Leer guías padre y `docs/api/contrato-operacion-integrada.md`. Servicios reciben una sesión sin commit; rutas confirman, errores revierten. Módulos de inventario/ventas exponen operaciones públicas. No registrar tarjetas, tokens de proveedor ni contraseñas en logs. La revisión periódica usa una configuración bloqueada y Beat único. Migración 0020 y API/frontend deben desplegarse juntos. Cuentas de prueba requieren opción explícita; Google real permanece disponible.

## Escenario sintético enriquecido · 27-10-2026

`semilla_catalogo.py` define doce productos de seis categorías, dieciséis ingredientes, recetas multingrediente, tres proveedores ficticios sin chat, lotes con diferentes estados y ventas deterministas. `semilla.py` aplica la ampliación una vez mediante marcador `demo-pasteleria-v2-2026`, en la transacción compartida. Conserva cuentas, ventas anteriores, lotes consumidos, planes inmutables y fichas/recetas que el usuario ya editó. Las nuevas recetas crean versiones, no reescriben planes. Una base ajena o una inicialización entrenando se rechaza. En demo existente con modelo listo se reserva una preparación nueva; no se inventa un modelo ni recibos de Telegram.

Pruebas en `test_semilla_demo.py`: primer arranque, repetición sin reponer stock, ampliación de v1 con historia operativa, cero versus ausencia, caducidad, conservación de ediciones y una sola reserva del modelo nuevo. Catálogo usa imágenes/etiquetas correspondientes a cada categoría. Pago sigue siendo simulado y referencia `SIM-`, sin proveedor financiero ni cargos.
