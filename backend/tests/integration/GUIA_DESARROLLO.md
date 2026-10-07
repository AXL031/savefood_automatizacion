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

**Integración 30-09-2026:** Pruebas reales de frontera: test_api_inicializacion_ventas.py cubre carga completa/rollback/versiones/stock/API L01; test_proveedores_l01.py incorpora la entrega de Aguirre y rollback del consumidor; test_migraciones_entregas.py ejecuta delta reversible. test_inventario_concurrencia_pg.py requiere V02_POSTGRES_TEST=1 y usa únicamente esquema v02_test_<uuid>.

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](../../../docs/equipo/avances/cueva.md) para el último estado.

## Integración E03/K01

`test_preparacion_e03.py` comprueba HTTP, carga/reintento idempotentes, rollback de reserva, CatBoost/backtest reales y recuperación. `E03_POSTGRES_TEST=1` aplica todas las migraciones en esquemas e03_test_<uuid>, comprueba concurrencia y ejecuta worker/Beat en una cola única de Redis DB 15. No usa ni modifica tablas o colas de la demo.

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

## Corte M02–M04 · 06-10-2026

`test_planificacion_m02.py` consume servicios reales de recetas/stock, verifica suma de ingredientes, cero frente a ausencia, vencimiento, snapshots, conflicto/revisión, rollback y propuesta con CatBoost. Reutiliza fixture E03 aislado; E03_POSTGRES_TEST=1 habilita concurrencia PG. `test_preparacion_e03.py` extiende el recorrido HTTP→Beat→modelo→plan→evaluación. SQLite usa BEGIN explícito para que un savepoint no confirme la transacción exterior.
