# Automatización y control

## 8.1 Automatización

Campos:
- id
- negocio_id
- tipo
- nombre
- habilitado
- programacion
- maximo_reintentos
- configuracion
- creado_en
- actualizado_en

Tipos:
- PLANIFICACION_DIARIA
- PEDIDO_PROVEEDOR
- SEGUIMIENTO_EXCEDENTES
- ACTIVACION_PROMOCION
- SEGUIMIENTO_PROMOCION

## 8.2 Ejecución de automatización

Campos:
- id
- automatizacion_id
- estado
- inicio_en
- fin_en
- datos_entrada
- datos_salida
- mensaje_error
- cantidad_reintentos

Estados:
- PENDIENTE
- EN_EJECUCION
- VERIFICANDO
- COMPLETADO
- REINTENTANDO
- FALLIDO
- CANCELADO

## 8.3 Intento de automatización

Campos:
- id
- ejecucion_automatizacion_id
- numero_intento
- inicio_en
- fin_en
- estado
- mensaje_error

## 8.4 Patrón de control

```text
ejecutar()
↓
verificar()
↓
¿correcto?

SI
↓
COMPLETADO

NO
↓
¿quedan reintentos?

SI
↓
REINTENTANDO
↓
ejecutar()

NO
↓
FALLIDO
↓
notificar()
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
generar pronóstico
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
faltante > 0
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
FALLIDO
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
calcular existencias restantes
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
