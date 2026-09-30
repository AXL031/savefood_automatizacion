# Avances — Edu Sanchez

**Responsable:** Edu Sanchez. **Bloque:** Inicialización, productos, ventas y estructura visual compartida. **Rama prevista:** `sanchez`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md). Este archivo se actualiza al terminar cada avance significativo.

## Resumen vigente

- **Estado:** E01 parcial implementado como servicio interno y migración; consumido por K01–K03 en prueba local SQLite con CSV piloto. Pendiente prueba PostgreSQL. E02–E04 siguen pendientes.
- **Punto de partida alcanzado:** Catálogo bakery desde la lista curada, mapeo de 139 SKU, carga agregada de ventas diarias, revisiones y lectura temporal pública sin inferir ceros ausentes. Hay CLI de carga local; no hay asistente ni API de ventas.
- **Contrato disponible:** [contrato de servicios E01](../../api/contratos.md#inicialización--ventas-y-catálogo) y [esquema objetivo](../../base_de_datos/esquema-objetivo-mvp.md).
- **Entrega a consumidores:** Kevin usa `listar_skus_bakery`, `nombres_productos`, `limites_historial` y `leer_historial` en K01–K03; prueba integral local con el CSV piloto acreditada en su registro.
- **Bloqueos:** Docker Desktop está instalado, pero su motor Linux requiere habilitar `Virtual Machine Platform` en Windows y reiniciar; falta verificar `0002_e01_ventas` y la carga en PostgreSQL.
- **Siguiente paso:** probar migración y carga en PostgreSQL; Edu completa el asistente y las rutas/pantallas de E01–E04.

| Tarea | Estado de seguimiento |
|---|---|
| E01 · Definir y cargar productos y ventas | EN_CURSO: corte interno para Kevin, sin API ni prueba PostgreSQL |
| E02 · Construir asistente XLSX/CSV | PENDIENTE DE VERIFICAR / COMPLETAR |
| E03 · Preparar primera inicialización | PENDIENTE DE VERIFICAR / COMPLETAR |
| E04 · Entregar pantallas y piezas comunes | PENDIENTE DE VERIFICAR / COMPLETAR |

## Bitácora

### E01 · Consumo local por Kevin y ampliación de lecturas públicas

- **Fecha/hora y zona:** 2026-09-29 (America/Bogota).
- **Autor y responsable del bloque:** Codex, trabajando en la frontera de Edu Sanchez a pedido del usuario; no atribuye la edición a Edu.
- **Tareas:** E01 parcial y dependencia de K01–K03.
- **Estado:** EN_CURSO; servicio consumido localmente por Kevin, sin PostgreSQL verificado.
- **Qué cambió y qué comportamiento está disponible:** se añadieron `listar_skus_bakery`, `nombres_productos` y `limites_historial` para evitar acceso de Kevin a modelos privados; se corrigió compatibilidad de consulta con SQLAlchemy 2.1. El importador y el entrenamiento procesaron el CSV piloto completo en SQLite.
- **Archivos clave:** `backend/app/modules/productos/servicio.py`, `backend/app/modules/ventas/servicio.py`, `backend/tests/integration/test_frontera_edu_kevin_e01.py`.
- **Contrato/función/ruta y ejemplo:** `listar_skus_bakery(sesion)` devuelve `{producto_id: sku}`; `limites_historial(sesion, [producto_id])` devuelve `(primera_fecha, ultima_fecha)`. Ver [contratos.md](../../api/contratos.md#inicialización--ventas-y-catálogo).
- **Migración/configuración necesaria:** `0002_e01_ventas`; CSV y lista curada en `foodsave-ml/`.
- **Pruebas:** `python -m pytest backend/tests foodsave-ml/tests -q`: 78 passed, 8 skipped, 6 subtests passed. Prueba integral local SQLite: 139 productos, 228936 líneas aceptadas, 1264 negativas excluidas y 27740 ventas diarias. Alembic generó SQL offline PostgreSQL de la cadena completa; no se ejecutó upgrade PostgreSQL.
- **Qué necesita el siguiente desarrollador y quién es:** Edu continúa E02/E03; Max y Vera podrán consumir catálogo y ventas según sus propios contratos; Kevin ya consumió esta frontera localmente.
- **Dependencias/bloqueos:** PostgreSQL/Compose no disponibles en esta PC; inicialización completa necesita Max y Vera.
- **Siguiente paso concreto:** verificar migración/carga en PostgreSQL y conectar E02/E03 sin modificar la interfaz temporal ya consumida.
- **Commit/PR:** cambios locales, sin commit.

### E01 · Corte de catálogo y ventas para K02/K03

- **Fecha/hora y zona:** 2026-09-29 (America/Bogota).
- **Autor y responsable del bloque:** IA de la sesión, trabajando en el bloque asignado a Edu Sanchez; no atribuye esta implementación a Edu.
- **Tareas:** E01 parcial.
- **Estado:** EN_CURSO; servicio listo para prueba de integración, aún sin PostgreSQL verificado.
- **Qué cambió y qué comportamiento está disponible:** `producto`/`sku_producto`, `importacion_venta`/`venta_diaria`/`revision_venta`; catálogo explícito desde `lista_productos_precios_limpia.md`; agregación diaria de `bakery_sales_limpio_final.csv`, excluyendo líneas negativas y sin convertir ausencia en cero; corrección con revisión; lectura por producto y rango que entrega SKU y revisión vigente. La lista de precios se usa como fuente de nombres/SKU, sin almacenar precios fuera del alcance E01.
- **Archivos clave:** `backend/app/modules/productos/{modelos,servicio}.py`, `backend/app/modules/ventas/{modelos,servicio,cargar_piloto}.py`, `backend/migrations/versions/0002_e01_ventas.py`, `backend/tests/integration/test_frontera_edu_kevin_e01.py`.
- **Contrato/función/ruta y ejemplo:** `leer_historial(sesion, [producto_id], date(2022, 8, 1), date(2022, 8, 24))` retorna solo ventas conocidas anteriores al 24 con `revision_venta_id`. Contrato en [contratos.md](../../api/contratos.md#inicialización--ventas-y-catálogo). No hay ruta HTTP nueva.
- **Migración/configuración:** `0002_e01_ventas` sucede a `0001c_motor`. Para carga explícita local, desde `backend/`: `python -m app.modules.ventas.cargar_piloto --productos ../foodsave-ml/lista_productos_precios_limpia.md --ventas ../foodsave-ml/bakery_sales_limpio_final.csv --clave piloto-bakery-v1`. Requiere `DATABASE_URL` y upgrade previo.
- **Pruebas ejecutadas:** comprobación estándar del CSV y lista: 230200 líneas, 139 SKU en ambos archivos, 1264 líneas negativas, 600 fechas; la agregación de las 228936 líneas no negativas produce 27740 pares SKU/fecha. `python -m compileall` correcto y `git diff --check` sin errores. `pytest`/Alembic/PostgreSQL no ejecutados: faltan dependencias Python y Docker en este entorno. La prueba de frontera fue escrita, no ejecutada.
- **Qué necesita el siguiente desarrollador y quién es:** Kevin consume `leer_historial` y `resolver_sku` para K02/K03; Edu continúa E02/E03 y conecta el mismo servicio a la transacción de primera carga. Axel coordina la cadena de migraciones posterior.
- **Dependencias/bloqueos:** verificar upgrade real y prueba de frontera; las funciones no hacen commit. Primera carga de recetas/stock depende de Max y Vera.
- **Siguiente paso concreto:** ejecutar Alembic y prueba de frontera con el runtime backend, comprobar carga piloto y registrar resultado; después Kevin integra K02.
- **Commit/PR:** cambios locales, sin commit.

### Preparación del registro

- **Autor:** IA que preparó el reparto y guías, sin atribuir implementación a Edu Sanchez.
- **Cambio:** se definieron las tareas y el lugar de documentación; no se implementó lógica de este bloque en esta entrega documental.
- **Pruebas:** la revisión de documentación comprueba enlaces, cobertura de carpetas y coherencia del reparto; no acredita funcionamiento del módulo.
- **Próximo autor:** registrar el primer avance con la [plantilla](README.md) y actualizar el resumen vigente.

