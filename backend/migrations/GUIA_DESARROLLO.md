# Guía de desarrollo — Migraciones y metadatos

## Conciliación de las revisiones locales · 06-10-2026

La cadena publicada de `origin/cueva` conserva sus revisiones y llega a
`0014_l04_recuperacion`. Las dos revisiones locales `0008_e03_modelo.py` y
`0009_m02_planes.py` mantienen exactamente su contenido en esta carpeta,
fuera de `versions/`; no son nuevas cabezas ni se ejecutan en una base nueva.

Si una base tiene uno de esos IDs, hacer copia de seguridad y detener API,
worker y Beat antes de ejecutar:

```sh
docker compose stop api worker beat
docker compose run --rm --no-deps migraciones python migrations/conciliar_local.py
docker compose up -d
docker compose exec -T api alembic current --check-heads
docker compose exec -T api alembic check
```

Construir previamente las imágenes del código conciliado. El puente usa una
única transacción PostgreSQL: conserva el enlace de preparación, artefactos,
catálogos, ventas, recetas, lotes y movimientos, adopta el esquema publicado
y cambia la revisión solo después de comparar todos los metadatos. Se
detiene sin eliminar datos si hay tareas activas o planes/necesidades
locales guardados; esos casos necesitan convertir sus snapshots en una
migración específica. No marcar una revisión con `stamp` para saltar DDL.
En una base publicada ya en 0014, repetir el puente es una lectura sin cambio.

`test_conciliacion_migraciones.py`, con `E03_POSTGRES_TEST=1`, comprueba en
esquemas aislados conservación de catálogo/estado/enlace/modelo, rollback de
un fallo intermedio y rechazo de planes existentes. Una base nueva utiliza
`alembic upgrade head` normalmente. Esta conciliación no transmite Telegram.

**Carpeta:** `backend/migrations`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../docs/guia-inicio-desarrollo.md).
- [docs/base_de_datos/esquema-objetivo-mvp.md](../../docs/base_de_datos/esquema-objetivo-mvp.md).

## Punto de partida

**30-09-2026 · Paso 5: 0012_l03_telegram_config sobre 0011 añade proveedor.destino_credencial_huella (String 64 nullable, SHA-256, no secreto). Invalida verificaciones heredadas sin evidencia. No modifica revisiones ya aplicadas. Downgrade revoca evidencia y conserva proveedor/chat.**

**Paso 2 local · 30-09-2026:** env.py incorpora PlanProduccion/ElementoPlan y la cabeza aditiva 0009_m02_planificacion. No modifica revisiones previas.

**Integración 30-09-2026:** env.py registra ConfiguracionInicial y todos los modelos nuevos. Cadena única hasta 0007_l01_proveedores. CI ejecuta alembic check sobre PostgreSQL.

Archivos técnicos observados al preparar esta guía: `env.py`, `script.py.mako`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../docs/equipo/avances/cueva.md) para el último estado.

Axel coordina integración de revisiones; no asume las tablas de los seis.

**E01 y Kevin:** `0002_e01_ventas` sucede a `0001c_motor` y crea catálogo/ventas; `0003_pronosticos` añade persistencia de modelo, corridas y evaluaciones. Los demás dominios agregan sus tablas en revisiones posteriores coordinadas, sin alterar migraciones ya aplicadas.

## Trabajo en esta carpeta

1. Coordinar una sola cadena de revisiones; cada dueño entrega sus tablas/restricciones.
2. Comparar modelos, esquema objetivo y migración antes de integrar.
3. No reescribir 0001 ni revisiones aplicadas por compañeros.
4. Probar upgrade en base vacía y restricciones de unicidad/FK/CHECK; documentar rollback de desarrollo.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Una base nueva llega a head y rechaza cantidades/identidades inválidas según contrato.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Paso 3 local · M03 · 30-09-2026

Necesidades y faltantes implementados en la transacción del plan. API/UI conservan aportes, unidades, lotes y lectura de stock; decimales como cadenas, agregación antes de redondear a tres decimales. Producción o stock ausente deja estado INCOMPLETAS y motivo; no se inventan ceros ni se modifica inventario. Migración aditiva 0010_m03_necesidades sobre 0009; planes antiguos quedan PENDIENTE_M03 y el administrador puede completarlos una vez. Servicio público obtener_necesidades y contrato M03 en docs/api/contratos.md. Compras y Telegram siguen pendientes. Cambios locales por Codex para Axel, sin commit ni cambios remotos.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.

## Cabeza vigente · Paso 6 · 0013_l03_aprobacion_envio

Revisión aditiva sobre 0012: decisión completa nullable en pedido_compra (clave única, FK usuario, hora, JSON) y nuevos estados; envio_pedido único por pedido con texto/chat/huella, lease/token, intento 1 y evidencia. ENVIADO exige message_id positivo y fin_en. Conserva borradores existentes. Downgrade admisible sin decisiones; con actividad se detiene sin quitar evidencia y exige migración correctiva. Reversibilidad, preservación de datos y comparación de metadatos en test_migraciones_entregas.py; no reescribir 0011/0012 aplicadas.

## Recuperación L04 · 01-10-2026

Codex para Axel bajo responsabilidad de Aguirre: POST /pedidos/{id}/conciliar registra ENVIADO o NO_ENVIADO con evidencia del último intento incierto; no transmite. POST /pedidos/{id}/reintentar reserva N+1 solo desde FALLIDO y con chat actual revisado/verificado. Conserva texto, plan, cantidades, autorización original e historial. GET incorpora envios/recuperaciones; envio sigue siendo el último. Locks fecha→propuesta→pedido→envío en recuperación/despacho/worker, respuesta tardía obsoleta ignorada. Clave/contenido/actor idempotentes, evidencia chat/message_id única. Usuario Operador consulta; solo Administrador actúa.

Migración aditiva 0014_l04_recuperacion sobre 0013, sin reescribir anteriores; downgrade bloqueado con acciones/reintentos. 57 pruebas PostgreSQL y 7 de migraciones correctas; typecheck/build correctos, API/UI/worker locales actualizados y alembic check sin diferencias. QA visual nuevo no acreditado: navegador integrado rechazó el entorno temporal con ERR_BLOCKED_BY_CLIENT. Pruebas usan transporte falso; no se envió otro Telegram. Contrato vigente: docs/api/contrato-pedidos.md, registro detallado en docs/equipo/avances/aguirre.md. Automático real, promociones y demo conjunta pendientes.

## Corte vigente · 11-10-2026 · Flujo y promociones

Codex para Axel implementó configuración reutilizable, comprobación de requisitos por interfaces públicas, calendario histórico diario de 1–31 días, modelo/modo conservados y pausa/cancelación/reprogramación de tareas sin despacho. Promociones tienen regla inmutable versionada, reserva transaccional después de cada ajuste nuevo de producto y evaluación idempotente con snapshot/motivo; API y pantalla reales. Se conserva la propiedad de cada dominio.

[Contrato vigente, APIs y límites](../../docs/api/contrato-flujo-promociones.md). Aplicar `0015_flujo_promociones` antes de actualizar API/worker/Beat. El diagnóstico no ejecuta inferencia ni envía mensajes; guardar configuración no agenda. Consultas de tareas/evaluaciones admiten paginación real con total. La pausa no recupera horas perdidas: reprogramar antes de reanudar. Deshabilitar promociones afecta ajustes nuevos; tareas ya reservadas conservan su versión. Hora simulada de evaluación avanza por el tiempo real transcurrido desde el ajuste para comprobar frescura.

Las notas fechadas de cortes anteriores son historial; no usar sus pendientes como estado actual. Pruebas y límites finales en los registros Cueva/Vera/Sanchez, incluyendo PostgreSQL/Redis y Telegram real solo si fueron ejecutados. No confundir fixtures QA con datos de operación.

El puente de revisiones locales ahora adopta la cadena hasta 0015 y compara los metadatos actuales. Una base publicada en 0014 se conserva sin cambio por el puente y debe usar `alembic upgrade head` normalmente; una base 0015 es lectura idempotente. No usar el puente para actualizar una instalación activa. Tests del puente PostgreSQL adaptados a la nueva cabeza, aún pendientes de ejecución en este entorno.

## Corte solicitado · 14-10-2026

Codex para Axel. Cabeza 0016_nombre_comercio sobre 0015: normaliza exclusivamente el nombre inicial heredado a Mi comercio. No reemplaza nombres personalizados ni restaura rótulos antiguos en downgrade. Cadena aplicada previamente intacta; puente local adopta 0016 y bases publicadas 0014/0015 usan upgrade normal.


## Gestión y avisos · 14-10-2026 · Codex para Axel

Cabeza 0017_pruebas_proveedor sobre 0016, tabla aditiva de intentos de prueba Telegram con FK a proveedor/usuario, clave única, estado, texto/destino/huella congelados y recibo. No contiene tokens ni toca ventas, stock, modelo o pedidos. Aplicar antes de reiniciar API. Puente de revisiones locales incorpora 0017; bases publicadas 0016 siguen Alembic normal.


## Recepción y corrección autorizadas · 15-10-2026

Codex para Axel coordina Compras/Inventario/Planificación. Contrato vigente: docs/api/contrato-pedidos.md y frontera de inventario en docs/api/contratos.md. Migración aditiva 0018: corrección enlazada de propuesta bloqueada sin envíos, nuevo plan y modo manual; recepción administrativa parcial/completa sobre pedido ENVIADO, con factor guardado, lotes y movimientos RECEPCION atómicos e idempotentes. UI distingue envío del mensaje y llegada física, muestra pendientes/historial y tabla de cantidades. Inventario etiqueta Recepción y filtra nuevas entradas anteriores a fecha_ingreso. Pruebas test_recepcion_compras.py; CI incluye su corte PostgreSQL. No implementa ventas en vivo ni simulación: solo plan en docs/equipo/plan-ventas-vivo-simulacion.md. Registro transversal y resultados reales en avances/cueva.md.


## Pruebas repetibles autorizadas · 21-10-2026

0020_pruebas_repetibles sucede a 0019_tienda_clientes; columna booleana false en propuesta_compra e índice único parcial de activas normales (activa AND NOT prueba_repetible). Conserva registros anteriores y FK/estados. Downgrade se detiene con cualquier prueba conservada. No modificar 0011/0018 ya aplicadas. Base local anterior en 0018 requiere también 0019 aditiva (cliente vacío); backup y validación de datos antes/después en registro Cueva.


## Caja presencial · 26-10-2026

0021 sobre 0020 crea cinco tablas de caja y amplía CHECK de movimientos VENTA/ANULA_VENTA solo de producto con signo correcto. No reescribe revisiones previas ni convierte el histórico. Downgrade bloqueado si existen operaciones de caja. `env.py` importa los modelos nuevos para comparar metadatos. [Contrato implementado](../../docs/api/contrato-caja-presencial.md). Autor de este corte: Codex para Axel; se conservan las responsabilidades de cada dominio. Evidencia y límites en el registro de Cueva.


## Entradas de productos · 28-10-2026

0022 sobre 0021 añade entrada_productos/linea_entrada_productos, lote_producto.fecha_ingreso nullable y CHECK de movimiento ENTRADA positivo de producto. Downgrade bloqueado si existe evidencia. Sin reescritura de revisiones anteriores; aplicar antes de reiniciar API. [Contrato implementado](../../docs/api/contrato-entradas-productos.md). Autor Codex para Axel; dominio Inventario de Vera y responsabilidades de los demás integrantes conservados. Evidencia en avances/cueva.md.

## Acoplamiento de Bohorquez · 28-10-2026

Backport adaptado 4c2a271: [contrato de operaciones](../../docs/api/contrato-operacion-integrada.md). Conserva tienda independiente por HTTP, caja y entradas múltiples de Cueva. Nueva migración 0023 sobre 0022; producción explícita, recepción asistida, avisos/monitor. No publica en tienda ni altera histórico/ML. Evidencia y límites en el registro de Cueva.

## Ampliación vigente · 28-10-2026 · Tienda por API

0024_comercio_tienda es aditiva: cinco tablas comerciales, columnas de integración/canal y segmentos. Mantiene filas y restricciones de identidad por canal; downgrade bloqueado si hay comercio o ventas online. Probar cadena completa y Alembic check en PostgreSQL aislado. No reescribir 0001–0023.
