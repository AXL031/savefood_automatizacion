# Guía de desarrollo — Tienda del cliente (backend)

> Actualización 21-10-2026 solicitada por Axel: la tienda es el proyecto independiente `tienda/`; solo se comunica con FoodSave por API HTTP. Payme Flex se integra exclusivamente en preproducción con cuatro botones. El inventario real sigue pendiente de T01/T03/T04. Prevalece ADR-010 y el contrato Payme; las ubicaciones y pagos simulados descritos abajo son el corte previo.


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
