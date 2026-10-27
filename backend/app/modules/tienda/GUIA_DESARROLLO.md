# Guía de desarrollo — Tienda del cliente (backend)

**Carpeta:** `backend/app/modules/tienda`.

**Responsable:** Max Rojas. Autor y coordinador del bloque Tienda.

**Bloque:** Tienda del cliente. **Tareas:** T01–T05; implementada T02.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [ADR-009](../../../../docs/arquitectura/decisiones/ADR-009-tienda-cliente.md) y [contrato de la tienda](../../../../docs/api/contrato-tienda.md).
- [Configurar Google](../../../../docs/api/configurar-google-tienda.md).
- [Interfaz del cliente](../../../../frontend/src/tienda/GUIA_DESARROLLO.md).

## Estado

**21-10-2026 · T02 implementada:** tabla `cliente` (migración `0019_tienda_clientes`), `POST /api/v1/tienda/sesion/google` y `GET /api/v1/tienda/sesion`. El backend verifica el ID token con las claves públicas de Google (firma RS256, `aud` = `GOOGLE_CLIENT_ID`, emisor, vigencia y `email_verified`), crea o actualiza el cliente por `sub` y emite un token propio con audiencia `tienda` firmado con `TIENDA_JWT_SECRET` (o una clave derivada de `JWT_SECRET`). T01, T03, T04 y T05 siguen pendientes.

| Archivo | Uso |
|---|---|
| `modelos.py` | `ClienteTienda` (`cliente`): `google_sub` único, correo, nombre, activo y fechas. |
| `autenticacion.py` | Verificación de Google, alta o actualización del cliente, emisión del token y dependencia `cliente_actual`. |
| `rutas.py` | Rutas `/tienda/sesion*`. |

## Reglas

1. Un token de cliente nunca abre rutas administrativas y uno administrativo nunca abre la tienda: clave distinta y audiencia `tienda`.
2. Identificar al cliente por `sub`, no por correo.
3. `obtener_verificador` es la única puerta a Google. Las pruebas la sustituyen o firman con claves RSA locales; ninguna prueba llama a Google.
4. Los servicios no confirman: la ruta hace `commit`, y ante una carrera de primer acceso reintenta una vez.
5. No guardar el ID token de Google ni datos de pago.

## Pruebas

`tests/integration/test_tienda_sesion.py` (SQLite y PostgreSQL con `E03_POSTGRES_TEST=1`).

## Operación integrada · 27-10-2026

Ampliación expresa del usuario, implementada por Codex; responsabilidades conservadas. [Contrato](../../../../docs/api/contrato-operacion-integrada.md) y [guía de reproducción/variables](../../../../docs/operacion-integrada.md). Migración aditiva 0020: producción por tandas, venta interna/tienda con movimientos, respuesta del proveedor de una hora, recepción asistida/avisos y monitor cada diez minutos con aprobación. Código en operaciones y fronteras públicas de inventario/ventas. No hay reposición ni pagos reales automáticos. Docker separado para pruebas; túnel gratuito y Render opcional de pago. Credenciales privadas fuera de Git. Consultar bitácora Cueva para pruebas realmente ejecutadas y límites.
