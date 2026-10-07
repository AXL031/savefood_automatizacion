# Guía de desarrollo — Integración continua

**Carpeta:** `.github/workflows`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../docs/guia-inicio-desarrollo.md).
- [docs/equipo/arranque-modulos.md](../../docs/equipo/arranque-modulos.md).

## Punto de partida

**30-09-2026 · Paso 5: suite Python descubre test_telegram_config_l03.py; el corte Docker PostgreSQL incluye el mismo archivo y prueba cifrado/API sin Telegram real. CI remoto pendiente; cambios sin publicar.**

**Paso 2 local · 30-09-2026:** base-ci.yml añade test_planificacion_m02.py al corte PostgreSQL/Redis y el test real E03 incluye la propuesta M02. Cambio solo local; no se ha publicado ni ejecutado CI remoto para este paso.

**Paso 1 · 30-09-2026:** CI añade E03_POSTGRES_TEST=1 a las pruebas Docker e incluye test_api_inicializacion_ventas.py y test_inicializacion_ml.py junto con A03/V02. El flujo real usa seis meses de datos de prueba, no archivos de negocio ni Telegram.

**Integración 30-09-2026:** CI comprueba alembic check después del upgrade y ejecuta A03/V02 en PostgreSQL/Redis con flags explícitos. Las pruebas V02 crean y eliminan solo sus esquemas aislados.

Archivos técnicos observados al preparar esta guía: `base-ci.yml`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../docs/equipo/avances/cueva.md) para el último estado.

## Integración E03/K01

CI incluye E03 en PostgreSQL/Redis: migración completa sobre esquema vacío, carga automática, entrenamiento/evaluación reales, reintentos y Beat. Validación remota pendiente hasta publicar los cambios.

## Trabajo en esta carpeta

**A01:** `base-ci.yml` incluye la prueba de contrato HTTP y configuración de Axel con SQLite aislado. El paso de Compose aplica también `0001a_configuracion` en PostgreSQL. Esta prueba no sustituye las futuras pruebas de Beat, Compras o consumidores.

**A02:** el paso Python incluye `test_programaciones_a02.py` y el upgrade de Compose alcanza `0001b_automatizaciones`. El CI remoto todavía debe ejecutarse al publicar los cambios.

**A03:** el paso Python incluye toda la suite `backend/tests/integration`; el paso Docker aplica `0001c_motor` al iniciar Compose y ejecuta la prueba A03 aislada con PostgreSQL y Redis. La validación remota sigue pendiente hasta publicar estos cambios.

**A04:** el flujo se dispara en push de cualquier rama y PR, instala el extra `ml`, exige `alembic current --check-heads` y prueba que worker puede escribir y API leer el mismo volumen de artefactos. El token Telegram permanece vacío en CI; ningún paso envía mensajes externos. Confirmar la ejecución remota antes de declararla validada.

1. Mantener base-ci.yml con instalación reproducible y validación de Compose.
2. Integrar pruebas unitarias y de frontera que aporta cada responsable.
3. Comprobar migraciones, API y cola; incorporar Beat cuando exista su implementación.
4. Sustituir Telegram por un adaptador falso en CI y mostrar registros de fallo sin secretos.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

El flujo falla ante una regresión significativa y detiene servicios al terminar; documentar lo no cubierto.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Paso 3 local · M03 · 30-09-2026

Necesidades y faltantes implementados en la transacción del plan. API/UI conservan aportes, unidades, lotes y lectura de stock; decimales como cadenas, agregación antes de redondear a tres decimales. Producción o stock ausente deja estado INCOMPLETAS y motivo; no se inventan ceros ni se modifica inventario. Migración aditiva 0010_m03_necesidades sobre 0009; planes antiguos quedan PENDIENTE_M03 y el administrador puede completarlos una vez. Servicio público obtener_necesidades y contrato M03 en docs/api/contratos.md. Compras y Telegram siguen pendientes. Cambios locales por Codex para Axel, sin commit ni cambios remotos.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.
