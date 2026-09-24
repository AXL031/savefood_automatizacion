# Contratos entre módulos

## Alcance y convenciones del MVP

Estos contratos usan una instalación local para un comercio y una sucursal, según [ADR-005](../arquitectura/decisiones/ADR-005-instalacion-local-mvp.md). Los `id` son internos a esa instalación. Toda ruta de negocio requiere autenticación salvo `POST /autenticacion/iniciar-sesion` y `/salud`. Las respuestas de éxito llevan `datos`; las de error usan el formato documentado en el README principal. Los servicios intercambian objetos tipados, no acceden al repositorio SQL de otro módulo.

Antes de implementar un consumidor y su proveedor, ambos responsables acuerdan: nombres y unidades de los campos, ausencia frente a cero, qué error devuelve, si la llamada puede repetirse y quién guarda el resultado. Los ejemplos siguientes son contratos iniciales; el esquema exacto se actualiza junto con la primera implementación de cada dominio.

### Ventas → Pronósticos

Entrada: `producto_id`, `fecha_local` y `unidades_vendidas` enteras no negativas, con identificador de origen para deduplicar importaciones. Un día sin fila permanece desconocido. El pronóstico para el día siguiente utiliza solo ventas anteriores al momento de ejecución. El adaptador de CSV debe rechazar archivos con más de un par `comercio_id`/`sucursal_id` en el MVP.

### Pronósticos → Planificación

Entrada: `producto_id`, `fecha_objetivo`, `cantidad_pronosticada` y `version_modelo`. `cantidad_pronosticada` representa unidades, no un porcentaje; si falta historial, se comunica `HISTORIAL_INSUFICIENTE`. El artefacto CatBoost queda en almacenamiento local y su versión se conserva con cada pronóstico.

### Planificación → Inventario → Compras

El plan consulta unidades disponibles de producto terminado y cantidades disponibles de ingredientes con su unidad. Entrega a compras `plan_id`, `ingrediente_id`, `cantidad_requerida`, `cantidad_disponible`, `cantidad_faltante` y `unidad`. Compras no vuelve a calcular el faltante; valida que no sea negativo y crea pedidos sin duplicarlos para el mismo plan e ingrediente.

### Compras → Canal de envío

Compras construye el pedido y llama a un adaptador con `pedido_id`, destinatario y texto. El adaptador devuelve `canal`, `identificador_externo`, `enviado_en` y `estado_envio`, o un error recuperable. Enviar con éxito significa que Telegram aceptó el mensaje; solo una respuesta explícita del proveedor cambia el pedido a `CONFIRMADO`. La repetición usa la misma clave de operación para evitar dos pedidos por un reintento.

### Automatizaciones → Módulos

Axel coordina servicios públicos de cada módulo mediante una clave de idempotencia, guarda ejecución e intentos, y registra el error o resultado. Cada módulo conserva la lógica de su dominio. Un fallo de red en Telegram deja el pedido pendiente y la ejecución programada para reintento; no se marca como confirmado.

## Planificación → Pronósticos

```python
servicio_pronosticos.obtener_pronostico(producto_id, fecha)
```

Respuesta:
```json
{
  "producto_id": 1,
  "fecha": "2026-09-24",
  "cantidad_pronosticada": 60,
  "confianza": 0.93
}
```

## Planificación → Inventario

```python
servicio_inventario.obtener_existencias(ingrediente_id)
```

Respuesta:
```json
{
  "ingrediente_id": 5,
  "existencias": 2,
  "unidad": "kg"
}
```

## Planificación → Compras

```json
{
  "ingrediente_id": 5,
  "requerido": 5.8,
  "disponible": 2,
  "faltante": 3.8
}
```

## Compras → Proveedores

```python
servicio_proveedores.buscar_proveedor_preferido(ingrediente_id)
```

## Excedentes → Promociones

```json
{
  "producto_id": 1,
  "existencias_actuales": 24,
  "ventas_estimadas": 9,
  "excedente_estimado": 15,
  "riesgo": "ALTO"
}
```
