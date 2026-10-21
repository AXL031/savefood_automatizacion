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
