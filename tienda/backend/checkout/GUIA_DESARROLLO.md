# Guía de desarrollo — Tienda · backend/checkout

Responsable de dominio: Max Rojas; separación y Payme sandbox: Codex para Axel (A04).
Leer [../../../AGENTS.md](../../../AGENTS.md), [responsabilidades](../../../docs/equipo/responsabilidades.md),
[dependencias](../../../docs/equipo/dependencias.md), [alcance](../../../docs/guia-inicio-desarrollo.md),
[ADR-010](../../../docs/arquitectura/decisiones/ADR-010-tienda-independiente-payme.md) y
[contrato Payme](../../../docs/api/contrato-payme-pruebas.md).

Proyecto con dependencias, configuración y datos propios. Única comunicación con
FoodSave: HTTP a sus APIs públicas. Prohibidos imports de sus módulos, acceso a su
PostgreSQL y montajes de sus archivos. No compartir sesión administrativa.
Catálogo de ejemplo y pago Payme preproducción son independientes del inventario.
No afirmar entrega o descuento real de stock. Nunca capturar PAN/CVV en componentes
propios ni exponer secretos/Access Token; Flex recibe solo nonce y payload.
Cada botón limita `display_settings.methods` a un método. QR/CIP y callbacks del
navegador no prueban pago. Guardar estados durables, capacidad privada e idempotencia.

Arranque, configuración y límites: [README](../../../tienda/README.md).
Verificar backend con pytest aislado y frontend con typecheck, build y tests Node;
recorrido visual del checkout. Registrar pruebas reales y bloqueos en
[avance Cueva](../../../docs/equipo/avances/cueva.md), con enlace al bloque de Rojas.

Cambiar solo método admite la misma clave/cuerpo únicamente en CREADO sin ninguna
transacción. No cambiar líneas, comprador, entrega, ID ni operación. Guardar métodos
preparados en snapshot y validar contra ellos las respuestas tardías; reflejar el
método real del resultado. JSON adicional es compatible con filas previas, sin
migración ni borrado de pagos.

## Ampliación vigente · 28-10-2026 · Tienda por API

Coordinación Codex para Axel (A04), conservando dominios Rojas (Tienda), Sanchez (Ventas/UI) y Vera (Inventario/Promociones). La ampliación usa dos proyectos y bases independientes: solo API HTTP, sin importar modelos, montar carpetas ni consultar PostgreSQL desde tienda. Payme solo preproducción y comprador invitado; cuatro botones independientes. Ver docs/api/contrato-integracion-tienda.md desde la raíz y registro Cueva para evidencia y límites. preparar_vinculo guarda solicitud estable antes de reservar por HTTP; preparar_salida solo tras verificación Payme. Reintento conserva evento/pedido/pago. PENDIENTE_VENTA se recupera por conciliador; reserva vencida, importe conflictivo o doble aprobación => REVISION_REQUERIDA. No hay reembolso automático ni segundo ticket. create_all solo agrega catálogo/pedido propios, sin alterar los pagos existentes.
