# Operación integrada

Cueva coordina; producción/tienda Rojas, inventario/promociones Vera, ventas Sanchez y compras Aguirre. Implementación por Codex para el usuario, sin atribuir autoría a integrantes.

Leer guías padre y `docs/api/contrato-operacion-integrada.md`. Servicios reciben una sesión sin commit; rutas confirman, errores revierten. Módulos de inventario/ventas exponen operaciones públicas. No registrar tarjetas, tokens de proveedor ni contraseñas en logs. La revisión periódica usa una configuración bloqueada y Beat único. Migración 0020 y API/frontend deben desplegarse juntos. Cuentas de prueba requieren opción explícita; Google real permanece disponible.
