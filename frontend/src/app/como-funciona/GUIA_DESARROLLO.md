# Guía de desarrollo — Cómo funciona

**Carpeta:** `frontend/src/app/como-funciona`. **Responsable:** Edu Sanchez (estructura visual compartida, E04).

Infografía del flujo completo del negocio, enlazada en la barra lateral debajo de Resumen. No consulta la API: el contenido es estático y describe el ciclo vigente (carga → modelo → automatización → plan y faltantes → pedidos → aprobación → Telegram → recepción → producción → venta → promociones → evaluación). Cada tarjeta, dato del ejemplo y chip lleva a su pantalla en la misma ventana; los nombres de pantalla salen de `components/layout/navegacion.tsx`.

Al cambiar una regla del flujo (por ejemplo, qué mueve el stock o cómo se aprueban pedidos), actualizar `PASOS` y `REGLAS` en `page.tsx` para que la guía no contradiga el alcance (`docs/guia-inicio-desarrollo.md`). Los ejemplos numéricos son ilustrativos, no datos del comercio. Estilos `fx-*` al final de `app/styles.css`; animaciones con `prefers-reduced-motion`.
