# Flujo configurable y promociones sugeridas · 11-10-2026

Coordinación A02/A03 de Axel; V03/V04 de Vera; interfaces públicas de Edu, Kevin, Max y Aguirre. Implementación por Codex para Axel. Una instalación local, escenarios históricos y stock únicamente por apertura/ajustes.

## Promociones

GET /api/v1/promociones/regla devuelve la última versión o null. PUT administrativo crea una versión inmutable (habilitada, hora_revision, hora_cierre, stock_umbral, descuento_pct, descuento_maximo_pct, antiguedad_maxima_stock_min, demora_segundos). Horas locales sin zona, revisión antes del cierre, descuento 1..máximo<=100, demora real 5..3600 segundos. Deshabilitar crea una versión; no altera evaluaciones ni tareas ya reservadas.

Un ajuste nuevo de producto reserva EVALUAR_PROMOCION en su misma transacción si la última regla está habilitada. Repetir el ajuste no reserva otra tarea. Se conserva regla, movimiento, lote, saldo y fecha/hora efectiva del escenario. Hora real = ahora UTC + demora; reloj simulado = hora efectiva del ajuste + tiempo real transcurrido desde el movimiento. La frescura se vuelve a comprobar al evaluar; una demora superior al límite registra rechazo. La evaluación no cambia stock/precios ni publica descuentos. Una lectura reemplazada por otro movimiento, fecha desconocida/vencida, horario incorrecto o stock insuficiente registra rechazo explicado. GET /promociones/evaluaciones admite limite 1..100 y desplazamiento y devuelve lista con metadatos.total; GET /promociones/evaluaciones/{id} conserva trazas. Consultas con sesión; cambios solo Administrador.

Inventario publica lectura_para_promocion(sesion,movimiento_id); promociones publica reservar_tras_ajuste(sesion,movimiento_id,usuario_id). Ninguno confirma la sesión. Worker usa evaluar_programada(sesion,contexto) y guarda una evaluación por movimiento y ejecución. Sin regla habilitada el ajuste sigue funcionando.

## Configuración y calendario

GET/PUT /api/v1/flujo-automatizacion/configuracion lee/guarda parámetros reutilizables; guardar no agenda ni autoriza mensajes. POST /flujo-automatizacion/comprobar revisa productos activos/SKU, modelo/partición, recetas, stock conocido, ingredientes activos/ofertas y destinos por interfaces públicas sin inferir ni red. Devuelve requisitos con listo, motivo y enlace para corregir; permisos de escritura administrativos. Diagnóstico no acredita precisión ni cobertura de inferencia.

POST /flujo-automatizacion/programar requiere clave_idempotencia y autorizar_envio=true para AUTOMATICO. Crea atómicamente de 1 a 31 programaciones: una por día real en la zona del negocio y un día histórico siguiente por cada ejecución. El rango debe pertenecer a la prueba reservada. No hay repetición indefinida ni pronóstico operativo de hoy. Horas ambiguas o inexistentes se rechazan. Todas las tareas conservan versión del modelo y modo. Repetir clave/contenido devuelve el calendario; cambiar contenido da 409. Validaciones se repiten al programar; el dominio revalida al ejecutar. Cambiar configuración no altera tareas guardadas. La protección de una compra activa por fecha permanece.

POST /programaciones-demo/{id}/gestionar recibe accion PAUSAR, REANUDAR o CANCELAR y motivo; PATCH /programaciones-demo/{id} modifica únicamente horario real futuro. Solo tareas GENERAR_PROPUESTA pendientes, sin despacho, lease o intento. Bloquear ejecución antes de programación conserva el orden del motor. PAUSADA no se despacha, CANCELADA conserva ejecución cancelada. Reanudar después de la hora requiere primero reprogramar: no se recuperan días perdidos enviando a ciegas. Cambios auditados (actor, motivo, estado/horario anterior, fecha); no cambian clave/entrada original ni efectos ya iniciados. Operador consulta, Administrador gestiona.

Parámetros: producto_ids (1..5 únicos), modelo_id opcional, fecha_objetivo_demo, hora_simulada (local), primera_ejecucion_local, dias (1..31), modo_envio_pedidos. El margen de producción sigue siendo cero según alcance; unidades y política de recompra se configuran en sus dominios.

GET de programaciones/ejecuciones admite limite (1–100), desplazamiento y metadatos.total. Programaciones pendientes/pausadas aparecen primero, por próximo horario; el resto por ID descendente. Ajuste HTTP incluye evaluacion_promocion_ejecucion_id nullable para seguir la tarea sin confundir un ajuste con una promoción ya evaluada.
