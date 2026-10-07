# Base de desarrollo del prototipo FoodSave

**Corte: 06-10-2026.** Decisiones cerradas, puertas de integración y riesgos abiertos. La [guía de alcance](guia-inicio-desarrollo.md) es la fuente normativa; el estado por tarea está en los [avances](equipo/avances/README.md).

## Decisiones cerradas para implementar

1. **Producto:** una instalación local, un comercio y una sucursal. El prototipo es una simulación histórica de planificación y promoción sugerida; sí crea pedidos desde el plan y envía mensajes reales a un chat de pruebas por Telegram. No activa descuentos.
2. **Fuente de datos:** dos libros XLSX o cinco CSV en la primera carga. Después, PostgreSQL es fuente de ventas y stock. Fecha sin venta es desconocida; cero explícito sí es dato.
3. **Identidad y unidades:** `negocio.id = 1`; SKU externo se resuelve a `producto.id`. Producto y ventas en enteros, ingrediente en `numeric(14,3)` y su unidad base. Lotes y movimientos conservan el historial.
4. **Modelo:** CatBoost diario de un día adelante. Separación temporal por meses completos; la prueba queda fuera del ajuste. Inferencia solo con observaciones anteriores a la fecha objetivo. El backtest y el dashboard se rotulan como evaluación histórica exploratoria.
5. **Plan y compra:** `max(0, pronóstico - stock elegible)`, margen de seguridad cero y faltantes por receta versionada. El plan genera pedidos borrador por proveedor. Crear o enviar un pedido no modifica inventario.
6. **Automatización:** carga aceptada → preparar modelo → evaluar modelo; Beat despacha propuesta programada y evaluación de promoción. La hora UTC real dispara y la fecha/hora histórica local selecciona el escenario. Hasta tres intentos totales; cada efecto es idempotente y auditable.
7. **Promoción:** la regla existente solo crea sugerencia o rechazo razonado por lote. No usa CatBoost para estimar ventas intradía ni modifica precios.
8. **API:** base `/api/v1`, sobre exitoso `datos`, error estable `error.codigo`, Bearer para dominio y Administrador para escrituras sensibles. Las rutas existentes y propuestas están en [rutas-api.md](api/rutas-api.md); códigos de error en [errores.md](api/errores.md).
9. **Envío:** modo inicial `REQUIERE_APROBACION`, configurable a `AUTOMATICO`. El envío real usa un bot de Telegram y un chat de pruebas vinculado; aceptación por Telegram no significa confirmación del proveedor. El escenario histórico se marca «demostración, no surtir».

## Orden de integración y puertas de aceptación

| Puerta | Entrega verificable | Responsable principal según la distribución actual | Estado |
|---|---|---|---|
| 0. Núcleo coherente | Validación de configuración, error uniforme, tipos de interfaz acordes a los estados del prototipo, CI verde y Compose reproducido en otra PC | Axel; Edu coordina componentes compartidos | Hecha salvo prueba en otra PC |
| 1. Persistencia | Migraciones `0002`–`0007` con FK, `CHECK`, unicidad y modelos de datos, incluido proveedor, oferta, pedido, líneas y envíos; migración arriba/abajo probada con base nueva | Axel coordina; cada dueño aporta su esquema según el [diccionario](base_de_datos/diccionario-de-datos.md) | Hecha hasta `0009`; faltan pedidos y promoción |
| 2. Primera carga | Archivos de ejemplo versionados sin datos personales, validación/vista previa, carga atómica, segunda carga idéntica sin duplicados y rechazo completo de SKU desconocido | Edu (asistente, estado, productos y ventas); Max (ingredientes/recetas); Vera (apertura de stock) | Hecha; cinco CSV sintéticos disponibles para repetir E03/K01 |
| 3. Modelo | Entrenamiento fuera de HTTP y del notebook, `.cbm` persistido con huella y partición, vector de inferencia validado, backtest sin fuga del día objetivo | Kevin; Axel integra ejecución durable | Hecha |
| 4. Plan y evaluación | Programación próxima ejecutada por Beat, una corrida y un plan por clave/entrada, faltantes con unidad, comparación posterior con ventas reales y cobertura visible | Kevin (pronóstico, evaluación y panel); Max (plan/necesidades); Vera (stock); Axel (Beat) | Hecha localmente: M02–M04, programador y evaluación; CI remoto/otra PC pendientes |
| 5. Pedidos y canal | Un pedido por plan/proveedor con líneas trazables; aprobación manual y modo automático probados; mensaje real al chat de pruebas con `message_id` y fallo incierto sin reenvío ciego | Leonardo Aguirre (compras y Telegram); Axel (configuración y worker) | Pendiente (L02–L04) |
| 6. Promoción | Ajuste atómico de lote, programación próxima, sugerencia o rechazo guardado con regla/version/horas y entrega repetida sin segundo efecto | Leonardo Vera (stock, regla y resultado); Axel (orquestación) | Pendiente (V03) |
| 7. Demo reproducible | Desde base vacía: migrar, cargar, entrenar, programar, comparar, pedir, enviar al chat de pruebas, ajustar y observar trazas. Probar caída transitoria, reintento y reentrega de Beat | Todo el equipo; Axel coordina la integración | Pendiente |

Ninguna puerta se declara terminada por documentación o maqueta. La evidencia mínima es una prueba o demostración reproducible con IDs persistidos, y la ruta de interfaz consulta la API real.

## Riesgos abiertos

- **Recompra entre planes:** Max y Aguirre deben cerrar cómo evitar un segundo pedido cuando se recalcula el plan de la misma fecha antes de habilitar compras automáticas.
- **Archivos de ejemplo:** cinco CSV sintéticos disponibles en `backend/tests/fixtures/primera_carga/`; documentan fechas y limitaciones del escenario. No representan ventas de un comercio real.
- **Verificación en PostgreSQL:** la cadena de migraciones sobre esquemas vacíos, concurrencia V02 y la frontera E03/K01 con worker/Beat reales ya pasaron localmente. La validación remota de CI y el arranque en otra PC siguen pendientes; plan/evaluación programados también verificados; pedidos y Telegram pendientes.
- **Interfaz:** la navegación y los estilos aún no siguen la [especificación visual](diseno/especificacion-visual.md#pendiente-en-el-código).

## Regla para cambiar esta base

Si un requisito nuevo altera alcance, tabla, ruta, evento o métrica, actualizar primero el contrato dueño y el criterio de aceptación afectado; luego implementar código, migración, interfaz y una prueba que recorra la frontera. Registrar una decisión arquitectónica cuando cambie una de las decisiones cerradas. Así cada responsable puede desarrollar en paralelo contra un contrato explícito.
