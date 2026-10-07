# Mapa de carpetas y responsables

Cada carpeta fuente o documental tiene una GUIA_DESARROLLO.md. Se excluyen Git, dependencias, entornos virtuales, cachés y salidas generadas. Las carpetas añadidas solo con documentación indican dónde implementar; no acreditan código disponible.

El [reparto](responsabilidades.md) es la fuente de propiedad. Consultar [dependencias](dependencias.md) y [avances](avances/README.md) antes de integrar.

| Carpeta | Responsable | Alcance | Guía |
|---|---|---|---|
| `.` | Axel Cueva | Compartida; coordinación | [Abrir](../../GUIA_DESARROLLO.md) |
| `.github` | Axel Cueva | Compartida; coordinación | [Abrir](../../.github/GUIA_DESARROLLO.md) |
| `.github/workflows` | Axel Cueva | Compartida; coordinación | [Abrir](../../.github/workflows/GUIA_DESARROLLO.md) |
| `backend` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/GUIA_DESARROLLO.md) |
| `backend/tests/fixtures/primera_carga` | Edu Sanchez, coordinación de Axel | Demo · Cinco CSV sintéticos para E03/K01 | [Abrir](../../backend/tests/fixtures/primera_carga/GUIA_DESARROLLO.md) |
| `backend/app` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/app/GUIA_DESARROLLO.md) |
| `backend/app/core` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/app/core/GUIA_DESARROLLO.md) |
| `backend/app/integrations` | Leonardo Aguirre | Compartida; coordinación | [Abrir](../../backend/app/integrations/GUIA_DESARROLLO.md) |
| `backend/app/integrations/canales_venta` | Leonardo Vera | Compartida; coordinación | [Abrir](../../backend/app/integrations/canales_venta/GUIA_DESARROLLO.md) |
| `backend/app/integrations/notificaciones` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/app/integrations/notificaciones/GUIA_DESARROLLO.md) |
| `backend/app/integrations/proveedores` | Leonardo Aguirre | Compartida; coordinación | [Abrir](../../backend/app/integrations/proveedores/GUIA_DESARROLLO.md) |
| `backend/app/modules` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/app/modules/GUIA_DESARROLLO.md) |
| `backend/app/modules/autenticacion` | Axel Cueva | Demo · Autenticación y sesión | [Abrir](../../backend/app/modules/autenticacion/GUIA_DESARROLLO.md) |
| `backend/app/modules/automatizaciones` | Axel Cueva | Demo · Programaciones, ejecuciones e intentos | [Abrir](../../backend/app/modules/automatizaciones/GUIA_DESARROLLO.md) |
| `backend/app/modules/compras` | Leonardo Aguirre | Demo · Pedidos, aprobación y envío | [Abrir](../../backend/app/modules/compras/GUIA_DESARROLLO.md) |
| `backend/app/modules/desperdicio` | Leonardo Vera | Futuro; custodia | [Abrir](../../backend/app/modules/desperdicio/GUIA_DESARROLLO.md) |
| `backend/app/modules/excedentes` | Leonardo Vera | Futuro; custodia | [Abrir](../../backend/app/modules/excedentes/GUIA_DESARROLLO.md) |
| `backend/app/modules/informes` | Kevin Bohorquez | Futuro; custodia | [Abrir](../../backend/app/modules/informes/GUIA_DESARROLLO.md) |
| `backend/app/modules/ingredientes` | Max Rojas | Demo · Ingredientes y unidades | [Abrir](../../backend/app/modules/ingredientes/GUIA_DESARROLLO.md) |
| `backend/app/modules/inicializacion` | Edu Sanchez | Demo · Asistente y primera carga | [Abrir](../../backend/app/modules/inicializacion/GUIA_DESARROLLO.md) |
| `backend/app/modules/inventario` | Leonardo Vera | Demo · Inventario por lotes y movimientos | [Abrir](../../backend/app/modules/inventario/GUIA_DESARROLLO.md) |
| `backend/app/modules/negocios` | Axel Cueva | Demo · Negocio y configuración | [Abrir](../../backend/app/modules/negocios/GUIA_DESARROLLO.md) |
| `backend/app/modules/notificaciones` | Axel Cueva | Futuro; custodia | [Abrir](../../backend/app/modules/notificaciones/GUIA_DESARROLLO.md) |
| `backend/app/modules/planificacion` | Max Rojas | Demo · Planificación y necesidades de ingredientes | [Abrir](../../backend/app/modules/planificacion/GUIA_DESARROLLO.md) |
| `backend/app/modules/produccion` | Leonardo Vera | Futuro; custodia | [Abrir](../../backend/app/modules/produccion/GUIA_DESARROLLO.md) |
| `backend/app/modules/productos` | Edu Sanchez | Demo · Catálogo de productos y SKU | [Abrir](../../backend/app/modules/productos/GUIA_DESARROLLO.md) |
| `backend/app/modules/promociones` | Leonardo Vera | Demo · Promociones sugeridas | [Abrir](../../backend/app/modules/promociones/GUIA_DESARROLLO.md) |
| `backend/app/modules/pronosticos` | Kevin Bohorquez | Demo · Pronósticos y evaluación histórica | [Abrir](../../backend/app/modules/pronosticos/GUIA_DESARROLLO.md) |
| `backend/app/modules/proveedores` | Leonardo Aguirre | Demo · Proveedores y ofertas | [Abrir](../../backend/app/modules/proveedores/GUIA_DESARROLLO.md) |
| `backend/app/modules/recetas` | Max Rojas | Demo · Recetas versionadas | [Abrir](../../backend/app/modules/recetas/GUIA_DESARROLLO.md) |
| `backend/app/modules/ventas` | Edu Sanchez | Demo · Ventas diarias e historial | [Abrir](../../backend/app/modules/ventas/GUIA_DESARROLLO.md) |
| `backend/app/shared` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/app/shared/GUIA_DESARROLLO.md) |
| `backend/app/shared/enums` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/app/shared/enums/GUIA_DESARROLLO.md) |
| `backend/app/shared/events` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/app/shared/events/GUIA_DESARROLLO.md) |
| `backend/app/shared/schemas` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/app/shared/schemas/GUIA_DESARROLLO.md) |
| `backend/app/shared/utils` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/app/shared/utils/GUIA_DESARROLLO.md) |
| `backend/app/workers` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/app/workers/GUIA_DESARROLLO.md) |
| `backend/app/workers/retry` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/app/workers/retry/GUIA_DESARROLLO.md) |
| `backend/app/workers/tasks` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/app/workers/tasks/GUIA_DESARROLLO.md) |
| `backend/migrations` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/migrations/GUIA_DESARROLLO.md) |
| `backend/migrations/versions` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/migrations/versions/GUIA_DESARROLLO.md) |
| `backend/tests` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/tests/GUIA_DESARROLLO.md) |
| `backend/tests/fixtures` | Edu Sanchez | Compartida; coordinación | [Abrir](../../backend/tests/fixtures/GUIA_DESARROLLO.md) |
| `backend/tests/integration` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/tests/integration/GUIA_DESARROLLO.md) |
| `backend/tests/unit` | Axel Cueva | Compartida; coordinación | [Abrir](../../backend/tests/unit/GUIA_DESARROLLO.md) |
| `docs` | Axel Cueva | Compartida; coordinación | [Abrir](../GUIA_DESARROLLO.md) |
| `docs/api` | Axel Cueva | Compartida; coordinación | [Abrir](../api/GUIA_DESARROLLO.md) |
| `docs/arquitectura` | Axel Cueva | Compartida; coordinación | [Abrir](../arquitectura/GUIA_DESARROLLO.md) |
| `docs/arquitectura/c4` | Axel Cueva | Compartida; coordinación | [Abrir](../arquitectura/c4/GUIA_DESARROLLO.md) |
| `docs/arquitectura/decisiones` | Axel Cueva | Compartida; coordinación | [Abrir](../arquitectura/decisiones/GUIA_DESARROLLO.md) |
| `docs/arquitectura/diagramas` | Axel Cueva | Compartida; coordinación | [Abrir](../arquitectura/diagramas/GUIA_DESARROLLO.md) |
| `docs/procesos` | Axel Cueva | Compartida; coordinación | [Abrir](../procesos/GUIA_DESARROLLO.md) |
| `docs/automatizacion` | Axel Cueva | Compartida; coordinación | [Abrir](../automatizacion/GUIA_DESARROLLO.md) |
| `docs/base_de_datos` | Axel Cueva | Compartida; coordinación | [Abrir](../base_de_datos/GUIA_DESARROLLO.md) |
| `docs/diseno` | Edu Sanchez | Compartida; coordinación | [Abrir](../diseno/GUIA_DESARROLLO.md) |
| `docs/diseno/mockups` | Edu Sanchez | Compartida; coordinación | [Abrir](../diseno/mockups/GUIA_DESARROLLO.md) |
| `docs/equipo` | Axel Cueva | Compartida; coordinación | [Abrir](GUIA_DESARROLLO.md) |
| `docs/equipo/avances` | Axel Cueva | Compartida; coordinación | [Abrir](avances/GUIA_DESARROLLO.md) |
| `docs/funcionalidades` | Axel Cueva | Compartida; coordinación | [Abrir](../funcionalidades/GUIA_DESARROLLO.md) |
| `foodsave-ml` | Kevin Bohorquez | Compartida; coordinación | [Abrir](../../foodsave-ml/GUIA_DESARROLLO.md) |
| `foodsave-ml/notebooks` | Kevin Bohorquez | Compartida; coordinación | [Abrir](../../foodsave-ml/notebooks/GUIA_DESARROLLO.md) |
| `foodsave-ml/tests` | Kevin Bohorquez | Compartida; coordinación | [Abrir](../../foodsave-ml/tests/GUIA_DESARROLLO.md) |
| `frontend` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/GUIA_DESARROLLO.md) |
| `frontend/public` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/public/GUIA_DESARROLLO.md) |
| `frontend/src` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/src/GUIA_DESARROLLO.md) |
| `frontend/src/app` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/src/app/GUIA_DESARROLLO.md) |
| `frontend/src/app/automatizaciones` | Axel Cueva | Demo · Programaciones, ejecuciones e intentos | [Abrir](../../frontend/src/app/automatizaciones/GUIA_DESARROLLO.md) |
| `frontend/src/app/automatizaciones/ejecuciones` | Axel Cueva | Demo · Programaciones, ejecuciones e intentos | [Abrir](../../frontend/src/app/automatizaciones/ejecuciones/GUIA_DESARROLLO.md) |
| `frontend/src/app/automatizaciones/ejecuciones/[id]` | Axel Cueva | Demo · Programaciones, ejecuciones e intentos | [Abrir](../../frontend/src/app/automatizaciones/ejecuciones/[id]/GUIA_DESARROLLO.md) |
| `frontend/src/app/compras` | Leonardo Aguirre | Demo · Pedidos, aprobación y envío | [Abrir](../../frontend/src/app/compras/GUIA_DESARROLLO.md) |
| `frontend/src/app/configuracion` | Axel Cueva | Demo · Negocio y configuración | [Abrir](../../frontend/src/app/configuracion/GUIA_DESARROLLO.md) |
| `frontend/src/app/excedentes` | Leonardo Vera | Futuro; custodia | [Abrir](../../frontend/src/app/excedentes/GUIA_DESARROLLO.md) |
| `frontend/src/app/informes` | Kevin Bohorquez | Futuro; custodia | [Abrir](../../frontend/src/app/informes/GUIA_DESARROLLO.md) |
| `frontend/src/app/ingredientes` | Max Rojas | Demo · Ingredientes y unidades | [Abrir](../../frontend/src/app/ingredientes/GUIA_DESARROLLO.md) |
| `frontend/src/app/inicializacion` | Edu Sanchez | Demo · Asistente y primera carga | [Abrir](../../frontend/src/app/inicializacion/GUIA_DESARROLLO.md) |
| `frontend/src/app/inicializacion/piloto` | Edu Sanchez, coordinación de Axel | Demo · Carga rápida del CSV bakery | [Abrir](../../frontend/src/app/inicializacion/piloto/GUIA_DESARROLLO.md) |
| `frontend/src/app/iniciar-sesion` | Axel Cueva | Demo · Autenticación y sesión | [Abrir](../../frontend/src/app/iniciar-sesion/GUIA_DESARROLLO.md) |
| `frontend/src/app/inventario` | Leonardo Vera | Demo · Inventario por lotes y movimientos | [Abrir](../../frontend/src/app/inventario/GUIA_DESARROLLO.md) |
| `frontend/src/app/notificaciones` | Axel Cueva | Futuro; custodia | [Abrir](../../frontend/src/app/notificaciones/GUIA_DESARROLLO.md) |
| `frontend/src/app/panel` | Kevin Bohorquez | Demo · Pronósticos y evaluación histórica | [Abrir](../../frontend/src/app/panel/GUIA_DESARROLLO.md) |
| `frontend/src/app/planificacion` | Max Rojas | Demo · Planificación y necesidades de ingredientes | [Abrir](../../frontend/src/app/planificacion/GUIA_DESARROLLO.md) |
| `frontend/src/app/produccion` | Leonardo Vera | Futuro; custodia | [Abrir](../../frontend/src/app/produccion/GUIA_DESARROLLO.md) |
| `frontend/src/app/productos` | Edu Sanchez | Demo · Catálogo de productos y SKU | [Abrir](../../frontend/src/app/productos/GUIA_DESARROLLO.md) |
| `frontend/src/app/promociones` | Leonardo Vera | Demo · Promociones sugeridas | [Abrir](../../frontend/src/app/promociones/GUIA_DESARROLLO.md) |
| `frontend/src/app/pronosticos` | Kevin Bohorquez | Demo · Pronósticos y evaluación histórica | [Abrir](../../frontend/src/app/pronosticos/GUIA_DESARROLLO.md) |
| `frontend/src/app/proveedores` | Leonardo Aguirre | Demo · Proveedores y ofertas | [Abrir](../../frontend/src/app/proveedores/GUIA_DESARROLLO.md) |
| `frontend/src/app/recetas` | Max Rojas | Demo · Recetas versionadas | [Abrir](../../frontend/src/app/recetas/GUIA_DESARROLLO.md) |
| `frontend/src/app/ventas` | Edu Sanchez | Demo · Ventas diarias e historial | [Abrir](../../frontend/src/app/ventas/GUIA_DESARROLLO.md) |
| `frontend/src/components` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/src/components/GUIA_DESARROLLO.md) |
| `frontend/src/components/automatizacion` | Axel Cueva | Compartida; coordinación | [Abrir](../../frontend/src/components/automatizacion/GUIA_DESARROLLO.md) |
| `frontend/src/components/charts` | Kevin Bohorquez | Compartida; coordinación | [Abrir](../../frontend/src/components/charts/GUIA_DESARROLLO.md) |
| `frontend/src/components/forms` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/src/components/forms/GUIA_DESARROLLO.md) |
| `frontend/src/components/layout` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/src/components/layout/GUIA_DESARROLLO.md) |
| `frontend/src/components/panel` | Kevin Bohorquez | Compartida; coordinación | [Abrir](../../frontend/src/components/panel/GUIA_DESARROLLO.md) |
| `frontend/src/components/tables` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/src/components/tables/GUIA_DESARROLLO.md) |
| `frontend/src/components/ui` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/src/components/ui/GUIA_DESARROLLO.md) |
| `frontend/src/constants` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/src/constants/GUIA_DESARROLLO.md) |
| `frontend/src/features` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/src/features/GUIA_DESARROLLO.md) |
| `frontend/src/features/automatizaciones` | Axel Cueva | Demo · Programaciones, ejecuciones e intentos | [Abrir](../../frontend/src/features/automatizaciones/GUIA_DESARROLLO.md) |
| `frontend/src/features/compras` | Leonardo Aguirre | Demo · Pedidos, aprobación y envío | [Abrir](../../frontend/src/features/compras/GUIA_DESARROLLO.md) |
| `frontend/src/features/desperdicio` | Leonardo Vera | Futuro; custodia | [Abrir](../../frontend/src/features/desperdicio/GUIA_DESARROLLO.md) |
| `frontend/src/features/excedentes` | Leonardo Vera | Futuro; custodia | [Abrir](../../frontend/src/features/excedentes/GUIA_DESARROLLO.md) |
| `frontend/src/features/ingredientes` | Max Rojas | Demo · Ingredientes y unidades | [Abrir](../../frontend/src/features/ingredientes/GUIA_DESARROLLO.md) |
| `frontend/src/features/inicializacion` | Edu Sanchez | Demo · Asistente y primera carga | [Abrir](../../frontend/src/features/inicializacion/GUIA_DESARROLLO.md) |
| `frontend/src/features/inventario` | Leonardo Vera | Demo · Inventario por lotes y movimientos | [Abrir](../../frontend/src/features/inventario/GUIA_DESARROLLO.md) |
| `frontend/src/features/planificacion` | Max Rojas | Demo · Planificación y necesidades de ingredientes | [Abrir](../../frontend/src/features/planificacion/GUIA_DESARROLLO.md) |
| `frontend/src/features/produccion` | Leonardo Vera | Futuro; custodia | [Abrir](../../frontend/src/features/produccion/GUIA_DESARROLLO.md) |
| `frontend/src/features/productos` | Edu Sanchez | Demo · Catálogo de productos y SKU | [Abrir](../../frontend/src/features/productos/GUIA_DESARROLLO.md) |
| `frontend/src/features/promociones` | Leonardo Vera | Demo · Promociones sugeridas | [Abrir](../../frontend/src/features/promociones/GUIA_DESARROLLO.md) |
| `frontend/src/features/pronosticos` | Kevin Bohorquez | Demo · Pronósticos y evaluación histórica | [Abrir](../../frontend/src/features/pronosticos/GUIA_DESARROLLO.md) |
| `frontend/src/features/proveedores` | Leonardo Aguirre | Demo · Proveedores y ofertas | [Abrir](../../frontend/src/features/proveedores/GUIA_DESARROLLO.md) |
| `frontend/src/features/recetas` | Max Rojas | Demo · Recetas versionadas | [Abrir](../../frontend/src/features/recetas/GUIA_DESARROLLO.md) |
| `frontend/src/features/ventas` | Edu Sanchez | Demo · Ventas diarias e historial | [Abrir](../../frontend/src/features/ventas/GUIA_DESARROLLO.md) |
| `frontend/src/hooks` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/src/hooks/GUIA_DESARROLLO.md) |
| `frontend/src/services` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/src/services/GUIA_DESARROLLO.md) |
| `frontend/src/types` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/src/types/GUIA_DESARROLLO.md) |
| `frontend/src/utils` | Edu Sanchez | Compartida; coordinación | [Abrir](../../frontend/src/utils/GUIA_DESARROLLO.md) |
| `scripts` | Axel Cueva | Compartida; coordinación | [Abrir](../../scripts/GUIA_DESARROLLO.md) |
