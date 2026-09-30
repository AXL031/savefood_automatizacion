# Avances — Leonardo Aguirre

**Responsable:** Leonardo Aguirre. **Bloque:** Proveedores, pedidos y Telegram. **Rama prevista:** `aguirre`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md). Este archivo se actualiza al terminar cada avance significativo.

## Resumen vigente

- **Estado L01 (2026-09-30):** proveedor y oferta persistidos y API integrada localmente por Codex para Axel a partir de `59305f6`. Usa infraestructura común, autenticación, Administrador en escrituras, FK a ingrediente, restricciones de conversión y migración 0007. Contrato de consulta para Compras probado; Telegram usa solo adaptador falso en pruebas y no hay adaptador real ni pantalla nueva. L01 parcial; L02–L04 pendientes.

- **Estado:** definición documental disponible; implementación del bloque por verificar/completar.
- **Punto de partida observado:** Existen contratos y carpetas de proveedores/compras. No existe integración Telegram ni pedido persistido. La política de recompra entre planes está pendiente de cerrar con Max.
- **Contrato disponible:** [reparto y tareas](../responsabilidades.md); las guías de [mapa-carpetas](../mapa-carpetas.md) enlazan contratos de dominio.
- **Entrega a consumidores:** todavía no se certifica una nueva API integrada en este registro.
- **Bloqueos:** consultar las entregas necesarias en [dependencias](../dependencias.md); registrar aquí el ID exacto cuando se materialice una espera.
- **Siguiente paso:** cerrar cuerpos de API, tipos/restricciones y ejemplos del primer corte del bloque; después implementar contra esos contratos.

| Tarea | Estado de seguimiento |
|---|---|
| L01 · Implementar proveedores y ofertas | PENDIENTE DE VERIFICAR / COMPLETAR |
| L02 · Generar pedidos desde necesidades | PENDIENTE DE VERIFICAR / COMPLETAR |
| L03 · Implementar aprobación y canal | PENDIENTE DE VERIFICAR / COMPLETAR |
| L04 · Resolver fallos y entregar UI | PENDIENTE DE VERIFICAR / COMPLETAR |

## Bitácora

### Integración coordinada de entregas Rojas/Aguirre · 30-09-2026

- **Fecha/zona y autor:** 2026-09-30, America/Bogota. Codex a solicitud de Axel Cueva, coordinación transversal A04; se conserva autoría original de Max/Leonardo y la entrega delegada registrada en [Vera](vera.md).
- **Estado:** integración local verificada en SQLite; LISTO_PARA_INTEGRAR en Git, PostgreSQL/Redis y revisión remota pendientes. No declara completa la demo.
- **Comportamiento:** proveedor y oferta persistidos y API integrada localmente por Codex para Axel a partir de `59305f6`. Usa infraestructura común, autenticación, Administrador en escrituras, FK a ingrediente, restricciones de conversión y migración 0007. Contrato de consulta para Compras probado; Telegram usa solo adaptador falso en pruebas y no hay adaptador real ni pantalla nueva. L01 parcial; L02–L04 pendientes.
- **Archivos/contrato:** [contratos](../../api/contratos.md), [importaciones](../../api/contrato-importaciones.md), [pedidos](../../api/contrato-pedidos.md), rutas de inicialización/ingredientes/recetas/inventario/proveedores, `backend/migrations/env.py`, nuevas revisiones 0005/0006/0007 y `backend/tests/integration/test_api_inicializacion_ventas.py`, `test_proveedores_l01.py`, `test_migraciones_entregas.py`, `test_inventario_concurrencia_pg.py`. Enlaces de coordinación: [Axel](cueva.md), [Max](rojas.md), [Vera](vera.md), [Aguirre](aguirre.md), [Edu](sanchez.md).
- **Ejemplo público:** POST autenticado `/api/v1/inicializacion/confirmar` con los cinco CSV y fechas válidas devuelve DATOS_CARGADOS; POST administrativo `/api/v1/proveedores/{id}/ofertas` exige ingrediente existente y conversión explícita. Servicios participantes hacen flush, el llamador confirma.
- **Migraciones/configuración:** continuar desde 0004 con 0005→0006→0007; registrar todos los modelos, incluido ConfiguracionInicial. Revisiones previas conservadas. Para concurrencia activar V02_POSTGRES_TEST=1 sobre esquema de pruebas aislado; no habilitar Telegram ni cambiar modo automático.
- **Pruebas realmente ejecutadas:** `.venv/Scripts/python.exe -m pytest backend/tests foodsave-ml/tests -q` → 112 passed, 10 skipped (8 A03 y 2 V02 por PostgreSQL/Redis), 6 subtests passed. `npm run typecheck` y `npm run build` correctos. Delta 0004→0007 arriba/abajo/arriba y comparación de metadatos en SQLite correctos; el índice de expresión del núcleo no se puede reflejar en SQLite. Docker Desktop no logró arrancar; CI incorpora alembic check y concurrencia V02. No se ejecutaron envíos externos.
- **Dependencias y siguiente paso:** revisión de la entrega conjunta y CI PostgreSQL; después integrar a main. Max continúa M02/M03; Aguirre completa adaptador/UI L01 y L02–L04; Vera V03; Edu/Kevin/Axel conectan ML desde asistente completo.
- **Commit/PR:** cambios locales en cueva; publicación de PR de integración pendiente.


### Preparación del registro

- **Autor:** IA que preparó el reparto y guías, sin atribuir implementación a Leonardo Aguirre.
- **Cambio:** se definieron las tareas y el lugar de documentación; no se implementó lógica de este bloque en esta entrega documental.
- **Pruebas:** la revisión de documentación comprueba enlaces, cobertura de carpetas y coherencia del reparto; no acredita funcionamiento del módulo.
- **Próximo autor:** registrar el primer avance con la [plantilla](README.md) y actualizar el resumen vigente.

