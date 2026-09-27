# Política de reintentos

**Prototipo universitario:** aplica a preparación del modelo y tareas programadas de pronóstico/plan/promoción. No hay envíos externos; las reglas de reconciliación de Telegram de abajo son una extensión futura.

La configuración inicial permite **dos reintentos después del intento inicial** (`maximo_reintentos = 2`), hasta **tres intentos totales**. El contador visible muestra `intento 1 de 3`, `2 de 3` o `3 de 3`; nunca «2 de 2» para este ajuste. Cada fallo queda registrado en `intento_automatizacion`.

Solo fallos transitorios (Redis o base temporalmente indisponibles) se reintentan automáticamente, con espera exponencial de 60 y 120 segundos y pequeña variación para evitar ráfagas. Errores de validación, datos incompletos, artefacto incompatible o claves reutilizadas con otra entrada son definitivos hasta corregir el origen. La nueva entrega conserva `clave_idempotencia` y crea el siguiente `numero_intento`. Para un canal externo futuro con respuesta ambigua, consultar su estado antes de reenviar; una clave única local no garantiza que Telegram entregue exactamente una vez.

```text
Primer intento → Fallo → Segundo intento → Fallo → Tercer intento
→ Fallo definitivo → Notificación
```
