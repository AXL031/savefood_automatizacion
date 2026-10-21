# Avances — Max Rojas

**Responsable:** Max Rojas. **Bloque:** Ingredientes, recetas y planificación. **Rama prevista:** `rojas`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md). Este archivo se actualiza al terminar cada avance significativo.

## Resumen vigente

- **21-10-2026 · Max Rojas con Claude Code, T02 (backend real):** inicio de sesión con Google implementado (migración `0019_tienda_clientes`, `/api/v1/tienda/sesion*`). Requiere `GOOGLE_CLIENT_ID` en `.env` ([guía](../../api/configurar-google-tienda.md)); sin él la tienda sigue con login simulado. Catálogo, stock y pedidos siguen de ejemplo.
- **21-10-2026 · Max Rojas con Claude Code, T02–T05 (interfaz):** tienda del cliente en `/tienda` desde el Figma «PaginaCliente»: inicio, menú, canasta y pago simulado, confirmación y mis pedidos. **Funciona con datos de ejemplo en el navegador**; backend T01–T04 pendiente. Ver bitácora del 21-10-2026.
- **20-10-2026 · Max Rojas con Claude Code, T01–T05 (diseño):** documentada la tienda del cliente: [ADR-009](../../arquitectura/decisiones/ADR-009-tienda-cliente.md), [contrato](../../api/contrato-tienda.md), ampliación en la guía de alcance, regla de stock en AGENTS.md y tareas en responsabilidades. **Sin código, migración ni pantalla.** Siguiente paso: revisión de Vera/Edu/Axel y luego migración `0019_tienda`.
- **14-10-2026 · Max Rojas (frontend y UX/UI temporal):** paleta hoja/yema y tipografía Bricolage + Manrope aplicadas en todo el frontend, login rediseñado con ilustración de panadería y textos de demostración/escenario/manual retirados de la interfaz. Ver bitácora del 14-10-2026.
- **11-10-2026 · Codex para Axel, M02/M04 y consumo K02/V02/L02:** M01–M04 están implementadas localmente; el flujo consume corrida, recetas y stock, conserva plan/necesidades y enlaza pedidos. El manejador usa el modelo elegido por el asistente. Margen cero, cantidades desconocidas nullable, versiones e inventario conservados.
- **Estado:** implementación real integrada en la instalación local. Consumidores de Promociones/motor/inventario verificados con PostgreSQL/Redis y navegación QA aislada; migración 0015 aplicada. CI remoto, otro PC y nuevo Telegram real no acreditados; ver entrada más reciente.
- **Contrato:** [flujo y promociones](../../api/contrato-flujo-promociones.md). Migración aditiva `0015_flujo_promociones` sobre 0014; conservar revisiones aplicadas.
- **Coordinación/dependencias:** Kevin, Vera y Aguirre por interfaces públicas; Cueva coordina. [Registro transversal](cueva.md) y [plan vigente](../plan-cierre-prototipo.md). Autor real de este corte: Codex para la solicitud de Axel; no se atribuye a integrantes.
- **Siguiente paso:** revisar los cambios locales y completar CI remoto, reproducción en otra PC y prueba Telegram real autorizada. La instalación habitual ya está actualizada y activa. Cambios locales, sin commit ni publicación.

## Bitácora

### 21-10-2026 America/Lima — Logo de la tienda

- **Autor y responsable:** Max Rojas, con Claude Code. Bloque Tienda (interfaz).
- **Qué cambió:** ilustración entregada por Max recortada en círculo con fondo transparente (`frontend/public/tienda/logo.png` 512 px, `logo-192.png` e `icono.png` 64 px para la pestaña). [LogoTienda.tsx](../../../frontend/src/tienda/componentes/LogoTienda.tsx) reemplaza el sello de huella del prototipo en encabezado, pie, login, portada, canasta, consejo del menú y «Horneado del día».
- **Pruebas:** typecheck, imagen de Docker reconstruida y revisión visual en Chrome headless (encabezado, portada, login y pie).
- **Commit/PR:** cambios locales, sin commit.

### 21-10-2026 America/Lima — Pago con tarjeta y retiro de rótulos de simulación

- **Autor y responsable:** Max Rojas, con Claude Code. Tarea T04 (interfaz).
- **Estado:** interfaz real; pago simulado.
- **Qué cambió:** se retiraron los rótulos «Pago simulado» del checkout, el total, la confirmación, el detalle del pedido y el pie. Con tarjeta, [FormularioTarjeta.tsx](../../../frontend/src/tienda/componentes/FormularioTarjeta.tsx) pide número, titular, vencimiento y CVV con validación local. Esos valores solo viven en memoria, no viajan en `confirmarPedido` y se borran al confirmar. AGENTS.md, ADR-009 y el contrato se actualizaron con esta regla.
- **Pruebas ejecutadas:** typecheck y recorrido en Chrome headless (ver resumen de la respuesta).
- **Commit/PR:** cambios locales, sin commit.

### 21-10-2026 America/Lima — T02: sesión de clientes con Google

- **Autor y responsable:** Max Rojas, con Claude Code. Tarea T02.
- **Estado:** LISTO_PARA_INTEGRAR en código; conexión con una cuenta real pendiente del ID de cliente OAuth del usuario.
- **Qué cambió:** módulo [backend/app/modules/tienda](../../../backend/app/modules/tienda/GUIA_DESARROLLO.md) con tabla `cliente`, verificación del ID token con las claves públicas de Google mediante PyJWT (sin dependencias nuevas), token propio con audiencia `tienda` y clave distinta de la administrativa. El frontend muestra el botón oficial de Google cuando existe `NEXT_PUBLIC_GOOGLE_CLIENT_ID`. Se retiraron las etiquetas «Stock actualizado en vivo» y «Aprobadas por la pastelería» del menú.
- **Migración/configuración:** `0019_tienda_clientes` aditiva sobre 0018. `GOOGLE_CLIENT_ID` en `compose.yaml` (API y argumento de build del frontend), `frontend/Dockerfile` y `.env.example`; `TIENDA_JWT_SECRET` opcional. Puente `conciliar_local.py` y pruebas de cabeza de migraciones actualizados a 0019 (archivos de coordinación de Axel).
- **Pruebas ejecutadas:** `test_tienda_sesion.py` (4), `test_migraciones_entregas.py` y `test_usuarios.py` en SQLite: 14 correctas, 1 omitida. Con PostgreSQL (`E03_POSTGRES_TEST=1`): tienda, conciliación de migraciones y usuarios, 11 correctas. Typecheck del frontend correcto. Suite completa en PostgreSQL: 251 correctas, 12 omitidas y 13 fallos por montar solo `backend/` (faltaba `foodsave-ml`); al repetir esos 6 módulos con `foodsave-ml` montado, 44/44 correctas. Migración 0019 aplicada en la instalación local.
- **Dependencias:** el usuario crea el ID de cliente en Google Cloud con origen `http://localhost:3000`. Axel revisa los cambios de `compose.yaml` y del puente.
- **Siguiente paso:** cargar `GOOGLE_CLIENT_ID`, reconstruir y probar con una cuenta real; luego T01/T03.
- **Commit/PR:** cambios locales, sin commit.

### 21-10-2026 America/Lima — Interfaz de la tienda del cliente

- **Autor y responsable:** Max Rojas, con Claude Code. Tareas T02–T05 (interfaz); T01 sin implementar.
- **Estado:** PARCIAL. Interfaz real; datos **simulados** (modo ejemplo en el navegador). Backend, migración `0019_tienda` y Google real pendientes.
- **Qué cambió:** carpetas nuevas `frontend/src/app/tienda/` (rutas `/tienda`, `/tienda/menu`, `/tienda/carrito`, `/tienda/pedido/[id]`, `/tienda/pedidos`, layout y `tienda.css`) y `frontend/src/tienda/` (tipos, servicios, contexto, componentes). Diseño del Figma con la marca Pastelería Maria Juanita, una sucursal en Lima y sin reseñas, 2×1, seguimiento, recojo, boleta ni boletín. Stock en tres estados, consulta cada 5 s. Pago simulado con tarjeta o Yape/Plin (QR y número ficticios rotulados). Login con Google: botón oficial en modo api; en modo ejemplo pide un correo Gmail y lo rotula como simulado.
- **Contrato:** [contrato-tienda.md](../../api/contrato-tienda.md) amplía la ficha del producto (categoría, descripción, presentación, imagen), añade `POST /tienda/carrito/cotizar` y cambia `precio_esperado` por `subtotal_esperado` por línea, porque una línea puede mezclar unidades con y sin promoción.
- **Compartidos tocados:** [ProtectedShell.tsx](../../../frontend/src/components/layout/ProtectedShell.tsx) (una línea: las rutas `/tienda` no exigen sesión administrativa; carpeta coordinada por Edu) y `frontend/package.json` (+ `@fontsource-variable/newsreader` y `@fontsource-variable/plus-jakarta-sans`). Imágenes y SVG del Figma en `frontend/public/tienda/` (capturas con la marca del mockup descartadas o recortadas).
- **Pruebas ejecutadas:** `npx tsc --noEmit` y `npm run build` correctos (27 rutas). Recorrido en Chrome headless contra `next start`: agregar 3 brioche y 2 croissant, confirmar sin sesión abre login, login simulado, 4 errores de entrega visibles, pedido #1001 confirmado, brioche pasa de Últimas unidades a Agotado, ninguna cantidad en el DOM y sin scroll horizontal a 390 px. Sin pruebas automatizadas en el repositorio (el frontend no tiene runner).
- **Dependencias:** backend T01–T04 propio; revisión de Vera (inventario/promociones), Edu (productos y `ProtectedShell`) y Axel (token de cliente, variables, Compose).
- **Siguiente paso:** migración `0019_tienda` y backend T01/T03 (precios, ficha, catálogo, stock, cotización); luego T02 y T04.
- **Commit/PR:** cambios locales, sin commit.

### 20-10-2026 America/Lima — Diseño de la tienda del cliente

- **Autor y responsable:** Max Rojas, con Claude Code. Tareas T01–T05 (nuevas, bloque Tienda).
- **Estado:** PENDIENTE de implementación; documentación lista para revisión.
- **Qué cambió:** decisión y contrato de una tienda separada (`/api/v1/tienda/*` y `/api/v1/tienda-admin/*`): login con Google, precios en PEN por CSV o manual, stock visible en tres estados, compra con pago simulado (tarjeta, Yape o Plin) y datos de entrega que termina en pedido `CONFIRMADO` (estados posteriores y cancelación quedan como desarrollo futuro), descuento por lote FEFO con `VENTA_TIENDA`, reserva de `EVALUAR_PROMOCION` en la misma transacción y promociones visibles solo tras aprobación. Compras de tienda fuera de Ventas/ML. Reloj de tienda por escenario o fecha actual, con apertura de lotes nuevos.
- **Archivos clave:** [ADR-009](../../arquitectura/decisiones/ADR-009-tienda-cliente.md), [contrato-tienda.md](../../api/contrato-tienda.md), [guía de alcance](../../guia-inicio-desarrollo.md), [AGENTS.md](../../../AGENTS.md), [responsabilidades](../responsabilidades.md), [errores](../../api/errores.md).
- **Migración/configuración:** ninguna aplicada. Prevista `0019_tienda` aditiva; variables futuras `GOOGLE_CLIENT_ID` y `TIENDA_JWT_SECRET`.
- **Pruebas:** no aplica (solo documentación); no se ejecutaron pruebas.
- **Dependencias:** Vera revisa las funciones nuevas de Inventario/Promociones; Edu, el alta manual de producto; Axel, el token de cliente y las variables. Registrar cliente OAuth de Google para `http://localhost:3100`.
- **Siguiente paso:** acordar el contrato con los dueños de frontera, crear las carpetas `tienda` con su guía y empezar por T01 (migración y precios).
- **Commit/PR:** cambios locales, sin commit.

### 14-10-2026 America/Lima — Identidad visual, login y textos de producto

- **Autor/responsabilidad/tareas:** Max Rojas, a cargo temporal del frontend y UX/UI. Toca la estructura visual compartida (Edu Sanchez) y la pantalla de acceso (Axel Cueva): coordinar antes de integrar.
- **Estado/comportamiento:** real, solo interfaz. Paleta en variables `:root`; fuentes autoalojadas; `badge-advertencia` y tonos de estado corregidos; login nuevo con `public/imagenes/panaderia-login.jpg` y `MarcaFoodSave`; se eliminó `GuiaPantalla` y se reescribieron textos de demostración, escenario, piloto, instalación local y API. Sin cambios en contratos, campos ni rutas de API.
- **Archivos clave:** [styles.css](../../../frontend/src/app/styles.css), [iniciar-sesion](../../../frontend/src/app/iniciar-sesion/page.tsx), [ProtectedShell](../../../frontend/src/components/layout/ProtectedShell.tsx), [MarcaFoodSave](../../../frontend/src/components/ui/MarcaFoodSave.tsx), [estados.ts](../../../frontend/src/utils/estados.ts), [especificación visual](../../diseno/especificacion-visual.md).
- **Configuración:** nuevas dependencias `@fontsource-variable/manrope` y `@fontsource-variable/bricolage-grotesque` (reconstruir la imagen del frontend con `iniciar-foodsave.cmd -Build`). Sin migraciones.
- **Pruebas realmente ejecutadas:** `npm ci` y `next build` correctos (compila y valida tipos); capturas Playwright de `/iniciar-sesion` (escritorio, móvil y error) e `/ingredientes` con API simulada. `tsc --noEmit` mantiene el error previo TS2882 sobre `./styles.css`. No se probó contra la API real ni en Docker.
- **Pendiente:** el backend sigue anteponiendo «DEMOSTRACIÓN — NO SURTIR» a los mensajes de Telegram (regla de seguridad del equipo); quitarlo requiere acuerdo y cambio en backend.
- **Git:** cambios locales, sin commit/push/PR.

### 11-10-2026 19:28 America/Lima — Promociones, flujo configurable y claridad

- **Autor/responsabilidad/tareas:** Codex para Axel; M02/M04 y consumo K02/V02/L02. Coordinación transversal en Cueva, dominios afectados enlazados desde dependencias.md.
- **Estado/comportamiento:** implementación LOCAL real. M01–M04 están implementadas localmente; el flujo consume corrida, recetas y stock, conserva plan/necesidades y enlaza pedidos. El manejador usa el modelo elegido por el asistente. Margen cero, cantidades desconocidas nullable, versiones e inventario conservados.
- **Archivos clave:** [manejadores.py](../../../backend/app/modules/planificacion/manejadores.py); [flujo.py](../../../backend/app/modules/automatizaciones/flujo.py). [Contrato y ejemplos públicos](../../api/contrato-flujo-promociones.md).
- **API/ejemplo:** guardar parámetros no agenda ni autoriza envíos. POST /flujo-automatizacion/programar conserva modelo/modo y crea calendario finito. PUT /promociones/regla habilita una versión; un ajuste nuevo reserva evaluación en su misma sesión. GET /promociones/evaluaciones devuelve motivo y referencias; acciones de gestión requieren Administrador, motivo y tarea sin despacho.
- **Migración/configuración:** `0015_flujo_promociones`; aplicar antes de reiniciar API/worker/Beat; ya aplicada en la instalación habitual. No reescribe 0014 ni tablas de otros cortes. Configuración sin tokens; no altera datos habituales ni ejecuta envíos reales.
- **Pruebas realmente ejecutadas:** suite amplia Windows: 255 passed, 24 skipped, 6 subtests passed, con una expectativa antigua de cabeza Alembic fallida y corregida; después 21 pruebas de flujo/migración/programación correctas. Build Next correcto (incluye /promociones). Corte final de fronteras: 72 passed, 2 skipped, 6 subtests passed. Revisión posterior de promociones/puente: 12 passed, 6 skipped (concurrencia/DDL PostgreSQL). Typecheck final correcto. QA Edge aislada verificó calendario de tres días, pausa, regla versionada, detalle/Escape, dos Excel/cinco CSV y móvil, sin errores JavaScript. Se corrigió una referencia visual de fecha detectada por build y se repitió QA correctamente; build final correcto, 23 páginas generadas; QA final también pasó contra la interfaz compilada, con datos cargados en escritorio y móvil. Después de que Axel abrió Docker, migración y alembic check correctos en PostgreSQL aislado. Corte amplio PostgreSQL/Redis inicial: 125 passed y 4 fallos; una prueba antigua del manejador ausente se aisló explícitamente, y los tres fallos ML se debían a escribir catboost_info en el montaje de código de solo lectura. Revalidación con imagen reconstruida: 24 passed de promociones/motor/inventario, incluida concurrencia, y 3 passed de CatBoost/Beat/plan real desde /tmp escribible. CI incorpora la nueva prueba concurrente. Suite completa final con imagen reconstruida y PostgreSQL/Redis: **283 passed, 6 subtests passed**, sin fallos ni omisiones (290,91 s). Advertencias existentes de dependencias y reflexión SQLite; migración y comparación PostgreSQL correctas. No se enviaron mensajes reales.
- **Dependencias y siguiente paso:** Kevin, Vera y Aguirre por interfaces públicas; Cueva coordina. Imágenes reconstruidas, 0015 aplicada y servicios habituales activos. Suite final completa correcta. Pendientes: CI remoto y demo conjunta/otra PC. La prueba Telegram automática requiere autorización concreta. No interpretar fixtures del modelo/Telegram como evidencia comercial ni de envío real.
- **Git:** cambios locales en cueva, sin commit/push/PR.

<details><summary>Resumen anterior conservado como historial; no es el estado vigente</summary>

- **Flujo completo y claridad transversal (30-09-2026, Codex para Axel):** Planificación y recetas muestran cantidades grandes en kg/L y etiquetas claras. Manejador consume el modo conservado de programación al generar compras. Mantiene snapshots, unidades base y política de stock/recetas; flujo completo verificado con PostgreSQL dentro de 54 pruebas correctas.
- **Paso 4 local (30-09-2026, Codex para Axel):** L01/L02 con UI /proveedores y /compras, generación desde necesidades M03, agrupación/conversión exacta, snapshots y política de una propuesta activa por fecha con cancelación explícita. GENERAR_PROPUESTA real llega a pedidos; API y motor consumen la entrega. Docker: 159 pruebas y 6 subpruebas correctas, más prueba adicional de recompra del motor correcta. Migración 0011/reversibilidad/alembic check y frontend typecheck/build correctos. Aprobación/Telegram siguen pendientes, sin envíos externos. Cambios locales sin commit ni remoto. [Contrato](../../api/contrato-pedidos.md#corte-l02-del-paso-4-local--30-09-2026).
- **Paso 3 local (30-09-2026, Codex para Axel):** M03 implementado: necesidades agregadas, faltantes nullable, trazas de recetas/lotes y API/UI. Consumido por API y GENERAR_PROPUESTA real; compras aún pendiente. Docker: 145 pruebas y 6 subpruebas correctas; migración 0010/reversibilidad/alembic check y frontend typecheck/build correctos. Cambios locales sin commit ni remoto. [Contrato M03](../../api/contratos.md#m03--paso-3-local-necesidades-y-faltantes-conservados).

- **Paso 2 local (2026-09-30, Codex para Axel):** M02 implementado y consumido por GENERAR_PROPUESTA; snapshots, estados nullable, recálculo, API/UI y evaluación posterior. Docker 140 pruebas + 6 subpruebas correctas; migración 0009 y frontend correctos. Sin commit ni cambios remotos. [Contrato](../../api/contratos.md#m02--paso-2-local-plan-reproducible). M03 pendiente; M04 parcial (trazas de productos disponibles, faltan insumos/pedidos).

- **Coordinación verificada (2026-09-30):** Codex para Axel concilió M01 y la entrega delegada V01/V02 con main en `cueva`. Reconstruyó las migraciones 0005/0006 a partir de los modelos publicados (no estaban en origin/rojas). Carga completa real, rollback de stock, versiones y migraciones delta verificadas en SQLite; PostgreSQL pendiente de CI. M02–M04 siguen pendientes; no se atribuye este trabajo de coordinación a Max.

- **Estado:** M01 disponible; M02 local LISTO_PARA_INTEGRAR por Codex para Axel. M03 local LISTO_PARA_INTEGRAR y M04 local con enlace y consumo de pedidos verificados. V01/V02 conservan autoría original por encargo de Leonardo Vera (ver [vera.md](vera.md)).
- **Disponible:** catálogo de ingredientes con unidad base, recetas versionadas, servicio de primera carga conectado al asistente de Edu y lectura versionada para el plan. Pantallas `/ingredientes` y `/recetas`.
- **Contrato:** [M01 en contratos.md](../../api/contratos.md#m01-disponible-ingredientes-y-recetas-versionadas-30-09-2026).
- **Para M02:** usar `recetas_activas(sesion, producto_ids)` y guardar `receta_id` en el plan; leer stock con `consultar_disponibilidad(sesion, fecha, producto_ids=…, ingrediente_ids=…)` y guardar su `huella`.
- **Bloqueos:** aprobar/enviar corresponde a L03; publicar los avances requiere permiso expreso de Axel.
- **Siguiente paso:** acompañar L03 preservando snapshots e identidad por fecha; L02 ya consume M03.

| Tarea | Estado de seguimiento |
|---|---|
| M01 · Implementar ingredientes y recetas | LISTO_PARA_INTEGRAR |
| M02 · Calcular plan de producción | LISTO_PARA_INTEGRAR LOCAL (Codex para Axel); consumidor automático probado |
| M03 · Calcular necesidades y faltantes | LISTO_PARA_INTEGRAR LOCAL; API/motor verificados |
| M04 · Entregar pantalla y contrato del plan | LISTO_PARA_INTEGRAR LOCAL; trazas y enlace a pedidos reales |

</details>



### Flujo completo, unidades y claridad · 30-09-2026

- **Fecha/zona/autor/estado:** 2026-09-30, America/Bogota. Codex para la tarea de Axel, bloque de rojas; coordinación transversal en [Cueva](cueva.md). LISTO_PARA_INTEGRAR local; consumo programado y outbox verificados en pruebas aisladas, sin atribuir autoría a integrantes.
- **Tareas/comportamiento:** M01/M02/M03 y consumidor A02/L03. generar_propuesta pasa contexto.parametros.modo_envio_pedidos a generar_pedidos. M03 no cambia cálculos ni ausencias; necesidades nullable siguen desconocidas. UI distingue producción sugerida, faltante, estado de pedido y envío; cantidades legibles conservan precisión y recetas versionadas.
- **Archivos clave:** [manejador](../../../backend/app/modules/planificacion/manejadores.py), [Planes](../../../frontend/src/app/planificacion/page.tsx), [Recetas](../../../frontend/src/app/recetas/page.tsx), [Ingredientes](../../../frontend/src/app/ingredientes/page.tsx).
- **Contrato/ejemplo:** [corte vigente de pedidos](../../api/contrato-pedidos.md#corte-vigente--envío-automático-y-prueba-real--30-09-2026), [A02/unidades](../../api/contratos.md), [programación](../../automatizacion/programacion.md), [diseño](../../diseno/especificacion-visual.md). Elegir AUTOMATICO por programación; 1503 g se presenta como 1,503 kg, sin cambiar API.
- **Configuración/migración:** sin migración nueva sobre 0013, sin secretos registrados. Imágenes finales API/worker/Beat/frontend/migraciones reconstruidas correctamente con docker compose build, sin el servidor temporal de QA. Los servicios habituales se detectaron detenidos durante la tarea y se conservarán apagados; solo PostgreSQL fue encendido temporalmente para QA. Bot/chat propio existente conserva configuración cifrada. Preferencia global manual preservada; no se agenda una hora sin elección del usuario.
- **Pruebas y límites:** 54 passed en PostgreSQL aislado: test_aprobacion_envio_l03.py, test_compras_l02.py, test_programaciones_a02.py y test_planificacion_m02.py. npm run typecheck correcto y 17 comprobaciones exactas de unidades correctas. Los intentos iniciales tuvieron dos expectativas obsoletas (texto de unidad y reloj del motor); se corrigieron y la suite completa pasó. Transporte automático falso, sin acreditar segundo envío real. Navegador comprobó Inicio, menú móvil, selección por nombre/mode y aprobación deshabilitada sin revisión; stock 0,5 kg→500 g en fixture aislada. La fixture SQLite temporal falló con consultas concurrentes y se cambió a PostgreSQL aislado para QA; instalación habitual no tiene ese backend SQLite. QA final: 15 pantallas principales con guía y sin errores de carga, más detalle de ejecución; Panel se verificó después de completar metadatos del modelo falso de la fixture. Entrada 0,5 kg→500 g en PostgreSQL aislado, tabla/fecha histórica comprobadas; se corrigió un catch de consulta abortada que sustituía el objetivo por hoy bajo StrictMode. Imagen final anterior verificó 5 pruebas automáticas adicionales (25 deselected). Typecheck final correcto. Build final correcto; servidor Next del puerto 3001, contenedores/esquema de QA y archivos temporales retirados. SQL final confirma 0 esquemas e03_test, pedido #1 ENVIADO/message_id=2 y 14 ajustes pequeños intactos. Servicios habituales apagados como estaban al terminar la revisión; no se acredita validación visual de todos los formularios ni entrenamiento real.
- **Dependencias/siguiente paso:** Revisar receta/oferta de cada ingrediente y calcular un plan nuevo para usar ajustes. No cambiar stocks/versiones desde la generación ni interpretar ENVIADO como recepción. Coordinación con otros registros enlazados desde dependencias.md.
- **Git:** rama cueva, cambios locales sin commit/push/PR/merge.
### Paso 4 · Proveedores, ofertas y pedidos L02 · 30-09-2026 (America/Bogota)

- **Autor/responsables y estado:** Codex por autorización de Axel Cueva. Coordinación A04 con L01/L02 de Aguirre, consumo M03/M04 de Max y K02/K03 de Kevin. LISTO_PARA_INTEGRAR LOCAL para borradores/API/UI; L03 y envío incierto de L04 siguen pendientes. No atribuye implementación nueva a los integrantes. [Axel](cueva.md), [Aguirre](aguirre.md), [Max](rojas.md), [Kevin](bohorquez.md).
- **Comportamiento:** ofertas preferidas explícitas, proveedor/ingrediente activos al configurar, cantidades por factor/minimo/múltiplo con Decimal exacto, pedidos agrupados por proveedor y snapshots de necesidad/oferta/modo. Sin faltantes no genera pedidos ni reserva fecha; datos incompletos, proveedor ausente o destino sin verificar quedan bloqueados con motivos y sin líneas inventadas. Bloqueo de un proveedor bloquea todo el conjunto. Plan/pedido nunca mueven inventario.
- **Política de recompra:** UNIQUE(plan_id), UNIQUE(plan_id,proveedor_id), UNIQUE(necesidad_ingrediente_id), índice parcial de una propuesta activa por fecha y lock de fecha PostgreSQL. Repetir recupera el original incluso tras cambio de oferta/modo. Otra propuesta de esa fecha devuelve RECOMPRA_FECHA; cancelar explícitamente la anterior con motivo/actor/hora conserva datos y libera fecha. El plan cancelado recupera historial; corregir requiere otro plan. No hay sustitución ni recompra incremental automática.
- **Contrato/archivos:** [pedidos](../../api/contrato-pedidos.md#corte-l02-del-paso-4-local--30-09-2026), [servicio](../../../backend/app/modules/compras/servicio.py), [modelos](../../../backend/app/modules/compras/modelos.py), [pantalla compras](../../../frontend/src/app/compras/page.tsx), [proveedores](../../../frontend/src/app/proveedores/page.tsx), [pruebas](../../../backend/tests/integration/test_compras_l02.py). POST /pedidos/generar {"plan_id":12}, GET /pedidos, GET /compras/propuestas y POST /compras/propuestas/{id}/cancelar {"motivo":"Usar plan corregido"}; consultas con sesión, cambios solo Administrador. Interfaces públicas: obtener_contexto_compras, oferta_preferida_para_compras, obtener_modo_envio_pedidos, generar_pedidos y detalle_propuesta; sin commit en servicios.
- **Consumidor verificado:** Beat/CatBoost/PostgreSQL/Redis generan corrida→plan→necesidades→pedido y reservan evaluación en una transacción. Destino verificado únicamente con adaptador falso de test; no se finge Telegram real. Alcance del motor PLAN_PEDIDOS_L02; RECOMPRA_FECHA deja nuevo plan y evaluación intactos. API/UI propia y enlace desde planificación; Operador consulta, Administrador configura/cancela.
- **Migración/configuración:** 0011_l02_compras sobre 0010, sin modificar revisiones previas. propuesta_compra/pedido_compra/linea_pedido con FKs y CHECK, compra Numeric(20,4), equivalencia base Numeric(30,8). Modo AUTOMATICO conservado pero bloqueado CANAL_PENDIENTE_L03; aprobación/manual o envío no se ejecutan en este corte. No se habilitó canal ni se cambió configuración del entorno habitual.
- **Pruebas ejecutadas:** Docker aislado foodsave-paso4-20260930; pytest tests foodsave-ml/tests con E03_POSTGRES_TEST/A03_POSTGRES_TEST/V02_POSTGRES_TEST=1: 159 passed, 6 subtests passed, sin omisiones; advertencias existentes de dependencias/reflexión SQLite. Prueba adicional test_motor_recompra_conserva_nuevo_plan_y_evaluacion: 1 passed. Usuarios/acceso previamente: 13 passed con concurrencia real. Alembic upgrade head/check/downgrade 0010/reupgrade correctos en PostgreSQL, sin diferencias de modelos. npm run typecheck y npm run build correctos. Primer intento focalizado tenía 8 errores de fixture por argumento usuario_id ausente; corregido, suite final completa correcta.
- **Dependencias/siguiente paso:** L03 implementará aprobación y adaptador/envío/conciliación con nuevas migraciones para sus estados, sin reescribir 0011. Debe preservar la reserva de fecha y prohibir cancelación simple tras aprobación/envío. Envío real necesita autorización explícita, chat propio verificado y rótulo DEMOSTRACIÓN — NO SURTIR. Promociones V03 siguen en el paso posterior. No declarar demo completa todavía.
- **Git:** cueva, HEAD sin cambios; cambios locales sin commit, push, PR ni merge remoto.
### Paso 3 · M03 necesidades y faltantes · 30-09-2026 (America/Bogota)

- **Autor y estado:** Codex por autorización de Axel Cueva, coordinando A04/M03 de Max Rojas. LISTO_PARA_INTEGRAR LOCAL; no atribuido como entrega personal de Max. [Coordinación Axel](cueva.md), [dominio Max](rojas.md), [stock Vera](vera.md), [próximo consumidor Aguirre](aguirre.md).
- **Comportamiento:** agrega aportes desde recetas y producción guardadas, Decimal exacto y redondeo final a tres decimales. Conserva disponible/faltante nullable, lotes excluidos/vigencia desconocida, productos impedidos y metadatos. CALCULADAS o INCOMPLETAS; las incompletas son subtotales no aptos para compras. Otro cálculo usa nueva clave y conserva anteriores. No mueve saldos ni envía mensajes.
- **Contrato y archivos:** [Contrato M03](../../api/contratos.md#m03--paso-3-local-necesidades-y-faltantes-conservados), [servicio público](../../../backend/app/modules/planificacion/servicio.py), [pantalla](../../../frontend/src/app/planificacion/page.tsx), [pruebas M03](../../../backend/tests/integration/test_necesidades_m03.py). obtener_necesidades(sesion, plan_id) entrega snapshots sin commit. GET del plan incluye filas/aportes; POST /api/v1/planes/{id}/necesidades, administrador y sin cuerpo, completa planes antiguos una vez.
- **Configuración/migración:** aplicar 0010_m03_necesidades sobre 0009; no se reescribe ninguna revisión aplicada. Planes previos quedan PENDIENTE_M03. Servicio y motor comparten transacción; consumidor real GENERAR_PROPUESTA informa PLAN_M03 y estado de necesidades. API verifica el contrato; Compras no está implementado ni se declara integrado.
- **Pruebas ejecutadas:** Docker aislado foodsave-paso2-20260930, suite backend y foodsave-ml con E03_POSTGRES_TEST/A03_POSTGRES_TEST/V02_POSTGRES_TEST=1: 145 correctas y 6 subpruebas, sin omisiones. Flujo CatBoost/Beat/PostgreSQL/Redis, concurrencia, rollback, suma compartida, stock desconocido, snapshots y rango. Alembic upgrade head/check/downgrade 0009/reupgrade correctos en PostgreSQL; sin diferencias de modelos. Frontend npm run typecheck y npm run build correctos. Verificación final focalizada: 20 pruebas correctas en PostgreSQL, incluida migración con plan existente; seis pruebas M03 también correctas en SQLite. Un intento con instalación mínima de pytest no pudo recoger tests por dependencia HTTP ausente; se repitió con .[test] completo y pasó. Advertencias de dependencias/reflexión SQLite, sin errores en las ejecuciones finales.
- **Dependencia y siguiente paso:** L02 de Aguirre consumirá únicamente CALCULADAS y conservará conversión/oferta por línea; cerrar política entre planes de igual fecha antes de compras automáticas. M04 tiene trazas de productos e ingredientes, falta enlace a pedidos. Siguiente autorización: paso 4 proveedores/ofertas/pedidos; Telegram se tratará según alcance y permiso expreso de envío.
- **Git:** rama cueva; cambios locales, sin commit, push, PR ni merge remoto.

### Paso 2 · Plan M02 reproducible y propuesta programada · 30-09-2026

- **Autor/responsables y estado:** Codex por autorización de Axel Cueva (America/Bogota), coordinación A04 con M02 de Max Rojas, K02/K03 de Kevin y V02 de Vera. LISTO_PARA_INTEGRAR en local, sin atribuir estos cambios a entregas personales de los integrantes. M03 y compras siguen pendientes.
- **Comportamiento real:** generar_plan consume corrida, recetas y disponibilidad por interfaces públicas; guarda referencia/versión/composición de receta, stock elegible y lotes, motivos y pronóstico. max(0, pronóstico-stock), margen 0. Cero explícito permite calcular; ausencia permanece null. Misma clave/huella recupera; otra entrada produce 409 y otra clave conserva un plan nuevo. Lectura del plan no cambia cuando se edita receta o ajusta inventario.
- **Consumidor verificado:** GENERAR_PROPUESTA de Beat/worker ejecuta inferencia real CatBoost, persiste plan y reserva EVALUAR_PRONOSTICO en la misma transacción. Fallo posterior al plan revierte plan y corrida; reentrega no duplica. Salida declara alcance PLAN_M02 y necesidades/pedidos pendientes. No modifica stock ni envía mensajes.
- **Archivos/contrato:** [M02](../../api/contratos.md#m02--paso-2-local-plan-reproducible), [planificacion/servicio.py](../../../backend/app/modules/planificacion/servicio.py), [manejadores.py](../../../backend/app/modules/planificacion/manejadores.py), [pantalla](../../../frontend/src/app/planificacion/page.tsx), [pruebas M02](../../../backend/tests/integration/test_planificacion_m02.py). Coordinación/consumidores: [Axel](cueva.md), [Max](rojas.md), [Kevin](bohorquez.md), [Vera](vera.md).
- **Ejemplo/API:** POST /api/v1/planes administrativo con {"corrida_id":12,"clave_ejecucion":"plan-12-v1"} devuelve 201 y snapshots; GET /planes y /planes/{id} requieren sesión. Desde /planificacion se consultan trazas y se prepara un recálculo con otra clave. /automatizaciones agenda el flujo automático.
- **Configuración/migración:** nueva [0009_m02_planificacion](../../../backend/migrations/versions/0009_m02_planificacion.py) sobre 0008; FKs, claves únicas, estados y CHECK de fórmula; env.py registra ambos modelos. Aplicar alembic upgrade head antes de ejecutar código nuevo (Compose lo hace al arrancar). Revisiones anteriores intactas. CI preparado localmente para incluir M02 con E03_POSTGRES_TEST=1.
- **Pruebas ejecutadas:** docker compose -p foodsave-paso2-20260930 run, PostgreSQL/Redis aislados, E03_POSTGRES_TEST=1 A03_POSTGRES_TEST=1 V02_POSTGRES_TEST=1, python -m pytest tests foodsave-ml/tests -q --basetemp=/tmp/pytest-paso2 → **140 passed, 6 subtests passed**, sin omisiones; 19 advertencias de dependencias/reflexión SQLite. Incluye permisos, desconocidos, límites/caducidad, cambios de stock/receta, snapshots, SQL, rollback, concurrencia y flujo real de seis meses de fixture con CatBoost/Beat. Upgrade a 0009, current --check-heads, alembic check, downgrade a 0008 y reaplicación/check correctos en la base aislada. npm run typecheck y npm run build correctos, ruta /planificacion incluida. Después de endurecer la validación de pronóstico, prueba M02 SQLite: 10 passed, 1 skipped (solo concurrencia PostgreSQL ya verificada en Docker).
- **Límites honestos:** suite amplia Windows no completó por permisos de su temporal; Docker valida el recorrido completo. Interfaz compilada, sin prueba manual de navegador. CI remoto no ejecutado para este corte; el workflow solo se editó localmente. No se modificó el entorno de datos habitual ni el remoto.
- **Dependencia/siguiente paso:** M03 de Max agregará necesidades/faltantes en unidad base y ampliará API/UI; luego Aguirre consumirá esas necesidades, cerrando antes la política de recompra entre planes de la misma fecha. Falta revisión de otra persona y reproducción en otra PC.
- **Commit/PR:** cambios locales sin commit en cueva; sin push, publicación, edición de PR ni merge remoto por instrucción expresa de Axel.

### Integración coordinada de entregas Rojas/Aguirre · 30-09-2026

- **Fecha/zona y autor:** 2026-09-30, America/Bogota. Codex a solicitud de Axel Cueva, coordinación transversal A04; se conserva autoría original de Max/Leonardo y la entrega delegada registrada en [Vera](vera.md).
- **Estado:** integración local verificada en SQLite; LISTO_PARA_INTEGRAR en Git, PostgreSQL/Redis y revisión remota pendientes. No declara completa la demo.
- **Comportamiento:** Codex para Axel concilió M01 y la entrega delegada V01/V02 con main en `cueva`. Reconstruyó las migraciones 0005/0006 a partir de los modelos publicados (no estaban en origin/rojas). Carga completa real, rollback de stock, versiones y migraciones delta verificadas en SQLite; PostgreSQL pendiente de CI. M02–M04 siguen pendientes; no se atribuye este trabajo de coordinación a Max.
- **Archivos/contrato:** [contratos](../../api/contratos.md), [importaciones](../../api/contrato-importaciones.md), [pedidos](../../api/contrato-pedidos.md), rutas de inicialización/ingredientes/recetas/inventario/proveedores, `backend/migrations/env.py`, nuevas revisiones 0005/0006/0007 y `backend/tests/integration/test_api_inicializacion_ventas.py`, `test_proveedores_l01.py`, `test_migraciones_entregas.py`, `test_inventario_concurrencia_pg.py`. Enlaces de coordinación: [Axel](cueva.md), [Max](rojas.md), [Vera](vera.md), [Aguirre](aguirre.md), [Edu](sanchez.md).
- **Ejemplo público:** POST autenticado `/api/v1/inicializacion/confirmar` con los cinco CSV y fechas válidas devuelve DATOS_CARGADOS; POST administrativo `/api/v1/proveedores/{id}/ofertas` exige ingrediente existente y conversión explícita. Servicios participantes hacen flush, el llamador confirma.
- **Migraciones/configuración:** continuar desde 0004 con 0005→0006→0007; registrar todos los modelos, incluido ConfiguracionInicial. Revisiones previas conservadas. Para concurrencia activar V02_POSTGRES_TEST=1 sobre esquema de pruebas aislado; no habilitar Telegram ni cambiar modo automático.
- **Pruebas realmente ejecutadas:** `.venv/Scripts/python.exe -m pytest backend/tests foodsave-ml/tests -q` → 112 passed, 10 skipped (8 A03 y 2 V02 por PostgreSQL/Redis), 6 subtests passed. `npm run typecheck` y `npm run build` correctos. Delta 0004→0007 arriba/abajo/arriba y comparación de metadatos en SQLite correctos; el índice de expresión del núcleo no se puede reflejar en SQLite. Docker Desktop no logró arrancar; CI incorpora alembic check y concurrencia V02. No se ejecutaron envíos externos.
- **Dependencias y siguiente paso:** revisión de la entrega conjunta y CI PostgreSQL; después integrar a main. Max continúa M02/M03; Aguirre completa adaptador/UI L01 y L02–L04; Vera V03; Edu/Kevin/Axel conectan ML desde asistente completo.
- **Commit/PR:** cambios locales en cueva; publicación de PR de integración pendiente.


### Preparación del registro

- **Autor:** IA que preparó el reparto y guías, sin atribuir implementación a Max Rojas.
- **Cambio:** se definieron las tareas y el lugar de documentación; no se implementó lógica de este bloque en esta entrega documental.
- **Pruebas:** la revisión de documentación comprueba enlaces, cobertura de carpetas y coherencia del reparto; no acredita funcionamiento del módulo.
- **Próximo autor:** registrar el primer avance con la [plantilla](README.md) y actualizar el resumen vigente.

### M01 · Ingredientes y recetas versionadas

- **Fecha/hora y zona:** 30-09-2026, America/Lima.
- **Autor y responsable del bloque:** Max Rojas, con asistencia de IA (Claude).
- **Tareas:** M01. En la misma entrega, V01 y V02 por encargo (registradas en [vera.md](vera.md)).
- **Estado:** LISTO_PARA_INTEGRAR.
- **Qué cambió:** tablas `ingrediente`, `receta` y `receta_ingrediente`. La unidad base no cambia si una receta o un lote la usa. Toda edición de receta crea la versión siguiente y desactiva la anterior; la misma composición no crea versión. `ServicioRecetasM01` implementa el puerto de Edu sin commit; la primera carga ahora termina en `DATOS_CARGADOS`.
- **Archivos clave:** [ingredientes/servicio.py](../../../backend/app/modules/ingredientes/servicio.py), [recetas/servicio.py](../../../backend/app/modules/recetas/servicio.py), [0005_m01_ingredientes_recetas.py](../../../backend/migrations/versions/0005_m01_ingredientes_recetas.py), [app/recetas/page.tsx](../../../frontend/src/app/recetas/page.tsx).
- **Contrato:** [contratos.md, sección M01](../../api/contratos.md#m01-disponible-ingredientes-y-recetas-versionadas-30-09-2026).
- **Migración:** `0005_m01_ingredientes_recetas` sobre `0004_e03_inicializacion`.
- **Cambios fuera del bloque (mínimos, avisar):** `inicializacion/rutas.py` pasa los dos puertos (Edu); `test_api_inicializacion_ventas.py` ahora espera `DATOS_CARGADOS` (Edu); `principal.py` y `migrations/env.py` registran rutas y modelos (Axel); menú "Producción" en `ProtectedShell.tsx` y clase `badge-prioridad` en `styles.css` (Edu).
- **Pruebas ejecutadas:**
  - `cd backend && python -m pytest -q tests` → 82 passed, 10 skipped (8 de A03 y 2 de V02 que requieren PostgreSQL).
  - `alembic upgrade head`, `downgrade 0004_e03_inicializacion` y `upgrade head` sobre PostgreSQL 16 local → sin error; `alembic check` sin diferencias en tablas de M01/V01.
  - Carga real por `POST /inicializacion/confirmar` sobre PostgreSQL → `DATOS_CARGADOS`, `pendiente_de: []`.
  - `cd frontend && npx tsc --noEmit` y `npx next build` → sin errores.
- **Aviso para Edu/Axel:** `migrations/env.py` no importa `ConfiguracionInicial`; un autogenerate propondría borrar `configuracion_inicial`. No se modificó.
- **Siguiente desarrollador:** Max (M02) consume `recetas_activas` y `consultar_disponibilidad`. Aguirre puede ligar `oferta_ingrediente.ingrediente_id` a `ingrediente.id`.
- **Siguiente paso concreto:** M02.
- **Commit/PR:** cambios locales, sin commit.


## Bitácora del corte local conservada · conciliación 06-10-2026

Estas entradas describen el corte local anterior. Sus pendientes históricos no sustituyen el contrato conciliado ni el resumen vigente.

### 06-10-2026 America/Lima — Entrega transversal M02–M04

- **Autor:** Codex a solicitud de Axel Cueva; dominio de planificación mantiene responsable Max Rojas. No modifica autoría de las entregas anteriores.
- **Resultado:** plan, necesidades, API/pantalla y handler programado disponibles; registro de archivos, contrato, migración, pruebas y límites en [Cueva](cueva.md). M03 pendiente consumo real por Aguirre; pedidos/canal fuera de este corte.
- **Commit/PR:** cambios locales en `cueva`, sin commit ni publicación.
