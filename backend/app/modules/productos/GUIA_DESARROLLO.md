# Guía de desarrollo — Catálogo de productos y SKU

**Carpeta:** `backend/app/modules/productos`.

**Responsable:** Edu Sanchez. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida. **Tareas:** E01.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-importaciones.md](../../../../docs/api/contrato-importaciones.md).
- [docs/arquitectura/decisiones/ADR-006-identidades-lotes-pronosticos.md](../../../../docs/arquitectura/decisiones/ADR-006-identidades-lotes-pronosticos.md).

## Punto de partida

**30-09-2026 · Completar piloto:** `registrar_catalogo(..., completar_piloto=True)` permite al coordinador E03 adoptar códigos legibles/nombres/demostrar del mismo catálogo técnico bakery, con SKU activos uno a uno y sin colisiones. Conserva IDs y mapeos. El modo habitual comprueba código→SKU, no solo el conjunto de códigos; un intercambio se rechaza. Escritura bajo bloqueo de productos en la sesión compartida, sin commit. Condiciones en el contrato de importaciones.

E01 parcial implementa `producto` y `sku_producto` en `0002_e01_ventas`. `cargar_catalogo_bakery(sesion, lista)` lee la lista curada de nombres y crea mapeos explícitos; `resolver_sku(sesion, origen, sku_externo)` devuelve el ID local o falla con `SKU_DESCONOCIDO`. `listar_skus_bakery(sesion)` y `nombres_productos(sesion, ids)` son lecturas públicas para Kevin y otros consumidores. Ninguna función confirma la transacción. Los precios de la lista son referencia del dataset y no forman parte del catálogo operativo de la demo. API y pantalla de productos siguen pendientes. Consultar el resumen vigente de [Edu Sanchez](../../../../docs/equipo/avances/sanchez.md).

## Trabajo en esta carpeta

1. Validar códigos internos y SKU externos; resolver origen/SKU a producto interno.
2. Crear lecturas y servicios de carga; desactivar catálogo usado sin borrarlo en cascada.
3. Exponer identidad estable a Ventas, Recetas, Inventario y Pronósticos.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `producto`, `sku_producto`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Catálogo de la primera carga y consultas de productos.
- **Entrega:** Producto interno y mapeo activo para consumidores.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- SKU desconocido se rechaza, no crea producto implícito.
- Código/SKU duplicado se informa antes de persistir.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Corte vigente · 11-10-2026 · Flujo y promociones

Codex para Axel implementó configuración reutilizable, comprobación de requisitos por interfaces públicas, calendario histórico diario de 1–31 días, modelo/modo conservados y pausa/cancelación/reprogramación de tareas sin despacho. Promociones tienen regla inmutable versionada, reserva transaccional después de cada ajuste nuevo de producto y evaluación idempotente con snapshot/motivo; API y pantalla reales. Se conserva la propiedad de cada dominio.

[Contrato vigente, APIs y límites](../../../../docs/api/contrato-flujo-promociones.md). Aplicar `0015_flujo_promociones` antes de actualizar API/worker/Beat. El diagnóstico no ejecuta inferencia ni envía mensajes; guardar configuración no agenda. Consultas de tareas/evaluaciones admiten paginación real con total. La pausa no recupera horas perdidas: reprogramar antes de reanudar. Deshabilitar promociones afecta ajustes nuevos; tareas ya reservadas conservan su versión. Hora simulada de evaluación avanza por el tiempo real transcurrido desde el ajuste para comprobar frescura.

Las notas fechadas de cortes anteriores son historial; no usar sus pendientes como estado actual. Pruebas y límites finales en los registros Cueva/Vera/Sanchez, incluyendo PostgreSQL/Redis y Telegram real solo si fueron ejecutados. No confundir fixtures QA con datos de operación.


## Caja presencial · 26-10-2026

`servicio.catalogo_para_ventas(sesion, ids=None, bloquear=False)` publica DTOs de catálogo; bloqueo opcional ordenado por ID coordina precios/cotizaciones/confirmaciones. Ventas mantiene precios propios versionados. [Contrato implementado](../../../../docs/api/contrato-caja-presencial.md). Autor de este corte: Codex para Axel; se conservan las responsabilidades de cada dominio. Evidencia y límites en el registro de Cueva.
