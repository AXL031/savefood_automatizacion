# Avances — Kevin Bohorquez

**Responsable:** Kevin Bohorquez. **Bloque:** Modelo predictivo, evaluación histórica y dashboard. **Rama prevista:** `bohorquez`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md). Este archivo se actualiza al terminar cada avance significativo.

## Resumen vigente

- **27-10-2026 · Corrección CI M03 solicitada por el usuario:** reproducido el fallo `DependentObjectsStillExist` del run [40531539375](https://github.com/AXL031/savefood_automatizacion/actions/runs/40531539375). La preparación de `test_migracion_preserva_plan_previo` omitía retirar la revisión 0020 antes de compras. Se añade al ciclo de downgrade/upgrade del test aislado; sin cambiar migraciones aplicadas ni datos de la demo. Validación nueva: seis pruebas M03 PostgreSQL correctas, caso de migración SQLite correcto y bloque completo de Actions **208 passed, 13 warnings, 319,55 s**. Nueva cabeza y resultado remoto se consultan en [Actions de bohorquez](https://github.com/AXL031/savefood_automatizacion/actions?query=branch%3Abohorquez); el resultado local no se presenta como aprobación remota.

- **27-10-2026 · Publicado en bohorquez por solicitud del usuario:** fetch/pull correctos sin conflictos; push normal `39723b4..6f41c43` confirmado mediante `git ls-remote`. Seis commits separan backend (`1462b8c`), pruebas/CI (`4239c1d`), interfaz (`ba76bbb`), infraestructura (`5550ea2`), auditorías/BPMN (`ce876db`) y contratos/guías (`6f41c43`). Typecheck, Compose, metadatos PostgreSQL, sintaxis y revisión de valores secretos correctos. [CI del código publicado](https://github.com/AXL031/savefood_automatizacion/actions/runs/40531257124) en curso al corte, sin acreditar éxito anticipado. Este registro se entrega en un commit documental adicional. Sin cambios en main, PR, secretos ni recursos de pago.

<!-- avance-operativo-2026-10-27 -->
- **27-10-2026 · Codex, operación integrada autorizada:** producción por tandas, ventas con FEFO, tienda/API real con pago simulado, enlace de proveedor de una hora, recepción asistida/incidencias, avisos y monitor de productos cada diez minutos con aprobación/publicación. Menú con sangría/tono, Docker de prueba aislado, túnel gratuito y Render opcional de pago. Cueva coordina, responsables y autorías previos conservados. [Contrato](../../api/contrato-operacion-integrada.md) y [guía/env/cuentas](../../operacion-integrada.md). LOCAL Y HTTPS PÚBLICO VERIFICADOS. PostgreSQL/Redis reales: 77 pruebas de operación, motor A03, promociones, aprobación y recuperación correctas (1652,58 s); versión final: 7 pruebas de operación correctas (258,49 s), incluidas concurrencia de venta sin sobreventa y producción sin exceder plan. No sumar los cinco casos repetidos como pruebas distintas. Además, cinco pruebas SQLite y cuatro de sesión correctas; typecheck y build web correctos. Migración 0020 upgrade/metadatos/downgrade vacío/reaplicación verificados y alembic check PostgreSQL sin cambios. Blueprint validado contra esquema oficial; Compose válido. Semilla real idempotente, CatBoost LISTO_DEMO y 30 corridas históricas reales. API viva: tres roles, plan/tanda, venta, aprobación y compra repetible sin duplicarse. Edge: panel, avisos, catálogo real, menú con sangría 16px y fondo propio, móvil 390px sin desbordamiento ni errores; compra completa con cuenta local, pago simulado y Mis pedidos (pedido sintético #4). Evidencia privada .tmp/qa-*.png y .tmp/operacion-final.xml. La suite general Windows perdió su sesión; no se acredita su resultado completo. Última imagen web con ajustes de formularios y textos de pago simulado compilada correctamente en Docker. Tras rechazo inicial de la revisión automática, el usuario autorizó expresamente publicar toda la web/API si era gratis; Quick Tunnel activo, URL en .tmp/url-publica.txt, catálogo HTTPS y API administrativa sin sesión denegada con 401. Edge público confirmó login, panel, avisos, tienda y móvil sin errores. No se verificó Render ni Telegram real; ningún recurso de pago creado ni mensaje externo enviado.

 Sin commit/push ni recursos Render creados.

<!-- fin-avance-operativo-2026-10-27 -->

- **26-10-2026 · Auditoría académica V2:** [contraste completo con la rúbrica](../auditoria-rubrica-v2-2026-10-26.md), PDF de ocho páginas leído y páginas 1/7 inspeccionadas. Usuario confirma sin observaciones V1 ni informe elaborado. Núcleo de automatización con soporte real; entrega completa no acreditada por informe/diseño formal y demo viva pendientes. ECA ya presentes en BPMN locales sin seguimiento; no se modifican. Pruebas focalizadas nuevas: 62 passed, 10 skipped PostgreSQL, 5 warnings, 74,76 s; transporte falso. Coordinación A04 de [Cueva](cueva.md), sin cambios de negocio, stock, mensajes ni publicación.

- **26-10-2026 · Codex, sincronización y revisión solicitadas:** fetch y pull fast-forward correctos; `bohorquez`, `origin/bohorquez` y `origin/main` coinciden en `39723b4` (incluye tienda PR #17). [Revisión vigente](../revision-proyecto-2026-10-26.md): tienda real pendiente salvo T02, dependencias Python versionadas, paginación de planes/compras/productos y cierre de infraestructura/otra PC. Typecheck correcto; 19 pruebas aisladas de sesión, reevaluación y migraciones correctas. Docker no disponible; CI remoto no consultado. Carpeta BPMN local conservada. Sin implementación nueva ni publicación; coordinación transversal A04 de Cueva y dependencias de [Rojas](rojas.md).

- **20-10-2026 · Entrega por commits autorizada por el usuario:** cambios separados en [f66d1a2](https://github.com/AXL031/savefood_automatizacion/commit/f66d1a2) (backend, reevaluacion y contratos); [7ff08de](https://github.com/AXL031/savefood_automatizacion/commit/7ff08de) (pruebas de regresion y guias); [9fb094c](https://github.com/AXL031/savefood_automatizacion/commit/9fb094c) (diseno web y analitica). Los registros, contratos y auditoria se entregan en un cuarto commit documental. Rama de publicacion: `bohorquez`; sin PR ni integracion en `main`. La evidencia de pruebas del corte se conserva; esta entrega Git no ejecuta nuevas pruebas ni despliega servicios.

- **20-10-2026 · Codex a solicitud del usuario, prioridad K03/K04 y diseño:** implementación local verificada de corrección→reevaluación transaccional, consumo exacto de revisiones, indicadores pendientes, filtros temporales y archivo completo de modelos/corridas. Inicio, Pronósticos, Evaluación y Reportes rediseñados con navegación común, tarjetas de métricas, gráfico por calendario/teclado, búsqueda y detalle de productos, partición visual y diseño móvil sin desbordamiento. Coordinación E01/E02/E04 con [Sanchez](sanchez.md) y A03/A04 con [Cueva](cueva.md); cada integrante conserva sus responsabilidades. [Contrato vigente](../../api/contratos.md#k03k04-y-frontera-e01--20-10-2026).
- **Validación de este corte:** **271 passed, 26 skipped, 39 warnings, 6 subtests passed, 190,80 s**; seis regresiones nuevas. Las omisiones requieren PostgreSQL/Redis. Typecheck y build Next correctos, 23 páginas. QA de navegador con API/SQLite reales y datos sintéticos aislados: fechas, filtro de error, historial más allá de 50, detalle/Escape, CSV y corrección de venta→reserva; escritorio 1280 px y móvil 390 px sin desbordamiento global. Consola sin errores en los recorridos comprobados. No acredita artefacto comercial, Beat/locks PostgreSQL en vivo ni mensajes reales.
- **Estado/siguiente:** LISTO_PARA_INTEGRAR LOCAL; rama `bohorquez`, base `a19a294`, commits del corte enlazados arriba; sin PR ni migraciones nuevas. Docker está apagado: la instalación habitual no se reconstruyó ni se procesaron sus tareas. Actualizar backend y frontend juntos y verificar el corte PostgreSQL/Redis/CI; después otra PC y envío automático real solo bajo tarea expresamente autorizada. Operación con ventas actuales y WhatsApp siguen pendientes de sus contratos/configuración.

- **11-10-2026 · Codex para Axel, K02/K04 y consumo A02/M02:** K01–K04, carga→modelo/evaluación y pronóstico→plan tienen implementación local y consumidores comprobados. El asistente elige un modelo preparado y conserva su ID para todas las fechas del calendario. La inferencia mantiene historia anterior al objetivo; partición y cobertura no se sustituyen por valores inventados.
- **Estado:** implementación real integrada en la instalación local. Consumidores de Promociones/motor/inventario verificados con PostgreSQL/Redis y navegación QA aislada; migración 0015 aplicada. CI remoto, otro PC y nuevo Telegram real no acreditados; ver entrada más reciente.
- **Contrato:** [flujo y promociones](../../api/contrato-flujo-promociones.md). Migración aditiva `0015_flujo_promociones` sobre 0014; conservar revisiones aplicadas.
- **Coordinación/dependencias:** Cueva y Rojas consumen K02; no atribuye nuevas reglas ML a Kevin. [Registro transversal](cueva.md) y [plan vigente](../plan-cierre-prototipo.md). Autor real de este corte: Codex para la solicitud de Axel; no se atribuye a integrantes.
- **Siguiente paso:** revisar los cambios locales y completar CI remoto, reproducción en otra PC y prueba Telegram real autorizada. La instalación habitual ya está actualizada y activa. Cambios locales, sin commit ni publicación.

## Bitácora

### 27-10-2026 America/Bogota — Corrección del fallo PostgreSQL en CI M03

- **Autor/responsabilidad:** Codex por reporte del usuario, en bohorquez; A04 coordina la frontera con M03 de Rojas. No se atribuye el arreglo a los integrantes.
- **Problema observado:** el paso Motor A03 del run `40531539375` terminó con 207 passed y un fallo. El test histórico de M03 intentaba retirar `pedido_compra` dejando la FK de `solicitud_proveedor` creada en 0020. Reproducción local del mismo fallo PostgreSQL: un caso fallido antes del cambio.
- **Corrección:** `backend/tests/integration/test_necesidades_m03.py` incorpora `0020_operacion_integrada` a las revisiones posteriores que retira en orden inverso y restaura al final. Se mantienen las comprobaciones del plan anterior y el recálculo de sus necesidades. Guía de integración actualizada; no se edita ninguna migración aplicada, no se usa CASCADE y no se cambia comportamiento de negocio.
- **Verificación realmente ejecutada:** módulo M03 completo con PostgreSQL: 6 passed, 1 warning, 10,96 s; caso de migración con SQLite: 1 passed, 2 warnings, 1,69 s. Mismo listado de 19 archivos del paso CI, con E03/A03/V02=1 y HABILITAR_ENLACES_PROVEEDOR=0: **208 passed, 13 warnings, 319,55 s**. Python 3.12 en contenedor temporal, esquemas/colas aislados; evidencia JUnit privada en `.tmp/ci-corregido.xml`. No se repiten builds o QA visual porque el cambio solo afecta la preparación del test y documentación.
- **Contrato/configuración/límites:** contratos, esquema operativo y revisión 0020 sin cambios; sin nueva migración, mensajes externos ni cambios de stock/cuentas. No se presenta el éxito local como CI remoto aprobado; consultar el run asociado al commit de corrección en [Actions](https://github.com/AXL031/savefood_automatizacion/actions?query=branch%3Abohorquez).
- **Entrega:** corrección y documentación en un commit `correccion(pruebas)` de bohorquez para push normal. Sin cambios en main ni PR. Siguiente: verificar la nueva ejecución remota; los dos runs fallidos anteriores se conservan como historial.

### 27-10-2026 America/Bogota — Publicación remota confirmada

- **Autor/tarea:** Codex para la petición de publicar en `bohorquez`; coordinación transversal A04, con responsabilidad y autoría anteriores conservadas.
- **Resultado:** `git push origin bohorquez` correcto, avance `39723b4..6f41c43`; `git ls-remote origin refs/heads/bohorquez` devuelve `6f41c4387b3067eb12baf2476cd0099bb90e8ad5`. Árbol limpio después de los seis commits. Este registro final es un commit documental adicional para acreditar la publicación sin afirmar que ocurrió antes de verificarla.
- **Commits:** [1462b8c, backend](https://github.com/AXL031/savefood_automatizacion/commit/1462b8c), [4239c1d, pruebas/CI](https://github.com/AXL031/savefood_automatizacion/commit/4239c1d), [ba76bbb, interfaz](https://github.com/AXL031/savefood_automatizacion/commit/ba76bbb), [5550ea2, infraestructura](https://github.com/AXL031/savefood_automatizacion/commit/5550ea2), [ce876db, auditorías/BPMN](https://github.com/AXL031/savefood_automatizacion/commit/ce876db) y [6f41c43, contratos/guías](https://github.com/AXL031/savefood_automatizacion/commit/6f41c43). Mensajes `tipo(modulo): descripción` conforme al flujo del repositorio.
- **Verificación local del corte:** tipos TypeScript, sintaxis Python, Compose, `alembic check`, formato Git y ausencia de valores privados del entorno en los 97 archivos publicados correctos. No se repitieron las suites del avance operativo; sus resultados 77/7 siguen siendo evidencia previa. Guías nuevas de carpetas incluidas y BPMN del usuario conservados sin cambiar su contenido.
- **CI remoto/límites:** GitHub confirma un run de push en curso, [40531257124](https://github.com/AXL031/savefood_automatizacion/actions/runs/40531257124), para `6f41c43`. No se presenta como aprobado ni se heredan checks de otra cabeza. La modificación añade pruebas operativas PostgreSQL/concurrencia y aísla el flag de texto Telegram en ese proceso de pruebas. Sin mensajes externos ni recursos cobrables.
- **Entrega/siguiente:** compañeros pueden actualizar `bohorquez` y seguir [Docker/variables/cuentas](../../operacion-integrada.md). Secretos, base de datos, modelos locales y contraseñas no se transfieren por Git; cada instalación genera sus credenciales. Revisar CI y realizar revisión del equipo antes de integrar main. No se abrió PR ni se hizo merge.
- **Estado:** código publicado para revisión; integración en main y CI final pendientes de sus comprobaciones.

### 27-10-2026 America/Bogota — Preparación de publicación por commits

- **Autor/tarea:** Codex por petición expresa del usuario; publicación de todos los avances conservados en `bohorquez`. Coordinación transversal A04 con Cueva; dominios/autores previos preservados.
- **Sincronización:** `git fetch origin --prune` y `git pull --ff-only origin bohorquez`, salida 0; HEAD y origin/bohorquez iguales a `39723b4`, también coincidente con origin/main al iniciar. Sin cambiar de rama, reescribir historia ni integrar main.
- **Contenido:** backend operativo/migración, pruebas de integración y concurrencia, UI/sidebar/tienda/proveedor, Docker local/túnel gratuito y configuración Render opcional de pago, contratos/guías/auditorías y BPMN originales del usuario sin modificar sus contenidos. Guía de BPMN y mapa añadidos para indicar el corte documental anterior.
- **Verificación de publicación:** `npx tsc --noEmit`, Compose `config --quiet`, `alembic check` PostgreSQL, `git diff --check` y parseo de los Python modificados correctos. Revisión privada de valores del entorno sin coincidencias en los 97 archivos candidatos. `.env.pruebas` y `.tmp/credenciales-pruebas.txt` ignorados; no se publican secretos ni datos de la base. Las suites 77 y 7 del avance operativo son evidencia previa, no una nueva ejecución en este corte.
- **CI:** se incorpora `test_operacion_integrada.py` al corte PostgreSQL para sus locks reales y se aísla el flag del texto de transporte heredado dentro de ese proceso de pruebas. Sin alterar configuración de la instalación, sin Telegram real. Validación remota pendiente del push.
- **Contrato/configuración:** [operación integrada](../../api/contrato-operacion-integrada.md), [guía de entornos](../../operacion-integrada.md), migración aditiva 0020 ya aplicada en la demo; no se reescriben revisiones.
- **Siguiente/estado:** commits y push normal a origin/bohorquez en curso; no PR ni merge solicitados. Registrar hashes y resultado remoto antes de entregar.

<!-- bitacora-operativa-2026-10-27 -->
### 27-10-2026 America/Bogota — Operación integrada y entornos

- **Autor/responsabilidad:** Codex por solicitud expresa del usuario; Cueva coordina A04/A03 y enlaza Rojas (producción/tienda), Vera (stock/promociones), Sanchez (ventas/UI), Aguirre (proveedor/recepción). No atribuye implementación a integrantes.
- **Comportamiento:** [guía completa](../../operacion-integrada.md), [contrato operativo](../../api/contrato-operacion-integrada.md). Producción no es automática por plan; venta descuenta producto y no ingredientes; tienda no alimenta ML. Respuesta de proveedor distinta de envío/recepción. Incidencias se resuelven internamente, sin reposición automática.
- **Archivos clave:** backend/app/modules/operaciones, inventario/operacion.py, ventas/operacion.py, compras/envios.py, workers/celery_app.py; frontend /operaciones, /notificaciones y /proveedor; guía/mapa y contratos actualizados.
- **Migración/configuración:** aditiva 0020, única cabeza; no reescribe aplicadas y niega downgrade con historia nueva. Compose original conservado y variante foodsave_pruebas aislada. .env.pruebas y contraseñas aleatorias en .tmp/credenciales-pruebas.txt, ignoradas por Git. Cuenta cliente local con hash real habilitable; Google real conservado. Render conectado consultado sin crear recursos; coste cero pedido por usuario → opción pública Quick Tunnel dependiente de PC encendida. Web espera salud real de API antes de arrancar.
- **Pruebas y límites:** LOCAL Y HTTPS PÚBLICO VERIFICADOS. PostgreSQL/Redis reales: 77 pruebas de operación, motor A03, promociones, aprobación y recuperación correctas (1652,58 s); versión final: 7 pruebas de operación correctas (258,49 s), incluidas concurrencia de venta sin sobreventa y producción sin exceder plan. No sumar los cinco casos repetidos como pruebas distintas. Además, cinco pruebas SQLite y cuatro de sesión correctas; typecheck y build web correctos. Migración 0020 upgrade/metadatos/downgrade vacío/reaplicación verificados y alembic check PostgreSQL sin cambios. Blueprint validado contra esquema oficial; Compose válido. Semilla real idempotente, CatBoost LISTO_DEMO y 30 corridas históricas reales. API viva: tres roles, plan/tanda, venta, aprobación y compra repetible sin duplicarse. Edge: panel, avisos, catálogo real, menú con sangría 16px y fondo propio, móvil 390px sin desbordamiento ni errores; compra completa con cuenta local, pago simulado y Mis pedidos (pedido sintético #4). Evidencia privada .tmp/qa-*.png y .tmp/operacion-final.xml. La suite general Windows perdió su sesión; no se acredita su resultado completo. Última imagen web con ajustes de formularios y textos de pago simulado compilada correctamente en Docker. Tras rechazo inicial de la revisión automática, el usuario autorizó expresamente publicar toda la web/API si era gratis; Quick Tunnel activo, URL en .tmp/url-publica.txt, catálogo HTTPS y API administrativa sin sesión denegada con 401. Edge público confirmó login, panel, avisos, tienda y móvil sin errores. No se verificó Render ni Telegram real; ningún recurso de pago creado ni mensaje externo enviado.


- **Dependencias/siguiente:** mantener PC/Docker activos para el túnel gratuito autorizado; configuración bot/Google real no se inventa ni se envían mensajes externos. Inferencia sigue en ventana histórica reservada; semilla sintética no acredita calidad comercial. No acreditar despliegue Render por tener un Blueprint.
- **Commit/PR:** sin commit, push ni PR; demo publicada por túnel gratuito autorizado, sin recursos Render.

<!-- fin-bitacora-operativa-2026-10-27 -->

### 26-10-2026 America/Bogota — Revisión académica de V2

- **Autor/alcance:** Codex por solicitud del usuario; auditoría transversal de automatización/control A04 y consumo K03/K04. Cada integrante conserva su autoría.
- **Estado/comportamiento:** auditoría real finalizada, sin implementación nueva. [Informe de auditoría](../auditoria-rubrica-v2-2026-10-26.md) contrasta ocho criterios/20 puntos, requisitos documentales, ECA, controles y guion normal/excepción. Distingue rúbrica específica página 7 del resumen inconsistente de página 1. No asigna nota ni porcentaje sin demo/requisitos.
- **Contrato/configuración:** sin cambios de API/migraciones. PDF aportado por el usuario; contratos de flujo/pedidos existentes y BPMN locales leídos sin editar.
- **Pruebas:** `python -m pytest backend/tests/integration/test_flujo_promociones.py backend/tests/integration/test_aprobacion_envio_l03.py backend/tests/integration/test_recuperacion_l04.py backend/tests/integration/test_motor_a03.py -q --tb=short -r s`: 62 passed, 10 skipped, 5 warnings, 74,76 s. SQLite temporal y Telegram falso; omisiones/rutas concurrentes requieren PostgreSQL. No acredita Beat/Redis vivo ni envío externo. Se conserva evidencia previa de typecheck y 19 pruebas, sin volver a ejecutarlas.
- **Dependencias/siguiente:** equipo prepara informe V2, formaliza RF/RNF/casos de uso/actividad/matriz y actualiza diagramas; Cueva coordina infraestructura para demo. Usuario confirma que no recibieron observaciones V1 y no existe informe. No inventar cambios solicitados por docente ni medición de desperdicio/ahorro.
- **Commit/PR:** documentación local, sin commit ni publicación.

### 26-10-2026 America/Bogota — Fetch, pull y revisión de pendientes

- **Autor/alcance:** Codex por solicitud del usuario, rama Bohorquez; revisión K03/K04 y transversal A04/T01–T05, sin atribuir cambios a integrantes.
- **Estado:** revisión real finalizada; cierre funcional del proyecto parcial. `git fetch origin` y `git pull --ff-only origin bohorquez` correctos, sin commits nuevos; HEAD/main remoto `39723b4`.
- **Archivos y contrato:** [informe](../revision-proyecto-2026-10-26.md), [tienda](../../api/contrato-tienda.md), [entrega Rojas](rojas.md). Contratos y comportamiento sin cambios; informe distingue T02 real de catálogo/pedido de ejemplo.
- **Pruebas/configuración:** typecheck salida 0; sesión tienda, reevaluación y migraciones: 19 passed, 19 warnings, SQLite temporal. Sin migraciones nuevas. Docker no disponible; no se acredita CI, Google real, Telegram, QA visual ni otra PC.
- **Dependencias/siguiente:** Rojas completa T01/T03 antes de integrar checkout/stock con Vera; Cueva coordina PostgreSQL/Redis, revisión de dependencias versionadas y reproducibilidad. K03/K04 conserva correcciones existentes. No se modifica stock, datos habituales ni archivos BPMN sin seguimiento.
- **Commit/PR:** documentación local, sin commit ni publicación.

### 20-10-2026 America/Bogota — Separacion y entrega Git

- **Autor/alcance:** Codex por solicitud expresa del usuario de separar y subir el avance a `bohorquez`. K03/K04, E01/E02/E04 y coordinacion A03/A04; responsabilidades personales conservadas.
- **Commits:** [f66d1a2](https://github.com/AXL031/savefood_automatizacion/commit/f66d1a2) (backend, reevaluacion y contratos); [7ff08de](https://github.com/AXL031/savefood_automatizacion/commit/7ff08de) (pruebas de regresion y guias); [9fb094c](https://github.com/AXL031/savefood_automatizacion/commit/9fb094c) (diseno web y analitica). Cuarto commit: registros y revision del proyecto. Sin cambios adicionales de comportamiento, contratos o migraciones en esta operacion.
- **Verificacion:** remoto consultado antes de crear commits; `HEAD` y `origin/bohorquez` coincidian en `a19a294`. `git diff --cached --check` correcto para cada grupo. Se conserva la validacion previa de 271 pruebas y seis subpruebas, 26 omisiones PostgreSQL/Redis y build de 23 paginas; no se repite ni se presenta como ejecutada nuevamente.
- **Dependencias/siguiente:** revisar backend y frontend juntos; completar PostgreSQL/Redis aislados, CI y otra PC. Destino remoto `origin/bohorquez`; publicar no acredita despliegue, revision de PR ni integracion en `main`. [Registro principal](bohorquez.md).


### 20-10-2026 America/Bogota — K03/K04: evaluaciones fiables y analítica rediseñada

- **Autor y alcance:** Codex a solicitud del usuario: avanzar también otros bloques, priorizando Bohorquez y buen diseño. K03/K04 coordinan E01/E02/E04 de Sanchez y consumen el motor A03 de Cueva. No atribuye la implementación a integrantes que no participaron en esta sesión. Entrega local real; no despliegue habitual ni publicación.
- **Comportamiento disponible:** PATCH de venta corrige y reserva reevaluaciones en una sola transacción; falla la reserva → rollback. Ventas informa los IDs/cantidad de tareas; no traslada una tarea manual al usuario ni cambia stock/planes/pedidos. Cada tarea evalúa las revisiones que conservó, aunque cambie la venta antes del worker; versiones antiguas permanecen. Bloqueo por corrida serializa pares compartidos. Snapshot vacío no se reemplaza por datos actuales; revisión ajena/duplicada/ausente se rechaza. Los reportes distinguen evaluación pendiente de venta desconocida.
- **Archivo y API:** modelos/corridas con limite/desplazamiento/total; corridas filtra versión/tipo/fechas y evaluación filtra fechas inclusivas. Lista compatible en datos, metadatos aditivos, permisos existentes. Frontend recorre todas las versiones y pagina todo el historial desde servidor. Lectura inicial acotada: 64 MiB por archivo, 128 MiB por entrega, hasta cinco archivos y duplicados sin distinguir mayúsculas.
- **Diseño y consumidor web:** Inicio, Pronósticos, Evaluación y Reportes comparten Analitica.tsx y paleta hoja/yema. Biblioteca con partición/huella y entrenamiento plegable; evaluación con KPIs, fechas, búsqueda, filtro ±20 y gráfico SVG operable con teclado/selector. Solo une fechas consecutivas comparables; ausencia no genera cero. Tabla/detalle y mensajes conservan null. Reportes comparte métricas/serie y presenta generación en zona del negocio; CSV mantiene todas las filas. Móvil con grid minmax(0,1fr) y desplazamiento interno.
- **Archivos clave:** [evaluación](../../../backend/app/modules/pronosticos/evaluacion.py), [manejador](../../../backend/app/modules/pronosticos/manejadores.py), [rutas](../../../backend/app/modules/pronosticos/rutas.py), [ventas](../../../backend/app/modules/ventas/rutas.py), [regresiones](../../../backend/tests/integration/test_evaluacion_revisiones.py), [Evaluación web](../../../frontend/src/app/panel/page.tsx), [Pronósticos web](../../../frontend/src/app/pronosticos/page.tsx), [piezas comunes](../../../frontend/src/components/panel/Analitica.tsx), [serie](../../../frontend/src/components/charts/SerieHistorica.tsx), [estilos](../../../frontend/src/app/styles.css). Guías de las carpetas y contratos de importación/reportes/rutas actualizados; README backend/pruebas deja de describir esqueleto inexistente.
- **Contrato/ejemplo:** [contratos](../../api/contratos.md#k03k04-y-frontera-e01--20-10-2026), [reportes](../../api/contrato-informes.md). Ejemplo: reservar revisión 1 con real 10, corregir a revisión 2 con real 12 y ejecutar ambas tareas conserva dos comparaciones; solo revisión 2 entra en métricas vigentes. `GET /pronosticos/corridas?modelo_id=1&tipo=BACKTEST&limite=10&desplazamiento=50` devuelve filas 51–60 y total filtrado. `PATCH /ventas/{id}` añade `reevaluaciones:[id...]` sin commits separados.
- **Configuración/migración:** ninguna migración nueva ni cambio de datos habituales, secretos o requisitos. Misma cabeza 0016. Backend y frontend deben actualizarse juntos por los metadatos de paginación; `iniciar-foodsave.cmd -Build` reconstruye según el procedimiento existente cuando se decida actualizar la instalación. No se ejecutó ese arranque porque Docker estaba apagado y esta tarea no autoriza envíos externos pendientes. QA usa puertos 3101/8011 y SQLite bajo .tmp; no inicia worker ni Telegram. Servidores QA detenidos tras la comprobación. CSV sintético trasladado a .tmp/qa-export-ventas.csv, separado de descargas habituales.
- **Pruebas realmente ejecutadas:** selección inicial de cuatro suites (nueva, K02/K03, informes y API inicialización/ventas): 40 passed, 1 warning, 25,10 s. Después suite general `python -m pytest backend/tests/unit backend/tests/integration foodsave-ml/tests -q --tb=short -r fEs`: **271 passed, 26 skipped, 39 warnings, 6 subtests passed, 190,80 s**. La selección está incluida, no sumar como pruebas distintas. Python 3.13, dependencias aisladas y TEMP/TMP/PYTHONPATH de revisión descritos en el informe; ejecución fuera del sandbox para HTTP/asíncrono de Windows. CatBoost real en las pruebas locales habilitadas. Omisiones: PostgreSQL/Redis para concurrencia, DDL, Beat y worker reales. Advertencias existentes Starlette/httpx, reflexión SQLite e índices y unidades temporales NumPy; no son fallos nuevos.
- **Interfaz realmente comprobada:** `npm run typecheck` y `npm run build` correctos, 23 páginas. Navegador de QA: login, cuatro rutas analíticas, rango 01–10/09 con exactamente diez opciones de fecha, filtro fuera ±20, último bloque de 60 pronósticos (51–60), detalle con ocho productos y Escape, selector de reporte/descarga CSV, venta sintética 91→92 con revisión 2 y una tarea de evaluación reservada. Se corrigió un desbordamiento detectado a 390 px; documento <=viewport después del ajuste. Sin errores JavaScript observados. Capturas locales .tmp/qa-evaluacion-escritorio.png, qa-evaluacion-movil.png, qa-pronosticos-escritorio.png y qa-reportes-escritorio.png; son datos de prueba, no evidencia de operación habitual.
- **Dependencias/siguiente paso/Git:** Sanchez conserva E01/E02/E04 y Cueva el motor/infraestructura; este registro coordina y enlaza ambos. Verificar locks y flujo real PostgreSQL/Redis en CI/entorno aislado, reproducir otra PC y obtener revisión del equipo antes de integrar. No se envía Telegram ni habilita WhatsApp; tampoco se extiende inferencia fuera de la prueba histórica. Cambios locales en bohorquez, sin commit, push ni PR. Los cambios documentales de la revisión anterior se conservaron.

### 11-10-2026 19:28 America/Lima — Promociones, flujo configurable y claridad

- **Autor/responsabilidad/tareas:** Codex para Axel; K02/K04 y consumo A02/M02. Coordinación transversal en Cueva, dominios afectados enlazados desde dependencias.md.
- **Estado/comportamiento:** implementación LOCAL real. K01–K04, carga→modelo/evaluación y pronóstico→plan tienen implementación local y consumidores comprobados. El asistente elige un modelo preparado y conserva su ID para todas las fechas del calendario. La inferencia mantiene historia anterior al objetivo; partición y cobertura no se sustituyen por valores inventados.
- **Archivos clave:** [manejadores.py](../../../backend/app/modules/planificacion/manejadores.py); [flujo.py](../../../backend/app/modules/automatizaciones/flujo.py); [AsistenteFlujo.tsx](../../../frontend/src/features/automatizaciones/AsistenteFlujo.tsx). [Contrato y ejemplos públicos](../../api/contrato-flujo-promociones.md).
- **API/ejemplo:** guardar parámetros no agenda ni autoriza envíos. POST /flujo-automatizacion/programar conserva modelo/modo y crea calendario finito. PUT /promociones/regla habilita una versión; un ajuste nuevo reserva evaluación en su misma sesión. GET /promociones/evaluaciones devuelve motivo y referencias; acciones de gestión requieren Administrador, motivo y tarea sin despacho.
- **Migración/configuración:** `0015_flujo_promociones`; aplicar antes de reiniciar API/worker/Beat; ya aplicada en la instalación habitual. No reescribe 0014 ni tablas de otros cortes. Configuración sin tokens; no altera datos habituales ni ejecuta envíos reales.
- **Pruebas realmente ejecutadas:** suite amplia Windows: 255 passed, 24 skipped, 6 subtests passed, con una expectativa antigua de cabeza Alembic fallida y corregida; después 21 pruebas de flujo/migración/programación correctas. Build Next correcto (incluye /promociones). Corte final de fronteras: 72 passed, 2 skipped, 6 subtests passed. Revisión posterior de promociones/puente: 12 passed, 6 skipped (concurrencia/DDL PostgreSQL). Typecheck final correcto. QA Edge aislada verificó calendario de tres días, pausa, regla versionada, detalle/Escape, dos Excel/cinco CSV y móvil, sin errores JavaScript. Se corrigió una referencia visual de fecha detectada por build y se repitió QA correctamente; build final correcto, 23 páginas generadas; QA final también pasó contra la interfaz compilada, con datos cargados en escritorio y móvil. Después de que Axel abrió Docker, migración y alembic check correctos en PostgreSQL aislado. Corte amplio PostgreSQL/Redis inicial: 125 passed y 4 fallos; una prueba antigua del manejador ausente se aisló explícitamente, y los tres fallos ML se debían a escribir catboost_info en el montaje de código de solo lectura. Revalidación con imagen reconstruida: 24 passed de promociones/motor/inventario, incluida concurrencia, y 3 passed de CatBoost/Beat/plan real desde /tmp escribible. CI incorpora la nueva prueba concurrente. Suite completa final con imagen reconstruida y PostgreSQL/Redis: **283 passed, 6 subtests passed**, sin fallos ni omisiones (290,91 s). Advertencias existentes de dependencias y reflexión SQLite; migración y comparación PostgreSQL correctas. No se enviaron mensajes reales.
- **Dependencias y siguiente paso:** Cueva y Rojas consumen K02; no atribuye nuevas reglas ML a Kevin. Imágenes reconstruidas, 0015 aplicada y servicios habituales activos. Suite final completa correcta. Pendientes: CI remoto y demo conjunta/otra PC. La prueba Telegram automática requiere autorización concreta. No interpretar fixtures del modelo/Telegram como evidencia comercial ni de envío real.
- **Git:** cambios locales en cueva, sin commit/push/PR.

<details><summary>Resumen anterior conservado como historial; no es el estado vigente</summary>

- **Dashboard y Reportes (01-10-2026, Codex para Axel):** gráficos reales en Inicio y `/informes` con ventas, evaluación K03 y estados de pedidos, filtros inclusivos por fecha/modelo, tablas paginadas, detalle en diálogo y CSV completo. 34 pruebas de reportes/ventas/ML correctas; typecheck y build web correctos. API/web activas; lectura real de septiembre: 13.383 unidades, 139 productos, 4.170 pares evaluables. Revisión visual aislada pendiente por ERR_BLOCKED_BY_CLIENT en puerto 3001. [Contrato](../../api/contrato-informes.md); integración transversal en [Cueva](cueva.md). Cambios locales, sin commit ni migración nueva.
- **Flujo completo y claridad transversal (30-09-2026, Codex para Axel):** Pronósticos y panel explican cálculo, modelo, partición, MAE/WAPE y cobertura en lenguaje legible; huellas/JSON técnicos en detalles. Automatización completa conserva pronóstico anterior al objetivo y evaluación posterior. No se cambia modelo, entrenamiento ni política cronológica.

- **Consumo K02/K03 verificado en paso 2 local (2026-09-30, Codex para Axel):** M02 utiliza consultar_corrida/obtener_pronosticos y GENERAR_PROPUESTA enlaza inferencia CatBoost → plan → evaluación histórica con Beat/PostgreSQL/Redis. [Entrega y límites](rojas.md); 140 pruebas y 6 subpruebas correctas. No es una entrega nueva personal de Kevin; falta M03/pedido y revisión antes de publicar.

- **Paso 1 verificado (2026-09-30, Codex para Axel):** E03 carga completa → preparación automática → estado durable → backtest y dashboard, con reintento sin reimportar. Prueba real CatBoost/Beat/PostgreSQL/Redis y fallo de evaluación recuperado reutilizando modelo; suite 128 pruebas + 6 subpruebas correctas. Código en cueva, revisión del PR #11 antes de main. [Contrato](../../api/contrato-importaciones.md#e03-disponible-carga-completa-y-preparación-automática-de-ml).

- **Estado:** K01–K04 implementados y listos para integrar en el prototipo local; no se declara integración con el plan de Max ni con la inicialización E03.
- **Punto de partida alcanzado:** Entrenamiento desde historial E01, artefacto CBM versionado y verificado, inferencia persistida con 13 características temporales, backtest por fecha/revisión, API protegida y panel histórico. El piloto tiene una versión nueva `piloto-q65v2-*` que selecciona iteración con el mismo cuantil 0.65 usado para entrenar. En PostgreSQL/Compose, 4 047 pares evaluables dieron 66 de 90 días con total pronosticado superior al real; la versión anterior se conserva para comparación.
- **Contrato disponible:** [artefacto ML](../../../foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md), [API y servicios](../../api/contratos.md#ventas--pronósticos) y [política de evaluación](../../../foodsave-ml/POLITICA_EVALUACION.md).
- **Entrega a consumidores:** `generar_corrida`/`obtener_pronosticos` y `solicitar_evaluacion_corrida` reciben la sesión del plan sin confirmarla; API `/pronosticos/*`, páginas `/pronosticos` y `/panel`, y adaptadores A03 para preparación/evaluación.
- **Bloqueos:** el CSV piloto ya dispara preparación y evaluación desde la carga web parcial de Edu; E03 completo queda conectado en el paso 1 de cueva; falta que Max consuma la corrida en su plan. No se ha probado el flujo plan/pedido.
- **Siguiente paso:** revisar el corte E03→ML y entregar K02 al consumidor M02; verificar el recorrido en otra computadora.

| Tarea | Estado de seguimiento |
|---|---|
| K01 · Extraer entrenamiento reutilizable | LISTO_PARA_INTEGRAR; entrenó CSV piloto desde E01 en PostgreSQL |
| K02 · Implementar inferencia y persistencia | LISTO_PARA_INTEGRAR; Max aún no consume el servicio |
| K03 · Implementar evaluación histórica | LISTO_PARA_INTEGRAR; backtest PostgreSQL con 4 047 pares |
| K04 · Construir dashboard y vistas de pronóstico | LISTO_PARA_INTEGRAR; API respondió en PostgreSQL y frontend compiló |

</details>



### Dashboard en Inicio y Reportes · 01-10-2026

- **Fecha/zona/autor/estado:** 2026-10-01, America/Bogota. Codex para la solicitud expresa de Axel, bloque K04 de Kevin; coordinación en [Cueva](cueva.md). LISTO_PARA_INTEGRAR local y activo en Compose; no se atribuye una entrega personal a Kevin. Revisión visual de pantallas protegidas pendiente por bloqueo del navegador de pruebas.
- **Comportamiento:** Inicio presenta ventas por día con espacios en fechas desconocidas, ocho productos principales y distribución de pedidos. Reportes filtra hasta 366 días y versión del modelo, reutiliza las métricas K03, distingue ausencia/cero y revisión vigente. Tablas paginadas y productos del pronóstico en diálogo accesible. CSV autenticado de ventas, pares de pronóstico/exclusiones y distribución de pedidos; incluye fecha/fuentes, neutraliza textos de fórmula y exporta todo el período.
- **Archivos/contrato:** [API y fuentes](../../api/contrato-informes.md), [servicio de informes](../../../backend/app/modules/informes/servicio.py), [Reportes](../../../frontend/src/app/informes/page.tsx), [gráficos](../../../frontend/src/components/charts/GraficosOperacion.tsx). `/api/v1/informes/resumen` y `/informes/exportar`; Operador y Administrador. Ejemplo: `?desde=2022-08-24&hasta=2022-08-24`, que conserva 1 pedido ENVIADO y 3 propuestas de esa fecha.
- **Fuentes públicas/dependencias:** Edu publica `resumen_ventas`/`periodo_ventas`; Aguirre `resumen_pedidos`/`periodo_propuestas`; K03 admite desde/hasta sin cambiar su comportamiento anterior cuando faltan filtros. Sin tablas privadas en Informes, commits, cálculo económico, entrenamiento, mensajes ni cambios de stock.
- **Pruebas ejecutadas:** `E03_POSTGRES_TEST=1 python -m pytest -q --tb=short -p no:cacheprovider tests/integration/test_informes.py tests/integration/test_pronosticos_k02_k03.py tests/integration/test_api_inicializacion_ventas.py`: **34 correctas**. Fixture PostgreSQL aislada para API/ventas/pedidos; pruebas K02/K03 usan SQLite según su fixture existente. Verifica permisos, límites, 75 días sin truncar, CSV/BOM/fórmulas, revisiones, MAE/WAPE/cobertura y no duplicar dos intentos ni mover stock. El primer montaje ocultó foodsave-ml; se corrigió la configuración de la prueba y se repitió correctamente.
- **Entorno/despliegue:** `npm run typecheck` correcto; build Next.js de 22 páginas correcto. La reconstrucción completa de API se quedó descargando CatBoost y se canceló; imagen local actualizada sobre sus dependencias ya instaladas/verificadas, sin cambios al Dockerfile fuente. API y frontend activados con Compose sin reconstruir volúmenes. Salud, Inicio y `/informes` HTTP 200; API sin sesión 401 y ambas rutas presentes en OpenAPI. Lectura real 01-09–30-09-2022: 13.383 unidades, 4.170 registros, 139 productos, modelo #2 y 4.170 pares; los tres CSV se generan correctamente.
- **Límites/limpieza/siguiente:** navegador pudo abrir login de 3000 pero bloqueó 3001 con ERR_BLOCKED_BY_CLIENT; no se declara revisión visual ni descarga por navegador verificada. API/frontend temporales y sus dos esquemas propios eliminados; cero esquemas e03_test remanentes. Validar vista protegida y CSV en navegador del usuario; luego retomar promociones/demostración final del plan vigente. Sin commit/PR/remoto ni nuevos mensajes externos. Informes económicos/impacto quedan fuera de este corte.


### Flujo completo, unidades y claridad · 30-09-2026

- **Fecha/zona/autor/estado:** 2026-09-30, America/Bogota. Codex para la tarea de Axel, bloque de bohorquez; coordinación transversal en [Cueva](cueva.md). LISTO_PARA_INTEGRAR local; consumo programado y outbox verificados en pruebas aisladas, sin atribuir autoría a integrantes.
- **Tareas/comportamiento:** K02/K04/K05, presentación y consumidor M02/A02. Se reemplazaron etiquetas visibles de corrida/estado/partición por nombres comprensibles y se aclararon vacíos/métricas. Inicio y guía común enlazan preparación, cálculo y evaluación. El motor programado se comprobó con inferencia controlada en fixture, no constituye un nuevo entrenamiento real.
- **Archivos clave:** [Pronósticos](../../../frontend/src/app/pronosticos/page.tsx), [Panel](../../../frontend/src/app/panel/page.tsx), [guía común](../../../frontend/src/components/layout/GuiaPantalla.tsx).
- **Contrato/ejemplo:** [corte vigente de pedidos](../../api/contrato-pedidos.md#corte-vigente--envío-automático-y-prueba-real--30-09-2026), [A02/unidades](../../api/contratos.md), [programación](../../automatizacion/programacion.md), [diseño](../../diseno/especificacion-visual.md). Elegir AUTOMATICO por programación; 1503 g se presenta como 1,503 kg, sin cambiar API.
- **Configuración/migración:** sin migración nueva sobre 0013, sin secretos registrados. Imágenes finales API/worker/Beat/frontend/migraciones reconstruidas correctamente con docker compose build, sin el servidor temporal de QA. Los servicios habituales se detectaron detenidos durante la tarea y se conservarán apagados; solo PostgreSQL fue encendido temporalmente para QA. Bot/chat propio existente conserva configuración cifrada. Preferencia global manual preservada; no se agenda una hora sin elección del usuario.
- **Pruebas y límites:** 54 passed en PostgreSQL aislado: test_aprobacion_envio_l03.py, test_compras_l02.py, test_programaciones_a02.py y test_planificacion_m02.py. npm run typecheck correcto y 17 comprobaciones exactas de unidades correctas. Los intentos iniciales tuvieron dos expectativas obsoletas (texto de unidad y reloj del motor); se corrigieron y la suite completa pasó. Transporte automático falso, sin acreditar segundo envío real. Navegador comprobó Inicio, menú móvil, selección por nombre/mode y aprobación deshabilitada sin revisión; stock 0,5 kg→500 g en fixture aislada. La fixture SQLite temporal falló con consultas concurrentes y se cambió a PostgreSQL aislado para QA; instalación habitual no tiene ese backend SQLite. QA final: 15 pantallas principales con guía y sin errores de carga, más detalle de ejecución; Panel se verificó después de completar metadatos del modelo falso de la fixture. Entrada 0,5 kg→500 g en PostgreSQL aislado, tabla/fecha histórica comprobadas; se corrigió un catch de consulta abortada que sustituía el objetivo por hoy bajo StrictMode. Imagen final anterior verificó 5 pruebas automáticas adicionales (25 deselected). Typecheck final correcto. Build final correcto; servidor Next del puerto 3001, contenedores/esquema de QA y archivos temporales retirados. SQL final confirma 0 esquemas e03_test, pedido #1 ENVIADO/message_id=2 y 14 ajustes pequeños intactos. Servicios habituales apagados como estaban al terminar la revisión; no se acredita validación visual de todos los formularios ni entrenamiento real.
- **Dependencias/siguiente paso:** Usar modelo listo e historial suficiente para cada fecha demo. Revisar métricas con dataset real completo; no confundir planificación histórica con recurrencia diaria operativa. Coordinación con otros registros enlazados desde dependencias.md.
- **Git:** rama cueva, cambios locales sin commit/push/PR/merge.

### Paso 1 · Inicialización completa → preparación y evaluación ML · 30-09-2026

- **Autor y tareas:** Codex por autorización de Axel, coordinación A04 con E03 y K01/K03. Implementación y prueba de frontera real; no se atribuyen estos cambios a nuevas entregas personales de Edu o Kevin. Plan, compras y promociones siguen pendientes.
- **Comportamiento:** confirmación reserva una única PREPARAR_MODELO en la transacción de la carga. Inicio durable publica ENTRENANDO antes del cálculo; éxito enlaza modelo y backtest; fallo vuelve a DATOS_CARGADOS conservando ventas/recetas/lotes. POST reintentar-preparacion sin archivos reutiliza trabajo activo o reserva generación nueva tras fallo, también cuando falló la evaluación. En ese último caso reutiliza el único modelo ya entrenado. UI refresca estado, muestra trazas y enlace al panel y oculta carga aceptada.
- **Archivos clave/contrato:** [contrato E03](../../api/contrato-importaciones.md#e03-disponible-carga-completa-y-preparación-automática-de-ml), inicializacion/{modelos,servicio,rutas}, pronosticos/{entrenamiento,manejadores}, workers/{motor,tasks/manejadores}, frontend/src/app/inicializacion/page.tsx, tipos/servicios de inicialización, tests/integration/test_inicializacion_ml.py. Coordinación: [Edu](sanchez.md), [Kevin](bohorquez.md), [Axel](cueva.md).
- **Configuración/migración:** nueva 0008_e03_preparacion_ml sobre 0007, sin reescribir previas. Referencias nullable a ejecución/modelo y contador no negativo. CI incorpora E03_POSTGRES_TEST=1 junto a A03/V02; cada prueba PostgreSQL crea su esquema y solo lo elimina al terminar. Cargas previas sin reserva pueden solicitar preparación sin archivos.
- **Pruebas ejecutadas:** suite Docker PostgreSQL/Redis con A03_POSTGRES_TEST=1, V02_POSTGRES_TEST=1, E03_POSTGRES_TEST=1: **128 passed, 6 subtests passed**, sin omisiones, 16 advertencias de dependencias/reflexión SQLite. Caso real: seis meses de ventas de fixture, CatBoost, Beat, backtest fallido controlado, reintento con un único artefacto, dashboard con pares evaluables y conteos de carga invariables. Permisos, reserva/repetición, rollback sin tarea pendiente, reintento simultáneo y recuperación de caída correctos. Upgrade head, downgrade 0007, reaplicación, current --check-heads y alembic check correctos. Frontend npm run typecheck y npm run build correctos (17 rutas). No hubo envíos externos ni cambios en volúmenes de negocio habituales.
- **Límites y siguiente paso:** modelo y evaluación usan estado separado; el test no acredita precisión comercial. Interfaz compilada, sin prueba manual de navegador en este corte. CI remoto pendiente para el commit de entrega. Sigue paso 2 M02 de Max, consumiendo contrato público de Kevin/Vera/M01; revisión antes de main.
- **Commit/PR:** entrega en cueva y seguimiento [PR #11](https://github.com/AXL031/savefood_automatizacion/pull/11), actualizado al alcance del paso 1; hash se consulta en el historial de la rama.


### K01/K03 · Preferencia moderada por pronóstico superior

- **Fecha/hora y zona:** 2026-09-29 (America/Lima).
- **Autor y responsable del bloque:** Codex por solicitud de Axel, trabajando en el bloque de Kevin Bohorquez; no atribuye esta corrección a Kevin.
- **Tareas y estado:** K01/K03, LISTO_PARA_INTEGRAR para el piloto histórico; calidad futura sin validar.
- **Comportamiento disponible:** `artefacto.py` conserva `Quantile:alpha=0.65` y usa la misma pérdida como `eval_metric` para escoger la iteración. Antes usaba MAE para esa selección. Se entrenó la nueva versión `piloto-q65v2-554d4ae35f90`, se evaluó automáticamente y se conservó `piloto-554d4ae35f90` con sus corridas originales. La inferencia sigue redondeando, limitando a cero y excluyendo historial insuficiente/ventas ausentes como antes.
- **Archivos clave:** `foodsave-ml/artefacto.py`, [experimento](../../../foodsave-ml/EXPERIMENTOS_CATBOOST.md), [contrato](../../../foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md), [versión desde la carga](sanchez.md).
- **Contrato/ejemplo:** `PREPARAR_MODELO` con `version_modelo="piloto-q65v2-554d4ae35f90"` guarda otro CBM; `EVALUAR_MODELO` produce backtest de esa versión. El consumidor toma el último modelo `LISTO_DEMO` salvo que pida un `modelo_id` concreto.
- **Configuración/migraciones:** sin migración; imágenes locales de API y worker reconstruidas, volumen y modelos anteriores conservados.
- **Pruebas ejecutadas:** comparación de cuantiles 0.65, 0.7, 0.72, 0.75, 0.8, 0.85 y 0.9 con selección cuantílica en validación. La nueva versión real en PostgreSQL completó `PREPARAR_MODELO` y `EVALUAR_MODELO`: 92 corridas, 4 047 pares evaluables, MAE 4.448 y WAPE 24.20%. En los 90 días evaluables, el total quedó por debajo 24 veces y por encima 66, frente a 52/38 en la versión anterior; faltantes 6 840 frente a 14 940 y sobrantes 11 161 frente a 9 410. Suite backend: 27 passed, 8 skipped, 6 subtests passed. La prueba julio–septiembre 2022 ya estaba inspeccionada y esta comparación es exploratoria, no una validación independiente.
- **Dependencias y siguiente paso:** Max debe consumir una corrida de la versión elegida; Kevin debe comprobar días posteriores no usados para ajuste antes de afirmar calidad fuera del piloto y acordar el costo real entre faltantes y sobrantes con el negocio.
- **Commit/PR:** commit local de `cueva`; push pendiente por Axel.

### K01/K03/K04 · Verificación del consumidor CSV en PostgreSQL

- **Fecha/hora y zona:** 2026-09-29 (America/Lima).
- **Autor y responsable del bloque:** Codex verificando el bloque de Kevin tras la carga parcial de Edu; no atribuye cambios de Kevin a Codex.
- **Tareas y estado:** K01/K03/K04, LISTO_PARA_INTEGRAR; M02 de Max sigue pendiente.
- **Comportamiento disponible:** el CSV real enviado por la nueva ruta de Edu reservó `PREPARAR_MODELO`; Beat/worker completaron el entrenamiento y `EVALUAR_MODELO` en PostgreSQL. API de modelos y evaluación respondió con datos reales. No se modificó código de Kevin.
- **Archivos clave:** [carga de Edu](sanchez.md), `backend/app/modules/pronosticos/entrenamiento.py`, `backend/app/modules/pronosticos/evaluacion.py`.
- **Contrato/ejemplo:** `POST /inicializacion/piloto-bakery` → ejecución `PREPARAR_MODELO` → `EVALUAR_MODELO` → `GET /pronosticos/evaluacion`.
- **Configuración/migraciones:** `0002_e01_ventas` y `0003_pronosticos` aplicadas en Compose; volumen de artefactos compartido.
- **Pruebas:** 1 modelo, 92 corridas y 4 047 evaluaciones persistidas; API de evaluación devolvió 4 047 pares; frontend `/inicializacion` respondió 200. Falta probar consumo M02 y el recorrido en otra PC.
- **Dependencias y siguiente paso:** Edu completa E03; Max integra `generar_corrida` en M02.
- **Commit/PR:** verificación incluida en el commit local de `cueva`; push pendiente por Axel.

### K01–K04 · Intento de arranque en Docker Desktop

- **Fecha/hora y zona:** 2026-09-29 15:01 (America/Bogota).
- **Autor y responsable del bloque:** Codex, verificando el bloque de Kevin Bohorquez a pedido del usuario; no atribuye esta prueba a Kevin.
- **Tareas:** verificación de despliegue de K01–K04 y dependencia A04.
- **Estado:** EN_CURSO; arranque de Compose bloqueado por configuración del host Windows.
- **Qué cambió y qué comportamiento está disponible:** se localizó Docker Desktop 4.93.0 y Docker Compose v5.5.1 en la instalación de usuario; se creó `.env` ignorado por Git con claves aleatorias locales y `docker compose config --quiet` pasó. El motor Linux no arranca; los registros indican `Virtual Machine Platform not enabled` y `No virtualization available`. El procesador reporta virtualización de firmware activada.
- **Archivos clave:** `.env` local ignorado (sin publicar secretos), `compose.yaml`, `backend/Dockerfile`.
- **Contrato/función/ruta y ejemplo:** el recorrido previsto es migración `0002`/`0003` → carga piloto E01 → `PREPARAR_MODELO` → `EVALUAR_MODELO` → `/panel`; aún no se ejecutó en Compose.
- **Migración/configuración necesaria:** habilitar `VirtualMachinePlatform` y WSL 2 en Windows con permisos de administrador, reiniciar la PC y comprobar `docker info` antes de `docker compose up --build -d`.
- **Pruebas:** `docker --version` y `docker compose version` correctos; `docker compose config --quiet` correcto. `docker desktop status` pasó de `starting` a `stopped`; `docker info` devolvió 500. No se ejecutaron migraciones ni carga en PostgreSQL.
- **Qué necesita el siguiente desarrollador y quién es:** Axel o el usuario con permisos de administrador habilita la característica de Windows; después Codex puede continuar el recorrido de prueba.
- **Dependencias/bloqueos:** requiere cambio del sistema y reinicio; la sesión actual no tiene elevación administrativa (`DISM` devolvió error 740).
- **Siguiente paso concreto:** habilitar Virtual Machine Platform y WSL 2 en PowerShell como administrador, reiniciar y volver a comprobar Docker.
- **Commit/PR:** cambios locales, sin commit.

### K03 · Comandos locales verificados y cobertura consistente

- **Fecha/hora y zona:** 2026-09-29 14:47 (America/Bogota).
- **Autor y responsable del bloque:** Codex, trabajando por solicitud del usuario en el bloque de Kevin Bohorquez; no atribuye este ajuste a Kevin.
- **Tareas:** K01/K03, verificación para la demo local.
- **Estado:** LISTO_PARA_INTEGRAR; CLI local ejecutado, Compose pendiente.
- **Qué cambió y qué comportamiento está disponible:** se ejecutaron normalización, entrenamiento CatBoost y verificación del artefacto con el CSV real. Se ajustó el backtest CLI para excluir SKU fuera del modelo o con menos de siete observaciones previas, contar fechas con pares evaluables y coincidir con el resumen backend. El panel usa solo corridas canónicas `backtest-{modelo_id}-{fecha}` para no duplicar una fecha por pruebas adicionales.
- **Archivos clave:** `foodsave-ml/ejecutar_backtest.py`, `foodsave-ml/tests/test_evaluacion_k03.py`, `backend/app/modules/pronosticos/evaluacion.py`.
- **Contrato/función/ruta y ejemplo:** `python foodsave-ml/normalizar_ventas.py --entrada foodsave-ml/bakery_sales_limpio_final.csv --formato bakery --comercio piloto --sucursal principal --salida .tmp/demo_manual`; después `python foodsave-ml/entrenar.py --csv .tmp/demo_manual/ventas_diarias_normalizadas.csv --comercio piloto --sucursal principal --salida .tmp/demo_manual/modelo --version demo-manual-v1`.
- **Migración/configuración necesaria:** ninguna para la CLI independiente; usa dependencias ML de `backend[ml]`. Para el panel persiste la necesidad de `0002_e01_ventas` y `0003_pronosticos`.
- **Pruebas:** los tres comandos locales y `ejecutar_backtest.py` finalizaron correctamente. El reporte CLI y el resumen backend coincidieron en 4047 pares, MAE 6.0168, WAPE 32.73 %, cobertura 79.89 % y 90 fechas evaluables del tramo julio–septiembre 2022. `python -m pytest backend/tests foodsave-ml/tests -q -p no:cacheprovider`: 78 passed, 8 skipped, 6 subtests passed. La CLI no registra el modelo en PostgreSQL ni lo muestra en el panel.
- **Qué necesita el siguiente desarrollador y quién es:** Axel o quien prepare la demo instala Docker/Compose, carga el CSV en PostgreSQL y comprueba la ruta administrativa de preparación; Edu y Max conservan las dependencias E03/M02 indicadas en el resumen.
- **Dependencias/bloqueos:** esta PC no tiene Docker ni PostgreSQL; el arranque completo sigue sin validarse.
- **Siguiente paso concreto:** verificar Compose y el recorrido manual cargar→preparar→evaluar→panel en una máquina con Docker.
- **Commit/PR:** cambios locales, sin commit.

### K01–K04 · Backend, evaluación persistida y panel del piloto

- **Fecha/hora y zona:** 2026-09-29 14:27 (America/Bogota).
- **Autor y responsable del bloque:** Codex, trabajando por solicitud del usuario en el bloque de Kevin Bohorquez; no atribuye estos cambios a Kevin.
- **Tareas:** K01, K02, K03 y K04; coordinación con el corte E01 de Edu.
- **Estado:** LISTO_PARA_INTEGRAR en entorno local; integración externa parcial.
- **Qué cambió y qué comportamiento está disponible:** el worker entrena desde ventas persistidas, exporta CBM/metadata con huella y versión, registra la partición y reserva `EVALUAR_MODELO`. La inferencia usa solo los 28 días previos, valida cobertura/artefacto y guarda corrida y cantidad nullable por producto. K03 conserva evaluaciones por revisión de venta y consolida MAE, WAPE, ±20% y cobertura sobre pares conocidos. K04 expone modelos, corridas, evaluaciones y un panel con serie, fecha, producto y enlace directo a la corrida. Se evitó acceder a tablas privadas de Edu desde los servicios de Kevin.
- **Archivos clave:** `backend/app/modules/pronosticos/{entrenamiento,servicio,evaluacion,rutas,modelos}.py`, `backend/migrations/versions/0003_pronosticos.py`, `backend/app/workers/tasks/manejadores.py`, `frontend/src/app/{pronosticos,panel}/page.tsx`, `frontend/src/components/charts/SerieHistorica.tsx`, `backend/tests/integration/test_pronosticos_k02_k03.py`.
- **Contrato/función/ruta y ejemplo:** `generar_corrida(sesion, ejecucion_id=1, clave_ejecucion="demo-1", fecha_objetivo=date(2022, 8, 24), producto_ids=[1])` devuelve una corrida; `obtener_pronosticos(sesion, corrida.id)` entrega estado y cantidad nullable. `GET /api/v1/pronosticos/evaluacion?modelo_id=1` entrega serie y métricas; `GET /api/v1/pronosticos/corridas/1` entrega trazas por producto. [Contrato completo](../../api/contratos.md#ventas--pronósticos).
- **Migración/configuración necesaria:** `0003_pronosticos` depende de `0002_e01_ventas`; `MODEL_ARTIFACT_DIR`, `ML_COMERCIO_ID`, `ML_SUCURSAL_ID`. El contenedor backend copia `foodsave-ml`; worker comparte el volumen de modelos con API.
- **Pruebas:** `python -m pytest backend/tests foodsave-ml/tests -q -p no:cacheprovider`: **78 passed, 8 skipped, 6 subtests passed**, incluida API protegida. `npm run typecheck` y `npm run build`: correctos. Prueba integral local con CSV real y SQLite temporal: 228936 líneas aceptadas, 1264 negativas excluidas, 27740 ventas diarias, CBM verificado, primera corrida de 139 productos (54 pronósticos disponibles, 38 pares evaluables); backtest canónico del tramo de 92 días: 4047 pares evaluables en 90 fechas, MAE 6.0168 y WAPE 32.73 %. Se excluyó del resumen una corrida exploratoria adicional de la primera fecha, que duplicaba 38 pares; el CLI independiente ahora usa la misma regla de cobertura y arroja iguales métricas. Estos valores son exploratorios de la muestra, no rendimiento comercial. Alembic generó SQL offline PostgreSQL de toda la cadena; no se ejecutó upgrade real ni Compose: Docker y `psql` no están instalados aquí.
- **Qué necesita el siguiente desarrollador y quién es:** Max (M02) llama `generar_corrida` y `obtener_pronosticos` en su transacción de plan, luego `solicitar_evaluacion_corrida`; Edu (E03) reserva `PREPARAR_MODELO` tras primera carga; Axel verifica despliegue A04 con PostgreSQL/Compose.
- **Dependencias/bloqueos:** E01 está consumido localmente, pero su carga integrada E03 y la migración PostgreSQL siguen pendientes; no se declara M02 integrado.
- **Siguiente paso concreto:** aplicar migraciones en PostgreSQL, probar worker/API y enlazar E03 y M02 conservando idempotencia y sesión compartida.
- **Commit/PR:** cambios locales, sin commit.

### K04 · Dashboard y vistas de pronóstico y evaluación histórica

- **Fecha/hora y zona:** 2026-09-29 13:15 (America/Lima)
- **Autor y responsable del bloque:** Kevin Bohorquez
- **Tareas:** K04 (Construir dashboard y vistas de pronóstico)
- **Estado:** LISTO_PARA_INTEGRAR
- **Qué cambió y qué comportamiento está disponible:**
  - Creación de tipos TypeScript en `frontend/src/types/pronosticos.ts` alineados con los contratos de métricas y evaluación.
  - Implementación de `frontend/src/services/pronosticos.ts` con clientes tipados para evaluación histórica y corridas, integrando el escenario demo 2022-08-24 precalculado.
  - Componente `TarjetasMetricas.tsx` mostrando MAE en unidades, WAPE porcentual (con "No definido" si la suma real es 0; sin restar de 100), cobertura y porcentaje dentro de ±20% / ±10%.
  - Componente `GraficoSerieHistorica.tsx`: gráfico SVG reactivo que compara total previsto vs total real por fecha (sumados exclusivamente sobre evaluables), con selector interactivo de fecha e indicación de productos excluidos.
  - Componente `BarrasProductoDia.tsx`: barras horizontales por producto con diferencia absoluta en unidades y badges de tolerancia.
  - Componente `TablaDesgloseProductos.tsx`: auditoría tabular con motivo de exclusión `VENTA_REAL_DESCONOCIDA` para ausencias.
  - Integración en `frontend/src/app/pronosticos/page.tsx` dentro de `ProtectedShell`, y adición del enlace "Pronósticos" en la barra lateral de navegación.
- **Archivos clave:**
  - `frontend/src/types/pronosticos.ts`
  - `frontend/src/services/pronosticos.ts`
  - `frontend/src/components/panel/TarjetasMetricas.tsx`
  - `frontend/src/components/charts/GraficoSerieHistorica.tsx`
  - `frontend/src/components/charts/BarrasProductoDia.tsx`
  - `frontend/src/components/tables/TablaDesgloseProductos.tsx`
  - `frontend/src/app/pronosticos/page.tsx`
  - `frontend/src/components/layout/ProtectedShell.tsx`
- **Contrato/función/ruta y ejemplo de uso:**
  - Ruta frontend: `/pronosticos`
  - Servicios: `obtenerEvaluacionHistorica(token)`, `listarCorridasPronostico(token)`
- **Migración/configuración necesaria:** Ninguna en BD; requiere `npm install` en `frontend/`.
- **Pruebas:** `npm run typecheck` (0 errores de tipos en TypeScript) y `npm run build` en `frontend` (ruta `/pronosticos` compilada y empaquetada estáticamente con éxito).
- **Qué necesita el siguiente desarrollador y quién es:**
  - Todo el equipo puede visualizar el desempeño del modelo y el caso objetivo demo 2022-08-24 directamente desde la interfaz web.
- **Dependencias/bloqueos:** Ninguno; K04 completamente funcional y validado.
- **Siguiente paso concreto:** Implementar modelos y servicio de inferencia K02 en el backend.
- **Commit/PR:** Commits en rama `bohorquez`.

### K03 · Implementación de métricas y evaluación histórica

- **Fecha/hora y zona:** 2026-09-29 12:30 (America/Lima)
- **Autor y responsable del bloque:** Kevin Bohorquez
- **Tareas:** K03 (Implementar evaluación histórica)
- **Estado:** LISTO_PARA_INTEGRAR
- **Qué cambió y qué comportamiento está disponible:**
  - Implementación de `metricas.py` con cálculo contractual de MAE (unidades), WAPE porcentual (retorna `None` si la suma real es cero, jamás calcula `100 - WAPE` ni lo denomina precisión), `% dentro de ±20%` y `±10%` usando `max(real, 1)` y cobertura (ausencia = desconocida, no cero).
  - Implementación de `evaluador.py` con `evaluar_dia` (suma total previsto y real exclusivamente sobre productos con venta real conocida) y `consolidar_evaluacion_tramo` (calcula MAE y WAPE sobre todos los pares producto-día juntos, sin promediar porcentajes diarios).
  - Implementación de `ejecutar_backtest.py`: CLI de simulación histórica que itera fecha por fecha sobre el tramo de prueba reservado, infiriendo un día adelante con ventas estrictamente anteriores y exportando el informe JSON.
- **Archivos clave:**
  - `foodsave-ml/metricas.py`
  - `foodsave-ml/evaluador.py`
  - `foodsave-ml/ejecutar_backtest.py`
  - `foodsave-ml/tests/test_evaluacion_k03.py`
- **Contrato/función/ruta y ejemplo de uso:**
  - `evaluar_pares(pares: Sequence[ParEvaluacion]) -> MetricasResultado`
  - `consolidar_evaluacion_tramo(version, ini, fin, pares) -> EvaluacionTramoCompleto`
  - `python foodsave-ml/ejecutar_backtest.py --artefacto-dir model_artifacts --csv ventas.csv --salida reporte.json`
- **Migración/configuración necesaria:** Ninguna en BD; utiliza dependencias de `requirements.txt`.
- **Pruebas:** `python -m pytest foodsave-ml/tests/test_evaluacion_k03.py -v` (20 passed de K03; 52 passed en total en el módulo).
- **Qué necesita el siguiente desarrollador y quién es:**
  - Max Rojas (M02) y Kevin (K02/K04) reciben la estructura de métricas y evaluación consolidada.
- **Dependencias/bloqueos:** Ninguno para evaluación offline. Persistencia en DB dependerá de K02.
- **Siguiente paso concreto:** Conectar la evaluación histórica al servicio de backend K02 y al panel K04.
- **Commit/PR:** Commits `694b05b` a `85d0fcb` en rama `bohorquez`.

### K01 · Entrenador CatBoost independiente de Colab

- **Fecha/hora y zona:** 2026-09-29 11:15 (America/Lima)
- **Autor y responsable del bloque:** Kevin Bohorquez
- **Tareas:** K01 (Extraer entrenamiento reutilizable)
- **Estado:** LISTO_PARA_INTEGRAR
- **Qué cambió y qué comportamiento está disponible:**
  - Pipeline de entrenamiento local CLI (`entrenar.py`) independiente de Google Colab.
  - Partición temporal según `POLITICA_EVALUACION.md` por meses completos (6, 12 o 24 meses).
  - Vector de 13 características contractuales en orden estricto (`features.py`).
  - Ventanas temporales por días calendario sin imputar ceros en ausencias (`ventanas.py`).
  - Guardado atómico de `catboost_model.cbm` y generación de `metadata.json` con SHA-256 (`artefacto.py`, `metadata.py`).
  - Verificador de integridad CLI (`verificar_artefacto.py`).
- **Archivos clave:**
  - `foodsave-ml/entrenar.py`
  - `foodsave-ml/particion.py`
  - `foodsave-ml/features.py`
  - `foodsave-ml/ventanas.py`
  - `foodsave-ml/artefacto.py`
  - `foodsave-ml/metadata.py`
  - `foodsave-ml/verificar_artefacto.py`
  - `foodsave-ml/tests/test_entrenador_k01.py`
- **Contrato/función/ruta y ejemplo de uso:**
  - `python foodsave-ml/entrenar.py --csv ventas.csv --comercio piloto --sucursal principal --salida model_artifacts`
  - `python foodsave-ml/verificar_artefacto.py --directorio model_artifacts`
- **Migración/configuración necesaria:** Ninguna en BD; escribe en volumen `MODEL_ARTIFACT_DIR`.
- **Pruebas:** `python -m pytest foodsave-ml/tests/test_entrenador_k01.py -v` (27 passed).
- **Qué necesita el siguiente desarrollador y quién es:**
  - Axel (A04) y Kevin (K02) pueden montar el directorio de artefactos y consumir el CBM verificado.
- **Dependencias/bloqueos:** Ninguno; K01 completado e integrado en `main` mediante PR #4.
- **Siguiente paso concreto:** Completar K03 (métricas y backtest) e iniciar K02 (inferencia en backend).
- **Commit/PR:** Pull Request #4 mergeado en `main` (`d016c35`).

### Preparación del registro

- **Autor:** IA que preparó el reparto y guías, sin atribuir implementación a Kevin Bohorquez.
- **Cambio:** se definieron las tareas y el lugar de documentación; no se implementó lógica de este bloque en esta entrega documental.
- **Pruebas:** la revisión de documentación comprueba enlaces, cobertura de carpetas y coherencia del reparto; no acredita funcionamiento del módulo.
- **Próximo autor:** registrar el primer avance con la plantilla y actualizar el resumen vigente.
