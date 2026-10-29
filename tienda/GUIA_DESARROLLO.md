# Guía de desarrollo — Proyecto independiente Tienda

Autor del prototipo y responsable de dominio: Max Rojas. Separación y Payme:
Codex para Axel, coordinación A04. Leer [AGENTS](../AGENTS.md),
[responsabilidades](../docs/equipo/responsabilidades.md),
[dependencias](../docs/equipo/dependencias.md),
[alcance](../docs/guia-inicio-desarrollo.md),
[ADR-010](../docs/arquitectura/decisiones/ADR-010-tienda-independiente-payme.md) y
[contrato Payme](../docs/api/contrato-payme-pruebas.md).

Frontend, API de pagos, configuración, dependencias y datos propios. FoodSave
solo se consume por API HTTP; no importar sus módulos, compartir PostgreSQL ni
montar sus archivos. Mantener secretos en .env y backend. Solo Payme sandbox,
un método por botón. Confirmar exclusivamente por Consulta o S2S firmado.
Catálogo de ejemplo no acredita integración de inventario ni entrega real.

[README](README.md) contiene arranque, credenciales, pruebas y límites. Verificar
typecheck/build/tests del frontend, pytest del backend y recorrido visual.
Actualizar contrato, guías y [avances de Cueva](../docs/equipo/avances/cueva.md)
con evidencia real; enlazar el bloque de Rojas sin atribuirle trabajo de Codex.

## Ampliación vigente · 28-10-2026 · Tienda por API

Coordinación Codex para Axel (A04), conservando dominios Rojas (Tienda), Sanchez (Ventas/UI) y Vera (Inventario/Promociones). La ampliación usa dos proyectos y bases independientes: solo API HTTP, sin importar modelos, montar carpetas ni consultar PostgreSQL desde tienda. Payme solo preproducción y comprador invitado; cuatro botones independientes. Ver docs/api/contrato-integracion-tienda.md desde la raíz y registro Cueva para evidencia y límites. TIENDA_MODO lo decide la API propia. api usa réplica de catálogo y servicios HTTP; ejemplo conserva JSON y pagos anteriores sin inventario. No reutilizar carritos entre orígenes. La carpeta sigue compilando fuera del repositorio.
