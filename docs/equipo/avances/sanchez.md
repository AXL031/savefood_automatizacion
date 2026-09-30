# Avances — Edu Sanchez

**Responsable:** Edu Sanchez. **Bloque:** Inicialización, productos, ventas y estructura visual compartida. **Rama prevista:** `sanchez`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md). Este archivo se actualiza al terminar cada avance significativo.

## Resumen vigente

- **Frontera E02/E03 verificada (2026-09-30):** Codex para Axel conectó `ServicioRecetasM01` y `ServicioInventarioV01` de la entrega de Rojas. La API completa termina en DATOS_CARGADOS con pendiente_de vacío; error de stock revierte también catálogo/ventas/recetas. Verificado en SQLite; PostgreSQL pendiente de CI. El piloto conserva su ruta y reserva de PREPARAR_MODELO; el disparador ML del asistente completo sigue pendiente.

- **Estado:** E01 amplía API HTTP; E02 y E03 implementados con pruebas en SQLite; E04 entrega los primitivos compartidos y las tres pantallas propias. `0004_e03_inicializacion` ya se aplicó en PostgreSQL local; la carga completa depende de Max (M01) y Vera (V01).
- **Punto de partida alcanzado:** lectores XLSX y CSV con encabezados exactos, adaptador del CSV de tickets del piloto, validación que reúne todos los errores por archivo y fila, vista previa que no escribe, carga atómica, estado durable `configuracion_inicial` con sus transiciones, y API de inicialización, productos y ventas.
- **Contrato disponible:** [contrato de servicios E01–E03](../../api/contratos.md#inicialización--ventas-y-catálogo), [contrato de primera carga](../../api/contrato-importaciones.md) y [esquema objetivo](../../base_de_datos/esquema-objetivo-mvp.md).
- **Entrega a consumidores:** Kevin sigue usando `leer_historial`, `listar_skus_bakery`, `nombres_productos` y `limites_historial`, y ahora puede leer el estado con `hay_datos_cargados(sesion)` y mover la transición con `marcar_entrenando` / `marcar_modelo_listo` / `marcar_fallo_entrenamiento`. Max y Vera tienen los puertos `ServicioRecetas` y `ServicioInventario`, que la carga invoca dentro de la misma sesión. Todos pueden reutilizar `components/forms`, `components/tables/TablaDatos` y `components/ui`.
- **Bloqueos:** La carga completa necesita los servicios de Max y Vera; sin ellos la instalación queda en `PENDIENTE` con constancia de qué falta. Falta una prueba de confirmación completa en PostgreSQL con esos servicios.
- **Siguiente paso:** conectar los servicios de Max y Vera y comprobar la confirmación completa en PostgreSQL.

| Tarea | Estado de seguimiento |
|---|---|
| E01 · Definir y cargar productos y ventas | LISTO_PARA_INTEGRAR: CSV piloto verificado en PostgreSQL; rutas generales probadas en SQLite y expuestas en Docker |
| E02 · Construir asistente XLSX/CSV | LISTO_PARA_INTEGRAR: lectores, adaptador bakery, validación, vista previa y carga atómica |
| E03 · Preparar primera inicialización | LISTO_PARA_INTEGRAR: `configuracion_inicial`, migración `0004` y transiciones |
| E04 · Entregar pantallas y piezas comunes | LISTO_PARA_INTEGRAR: primitivos compartidos, navegación y pantallas de carga, productos y ventas |

## Bitácora

### Integración coordinada de entregas Rojas/Aguirre · 30-09-2026

- **Fecha/zona y autor:** 2026-09-30, America/Bogota. Codex a solicitud de Axel Cueva, coordinación transversal A04; se conserva autoría original de Max/Leonardo y la entrega delegada registrada en [Vera](vera.md).
- **Estado:** integración local verificada en SQLite; LISTO_PARA_INTEGRAR en Git, PostgreSQL/Redis y revisión remota pendientes. No declara completa la demo.
- **Comportamiento:** Codex para Axel conectó `ServicioRecetasM01` y `ServicioInventarioV01` de la entrega de Rojas. La API completa termina en DATOS_CARGADOS con pendiente_de vacío; error de stock revierte también catálogo/ventas/recetas. Verificado en SQLite; PostgreSQL pendiente de CI. El piloto conserva su ruta y reserva de PREPARAR_MODELO; el disparador ML del asistente completo sigue pendiente.
- **Archivos/contrato:** [contratos](../../api/contratos.md), [importaciones](../../api/contrato-importaciones.md), [pedidos](../../api/contrato-pedidos.md), rutas de inicialización/ingredientes/recetas/inventario/proveedores, `backend/migrations/env.py`, nuevas revisiones 0005/0006/0007 y `backend/tests/integration/test_api_inicializacion_ventas.py`, `test_proveedores_l01.py`, `test_migraciones_entregas.py`, `test_inventario_concurrencia_pg.py`. Enlaces de coordinación: [Axel](cueva.md), [Max](rojas.md), [Vera](vera.md), [Aguirre](aguirre.md), [Edu](sanchez.md).
- **Ejemplo público:** POST autenticado `/api/v1/inicializacion/confirmar` con los cinco CSV y fechas válidas devuelve DATOS_CARGADOS; POST administrativo `/api/v1/proveedores/{id}/ofertas` exige ingrediente existente y conversión explícita. Servicios participantes hacen flush, el llamador confirma.
- **Migraciones/configuración:** continuar desde 0004 con 0005→0006→0007; registrar todos los modelos, incluido ConfiguracionInicial. Revisiones previas conservadas. Para concurrencia activar V02_POSTGRES_TEST=1 sobre esquema de pruebas aislado; no habilitar Telegram ni cambiar modo automático.
- **Pruebas realmente ejecutadas:** `.venv/Scripts/python.exe -m pytest backend/tests foodsave-ml/tests -q` → 112 passed, 10 skipped (8 A03 y 2 V02 por PostgreSQL/Redis), 6 subtests passed. `npm run typecheck` y `npm run build` correctos. Delta 0004→0007 arriba/abajo/arriba y comparación de metadatos en SQLite correctos; el índice de expresión del núcleo no se puede reflejar en SQLite. Docker Desktop no logró arrancar; CI incorpora alembic check y concurrencia V02. No se ejecutaron envíos externos.
- **Dependencias y siguiente paso:** revisión de la entrega conjunta y CI PostgreSQL; después integrar a main. Max continúa M02/M03; Aguirre completa adaptador/UI L01 y L02–L04; Vera V03; Edu/Kevin/Axel conectan ML desde asistente completo.
- **Commit/PR:** cambios locales en cueva; publicación de PR de integración pendiente.


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

### Coordinación de integración del asistente y piloto en `cueva`

- **Fecha y autor:** 2026-09-29 (America/Lima), Codex a solicitud de Axel Cueva; esta entrada no atribuye la edición a Edu Sanchez.
- **Tareas y estado:** E02–E04 conservados desde `origin/main`; piloto bakery preservado como ruta separada. La integración de Max y Vera sigue pendiente.
- **Comportamiento disponible:** el asistente completo mantiene vista previa, confirmación, productos y ventas. `piloto.py` conserva la carga rápida e idempotente del CSV existente y la reserva `PREPARAR_MODELO`; la página `/inicializacion/piloto` la consume. El catálogo curado se encuentra también dentro de Docker.
- **Archivos y contrato:** `backend/app/modules/inicializacion/{rutas,servicio,piloto}.py`, `frontend/src/app/inicializacion/{page,piloto/page}.tsx`; [contratos](../../api/contratos.md) y [guía local](../../../backend/app/modules/inicializacion/GUIA_DESARROLLO.md).
- **Configuración/migración:** `0004_e03_inicializacion` sucede a `0003_pronosticos`. La carga rápida no cambia el estado de `configuracion_inicial`.
- **Pruebas y siguiente paso:** 79 pruebas correctas, 8 omitidas y 6 subpruebas correctas en el entorno Python local (se excluyó la evaluación que requiere CatBoost local); `npm run typecheck` y `npm run build` correctos. Docker aplicó `0004_e03_inicializacion`; antes y después conservó 139 productos, 27 740 ventas y 2 modelos. El catálogo curado en `/code` devolvió 139 SKU; OpenAPI expone asistente y piloto, y ambas páginas respondieron 200. Conectar los puertos de Max y Vera sin alterar el flujo piloto. Commit/PR aún pendientes en el momento de esta entrada.

### E02, E03 y E04 · Asistente de primera carga, estado durable y piezas visuales

- **Fecha/hora y zona:** 2026-09-29 (America/Bogota).
- **Autor y responsable del bloque:** IA de la sesión, trabajando en el bloque asignado a Edu Sanchez a pedido del usuario; no atribuye la implementación a Edu.
- **Tareas:** E02, E03, E04 y ampliación de E01 con rutas HTTP.
- **Estado:** LISTO_PARA_INTEGRAR en SQLite; sin verificar en PostgreSQL.
- **Qué cambió y qué comportamiento está disponible:**
  - Lectores de los dos libros XLSX o los cinco CSV, con encabezados exactos, columnas opcionales del contrato y rechazo de columnas no previstas.
  - Adaptador del CSV real de tickets (`date,time,ticket_number,article,Quantity,unit_price`): valida cada artículo contra `lista_productos_precios_limpia.md`, excluye las líneas negativas informando cuántas y agrega por fecha y artículo. Sobre el archivo del piloto reproduce las cifras del importador de E01: 230 200 líneas leídas, 1 264 negativas, 228 936 aceptadas, 27 740 ventas diarias y 139 artículos.
  - Validación que reúne **todos** los problemas con su archivo y número de fila en lugar de detenerse en el primero, y rechaza el lote entero si queda uno. Cubre SKU sin producto, pareja fecha/SKU repetida, unidades negativas, decimales fuera de la unidad base, límite de venta posterior a la caducidad, producto de demo sin receta y ausencia de fila de stock, que significa desconocido y no cero.
  - Vista previa que no escribe nada: filas por hoja, fechas cubiertas, productos de demo, huellas y errores ubicados.
  - Carga atómica en una sola sesión, con huella de solicitud que reconoce un reintento idéntico y no duplica.
  - `configuracion_inicial` con los cinco estados y sus transiciones; un fallo de entrenamiento vuelve a `DATOS_CARGADOS` sin recargar datos.
  - Puertos `ServicioRecetas` (Max) y `ServicioInventario` (Vera). Mientras no existan, la carga persiste catálogo y ventas y deja la instalación en `PENDIENTE` con el detalle de qué falta, en lugar de declararla inicializada.
  - API nueva: `GET /inicializacion/estado`, `POST /inicializacion/vista-previa`, `POST /inicializacion/confirmar`, `GET /productos`, `GET /ventas`, `GET /ventas/{id}/revisiones` y `PATCH /ventas/{id}`.
  - Frontend: `components/forms` (campo base, texto, fecha, archivo, select, botón sin doble envío y resumen de errores), `TablaDatos` genérica, `ValorOpcional` para distinguir ausente de cero, `PasosAsistente`, tono de éxito en `EstadoPanel`, grupo «Datos» en la navegación y `enviarFormulario` multipart en el cliente HTTP común. Pantallas de primera carga, productos y ventas contra la API real.
- **Archivos clave:** `backend/app/modules/inicializacion/{lectores,validacion,adaptador_bakery,modelos,puertos,servicio,rutas}.py`, `backend/migrations/versions/0004_e03_inicializacion.py`, `backend/app/modules/{productos,ventas}/rutas.py`, `frontend/src/app/{inicializacion,productos,ventas}/page.tsx`, `frontend/src/components/{forms,tables,ui}`.
- **Contrato/función/ruta y ejemplo de uso:** `POST /api/v1/inicializacion/vista-previa` (Administrador, multipart con `archivos`, `fecha_objetivo_demo` y `fecha_referencia_stock`) devuelve `datos.aceptable`, `datos.errores[]` con `campo` en forma `archivo:fila/columna` y `datos.huellas.solicitud`. `POST /api/v1/inicializacion/confirmar` añade `clave_importacion` y devuelve `datos.estado` y `datos.pendiente_de[]`. Para Kevin: `hay_datos_cargados(sesion)` y `marcar_entrenando(sesion)`.
- **Migración/configuración necesaria:** `0004_e03_inicializacion` sucede a `0003_pronosticos` y crea la fila única en `PENDIENTE`. Se declararon en `backend/pyproject.toml` las dependencias de este bloque: `openpyxl` para XLSX y `python-multipart` para la subida. Axel coordina el archivo; la dependencia es de E02.
- **Pruebas:** `PYTHONPATH=backend python -m pytest backend/tests foodsave-ml/tests -q --ignore=foodsave-ml/tests/test_evaluacion_k03.py` → **77 passed, 8 skipped**, incluidas 12 pruebas nuevas de E02/E03 y 8 de la API. `npx tsc --noEmit` sin errores y `npm run build` correcto con 13 rutas. Límites del entorno: `catboost` no está instalado, por lo que `test_evaluacion_k03.py` no se ejecutó; Alembic y PostgreSQL **no** se ejecutaron, así que `0004` está sin aplicar; el adaptador se comprobó contra el CSV real del piloto, pero la carga completa no se probó de extremo a extremo por falta de los servicios de Max y Vera.
- **Qué necesita el siguiente desarrollador y quién es:** Max implementa `ServicioRecetas` y Vera `ServicioInventario` según `backend/app/modules/inicializacion/puertos.py`; ambos reciben la sesión abierta y no hacen commit. Kevin puede sustituir `ML_COMERCIO_ID`/`ML_SUCURSAL_ID` por la lectura del estado. Axel revisa la cadena de migraciones y las dos dependencias añadidas.
- **Dependencias/bloqueos y responsable:** Docker y PostgreSQL en esta PC (Edu); recetas y apertura de lotes (Max y Vera).
- **Siguiente paso concreto:** aplicar `alembic upgrade head` en PostgreSQL y repetir la carga del piloto por la API; después conectar los dos puertos.
- **Commit/PR:** cambios locales, sin commit.

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

