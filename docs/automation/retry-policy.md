# Política de reintentos

Configuración base:
```text
max_retries = 2
```

Flujo:
```text
Attempt 1
↓
FAIL

Attempt 2
↓
FAIL

Attempt 3
↓
FAIL

AutomationExecution = FAILED
↓
Notification
```
