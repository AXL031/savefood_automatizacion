# Programación de automatizaciones

Según las secciones 8.5 y 8.7 del [README principal](../../README.md):

| Proceso | Frecuencia propuesta | Resultado |
|---|---|---|
| Planificación diaria | Todos los días a las 22:00 | Pronóstico, plan y faltantes de ingredientes |
| Control de excedentes | Cada 30 minutos | Excedente estimado y nivel de riesgo |

La hora de planificación debe interpretarse en la zona horaria de cada negocio (`Negocio.zona_horaria`). Antes de habilitar tareas reales, hay que definir la política para ejecuciones perdidas, duplicadas y cambios de horario.
