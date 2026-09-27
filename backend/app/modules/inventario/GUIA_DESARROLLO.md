# Guía de desarrollo — Inventario por lotes y movimientos

**Carpeta:** `backend/app/modules/inventario`.

**Responsable:** Leonardo Vera. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Inventario por lotes y promociones sugeridas. **Tareas:** V01, V02.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contratos.md](../../../../docs/api/contratos.md).
- [docs/base_de_datos/esquema-objetivo-mvp.md](../../../../docs/base_de_datos/esquema-objetivo-mvp.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Leonardo Vera](../../../../docs/equipo/avances/vera.md) para el último estado.

## Trabajo en esta carpeta

1. Exponer apertura en la transacción de Edu y validar lote/unidad/caducidad.
2. Bloquear lote y guardar movimiento/saldo juntos con motivo y clave idempotente.
3. Entregar a Max disponibilidad elegible por fecha, advertencias y cifras reproducibles.
4. Tras ajuste de producto, solicitar evaluación de promoción al motor de Axel.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `lote_producto`, `lote_ingrediente`, `movimiento_inventario`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Apertura o ajuste de lote y fecha objetivo para consultar.
- **Entrega:** Saldos, movimientos y disponibilidad; evento para evaluar promoción.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Repetición de clave no aplica delta dos veces; datos distintos producen conflicto.
- Concurrencia no deja stock negativo.
- Lote vencido no cuenta; vigencia desconocida se advierte.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/vera.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
