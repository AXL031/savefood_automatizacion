# Avances — Axel Cueva

**Responsable:** Axel Cueva. **Bloque:** Acceso, configuración y motor de automatizaciones. **Rama prevista:** `cueva`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md). Este archivo se actualiza al terminar cada avance significativo.

## Resumen vigente

- **Estado:** A01 y A02 implementados y listos para integrar; A03/A04 pendientes. Ningún bloque se declara integrado hasta que su consumidor pruebe la frontera.
- **Comportamiento disponible:** A01 ofrece identidad, roles, error uniforme y configuración del modo de pedidos. A02 guarda programaciones y ejecuciones pendientes idempotentes, permite consultar estados e intentos y ofrece servicios transaccionales sin commit para eventos y resultados de los módulos. `0001a_configuracion` y `0001b_automatizaciones` están aplicadas en PostgreSQL local. La UI de automatizaciones usa las rutas reales y muestra el escenario histórico separado de la hora real.
- **Contrato disponible:** [A01 y A02 en contratos HTTP](../../api/contratos.md), [rutas disponibles](../../api/rutas-api.md), `obtener_modo_envio_pedidos(sesion)` y `automatizaciones.servicio` (`crear_o_recuperar_ejecucion`, `iniciar_intento`, `finalizar_intento`).
- **Entrega a consumidores:** Edu puede consumir sesión/error y crear la ejecución de preparación de modelo en su transacción de carga; Kevin, Vera, Max y Aguirre pueden usar claves y trazas A02 para sus servicios con fixtures. Todos pueden iniciar su bloque; la integración de despacho/cálculos espera A03 y las entregas de dominio de la [matriz](../dependencias.md). Cada consumidor registra su prueba de frontera.
- **Bloqueos:** no hay bloqueo para empezar a desarrollar ni para consumir A01/A02. Beat, lease, reintentos automáticos y la migración compartida `0002` siguen pendientes; no se ha probado el recorrido completo ni un envío Telegram.
- **Siguiente paso:** A03 implementa despacho recuperable sobre estas tablas y conecta las funciones públicas de dominio cuando estén entregadas. La futura `0002` debe depender de `0001b_automatizaciones`.

| Tarea | Estado de seguimiento |
|---|---|
| A01 · Completar identidad, roles y configuración | LISTO_PARA_INTEGRAR; consumidor aún por verificar |
| A02 · Construir programaciones y ejecuciones durables | LISTO_PARA_INTEGRAR; consumidor aún por verificar |
| A03 · Implementar Beat y recuperación | PENDIENTE DE VERIFICAR / COMPLETAR |
| A04 · Preparar infraestructura común | PENDIENTE DE VERIFICAR / COMPLETAR |

## Bitácora

### 2026-09-27 11:07 America/Lima — corte 2: programación y ejecuciones durables

- **Autor:** IA de la sesión para el bloque de Axel Cueva. **Tarea:** A02. **Estado:** LISTO_PARA_INTEGRAR; falta prueba de consumo por Edu, Kevin, Vera, Max y Aguirre. Cambios locales en `cueva` al registrar esta entrada.
- **Qué cambió:** `POST /api/v1/programaciones-demo` valida reloj UTC futuro, reloj local histórico, fecha coincidente, 1–5 IDs de producto y clave. Guarda programación más ejecución `PENDIENTE` de forma atómica; una misma clave/entrada recupera el ID y otra entrada da 409. Las rutas GET listan y detallan programaciones, ejecuciones e intentos. El servicio público crea/recupera ejecuciones de eventos, inicia y finaliza intentos sin confirmar la sesión del consumidor. Las pantallas reales muestran estados y referencias temporales sin fingir resultados.
- **Archivos clave:** [servicio](../../../backend/app/modules/automatizaciones/servicio.py), [API](../../../backend/app/modules/automatizaciones/rutas.py), [modelo](../../../backend/app/modules/automatizaciones/modelos.py), [migración](../../../backend/migrations/versions/0001b_automatizaciones.py), [prueba A02](../../../backend/tests/integration/test_programaciones_a02.py), [pantalla](../../../frontend/src/app/automatizaciones/page.tsx) y [detalle](../../../frontend/src/app/automatizaciones/ejecuciones/[id]/page.tsx).
- **Contrato/ejemplo:** [contrato A02](../../api/contratos.md#contrato-a02-programación-y-trazas-persistidas). Un `POST` con Bearer Administrador, `tipo=GENERAR_PROPUESTA`, `ejecutar_desde_utc` futuro, `fecha_hora_simulada_local=2022-08-24T10:00:00`, `fecha_objetivo_demo=2022-08-24`, `producto_ids=[1,2,3]` y `clave_idempotencia=demo-propuesta-2022-08-24-v1` devuelve `ejecucion_id` pendiente. Para la carga, Edu puede llamar `crear_o_recuperar_ejecucion(sesion, "PREPARAR_MODELO", clave, {"importacion_id": id})` dentro de su propia transacción y hacer rollback junto con su carga.
- **Configuración/migración:** `0001b_automatizaciones` depende de `0001a_configuracion` y crea las tres tablas con unicidad, claves externas, estados e índices. `alembic current` en PostgreSQL local confirma `0001b_automatizaciones (head)`. La futura `0002` depende de esta cabeza. No se añadieron credenciales ni se modificó `0001_nucleo`.
- **Pruebas ejecutadas:** suite Python equivalente al paso CI: `24 passed, 6 subtests passed`, una advertencia de deprecación de TestClient; cubre permisos, validación, idempotencia, consultas, rollback y trazas. `npm run typecheck` y `npm run build` terminaron correctamente. Docker reconstruyó la API y aplicó `alembic upgrade head`; una prueba con servicio real en PostgreSQL creó ejecución pendiente y su rollback dejó `None`. API local: `/salud` 200 y programaciones sin token 401. `git diff --check` sin errores. El flujo de GitHub Actions y una sesión de navegador con administrador real no se han ejecutado.
- **Dependencias/siguiente paso:** Edu, Kevin, Vera, Max y Aguirre pueden desarrollar su dominio con el contrato y fixtures; cada uno debe probar su consumidor antes de declararlo integrado. A03 aportará Beat, lease y reintentos automáticos; los cálculos de ML, plan, stock, pedidos y promoción pertenecen a sus responsables. La UI solicita IDs manuales hasta que Edu entregue catálogo; aún no verifica que existan. Ningún intento se inicia automáticamente ni se envía Telegram en A02.
- **Commit/PR:** entrega de A01 y A02 en la rama `cueva`, con commit de mensaje corto; sin PR. El identificador se consulta en el historial Git de la rama.

### 2026-09-27 10:43 America/Lima — corte 1: acceso y configuración

- **Autor:** IA de la sesión para el bloque de Axel Cueva. **Tarea:** A01. **Estado:** LISTO_PARA_INTEGRAR, cambios locales en rama `cueva`, sin commit ni PR; falta prueba de consumo por Edu y Aguirre.
- **Qué cambió:** se unificó `error.codigo/mensaje/detalles`, se corrigió el 401 sin Bearer, se mantuvo 403 para Operador, se validan zona IANA, moneda y modo antes de guardar, y la configuración muestra el selector real. Las solicitudes protegidas que reciben 401 limpian sesión y vuelven al acceso. El selector no genera ni envía pedidos por sí mismo.
- **Archivos clave:** [identidad](../../../backend/app/core/identidad.py), [errores](../../../backend/app/core/errores.py), [negocio](../../../backend/app/modules/negocios/rutas.py), [lectura pública](../../../backend/app/modules/negocios/servicio.py), [migración](../../../backend/migrations/versions/0001a_configuracion.py), [configuración web](../../../frontend/src/app/configuracion/page.tsx) y [prueba](../../../backend/tests/integration/test_acceso_configuracion.py).
- **Contrato y ejemplo:** [A01 en contratos HTTP](../../api/contratos.md#contrato-a01-disponible-acceso-y-configuración). `PATCH /api/v1/negocios/actual` con Bearer Administrador y `{"modo_envio_pedidos":"AUTOMATICO"}` devuelve el negocio actualizado; la lectura pública `obtener_modo_envio_pedidos(sesion)` no hace commit. `PATCH` como Operador devuelve `403 PERMISO_DENEGADO`; zona inválida devuelve `422 DATOS_INVALIDOS` sin cambios.
- **Configuración/migración:** `0001a_configuracion` depende de `0001_nucleo`, agrega `negocio.modo_envio_pedidos` con valor inicial manual y `CHECK`. La futura `0002` debe depender de `0001a_configuracion`. Se agregó `tzdata` para validar IANA también en Windows. Se creó `.env` local ignorado por Git con secretos aleatorios, sin token de Telegram; PostgreSQL, Redis y API quedaron encendidos para verificación local.
- **Pruebas ejecutadas:** `python -m pytest backend/tests/unit backend/tests/integration/test_acceso_configuracion.py -q`: 16 passed, 6 subtests passed, una advertencia de deprecación de TestClient; `npm run typecheck`: correcto; `npm run build`: correcto. `alembic heads` y SQL offline mostraron `0001a_configuracion`; `docker compose run --rm --no-deps api alembic upgrade head` terminó correctamente en PostgreSQL vacío. En PostgreSQL se confirmó la revisión, valor inicial y `CHECK`; un `UPDATE` inválido fue rechazado y el valor quedó intacto. API local: `/salud` 200, negocio sin Bearer 401, ruta ausente 404 con sobre de error. No se probó todavía una sesión de navegador conectada al PostgreSQL ni el consumo de Compras, que aún no existe.
- **CI:** se añadió la prueba A01 al paso Python de `base-ci.yml`; el flujo completo de GitHub Actions todavía no se ha ejecutado para estos cambios locales.
- **Suite conjunta local:** el comando Python configurado en CI, con `foodsave-ml/tests`, terminó con 21 passed, 6 subtests passed y la misma advertencia de TestClient. Incluye token vencido y confirma que A01 no rompe las pruebas actuales de promoción y normalización de ventas.
- **Cliente compartido:** `HttpError` conserva `status`, `codigo` y `detalles` del sobre; las pantallas futuras pueden mostrar errores por campo sin extraer significado del mensaje. Typecheck volvió a pasar después de este ajuste.
- **Límite de la instalación local:** esta base PostgreSQL nueva todavía no tiene un usuario administrador. Para probar el inicio de sesión en la interfaz, ejecutar `docker compose exec api python -m app.core.crear_admin` e introducir correo y contraseña propios. El frontend no quedó levantado; sí API, PostgreSQL y Redis. No se añadieron credenciales de prueba al repositorio.
- **Dependencias y siguiente paso:** Edu debe comprobar el cliente HTTP con una ruta propia; Aguirre debe usar el modo dentro de su transacción y copiarlo al pedido. Axel sigue con A02; A03/A04 continúan pendientes. Ningún envío a Telegram se ejecutó.

### 2026-09-26 20:31 America/Lima — reparto, guías y registro de avances

- **Autor:** IA de la sesión, preparando documentación transversal para el equipo. Axel figura como coordinador, no como autor de implementación de los otros cinco bloques.
- **Estado de esta entrega:** LISTO_PARA_INTEGRAR, cambios locales sin commit. A01–A04 no se marcan completas por este trabajo documental.
- **Qué cambió:** se aplicó el reparto aprobado en el README, asignaciones de tablas y especificación funcional. Se añadieron 115 guías de carpeta, 24 tareas principales con aceptación y seis registros de avance. Nueve carpetas nuevas contienen únicamente documentación de funciones que no tenían ubicación.
- **Archivos clave:** [README principal](../../../README.md), [responsabilidades](../responsabilidades.md), [mapa de carpetas](../mapa-carpetas.md), [dependencias](../dependencias.md), [instrucciones IA](../../../AGENTS.md) y [plantilla de registro](README.md).
- **Contrato entregado:** cada carpeta identifica responsable, alcance, tareas, entradas/salidas, aceptación y registro. Las dependencias identifican proveedor, consumidor, trabajo adelantable y bloqueo real. Cada avance significativo debe actualizar resumen vigente y bitácora antes de entregarse.
- **Ejemplo para el siguiente integrante:** Max abre rojas.md, consulta M02 en responsabilidades, revisa los registros bohorquez.md y vera.md, y usa la guía de backend/app/modules/planificacion. Al entregar su servicio, registra contrato, archivos y prueba para Aguirre.
- **Verificación:** comprobación local con Node de cobertura 115/115, dueños válidos, presencia de instrucciones de seguimiento y enlaces Markdown locales sin destinos rotos; 24 IDs de tareas presentes en el reparto. Revisión de whitespace mediante `git -c core.safecrlf=false diff --check`. Se corrigieron enlaces de responsables antiguos y un salto final sobrante. No se modificó lógica Python/TypeScript ni se ejecutaron pruebas de aplicación para esta entrega documental.
- **Configuración/migración:** ninguna nueva para usar estas guías. Conservar los cambios de alcance/pedidos y configuración que ya estaban en la sesión.
- **Pendientes:** los cuerpos exactos de API, restricciones finales de 0002 y la política de recompra entre planes siguen como trabajo de definición asignado; no confundir guías completas con backend implementado.
- **Siguiente paso:** cada integrante toma su primer ID, entrega contrato y fixture al consumidor y documenta el primer corte funcional en su registro.

### Preparación del registro

- **Autor:** IA que preparó el reparto y guías, sin atribuir implementación a Axel Cueva.
- **Cambio:** se definieron las tareas y el lugar de documentación; no se implementó lógica de este bloque en esta entrega documental.
- **Pruebas:** la revisión de documentación comprueba enlaces, cobertura de carpetas y coherencia del reparto; no acredita funcionamiento del módulo.
- **Próximo autor:** registrar el primer avance con la [plantilla](README.md) y actualizar el resumen vigente.

