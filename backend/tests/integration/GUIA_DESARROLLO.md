# Guía de desarrollo — Pruebas de transacciones y fronteras

**Carpeta:** `backend/tests/integration`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../docs/guia-inicio-desarrollo.md).
- [docs/guia-inicio-desarrollo.md](../../../docs/guia-inicio-desarrollo.md).

## Punto de partida

**30-09-2026 · Paso 5: test_telegram_config_l03.py cubre cifrado/persistencia, permisos API, bot, vínculo, rotación/deshabilitación, búsqueda /start sin confirmar updates, webhook y permisos de grupo con transporte falso; test_migraciones_entregas.py verifica 0012 y conservación de proveedor/chat. Fixtures aíslan secretos/credencial de prueba. No se envían mensajes reales.**

**Paso 2 local · 30-09-2026:** test_planificacion_m02.py prueba snapshots, estados desconocidos, caducidad/límite, recálculo, permisos, rollback del consumidor, reentrega y concurrencia PostgreSQL (E03_POSTGRES_TEST=1). La prueba real de test_inicializacion_ml.py incorpora Beat → inferencia CatBoost → plan → evaluación posterior.

**Paso 1 · 30-09-2026:** test_inicializacion_ml.py verifica reservas, permisos, rollback, reintento concurrente y recuperación. E03_POSTGRES_TEST=1 habilita la fixture API en esquemas e03_test_<uuid> y el recorrido real CatBoost/Beat/Redis: fallo de backtest y recuperación sin reentrenar. Solo limpia su esquema, cola y artefactos temporales.

**Integración 30-09-2026:** Pruebas reales de frontera: test_api_inicializacion_ventas.py cubre carga completa/rollback/versiones/stock/API L01; test_proveedores_l01.py incorpora la entrega de Aguirre y rollback del consumidor; test_migraciones_entregas.py ejecuta delta reversible. test_inventario_concurrencia_pg.py requiere V02_POSTGRES_TEST=1 y usa únicamente esquema v02_test_<uuid>.

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](../../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

**A01:** `test_acceso_configuracion.py` comprueba rutas reales de FastAPI, roles y persistencia con SQLite temporal y un `char_length` de prueba. Se ejecuta en CI sin servicios externos; la migración se verifica por separado con PostgreSQL en Compose.

**A03:** `test_motor_a03.py` prueba política local sin servicios y, con `A03_POSTGRES_TEST=1`, usa un esquema PostgreSQL aislado y Redis de pruebas para concurrencia, recuperación, reintentos y Beat real. Ejecutar esa parte dentro de Compose con PostgreSQL y Redis levantados. Los handlers de prueba son efectos locales controlados, no módulos de negocio integrados.

1. Edu prueba rollback total de carga con servicios de Max/Vera.
2. Vera prueba ajustes concurrentes con PostgreSQL real.
3. Axel prueba Beat/reentrega/recuperación con Redis; cada dueño valida efecto final.
4. Aguirre prueba timeout del cliente falso y control de recompra; Kevin prueba persistencia de evaluación.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Los fallos inducidos dejan estados recuperables y no duplican saldos, planes o pedidos.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Paso 3 local · M03 · 30-09-2026

Necesidades y faltantes implementados en la transacción del plan. API/UI conservan aportes, unidades, lotes y lectura de stock; decimales como cadenas, agregación antes de redondear a tres decimales. Producción o stock ausente deja estado INCOMPLETAS y motivo; no se inventan ceros ni se modifica inventario. Migración aditiva 0010_m03_necesidades sobre 0009; planes antiguos quedan PENDIENTE_M03 y el administrador puede completarlos una vez. Servicio público obtener_necesidades y contrato M03 en docs/api/contratos.md. Compras y Telegram siguen pendientes. Cambios locales por Codex para Axel, sin commit ni cambios remotos.

## Gestión de usuarios local · 30-09-2026

A01 ampliado por Codex para Axel: API /usuarios y pantalla administrativa para listado, creación, edición de datos/roles y activación. Contraseñas protegidas y respuestas sin hash; última cuenta administrativa activa protegida con locks ordenados. Sin migración. PostgreSQL: 13 pruebas de usuarios/acceso correctas, incluidas operaciones concurrentes. Typecheck y build correctos. Guía/mapa de /usuarios actualizados; sin publicación remota.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.

## Paso 6 · pruebas L03

test_aprobacion_envio_l03.py verifica API real→decisión→outbox→worker con Telegram simulado: permisos, auditoría, clave/duplicados, rechazo incluso bloqueado, chat/token cambiados, reserva de fecha, stock intacto, publicación perdida, interrupción y confirmación tardía sin retry. PostgreSQL con E03_POSTGRES_TEST=1 prueba carreras entre decisiones y entre despachos/workers. Fixture usa esquemas aislados y nunca envía mensajes reales. Migración 0013 se compara con modelos, conserva borradores y rechaza downgrade que borraría decisiones. El check de tipos/build no sustituye estas pruebas.

## Claridad y flujo completo · 30-09-2026

test_aprobacion_envio_l03 cubre automático sin decisión manual, deduplicación, revalidación, actualización sin envío sorpresa y motor programado → plan → outbox → Telegram falso. Usar E03_POSTGRES_TEST=1 para esquemas aislados. El transporte falso no acredita envío real.

Los casos de recompra y aprobación/envío también verifican los avisos para borrador, envío autorizado y enviado: no recomendar cancelar un pedido ya autorizado o transmitido, sin duplicar red ni movimientos.
