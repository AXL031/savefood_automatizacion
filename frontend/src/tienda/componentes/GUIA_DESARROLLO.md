# Guía de desarrollo — Componentes de la tienda

**Carpeta:** `frontend/src/tienda/componentes`.

**Responsable:** Max Rojas. **Bloque:** Tienda del cliente.

Leer primero la [guía del módulo](../GUIA_DESARROLLO.md) y el [contrato](../../../../docs/api/contrato-tienda.md).

Componentes visuales del prototipo Figma «PaginaCliente», con clases `t-*` definidas en `frontend/src/app/tienda/tienda.css`. Los íconos exportados de Figma están en `frontend/public/tienda/iconos/` y se usan con `IconoArchivo`; los de interacción, con `Icono` en línea.

- `ShellTienda`: proveedor de contexto, encabezado, pie, login y aviso flotante.
- `TarjetaProducto` / `TarjetaProductoHorizontal`: imagen, estado de stock, promoción y botón Agregar (deshabilitado si está agotado).
- `EstadoStock`: única forma de mostrar stock (tres estados).
- `ModalLogin`: botón oficial de Google en modo api; en modo ejemplo, formulario de correo Gmail rotulado como simulado.
- `QrFicticio`: patrón decorativo, no codifica datos.
- `DetallePedido`, `EstadoCarga`, `Iconos`, `Pie`, `Encabezado`.

Mantener accesibilidad: etiquetas en botones de solo ícono, foco visible, Escape cierra el login y menús, contraste del texto sobre fondos crema.

## Operación integrada · 27-10-2026

Ampliación expresa del usuario, implementada por Codex; responsabilidades conservadas. [Contrato](../../../../docs/api/contrato-operacion-integrada.md) y [guía de reproducción/variables](../../../../docs/operacion-integrada.md). Migración aditiva 0020: producción por tandas, venta interna/tienda con movimientos, respuesta del proveedor de una hora, recepción asistida/avisos y monitor cada diez minutos con aprobación. Código en operaciones y fronteras públicas de inventario/ventas. No hay reposición ni pagos reales automáticos. Docker separado para pruebas; túnel gratuito y Render opcional de pago. Credenciales privadas fuera de Git. Consultar bitácora Cueva para pruebas realmente ejecutadas y límites.
