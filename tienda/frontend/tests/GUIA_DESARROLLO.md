# Guía de desarrollo — Tienda · frontend/tests

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

`npm test` ejecuta los tests Node y las interacciones React/jsdom con fetch/Flex simulados. Verificar cambio de método con UUID único, desmontaje anterior, cierre, errores de nonce y callback tardío. No usar credenciales reales ni una API de operación en estas pruebas.

## Ampliación vigente · 28-10-2026 · Tienda por API

payme-integracion.test.cjs prueba respuesta perdida y recuperación del mismo intento, quote congelada, rechazo de otra compra y reintento comercial con capacidad privada. No es comprobación visual ni prueba de un pago real de Payme.
