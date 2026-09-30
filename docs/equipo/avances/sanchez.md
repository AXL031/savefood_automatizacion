# Avances — Edu Sanchez

**Responsable:** Edu Sanchez. **Bloque:** Inicialización, productos, ventas y estructura visual compartida. **Rama prevista:** `sanchez`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md). Este archivo se actualiza al terminar cada avance significativo.

## Resumen vigente

- **Estado:** E01 verificado con el CSV piloto en PostgreSQL; E02/E03 tienen un corte web parcial que carga el CSV bakery y reserva el entrenamiento en la misma transacción. El asistente completo y E04 siguen pendientes.
- **Punto de partida alcanzado:** Catálogo bakery desde la lista curada, mapeo de 139 SKU, carga agregada de 27 740 ventas diarias, revisiones y lectura temporal pública sin inferir ceros ausentes. La página `/inicializacion` sube el CSV y muestra ejecución, con reintento ML; la versión nueva `q65v2` permite entrenar el modelo corregido sin duplicar ventas. No hay XLSX, recetas, stock inicial ni API general de ventas.
- **Contrato disponible:** [contrato de servicios E01](../../api/contratos.md#inicialización--ventas-y-catálogo) y [esquema objetivo](../../base_de_datos/esquema-objetivo-mvp.md).
- **Entrega a consumidores:** Kevin usa `listar_skus_bakery`, `nombres_productos`, `limites_historial` y `leer_historial`; la carga web en PostgreSQL disparó K01/K03 y produjo 92 corridas y 4 047 evaluaciones. Max y Vera aún deben entregar recetas y apertura de lotes para la primera inicialización completa.
- **Bloqueos:** el corte web solo acepta CSV bakery; falta validar dos XLSX o cinco CSV, orquestar Max/Vera, guardar `configuracion_inicial` y entregar ventas/productos generales.
- **Siguiente paso:** Edu completa E02/E03 y las rutas/pantallas de E01/E04 sin sustituir la lectura temporal ya consumida por Kevin.

| Tarea | Estado de seguimiento |
|---|---|
| E01 · Definir y cargar productos y ventas | EN_CURSO: corte bakery verificado en PostgreSQL; faltan API/pantallas generales |
| E02 · Construir asistente XLSX/CSV | EN_CURSO: subida web del CSV bakery, sin asistente completo |
| E03 · Preparar primera inicialización | EN_CURSO: reserva ML tras CSV piloto, sin estado ni carga total |
| E04 · Entregar pantallas y piezas comunes | PENDIENTE DE VERIFICAR / COMPLETAR |

## Bitácora

### E03 parcial · Versión nueva del entrenamiento del CSV piloto

- **Fecha/hora y zona:** 2026-09-29 (America/Lima).
- **Autor y responsable del bloque:** Codex por solicitud de Axel, editando la frontera de Edu Sanchez con el modelo de Kevin; no atribuye el cambio a Edu.
- **Tareas y estado:** E03 parcial, EN_CURSO; primera inicialización completa pendiente.
- **Comportamiento disponible:** la ruta del CSV genera `piloto-q65v2-<huella>` y otra clave de `PREPARAR_MODELO` para aplicar la corrección de Kevin. La misma importación de ventas se recupera; versiones y evaluaciones anteriores permanecen. El sistema ya entrenó y evaluó esa nueva versión en PostgreSQL sin volver a cargar ventas.
- **Archivos clave:** `backend/app/modules/inicializacion/rutas.py`, `backend/tests/integration/test_carga_csv_piloto.py`, [cambio de Kevin](bohorquez.md).
- **Contrato/ejemplo:** repetir el CSV anterior devuelve `repetida=true`, sin crear ventas nuevas, y usa la ejecución de `piloto-q65v2-*` dentro de la política actual; ver [contrato](../../api/contrato-importaciones.md#acceso-rápido-del-piloto-implementado).
- **Configuración/migraciones:** ninguna nueva; no se reescribieron las migraciones ni se borraron datos.
- **Pruebas ejecutadas:** test de carga web 2 passed; suite backend 27 passed, 8 skipped, 6 subtests passed. La preparación y el backtest de la nueva versión terminaron en Compose con 4 047 pares evaluables; falta el recorrido E03 completo.
- **Dependencias y siguiente paso:** Edu completa asistente XLSX/CSV, estado de inicialización y servicios de Max/Vera; Kevin mantiene la política y sus versiones.
- **Commit/PR:** commit local de `cueva`; push pendiente por Axel.

### E01–E03 · Carga web del CSV piloto y preparación real en PostgreSQL

- **Fecha/hora y zona:** 2026-09-29 (America/Lima).
- **Autor y responsable del bloque:** Codex por solicitud de Axel, trabajando en el bloque de Edu Sanchez; no atribuye estas ediciones a Edu.
- **Tareas y estado:** E01 verificado en PostgreSQL; E02/E03 parciales, EN_CURSO.
- **Comportamiento disponible:** `POST /inicializacion/piloto-bakery` recibe multipart de Administrador, limita a 25 MB, carga el catálogo curado y ventas agregadas, y reserva `PREPARAR_MODELO` en un commit. La misma huella recupera importación/ejecución sin duplicar. La página permite subir el archivo, consultar el estado y reintentar preparación fallida sin recargar ventas. El CSV no se copia a la imagen Docker.
- **Archivos clave:** `backend/app/modules/inicializacion/rutas.py`, `frontend/src/app/inicializacion/page.tsx`, `frontend/src/services/inicializacion.ts`, `backend/tests/integration/test_carga_csv_piloto.py`.
- **Contrato/ejemplo:** `POST /api/v1/inicializacion/piloto-bakery`, campo `archivo` con el CSV bakery; devuelve `importacion_id`, conteos, `version_modelo` y `ejecucion_id`. Ver [contrato de importaciones](../../api/contrato-importaciones.md#acceso-rápido-del-piloto-implementado).
- **Configuración/migraciones:** se añadió `python-multipart`; usa `0002_e01_ventas` y `0003_pronosticos` ya existentes. No se alteraron migraciones.
- **Pruebas ejecutadas:** prueba enfocada `test_carga_csv_piloto.py` y frontera E01: 4 passed; suite backend: 27 passed, 8 skipped, 6 subtests passed. `npm run typecheck` y `npm run build` correctos. Subida real por HTTP a PostgreSQL: 139 productos, 228 936 líneas aceptadas, 1 264 negativas excluidas y 27 740 ventas diarias; repetición mantuvo una importación y la misma ejecución. Worker completó preparación y backtest: 1 modelo, 92 corridas y 4 047 evaluaciones; API de evaluación devolvió 4 047 pares. La suite combinada `backend/tests foodsave-ml/tests` no pudo recolectarse en `.venv` porque allí falta CatBoost; el flujo ML real sí se ejecutó en Docker. No se probó asistente XLSX ni integración con recetas/stock.
- **Dependencias:** Max entrega recetas, Vera apertura de lotes; Kevin mantiene el modelo y Max aún debe consumir su corrida en el plan.
- **Siguiente paso concreto:** completar validación/vista previa XLSX y CSV general, estado `configuracion_inicial` y carga atómica con los servicios de Max y Vera.
- **Commit/PR:** incluido en el commit local de `cueva`; push pendiente por Axel.

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

