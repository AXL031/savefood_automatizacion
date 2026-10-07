# Guía de desarrollo — Planificación y necesidades de ingredientes

**Carpeta:** `backend/app/modules/planificacion`.

**Responsable:** Max Rojas. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Ingredientes, recetas y planificación. **Tareas:** M02, M03, M04.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contratos.md](../../../../docs/api/contratos.md).
- [docs/api/contrato-pedidos.md](../../../../docs/api/contrato-pedidos.md).

## Punto de partida

**Paso 2 local · 30-09-2026:** M02 implementa generar_plan, API /planes y snapshots reproducibles de corrida/receta/stock. Los estados por producto preservan cantidades null con motivo; no mueve saldos. GENERAR_PROPUESTA enlaza inferencia, plan y evaluación en una transacción. M03 quedó implementado en el paso 3 local (ver actualización al final); [contrato M02](../../../../docs/api/contratos.md#m02--paso-2-local-plan-reproducible).

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Max Rojas](../../../../docs/equipo/avances/rojas.md) para el último estado.

## Trabajo en esta carpeta

1. Consumir pronóstico de Kevin y stock por fecha de Vera mediante interfaces públicas.
2. Calcular producción con margen cero y guardar receta/stock/pronóstico de referencia.
3. Sumar necesidades por ingrediente antes del redondeo final y calcular faltantes.
4. Entregar plan y necesidades a Compras; mantener los planes anteriores cuando cambien entradas.
5. Construir detalle de cantidades, avisos y enlaces a corrida/pedidos.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `plan_produccion`, `elemento_plan`, `necesidad_ingrediente`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Corrida, recetas versionadas, disponibilidad por fecha y clave de operación.
- **Entrega:** Plan reproducible y necesidades para Aguirre.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- No modifica inventario y no inventa ceros para predicción no disponible.
- Ingrediente compartido por varios productos se suma una vez correctamente.
- Repetir entrada recupera el plan; recálculo conserva el anterior.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/rojas.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Paso 3 local · M03 · 30-09-2026

Necesidades y faltantes implementados en la transacción del plan. API/UI conservan aportes, unidades, lotes y lectura de stock; decimales como cadenas, agregación antes de redondear a tres decimales. Producción o stock ausente deja estado INCOMPLETAS y motivo; no se inventan ceros ni se modifica inventario. Migración aditiva 0010_m03_necesidades sobre 0009; planes antiguos quedan PENDIENTE_M03 y el administrador puede completarlos una vez. Servicio público obtener_necesidades y contrato M03 en docs/api/contratos.md. Compras y Telegram siguen pendientes. Cambios locales por Codex para Axel, sin commit ni cambios remotos.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.

## Claridad y flujo completo · 30-09-2026

GENERAR_PROPUESTA pasa modo_envio_pedidos conservado a generar_pedidos; sin valor usa negocio vigente. Consume M03 y compras en misma transacción. Resultado de compra/outbox no equivale a entrega Telegram.

## Conciliación de cueva

Conciliación 06-10-2026: prevalece el contrato que consume compras (elementos nullable con estados y necesidades conservadas). Las fechas de lectura/creación se serializan siempre en UTC; las pruebas del corte local se conservan adaptadas en test_planificacion_conciliada.py y usan cinco CSV sintéticos.
