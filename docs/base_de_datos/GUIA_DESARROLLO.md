# Guía de desarrollo — Modelo de datos compartido

**Carpeta:** `docs/base_de_datos`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../equipo/responsabilidades.md).
- [Dependencias entre integrantes](../equipo/dependencias.md).
- [Alcance de la demo](../guia-inicio-desarrollo.md).
- [docs/base_de_datos/esquema-objetivo-mvp.md](esquema-objetivo-mvp.md).

## Punto de partida

**30-09-2026 · Paso 5: migración 0012 agrega destino_credencial_huella a proveedor y revoca verificaciones anteriores; el secreto Telegram cifrado vive fuera de PostgreSQL. Diccionario/esquema/ER reflejan metadatos de verificación.**

**Paso 2 local · 30-09-2026:** esquema/diccionario/ER describen plan y elementos implementados en 0009, referencias/snapshots y cantidades nullable con motivo. La receta es opcional para el elemento impedido.

Archivos técnicos observados al preparar esta guía: `diagrama-entidad-relacion.mmd`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Cada dueño define columnas, nulabilidad, precisión, FK, CHECK e índices de sus entidades.
2. Axel coordina consistencia ER/diccionario/esquema y orden de migración.
3. Edu posee producto/venta/inicialización; Max receta/plan; Kevin ML; Vera stock/promoción; Aguirre compra.
4. No declarar listo 0002 hasta revisar constraints y estrategia de migración entre los seis.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

La tabla de propiedad coincide con reparto; SQL objetivo y API usan las mismas identidades.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../equipo/avances/cueva.md) siguiendo [la plantilla](../equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Paso 3 local · M03 · 30-09-2026

Necesidades y faltantes implementados en la transacción del plan. API/UI conservan aportes, unidades, lotes y lectura de stock; decimales como cadenas, agregación antes de redondear a tres decimales. Producción o stock ausente deja estado INCOMPLETAS y motivo; no se inventan ceros ni se modifica inventario. Migración aditiva 0010_m03_necesidades sobre 0009; planes antiguos quedan PENDIENTE_M03 y el administrador puede completarlos una vez. Servicio público obtener_necesidades y contrato M03 en docs/api/contratos.md. Compras y Telegram siguen pendientes. Cambios locales por Codex para Axel, sin commit ni cambios remotos.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.

## Paso 6 · decisión y envío (0013)

pedido_compra agrega clave_decision varchar(80) única nullable, decidido_por FK usuario nullable, decidido_en timestamptz nullable y decision_json nullable; CHECK exige los cuatro completos o todos NULL. Snapshot de nombre/acción/motivo, sin credencial. Estados incluyen RECHAZADO/PENDIENTE_ENVIO/ENVIANDO/ENVIADO/FALLIDO/PENDIENTE_VERIFICACION además de los previos.

envio_pedido es outbox y evidencia: UNIQUE(pedido_id), numero_intento=1 en este corte, chat_id varchar(64), credencial_huella SHA-256, texto plano congelado, estado, creado_en/inicio_en/fin_en/fecha_telegram, message_id bigint, código/error saneado, despachado_en/lease_hasta/token_despacho. CHECK ENVIADO requiere message_id>0 y fin; otros estados sin message_id. Índice estado/lease. Huella/token_despacho son internos; token del bot sigue cifrado fuera de PostgreSQL. Creación junto a aprobación; llamada externa después de confirmar ENVIANDO. Nuevos intentos/conciliación pendientes del paso 7; nunca borrar auditoría mediante downgrade con decisiones.

## Recuperación L04 · 01-10-2026

Codex para Axel bajo responsabilidad de Aguirre: POST /pedidos/{id}/conciliar registra ENVIADO o NO_ENVIADO con evidencia del último intento incierto; no transmite. POST /pedidos/{id}/reintentar reserva N+1 solo desde FALLIDO y con chat actual revisado/verificado. Conserva texto, plan, cantidades, autorización original e historial. GET incorpora envios/recuperaciones; envio sigue siendo el último. Locks fecha→propuesta→pedido→envío en recuperación/despacho/worker, respuesta tardía obsoleta ignorada. Clave/contenido/actor idempotentes, evidencia chat/message_id única. Usuario Operador consulta; solo Administrador actúa.

Migración aditiva 0014_l04_recuperacion sobre 0013, sin reescribir anteriores; downgrade bloqueado con acciones/reintentos. 57 pruebas PostgreSQL y 7 de migraciones correctas; typecheck/build correctos, API/UI/worker locales actualizados y alembic check sin diferencias. QA visual nuevo no acreditado: navegador integrado rechazó el entorno temporal con ERR_BLOCKED_BY_CLIENT. Pruebas usan transporte falso; no se envió otro Telegram. Contrato vigente: docs/api/contrato-pedidos.md, registro detallado en docs/equipo/avances/aguirre.md. Automático real, promociones y demo conjunta pendientes.
