# Guía de desarrollo — Tipos de contratos

**Carpeta:** `frontend/src/types`.

**Responsable:** Edu Sanchez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contratos.md](../../../docs/api/contratos.md).

## Punto de partida

**30-09-2026 · Paso 5: EstadoTelegram/VerificacionDestino tipan el estado seguro sin token; Proveedor añade destino_verificado_en y verificación efectiva de la credencial vigente.**

**Paso 2 local · 30-09-2026:** planificacion.ts representa cantidades nullable, estados de elemento, snapshots de receta/stock y referencias de corrida/modelo. Necesidades y pedidos siguen pendientes.

**Paso 1 · 30-09-2026:** ConfiguracionInicial incluye modelo_id, preparacion_numero y resumen nullable de preparación/evaluación con estado e ID durable. La carga y el estado de ML no se confunden.

Archivos técnicos observados al preparar esta guía: `api.ts`, `autenticacion.ts`, `automatizacion.ts`, `notificacion.ts`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Edu Sanchez](../../../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

**A01:** `Negocio` incluye `modo_envio_pedidos` como `REQUIERE_APROBACION | AUTOMATICO`; el PATCH acepta un subconjunto de campos. Los consumidores de Compras deben usar estos mismos valores al crear pedidos, sin inventar otros estados.

**A02:** `automatizacion.ts` define programación, ejecución e intento con los estados y campos disponibles en API. Una ejecución pendiente tiene `inicio_en = null` e `intentos = []`.

**A03:** `automatizacion.ts` incluye `despachada_en` y `lease_hasta` de la ejecución. El dueño Axel mantiene estos tipos y el contrato HTTP alineados; Edu coordina la carpeta compartida.

1. Cada dueño mantiene request/response de su dominio; Edu coordina organización.
2. Axel alinea estados de ejecución con esquema de demo y Aguirre los de pedido.
3. Representar null, decimales, fechas y paginación como en API.
4. Distinguir contratos propuestos de implementados; no agregar campos por lo que muestra una maqueta.

`inicializacion.ts` tipa los conteos y la ejecución devueltos por la carga web parcial del CSV bakery. No representa todavía el estado de la primera inicialización completa.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Typecheck y ejemplos de API coinciden en campos y estados.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Paso 3 local · M03 · 30-09-2026

Necesidades y faltantes implementados en la transacción del plan. API/UI conservan aportes, unidades, lotes y lectura de stock; decimales como cadenas, agregación antes de redondear a tres decimales. Producción o stock ausente deja estado INCOMPLETAS y motivo; no se inventan ceros ni se modifica inventario. Migración aditiva 0010_m03_necesidades sobre 0009; planes antiguos quedan PENDIENTE_M03 y el administrador puede completarlos una vez. Servicio público obtener_necesidades y contrato M03 en docs/api/contratos.md. Compras y Telegram siguen pendientes. Cambios locales por Codex para Axel, sin commit ni cambios remotos.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.

## Contrato L03 · Paso 6

Compras incorpora aprobarPedido (clave_idempotencia,chat_id_revisado), rechazarPedido (clave,motivo) y verificarDestinosPropuesta. Pedido incluye decision, destino_actual, mensaje y envio (intento, chat conservado, tiempos/message_id/error saneado). UI conserva clave al repetir una solicitud; 202 es aprobación pendiente de worker, no envío confirmado. Destino actual es consulta viva, snapshots y mensaje aprobado permanecen. No exponer huella/token ni inventar estado ENVIADO. Contrato-pedidos y pruebas L03 son la referencia vigente.
