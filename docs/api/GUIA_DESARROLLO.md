# Guía de desarrollo — Catálogo y contratos HTTP

**Carpeta:** `docs/api`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../equipo/responsabilidades.md).
- [Dependencias entre integrantes](../equipo/dependencias.md).
- [Alcance de la demo](../guia-inicio-desarrollo.md).
- [docs/api/rutas-api.md](rutas-api.md).

## Punto de partida

**30-09-2026 · Paso 5: contrato-pedidos.md define configuración cifrada/bot/chat, búsqueda /start, códigos, permisos y límites; rutas-api.md publica rutas reales. Verificación de acceso no acredita entrega. Pasos 6/7 pendientes.**

**Paso 2 local · 30-09-2026:** contratos.md y rutas-api.md documentan /planes y la frontera M02; necesitan migración 0009. Necesidades M03 y compras siguen como diseño pendiente.

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](../equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Cada dueño define cuerpos, campos, permisos, errores y ejemplos de sus rutas.
2. Edu mantiene importación; Kevin pronóstico/evaluación; Max receta/plan; Vera stock/promoción; Aguirre pedido/canal.
3. Axel coordina sobre y catálogo de rutas; cambios de contrato incluyen consumidor.
4. Indicar estado propuesto o implementado y enlazar prueba de aceptación.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

El frontend se implementa contra un ejemplo completo sin adivinar nombres o estados.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../equipo/avances/cueva.md) siguiendo [la plantilla](../equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Paso 3 local · M03 · 30-09-2026

Necesidades y faltantes implementados en la transacción del plan. API/UI conservan aportes, unidades, lotes y lectura de stock; decimales como cadenas, agregación antes de redondear a tres decimales. Producción o stock ausente deja estado INCOMPLETAS y motivo; no se inventan ceros ni se modifica inventario. Migración aditiva 0010_m03_necesidades sobre 0009; planes antiguos quedan PENDIENTE_M03 y el administrador puede completarlos una vez. Servicio público obtener_necesidades y contrato M03 en docs/api/contratos.md. Compras y Telegram siguen pendientes. Cambios locales por Codex para Axel, sin commit ni cambios remotos.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.
