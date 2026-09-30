# Guía de desarrollo — Migraciones y metadatos

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
