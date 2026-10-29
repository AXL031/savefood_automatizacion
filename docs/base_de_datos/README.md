# Base de datos

**Estado actual verificado · 28-10-2026:** 50 tablas de dominio tras `0023_operaciones_compatibles`; las 45 anteriores conservaron sus datos y las cinco nuevas quedaron vacías. [Contrato de operaciones](../api/contrato-operacion-integrada.md). Las notas siguientes y el ER fechado son cortes previos.

**28-10-2026 · Esquema actual:** 45 tablas tras 0022, con [entradas de productos](../api/contrato-entradas-productos.md). Snapshot ER/estructura física hasta 0019 conserva 38 tablas; las migraciones 0021/0022 describen las ampliaciones posteriores.

**26-10-2026 · Esquema actual:** 43 tablas tras 0021; cinco nuevas de [caja presencial](../api/contrato-caja-presencial.md). El ER y estructura física enlazados conservan el snapshot hasta 0019 (38 tablas), sin las tablas nuevas; consultar la migración 0021 para su DDL.

> Guía vigente: [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md). Responsable de coordinación: **Axel Cueva**. Tareas, dependencias y avances se detallan en la guía local.

- [Esquema](esquema-objetivo-mvp.md): columnas, restricciones y migración de cada tabla.
- [Diccionario](diccionario-de-datos.md): definiciones canónicas y dueños.
- [Diagrama entidad-relación](diagrama-entidad-relacion.md).
- [Estructura física completa](estructura-fisica.md): 38 tablas del código hasta 0019, columnas y tipos PostgreSQL, PK/FK/UK, nulabilidad, defaults, CHECK e índices.

## Estado posterior · 28-10-2026 · Acoplamiento

50 entidades tras0023: conserva45 anteriores y añade registro_operacion, configuracion_operacion, aviso_operacion, solicitud_proveedor y promocion_operacion. Snapshot ER/estructura física de0019 se conserva fechado; DDL posterior en migraciones0021–0023 y [contrato operativo](../api/contrato-operacion-integrada.md). No incluye la base de tienda independiente.

## Integración comercial · 28-10-2026

Corte 28-10-2026: 0024_comercio_tienda añade cinco tablas a las cincuenta de 0023: configuracion_comercio, publicacion_producto, evento_publicacion, reserva_tienda y asignacion_reserva. Ampliaciones de cotización/ticket/línea en la migración aditiva y contrato-integracion-tienda. Los diagramas/cifras de cortes anteriores son históricos; SQLite de tienda continúa separado.
