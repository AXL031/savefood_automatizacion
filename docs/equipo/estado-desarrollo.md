# Estado verificado de desarrollo — 30-09-2026

Corte funcional: `main` / `origin/main` en `902f0e6` (PR #10). Auditoría de Codex para coordinación de Axel Cueva. Se contrastaron responsabilidades, registros, código, rutas registradas, migraciones, pantallas y pruebas. El [reparto](responsabilidades.md) y el [alcance](../guia-inicio-desarrollo.md) siguen vigentes.

La base de datos, la carga, ML, recetas e inventario tienen implementación real. La demo completa aún no termina el recorrido carga → modelo → plan → faltantes → pedidos → Telegram y ajuste → promoción. Una carpeta documental o un tipo de ejecución admitido no acredita su implementación.

## Qué existe y qué falta

«Disponible» identifica código utilizable y evidencia del corte; no declara cumplidos todos los criterios de demo o el consumo por módulos todavía ausentes.

| Responsable / tareas | Disponible | Falta desarrollar o verificar |
|---|---|---|
| Axel · A01–A04 | Identidad/roles, negocio/modo de aprobación, errores comunes; programación durable, Beat, lease, reintentos, trazas y pantallas; Compose, CI, runtime ML y volumen de modelos. | Conectar adaptadores de los dominios pendientes; prueba de toda la demo y reproducción del arranque en otra PC. El motor no sustituye la lógica de plan, compra o promoción. |
| Edu · E01–E04 | Productos/SKU, ventas agregadas y revisiones; ausencia distinta de cero; XLSX/CSV, validación, vista previa, carga atómica de productos/ventas/ingredientes/recetas/lotes y estado DATOS_CARGADOS; UI y componentes comunes. Piloto CSV sí agenda PREPARAR_MODELO. | E03 parcial: el asistente completo no agenda entrenamiento ni consume sus transiciones ENTRENANDO/MODELO_LISTO/fallo. Probar la confirmación completa HTTP contra PostgreSQL y el reintento ML sin reimportar. |
| Kevin · K01–K04 | CatBoost ejecutable sin notebook, CBM/metadatos/versiones, 13 características sin historia del objetivo, inferencia persistida, cobertura/motivos de ausencia, backtest, métricas y páginas pronósticos/panel. Adaptadores PREPARAR_MODELO, EVALUAR_MODELO y EVALUAR_PRONOSTICO registrados. | Integración con el estado de E03 y consumidor M02; evaluación posterior a la propuesta real. El backtest existente no prueba un flujo plan/pedido. |
| Vera · V01–V04 | Lotes, apertura compartida, cero explícito, caducidad/disponibilidad por fecha, ajustes idempotentes y bloqueo contra saldo negativo; UI de inventario y movimientos. V01/V02 entregados por Max por encargo de Vera. Regla pura de promoción con pruebas unitarias. | V03 y parte de V04: persistir/versionar reglas y evaluaciones, agendar EVALUAR_PROMOCION tras ajuste en la misma transacción, registrar manejador y API, mostrar sugerencia/rechazo con trazas. No hay publicación de descuentos en este alcance. |
| Aguirre · L01–L04 | L01 parcial: proveedor/ofertas, conversiones/mínimos/múltiplos, preferida única activa, permisos, migración 0007 y consulta pública para compras. Vinculación de chat y bloqueo de destino no verificado. | Adaptador Telegram real y UI de proveedores. L02–L04: modelos/migraciones/API/servicios/UI de pedido, líneas y envío; agrupación por proveedor, snapshot del modo, aprobación, message_id, conciliación y estado incierto. Cerrar recompra entre planes de la misma fecha con Max antes del automático. |
| Max · M01–M04 | M01: ingredientes/unidades, recetas versionadas y formularios; servicio de carga en sesión compartida. Lecturas públicas de receta y stock ya disponibles. | M02–M04: plan persistido y versionado, max(0, pronóstico−stock), snapshots de corrida/receta/stock, necesidades agregadas y faltantes en unidad base, API/UI de trazas e idempotencia. No descontar stock al planificar. |

## Evidencia y límites

- [Inicialización](../../backend/app/modules/inicializacion/rutas.py) conecta ServicioRecetasM01 y ServicioInventarioV01. [Servicio](../../backend/app/modules/inicializacion/servicio.py) termina en DATOS_CARGADOS y define transiciones de ML que hoy no consume código de producción. [Piloto](../../backend/app/modules/inicializacion/piloto.py) sí reserva preparación.
- [Registro de tareas](../../backend/app/workers/tasks/manejadores.py): solo los tres adaptadores de ML. GENERAR_PROPUESTA y EVALUAR_PROMOCION admiten programación, pero sin adaptador entregado finalizan con error de servicio pendiente de integración. El formulario de automatización no acredita un plan generado.
- [Inferencia](../../backend/app/modules/pronosticos/servicio.py) publica generar_corrida/obtener_pronosticos. [Planificación](../../backend/app/modules/planificacion/README.md) y [compras](../../backend/app/modules/compras/README.md) solo tienen documentación; no hay modelos, migraciones ni pantallas implementadas de esos dominios.
- [Proveedores](../../backend/app/modules/proveedores/servicio.py) declara un protocolo de Telegram, pero su dependencia real no inyecta adaptador. Verificar destino responde «Adaptador Telegram no configurado»; no acredita un mensaje real.
- [Promociones](../../backend/app/modules/promociones/reglas.py) contiene una regla pura; no tiene persistencia/API/página/manejador de evaluación.
- Verificación previa de esta sesión para el mismo árbol funcional: Docker con PostgreSQL/Redis, **122 pruebas y 6 subpruebas correctas**, sin omisiones. Migraciones hasta 0007, downgrade a 0004, reaplicación y alembic check correctos. Frontend typecheck/build y dos checks del PR #10 correctos. En esta auditoría no se repitieron pruebas: solo se inspeccionaron código y documentación. Las fronteras HTTP de la carga completa se probaron en SQLite, aunque el proceso pytest corriera dentro de Docker; falta su flujo completo en PostgreSQL.
- Los registros personales y dependencias conservan textos antiguos «LISTO_PARA_INTEGRAR», «faltan M01/V01» o «PostgreSQL pendiente». La entrada reciente de coordinación y este diagnóstico separan integración Git de finalización funcional. Los dueños deben ajustar sus resúmenes al próximo corte; no se inventan nuevas entregas suyas.

## Orden para cerrar la demo

1. **Edu + Kevin, coordinación de Axel:** carga completa → reserva única de entrenamiento → ENTRENANDO → MODELO_LISTO o fallo recuperable, backtest y UI. Probar transacción, repetición y reintento sin recarga en PostgreSQL.
2. **Max:** M02/M03 sobre contratos ya disponibles de Kevin/Vera/M01; conservar versiones y cantidades nulas con motivo. Entregar plan/necesidades y probar consumidor, no esperar código adicional de Axel para el dominio.
3. **Max + Aguirre:** definir identidad del escenario y política de recompra por fecha antes de pedidos automáticos. Implementar L02 con necesidades reales, conversión, agrupación y trazas.
4. **Aguirre:** terminar UI/adaptador L01 y L03/L04, aprobación manual/automática y envío al chat propio autorizado, sin reenvío ciego ante timeout. Etiquetar el mensaje histórico DEMOSTRACIÓN — NO SURTIR.
5. **Vera, en paralelo:** V03 y UI restante V04, ajuste → regla versionada → evaluación persistida → sugerencia o rechazo explicado.
6. **Todos:** registrar adaptadores y verificar Beat → pronóstico → plan → necesidades → pedido → aprobación/envío, evaluación posterior/dashboard y ajuste/promoción. Repetir con duplicados, reinicio, errores y otro integrante/PC.

Producción física, pagos, recepción, activación real de descuentos e informes de impacto están fuera del prototipo: su ausencia no cuenta como deuda de esta demo. Ver [criterio de demo completa](../guia-inicio-desarrollo.md#criterio-de-demo-completa).
