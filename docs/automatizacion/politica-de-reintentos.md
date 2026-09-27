# Política de reintentos

**Prototipo universitario:** aplica a preparación del modelo y tareas programadas de pronóstico/plan/promoción. También hay envío real por Telegram a un chat de pruebas; su política especial está en el [contrato de pedidos](../api/contrato-pedidos.md).

La configuración inicial permite **dos reintentos después del intento inicial** (`maximo_reintentos = 2`), hasta **tres intentos totales**. El contador visible muestra `intento 1 de 3`, `2 de 3` o `3 de 3`; nunca «2 de 2» para este ajuste. Cada fallo queda registrado en `intento_automatizacion`.

Solo fallos transitorios de tareas **internas** (Redis o base temporalmente indisponibles) se reintentan automáticamente, con espera exponencial de 60 y 120 segundos y pequeña variación para evitar ráfagas. Errores de validación, datos incompletos, artefacto incompatible o claves reutilizadas con otra entrada son definitivos hasta corregir el origen. La nueva entrega conserva `clave_idempotencia` y crea el siguiente `numero_intento`. Un timeout **después de intentar enviar** por Telegram queda `PENDIENTE_VERIFICACION`: una clave única local no evita un duplicado externo y no se reenvía a ciegas.

```text
Primer intento → Fallo → Segundo intento → Fallo → Tercer intento
→ Fallo definitivo → Notificación
```
