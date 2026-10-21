# Guía de desarrollo — Tienda del cliente (módulo)

**Carpeta:** `frontend/src/tienda`.

**Responsable:** Max Rojas. Autor y coordinador del bloque Tienda.

**Bloque:** Tienda del cliente. **Tareas:** T02–T05 (interfaz y frontera de datos).

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Contrato de la tienda](../../../docs/api/contrato-tienda.md) y [ADR-009](../../../docs/arquitectura/decisiones/ADR-009-tienda-cliente.md).
- [Rutas que consumen este módulo](../app/tienda/GUIA_DESARROLLO.md).

## Contenido

| Archivo | Uso |
|---|---|
| `tipos.ts` | Tipos del contrato (producto, estado de stock, pedido, pago simulado, errores). |
| `servicios.ts` | Única frontera de datos. Modo `ejemplo` (por defecto) o `api` (`NEXT_PUBLIC_TIENDA_MODO=api`). Cliente HTTP propio, separado del administrador. |
| `datos-ejemplo.ts` | Catálogo, stock interno, promociones aprobadas y datos del comercio para el modo ejemplo. Solo lo importa `servicios.ts`. |
| `contexto.tsx` | Carrito (localStorage), sesión del cliente, ventana de login, catálogo y consulta de stock cada 5 s. |
| `dinero.ts` | Céntimos enteros, descuento con redondeo a céntimos y formato `S/`. |
| `componentes/` | Encabezado, pie, tarjetas, estado de stock, login, QR ficticio, detalle de pedido. Guía propia. |

## Modo ejemplo

Reproduce el contrato sin backend: cotiza la canasta, valida datos de entrega, exige sesión, aplica idempotencia por cliente y clave, descuenta stock y unidades de promoción en un solo guardado y rechaza con `STOCK_INSUFICIENTE` o `PRECIO_CAMBIADO`. El estado vive en el navegador (`foodsave-tienda-ejemplo-v1`); `reiniciarDatosEjemplo()` lo restablece. **No es la fuente real**: no crea movimientos de inventario ni reserva `EVALUAR_PROMOCION`. El login de ejemplo pide un correo Gmail y no verifica identidad.

## Pasar a la API real

1. Implementar T01–T04 en el backend según el contrato.
2. Definir `NEXT_PUBLIC_TIENDA_MODO=api`, `NEXT_PUBLIC_API_URL` y `NEXT_PUBLIC_GOOGLE_CLIENT_ID` (cliente OAuth con el origen local registrado).
3. Las pantallas no cambian: solo `servicios.ts` decide el origen de datos.

## Límites

No guardar ni pedir datos de pago. No mostrar cantidades de stock. No reutilizar la sesión ni el cliente HTTP administrativo (su evento de sesión vencida cerraría la sesión equivocada).
