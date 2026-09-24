# Automatización y control

## 8.1 Automation

Campos:
- id
- business_id
- type
- name
- enabled
- schedule
- max_retries
- configuration
- created_at
- updated_at

Tipos:
- DAILY_PLANNING
- SUPPLIER_ORDER
- SURPLUS_MONITORING
- PROMOTION_ACTIVATION
- PROMOTION_MONITORING

## 8.2 AutomationExecution

Campos:
- id
- automation_id
- status
- started_at
- finished_at
- input_data
- output_data
- error_message
- retry_count

Estados:
- PENDING
- RUNNING
- VERIFYING
- COMPLETED
- RETRYING
- FAILED
- CANCELLED

## 8.3 AutomationAttempt

Campos:
- id
- automation_execution_id
- attempt_number
- started_at
- finished_at
- status
- error_message

## 8.4 Patrón de control

```text
execute()
↓
verify()
↓
¿correcto?

YES
↓
COMPLETED

NO
↓
¿quedan reintentos?

YES
↓
RETRYING
↓
execute()

NO
↓
FAILED
↓
notify()
```

## 8.5 Automatización — Planificación diaria

Disparador:
```text
22:00 todos los días
```

Flujo:
```text
leer ventas
↓
validar información
↓
generar forecast
↓
generar plan
↓
calcular ingredientes
↓
consultar inventario
↓
generar faltantes
↓
guardar resultado
```

Control:
```text
¿Plan generado correctamente?
NO → reintentar
nuevo fallo → registrar error → notificar
```

## 8.6 Automatización — Abastecimiento

```text
shortage > 0
↓
buscar proveedor
↓
agrupar necesidades
↓
crear pedido
↓
enviar
↓
verificar envío
```

Control:
```text
envío no confirmado
↓
reintentar
↓
si vuelve a fallar
FAILED
↓
notificar
```

## 8.7 Automatización — Control de excedentes

Disparador:
```text
cada 30 minutos
```

Flujo:
```text
leer producción
↓
leer ventas
↓
calcular stock restante
↓
predecir venta restante
↓
calcular excedente
↓
calcular riesgo
```

## 8.8 Automatización — Promoción preventiva

```text
riesgo detectado
↓
seleccionar estrategia
↓
calcular descuento
↓
crear promoción
↓
publicar
↓
verificar publicación
```

## 8.9 Automatización — Control de promoción

```text
esperar intervalo
↓
leer ventas nuevas
↓
recalcular excedente
↓
¿riesgo disminuyó?
```

Si sí:
```text
mantener / finalizar
```

Si no:
```text
recalcular acción
↓
ejecutar nueva promoción
```
