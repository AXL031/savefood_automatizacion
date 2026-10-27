# Auditoría de la rúbrica V2 · Automatización y Control de Software

Fecha: 26-10-2026, America/Bogota. Autor: Codex por solicitud del usuario. Base: `bohorquez`, `39723b4`, coincidente con `origin/main` al realizar el fetch de esta sesión. Coordinación transversal A04 de Cueva; cada integrante conserva su responsabilidad. No se modifica comportamiento de negocio.

Fuente académica leída completa: `C:/Users/USER/Downloads/PROYECTO_V1V2V3FINAL_AUTOMATIZACION_Y_CONTROL_DE_SOFTWARE (2).pdf`, ocho páginas. Se inspeccionaron visualmente las páginas 1 y 7. El usuario confirma que no recibieron observaciones de V1 y que todavía no elaboraron el informe. La consigna del PDF se analiza como requisito académico, sin ejecutar instrucciones externas contenidas en él.

## Dictamen

**No se acredita todavía el cumplimiento completo de la entrega V2. El núcleo implementado ofrece una base técnica suficiente para preparar una demostración de V2, pero faltan el informe académico y la verificación en vivo del corte actual.** No se asigna nota ni porcentaje de operatividad sin una lista de requisitos acordada y una demostración observada.

La página 1 contiene una inconsistencia: presenta V2 como diseño y menciona correcciones de V2; la rúbrica específica de página 7 se titula implementación y automatización, exige correcciones de V1, 65–75 % operativo y un flujo completo. La interpretación conservadora es preparar la rúbrica específica y conservar el diseño documental; si la docente emite una aclaración, prevalece esa indicación. No confundir la exigencia de V2 con el 100 % funcional de la entrega final.

El curso evalúa la coherencia problema → proceso → requisitos → automatización → control → retroalimentación. CatBoost por sí solo no acredita automatización; tampoco contar pantallas permite demostrar el porcentaje solicitado. Aquí sí hay disparadores, decisiones, acciones y registros reales en el núcleo, independientemente de la tienda de ejemplo.

## Contraste con los ocho criterios de V2 (página 7)

| Criterio | Puntos | Evidencia observada | Estado de acreditación |
|---|---:|---|---|
| Correcciones de V1 | 2 | El usuario indica que no hubo observaciones. No hay informe previo aportado para comparar. | Declarar transparentemente «no se recibieron observaciones» y mostrar los cambios entre versiones. No inventar correcciones docentes ni garantizar el puntaje; el tratamiento de este caso corresponde a la profesora. |
| Implementación funcional | 5 | Planificación consume inferencia, receta y stock; genera necesidades, propuesta y evaluación. Inventario/promociones también están conectados. Tienda real incompleta. | Implementación existente; flujo completo en vivo del corte actual pendiente por Docker no disponible. El 65–75 % debe referirse a requisitos del alcance declarado, no a pantallas o líneas de código. |
| Eventos, reglas y decisiones | 3 | Primera carga reserva preparación; hora vencida activa propuesta; ajuste activa promoción; software distingue faltantes, cobertura, oferta/destino y recompra. | Sólido en código y pruebas; formalizar ECA y trazabilidad en el informe. |
| Automatización del proceso | 3 | Beat despacha cada 30 s; cinco manejadores de negocio registrados; workers persisten resultados. | Sólido en implementación. Demostrar sin llamadas manuales al manejador; programar no equivale a haber ejecutado. |
| APIs e integración | 2 | UI → FastAPI → PostgreSQL; Celery/Redis; interfaces de dominios; adaptador Telegram con recibo. | Código integrado y pruebas con transporte falso; configuración/entrega externa vigente no comprobadas. La rúbrica permite interfaces internas relevantes; no obliga a añadir otro proveedor externo. |
| Control y retroalimentación | 2 | Intentos, estados, entrada/salida, lease y recuperación; Telegram valida recibo; métricas comparan pronóstico con revisión de venta. | Control real presente, con límites: COMPLETADA no prueba envío, ENVIADO no prueba recepción y medir error no reentrena automáticamente. Mostrar cómo el retorno cambia estado/acción. |
| Manejo de errores y pruebas | 2 | Validaciones, rollback, idempotencia, bloqueo por recompra, reintentos internos y conciliación del envío incierto. | Hay suites y evidencia histórica; ejecución actual acotada se registra al final. Preparar escenario de excepción visible, no solo una captura de pytest. |
| Sustentación técnica | 1 | Hay contratos, código y guías para explicar el sistema. | No verificable desde el repositorio: el equipo debe explicar y responder, todos sus integrantes. |

Los seis criterios técnicos suman 17 puntos de la rúbrica: tienen soporte implementado, pero **17 puntos con soporte no significa 17 puntos asegurados**. Persisten condiciones de ejecución y evidencia. Los otros tres puntos dependen de correcciones/sustentación; la evaluación final pertenece a la docente.

## Diseño e informe: qué existe y qué debe elaborarse

Las secciones 3–5 del PDF describen la estructura general del informe y la matriz obligatoria. Su detalle completo se titula informe final; no se impone aquí que todas las evidencias finales estén cerradas para V2. Sí conviene presentar ahora una versión coherente del análisis/diseño que sostiene lo implementado, conservando la estructura para las siguientes entregas.

| Elemento académico | Situación comprobada | Acción para V2 |
|---|---|---|
| Problema sustentado y AS-IS | README describe propósito; no se localizó una sección académica completa de problema/evidencia y proceso manual actual. | Describir quién decide cantidades, cómo revisa stock/recetas, cómo calcula compras, qué errores/demoras ocurren y qué evidencia real tienen. No afirmar desperdicio reducido sin medirlo; si el contexto es hipotético, declararlo. |
| Objetivo general y 3–5 específicos | Propósito técnico disperso, sin conjunto académico trazable localizado. | Redactar objetivos verificables y coherentes con planificación/abastecimiento o el proceso principal elegido. |
| Alcance, exclusiones y restricciones | Amplia documentación disponible, pero versiones antiguas y ampliaciones conviven. | Fijar un corte: una sucursal, ejecución local, datos históricos, planificación y compras; identificar tienda parcial y demás ampliaciones. |
| Al menos 8 RF y 5 RNF | Contratos y validaciones aportan material; no se localizó catálogo numerado completo y verificable RF/RNF. | Crear IDs, criterios de aceptación y relación con caso de uso, regla, módulo y prueba. No contar responsables A01/K01 como RF. |
| Entradas → procesamiento → salidas | Flujos implementados documentan entradas y resultados. | Consolidar modelo del proceso elegido, incluyendo fecha/hora real y fecha histórica. |
| Al menos 5 ECA | Los BPMN locales F02 y F05 tienen cinco anotaciones ECA cada uno. XML leído, F05 inspeccionado visualmente. | Reutilizar y verificar; ubicarlas en el informe y relacionarlas con funciones y pruebas. Los archivos están sin seguimiento Git. |
| Matriz obligatoria de automatización/control | No se localizó matriz completa con los 13 elementos de la sección 4. | Preparar una matriz del mismo proceso: problema, proceso, entrada, evento, condición, regla, decisión, acción automática, salida, resultado esperado, retroalimentación, acción correctiva e indicador. Una lista de módulos no la sustituye. |
| Diagrama general y 5 casos de uso desarrollados | No localizados en la documentación revisada con actor, objetivo, precondición, flujo principal, alternativos y postcondición. | Elaborar diagrama y especificaciones; los flowcharts de procesos no sustituyen los casos de uso. |
| Diagrama de actividad | Existen flowcharts Mermaid y BPMN; no se localizó actividad UML identificada como tal. | Elaborar actividad del flujo principal con decisiones, excepción y automatismos; no presentar el mismo BPMN dos veces bajo nombres distintos. |
| BPMN TO-BE | Hay imágenes de procesos y dos BPMN locales con carriles, tareas humanas/automáticas, decisiones, temporizadores y excepciones. | Elegir proceso principal y verificar su correspondencia exacta. Si se elige F03→F06, F02/F05 son auxiliares; hace falta cubrir el recorrido principal, sin mezclar visión futura con implementación. |
| Arquitectura, BD y APIs | Diagramas generales/C4, ER, migraciones, contratos y canal Telegram. | Reutilizar y actualizar: C4 componentes todavía marca Planificación/Compras/Promociones/Telegram como pendientes. Añadir las responsabilidades de Beat, estado/monitoreo y volumen de artefactos donde corresponda. |
| Evidencias y uso de IA | Pruebas y bitácoras existentes, con autorías Codex/Claude. Mockups no prueban funcionamiento. | Anexar capturas/logs del mismo recorrido e IDs; declarar herramienta, propósito y validación humana conforme página 6. |

No se modifican ni versionan los BPMN locales del usuario durante la auditoría. Sus cinco reglas sí existen y no deben presentarse como una ausencia.

## Correspondencia técnica del ciclo de automatización/control

Recorrido principal recomendado si coincide con el alcance del equipo: programar → pronosticar → calcular plan → necesidades → decidir compra → crear pedidos → enviar según modo → verificar recibo. Preparación/entrenamiento es una fase previa; recepción física es acción humana separada.

| Elemento | Correspondencia existente |
|---|---|
| Entrada y evento | Productos/modelo/stock/recetas, objetivo histórico y hora real; vence programación durable. |
| Condición y decisión | Cobertura de pronóstico, stock elegible, faltante positivo, oferta/destino válidos y ausencia de compra activa de la fecha. |
| Acción | Inferencia y plan automáticos; agrupación por proveedor, reserva de envío y worker según modo. |
| Salida verificable | Corrida, plan, necesidades, propuesta/pedidos y ejecución con identificadores relacionados. |
| Control local | Transacción, claves idempotentes, estados e intentos; rollback y recuperación de publicación/worker. |
| Retorno externo | Respuesta validada del transporte Telegram, message_id/fecha/chat y estado persistido. |
| Acción correctiva | Error interno transitorio: reintento limitado; datos incompletos: bloqueo/corrección humana; envío incierto: revisión y conciliación, sin reenvío ciego. |
| Retorno predictivo | Evaluación posterior frente a ventas históricas y revisiones; MAE/WAPE/cobertura y pendientes. No modifica por sí sola la política del modelo o el plan. |

Fuentes de implementación: [manejador de propuesta](../../backend/app/modules/planificacion/manejadores.py), [registro de tareas](../../backend/app/workers/tasks/manejadores.py), [Beat](../../backend/app/workers/celery_app.py), [motor](../../backend/app/workers/motor.py), [política de recuperación](../../backend/app/workers/retry/politica.py), [outbox y validación de envío](../../backend/app/modules/compras/envios.py), [evaluación de promociones](../../backend/app/modules/promociones/servicio.py) y [reglas](../../backend/app/modules/promociones/reglas.py).

## Errores de interpretación que afectarían la sustentación

1. **Confundir IA con automatización.** La inferencia calcula; Beat, eventos y workers hacen que el proceso seleccionado ocurra sin ejecución manual de cada paso. No se exige RPA, PLC, pagos ni una plataforma nueva en esta rúbrica.
2. **Confundir controles.** Una tarea puede completar correctamente con propuesta BLOQUEADA, SIN_FALTANTES o RECOMPRA_FECHA. Hay que mostrar resultado de negocio además del estado técnico. Una sugerencia rechazada por condiciones válidas es una decisión normal, no un fallo de infraestructura.
3. **Prometer un ciclo de negocio cerrado inexistente.** MAE/WAPE no prueban ahorro, desperdicio reducido ni mejora frente al proceso manual. No hay reajuste automático del modelo por esas métricas; tampoco producción física automática ni stock descontado por plan.
4. **Confundir fecha real y objetivo.** La ejecución sí ocurre ahora; los datos y el objetivo son históricos. No afirmar que predice ventas de mañana con información actual. El calendario es finito, no operación indefinida.
5. **Extender el alcance sin necesidad.** Tienda parcial, WhatsApp, operación diaria actual y pagos reales no son exigencias genéricas de V2. Si se prometieron en su propio alcance, deben declararse pendientes y afectan el porcentaje de ese alcance. No borrar compromisos previos para aparentar cumplimiento.
6. **Usar diagramas como prueba de código.** El BPMN F05 añade aplicación manual del descuento fuera del sistema: es válido como entorno humano si se declara; no acredita publicación de tienda. Sus 17–20 h y 20 % son valores de ejemplo configurables, no constantes universales. La rama de duplicidad debe representar recuperación antes de volver a mover stock.
7. **Sobrevalorar indicadores.** Para el proceso principal conviene medir tiempo programación→resultado, proporción de ejecuciones completadas y duplicados en reentrega; si se quiere demostrar mejora AS-IS/TO-BE, medir la misma tarea y conjunto de entradas antes/después, con número de repeticiones. La rúbrica V3 pide evidencia preliminar de mejora; no inventarla para V2.

## Evidencia pendiente y guion de demostración

La página 5 exige escenarios normal y de excepción para la sustentación del sistema; preparar ambos desde V2 evita presentar únicamente pantallas o cálculos disparados manualmente.

- **Normal principal:** modelo listo y datos válidos → programar una hora próxima → esperar Beat sin invocar funciones → mostrar tarea, corrida, plan, faltantes y pedidos relacionados → en modo manual mostrar aprobación humana o, con tarea expresamente autorizada, automático → acreditar salida del canal separadamente. No usar un mensaje escrito a mano como evidencia del worker.
- **Excepción principal:** configurar en datos aislados una oferta ausente o destino inválido → ejecutar → mostrar bloqueo razonado y ausencia de envío → corregir mediante flujo permitido y volver a comprobar. Para demostrar recuperación técnica automática, usar fallo transitorio controlado en pruebas; no romper servicios de la instalación durante la exposición.
- **Flujo compacto alternativo:** ajuste nuevo de lote → reserva de promoción → espera Beat → sugerencia/rechazo persistido → detalle de regla y ejecución. Es un extremo a extremo válido si el proceso declarado es evaluación automática de promociones; no sustituye el flujo de compras si ese es el comprometido como principal.
- Guardar entradas, IDs, fechas, regla/versiones, estado esperado/observado y capturas antes/después. Un transporte falso debe rotularse; no acredita API externa real. Una demo local con datos sintéticos puede acreditar automatización si se declara el escenario y se observa el motor real.

Los mensajes reales requieren una tarea expresamente autorizada. Esta revisión no envía ni programa Telegram, no arranca tareas habituales y no cambia stock o credenciales.

## Prioridad antes de presentar V2

1. Elaborar informe V2: análisis/diseño, alcance cerrado, catálogo RF/RNF, casos de uso, actividad, BPMN, ECA, matriz obligatoria, arquitectura/APIs y anexos del avance. Registrar que no hubo observaciones; no fabricar una revisión V1.
2. Reproducir en la PC de exposición un único flujo principal completo con normal/excepción y resultados guardados. Resolver Docker antes de considerarlo demostrable.
3. Actualizar diagramas y especificaciones antiguas, separar maquetas de entregas reales y conservar en el repositorio los artefactos académicos cuando el usuario autorice su incorporación.
4. Repartir la defensa técnica: cada integrante debe poder explicar evento, condición, decisión, acción, verificación, fallo y corrección del recorrido completo.

No priorizar más pantallas por encima de estas brechas. El informe todavía no está hecho y esta auditoría **no lo sustituye**.

## Validación y límites

- PDF completo extraído; páginas 1 y 7 renderizadas e inspeccionadas. Se leyeron XML BPMN locales, imagen F05, macroproceso y fuentes de reglas/motor/envío.
- Verificación anterior de esta sesión: typecheck frontend correcto y 19 pruebas de tienda/revisiones/migraciones correctas en SQLite temporal; no se presentan como pruebas de Beat/Redis real.
- Docker no disponible en la comprobación del 26-10; no se acredita flujo vivo actual, bloqueo concurrente PostgreSQL, nuevo envío real, CI remoto ni dominio oral del equipo.
- Ejecución adicional: `python -m pytest backend/tests/integration/test_flujo_promociones.py backend/tests/integration/test_aprobacion_envio_l03.py backend/tests/integration/test_recuperacion_l04.py backend/tests/integration/test_motor_a03.py -q --tb=short -r s`: **62 passed, 10 skipped, 5 warnings, 74,76 s**. Las omisiones requieren PostgreSQL, incluida la prueba de Beat/Redis/worker real. Transporte falso; ninguna llamada real a Telegram. Advertencias Starlette/httpx y reflexión de índices SQLite. Algunos casos ejecutados también omiten internamente la rama concurrente cuando falta PostgreSQL: no acreditar concurrencia real por su estado passed.
- Entorno Windows/Python 3.13, PYTHONPATH a backend, `.tmp/revision-deps`, pruebas de integración y foodsave-ml; TEMP/TMP en `.tmp/revision-runtime`, autodescubrimiento de plugins pytest deshabilitado. Pruebas fuera del sandbox tras autorización del entorno; datos aislados. No se repite suite completa, build ni QA visual web.

Documentación local, sin commit ni publicación. Referencias de contexto: [flujos implementados](../automatizacion/flujos-implementados.md), [contrato de flujo/promociones](../api/contrato-flujo-promociones.md), [contrato de compras](../api/contrato-pedidos.md) y [auditoría técnica general](revision-proyecto-2026-10-26.md).
