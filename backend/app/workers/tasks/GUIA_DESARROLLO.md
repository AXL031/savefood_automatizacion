# Guía de desarrollo — Envoltorios de tareas por dominio

**Carpeta:** `backend/app/workers/tasks`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/automatizacion/flujos.md](../../../../docs/automatizacion/flujos.md).

## Punto de partida

**Paso 2 local · 30-09-2026:** GENERAR_PROPUESTA registra el adaptador M02: corrida → plan → reserva EVALUAR_PRONOSTICO. La salida declara alcance PLAN_M02 y necesidades/pedidos pendientes. La transacción del motor revierte todos esos efectos si falla el consumidor; EVALUAR_PROMOCION sigue pendiente.

**Paso 1 · 30-09-2026:** AL_INICIAR/AL_FALLAR registran callbacks transaccionales del dominio. Solo PREPARAR_MODELO con huella_inicializacion actualiza E03; piloto/manual no modifican inicialización. Los callbacks no hacen commit/rollback ni efectos externos.

`manejadores.py` define `ContextoEjecucion` y el registro explícito `MANEJADORES`. Los adaptadores de Kevin para `PREPARAR_MODELO`, `EVALUAR_MODELO` y `EVALUAR_PRONOSTICO` están registrados; plan y promoción continúan sin manejador y terminan con error visible. Cada dueño registra su función pública `(sesion, contexto) -> dict`, sin commit ni rollback propios. Consultar el resumen vigente de [Axel Cueva](../../../../docs/equipo/avances/cueva.md) y [Kevin Bohorquez](../../../../docs/equipo/avances/bohorquez.md).

Axel mantiene infraestructura; cada dueño implementa la función de su dominio y sus pruebas.

## Integración E03/K01

`AL_INICIAR` y `AL_FALLAR` registran callbacks transaccionales por tipo. PREPARAR_MODELO conecta el estado de E03 solo si la entrada pertenece a esa carga; el éxito lo confirma el handler de Kevin junto al artefacto.

## Trabajo en esta carpeta

1. Crear envoltorios finos de PREPARAR_MODELO, EVALUAR_MODELO, GENERAR_PROPUESTA y EVALUAR_PROMOCION.
2. Kevin implementa entrenamiento/inferencia/evaluación; Max plan; Vera promoción; Aguirre pedido y envío.
3. Usar claves durables y persistir salida/error a través del motor.
4. Separar generación de pedido de intento externo para no reejecutar envío al repetir el plan.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Reentrega usa el resultado persistido y no repite el efecto de dominio.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Paso 3 local · M03 · 30-09-2026

Necesidades y faltantes implementados en la transacción del plan. API/UI conservan aportes, unidades, lotes y lectura de stock; decimales como cadenas, agregación antes de redondear a tres decimales. Producción o stock ausente deja estado INCOMPLETAS y motivo; no se inventan ceros ni se modifica inventario. Migración aditiva 0010_m03_necesidades sobre 0009; planes antiguos quedan PENDIENTE_M03 y el administrador puede completarlos una vez. Servicio público obtener_necesidades y contrato M03 en docs/api/contratos.md. Compras y Telegram siguen pendientes. Cambios locales por Codex para Axel, sin commit ni cambios remotos.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.
