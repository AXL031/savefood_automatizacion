# Guía de desarrollo — Dashboard y reportes de lectura

**Responsable:** Kevin Bohorquez (K04). Integración transversal por Codex para Axel; no se atribuye autoría personal a otros integrantes.

## Leer antes de trabajar

Leer guías padre, [responsabilidades](../../../../docs/equipo/responsabilidades.md), [dependencias](../../../../docs/equipo/dependencias.md), [alcance](../../../../docs/guia-inicio-desarrollo.md) y [contrato de reportes](../../../../docs/api/contrato-informes.md).

## Ampliación expresa y fuentes

Solicitud del usuario del 01-10-2026: gráficos en Inicio y módulo Reportes. Este corte consulta ventas actuales, evaluación histórica K03 y estados de pedidos por fecha del escenario; las consultas y exportaciones son de lectura. No incluye dinero, desperdicio, recepción de compras o impacto inventado.

## Interfaces y reglas

Backend: `rutas.py` registra `/informes/resumen` y `/informes/exportar`; `servicio.py` coordina interfaces públicas de ventas, compras y evaluación sin repositorios privados. No hay entidades propias ni migraciones. Fecha inicial/final inclusivas, máximo 366 días. El rango inicial termina en la última venta conocida. Pedidos cuenta cada pedido una sola vez, sin multiplicarlo por intentos.

Frontend: `/informes` (etiqueta Reportes) usa `services/informes.ts`, `types/informes.ts`, gráficos compartidos, TablaPaginada y PanelDetalle. Descarga CSV autenticada sin token en URL. Todas las filas agregadas del período se exportan, con fuentes y filtros; nunca solo la página visible. Inicio usa el mismo resumen sin evaluación para evitar trabajo ML innecesario.

## Verificación y entrega

`backend/tests/integration/test_informes.py` verifica permisos, filtros, ausencias/cero, revisión vigente, cobertura, agregados completos, CSV y conteo sin duplicar intentos. Typecheck/build verifican consumidor web. Evidencia final y limitaciones en [Bohorquez](../../../../docs/equipo/avances/bohorquez.md) y coordinación en [Cueva](../../../../docs/equipo/avances/cueva.md). Una prueba con fixtures no equivale a entrenamiento ni envío real.

## Documentar cada avance

Actualizar resumen vigente y bitácora del responsable, contrato y guía cuando cambie una frontera. Mantener las limitaciones reales del entorno y los indicadores económicos como evolución futura.
