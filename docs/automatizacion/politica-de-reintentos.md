# Política de reintentos

La configuración inicial permite dos reintentos después del primer intento fallido (`max_retries = 2`). Cada fallo debe quedar registrado.

```text
Primer intento → Fallo → Segundo intento → Fallo → Tercer intento
→ Fallo definitivo → Notificación
```
