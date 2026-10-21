# Guía de desarrollo — Tienda del cliente (rutas)

**Carpeta:** `frontend/src/app/tienda`.

**Responsable:** Max Rojas. Autor y coordinador del bloque Tienda.

**Bloque:** Tienda del cliente. **Tareas:** T02–T05 (interfaz).

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [ADR-009](../../../../docs/arquitectura/decisiones/ADR-009-tienda-cliente.md) y [contrato de la tienda](../../../../docs/api/contrato-tienda.md).
- [Reparto vigente](../../../../docs/equipo/responsabilidades.md) y [alcance](../../../../docs/guia-inicio-desarrollo.md).
- [Código del módulo](../../tienda/GUIA_DESARROLLO.md).

## Punto de partida

**21-10-2026:** rutas implementadas a partir del prototipo Figma «PaginaCliente»: `/tienda` (inicio), `/tienda/menu` (catálogo por categorías con búsqueda y filtro por estado), `/tienda/carrito` (canasta, datos de entrega y pago simulado), `/tienda/pedido/[id]` (confirmación) y `/tienda/pedidos` (mis pedidos). Funcionan con **datos de ejemplo** hasta que exista el backend T01–T04. Consultar el resumen vigente de [Max Rojas](../../../../docs/equipo/avances/rojas.md).

## Reglas de esta carpeta

1. `layout.tsx` monta su propio encabezado, pie, sesión de cliente y estilos (`tienda.css`, todo bajo `.tienda`). No usa `ProtectedShell` ni la sesión administrativa; `AppShell` deja pasar las rutas `/tienda`.
2. Las páginas solo consumen `@/tienda/servicios`, `@/tienda/contexto` y `@/tienda/componentes`. No importar servicios, tipos ni componentes del administrador.
3. El stock se muestra solo como Disponible, Últimas unidades o Agotado. Nunca cantidades ni lotes.
4. El pago es simulado (tarjeta, Yape o Plin). No añadir campos de tarjeta, cuentas ni comprobantes. El QR y el número de pago son ficticios y llevan el rótulo de simulación.
5. El pedido termina en `CONFIRMADO`. Estados posteriores, cancelación, seguimiento, reseñas, avisos por WhatsApp y recojo en tienda son desarrollo futuro.
6. Navegar no exige sesión; confirmar sí (Google).

## Verificación

`npm run typecheck` y `npm run build`. Recorrido manual: agregar productos, confirmar sin sesión (abre login), errores de entrega, confirmar, ver el pedido y comprobar que el estado de stock cambia en el menú. Revisar también a 390 px sin scroll horizontal.
