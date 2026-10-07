# Guía de desarrollo — Revisiones Alembic

**Carpeta:** `backend/migrations/versions`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../docs/guia-inicio-desarrollo.md).
- [docs/base_de_datos/esquema-objetivo-mvp.md](../../../docs/base_de_datos/esquema-objetivo-mvp.md).

## Punto de partida

**30-09-2026 · Paso 5: cabeza 0012_l03_telegram_config; columna nullable de huella en proveedor, sin token en DB. Upgrade/downgrade invalidan verificaciones, conservan catálogo/chat. Prueba reversible y de datos en test_migraciones_entregas.py.**

**Paso 2 local · 30-09-2026:** 0009_m02_planificacion sobre 0008 crea plan/elementos, FKs, unicidad, estados nullable y CHECK de fórmula. NecesidadIngrediente corresponde al siguiente paso.

**Paso 1 · 30-09-2026:** 0008_e03_preparacion_ml añade a configuracion_inicial referencias de preparación/modelo y contador no negativo. Upgrade, downgrade a 0007 y reaplicación verificados en PostgreSQL; revisión previa conservada.

**Integración 30-09-2026:** Nuevas revisiones 0005_m01_ingredientes_recetas → 0006_v01_inventario → 0007_l01_proveedores sobre 0004. Las revisiones previamente aplicadas no se reescriben. Delta reversible probado en SQLite; cadena completa PostgreSQL se verifica en CI.

Archivos técnicos observados al preparar esta guía: `0001_nucleo.py`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../../docs/equipo/avances/cueva.md) para el último estado.

Axel coordina integración de revisiones; no asume las tablas de los seis.

**Cadena tras Kevin:** `0001_nucleo → 0001a_configuracion → 0001b_automatizaciones → 0001c_motor → 0002_e01_ventas → 0003_pronosticos`. `0002` agrega catálogo y ventas; `0003` agrega persistencia ML. Las siguientes revisiones de dominio dependen de `0003_pronosticos` o de su sucesora, sin modificar migraciones ya aplicadas. Coordinar tipos, FK y CHECK restantes con sus dueños.

## Integración E03/K01

0008_e03_preparacion_ml es la revisión publicada tras 0007; la única cabeza es 0014_l04_recuperacion. Las dos revisiones locales se conservan sin alterar contenido en la carpeta padre, fuera del descubrimiento de Alembic. Consultar conciliar_local.py y la guía padre antes de actualizar una base con esos IDs.

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

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

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
