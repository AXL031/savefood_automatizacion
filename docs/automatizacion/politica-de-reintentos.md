# Política de reintentos

**Prototipo universitario:** aplica a preparación del modelo y tareas programadas de pronóstico/plan/promoción. También hay envío real por Telegram a un chat de pruebas; su política especial está en el [contrato de pedidos](../api/contrato-pedidos.md).

La configuración inicial permite **dos reintentos después del intento inicial** (`maximo_reintentos = 2`), hasta **tres intentos totales**. El contador visible muestra `intento 1 de 3`, `2 de 3` o `3 de 3`; nunca «2 de 2» para este ajuste. Cada fallo queda registrado en `intento_automatizacion`.

Solo fallos transitorios de tareas **internas** se reintentan automáticamente: `ErrorTransitorioInterno` declarado por el adaptador, desconexión de PostgreSQL, serialización fallida, deadlock o falta temporal de recursos de base. El intervalo es de 60–65 y 120–125 segundos, con variación aleatoria de 0–5 segundos para evitar ráfagas. Un fallo al publicar en Redis conserva el reclamo y se recupera por lease, sin consumir intento. Errores de validación, datos incompletos, artefacto incompatible o claves reutilizadas con otra entrada son definitivos hasta corregir el origen. La nueva entrega conserva `clave_idempotencia` y crea el siguiente `numero_intento`. Un timeout **después de intentar enviar** por Telegram queda `PENDIENTE_VERIFICACION`: una clave única local no evita un duplicado externo y no se reenvía a ciegas. Un `TimeoutError` genérico no se clasifica como reintentable porque podría pertenecer a un efecto externo.

```text
Primer intento → Fallo → Segundo intento → Fallo → Tercer intento
→ Fallo definitivo → Notificación
```

La notificación es un aviso en la bandeja de **Notificaciones e incidencias** (campana «Avisos»). Se crea solo cuando la ejecución queda `FALLIDA` (agotó sus reintentos o tuvo un error definitivo), en la misma transacción que cierra la ejecución, con clave `tarea-fallida:<id>` para no duplicarse. Incluye el tipo de tarea, intentos, motivo y un enlace a la ejecución; el administrador puede marcarlo leído y registrar la corrección aplicada. Los intentos que pasan a `REINTENTANDO` no avisan. Código: `backend/app/modules/automatizaciones/avisos.py`, llamado desde `backend/app/workers/motor.py`. Las acciones manuales inmediatas (crear un plan, generar pedidos, registrar una venta) muestran su error en la misma pantalla y no pasan por aquí.
