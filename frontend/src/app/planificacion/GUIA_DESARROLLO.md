# Guía de desarrollo — Planificación y necesidades de ingredientes

**Carpeta:** `frontend/src/app/planificacion`.

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

**Paso 2 local · 30-09-2026:** page.tsx consume /planes: consulta propuestas y trazas conservadas, distingue cantidad desconocida de cero, permite a Administrador generar desde corrida o preparar nueva clave. Necesidades/pedidos se identifican como siguiente desarrollo; no hay aprobación física ni ajuste de inventario.

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Max Rojas](../../../../docs/equipo/avances/rojas.md) para el último estado.

## Trabajo en esta carpeta

1. Mostrar producción sugerida por producto con pronóstico, stock y receta de origen.
2. Mostrar necesidades agregadas con disponible/faltante/unidad y advertencias.
3. Enlazar corrida y pedidos; nunca cambiar stock desde una acción de consultar/generar plan.

## Organización de implementación

La ruta compone `page.tsx` y componentes del feature correspondiente. Usar layout protegido y cliente HTTP común. Resolver carga, vacío, error, permisos y sesión vencida. Tener una carpeta y una guía no hace que la página exista: conectarla solo cuando su contrato esté publicado.

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

Necesidades muestran cantidades/unidades legibles kg/L; estados de compras en español. Clave generada en detalles. Plan/pedido no mueve inventario y snapshot no se recalcula por ajustes posteriores.


## Ajustes de interfaz · 30-09-2026

Tablas con paginador común y tamaños 10/25/50/100. Sesión/marco persistentes en AppShell; no usar recarga del documento para navegar. Detalle/edición en PanelDetalle, cierre/Escape y retorno a la página de origen; conservar permisos, snapshots y unidades. Las APIs mantienen listas recientes hasta 50 registros, identificadas en la pantalla; paginar esas filas no amplía el contrato histórico.
