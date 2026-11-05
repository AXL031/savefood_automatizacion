# Guía de desarrollo — Tienda · frontend/src/tienda/componentes

Responsable de dominio: Max Rojas; separación y Payme sandbox: Codex para Axel (A04).
Leer [../../../../../AGENTS.md](../../../../../AGENTS.md), [responsabilidades](../../../../../docs/equipo/responsabilidades.md),
[dependencias](../../../../../docs/equipo/dependencias.md), [alcance](../../../../../docs/guia-inicio-desarrollo.md),
[ADR-010](../../../../../docs/arquitectura/decisiones/ADR-010-tienda-independiente-payme.md) y
[contrato Payme](../../../../../docs/api/contrato-payme-pruebas.md).

Proyecto con dependencias, configuración y datos propios. Única comunicación con
FoodSave: HTTP a sus APIs públicas. Prohibidos imports de sus módulos, acceso a su
PostgreSQL y montajes de sus archivos. No compartir sesión administrativa.
Catálogo de ejemplo y pago Payme preproducción son independientes del inventario.
No afirmar entrega o descuento real de stock. Nunca capturar PAN/CVV en componentes
propios ni exponer secretos/Access Token; Flex recibe solo nonce y payload.
Cada botón limita `display_settings.methods` a un método. QR/CIP y callbacks del
navegador no prueban pago. Guardar estados durables, capacidad privada e idempotencia.

Arranque, configuración y límites: [README](../../../../../tienda/README.md).
Verificar backend con pytest aislado y frontend con typecheck, build y tests Node;
recorrido visual del checkout. Registrar pruebas reales y bloqueos en
[avance Cueva](../../../../../docs/equipo/avances/cueva.md), con enlace al bloque de Rojas.

Cambio de método: `CREADO` sin transaction_id no equivale a pago en curso. Mantener
botones habilitados, desmontar SDK previo y conservar clave/operación. Una respuesta
recibida se verifica incluso si pertenece al formulario anterior. Para transacciones
registradas, mostrar Consulta; no simular cancelación ni borrar su referencia.
Regresión de interacción: `npm test` (jsdom/SDK simulado, sin llamadas Payme).

## Resultado antes de navegar · 04-11-2026

`configuracionFlex` habilita `display_result_screen`. Al recibir `pagado=true` de la API propia, `PagoPayme` conserva Flex montado cuatro segundos, anuncia la próxima navegación y bloquea métodos/datos del comprador. Después termina la instancia, libera el borrador y llama `alAprobar` una sola vez; el carrito se vacía en ese consumidor, sin cortar antes el resultado. El callback solo inicia la verificación, nunca confirma por sí mismo. Repeticiones/cierres tardíos no reinician la espera; desmontar cancela el temporizador y conserva la referencia recuperable. Recuperar un pago ya confirmado sin Flex activo navega directamente. La pausa es de presentación, no retrasa la confirmación del servidor ni el registro comercial. No garantiza la duración interna de una versión del SDK; comprobarla con sandbox en una prueba autorizada.

## Ampliación vigente · 28-10-2026 · Tienda por API

PagoPayme usa quote autoritativa, conserva reserva/importe al cambiar de método y recupera el pago pendiente. DetallePagoPayme muestra pago y venta por separado y permite reintentar entrega HTTP sin volver a cobrar. Imágenes ausentes usan marcador neutral y catálogo vacío indica publicación pendiente. Coordinación Codex para Axel (A04), conservando dominios Rojas (Tienda), Sanchez (Ventas/UI) y Vera (Inventario/Promociones). La ampliación usa dos proyectos y bases independientes: solo API HTTP, sin importar modelos, montar carpetas ni consultar PostgreSQL desde tienda. Payme solo preproducción y comprador invitado; cuatro botones independientes. Ver docs/api/contrato-integracion-tienda.md desde la raíz y registro Cueva para evidencia y límites.
