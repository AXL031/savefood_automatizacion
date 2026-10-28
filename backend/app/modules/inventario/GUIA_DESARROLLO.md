# Guía de desarrollo — Inventario por lotes y movimientos

**28-10-2026 · Entrada de productos:** `entradas.py` publica contexto, esquemas estrictos, registro y detalle; rutas en `rutas.py`. Entrada/código/producto, movimiento positivo ENTRADA y saldo comparten una transacción; hasta 100 lotes, clave por usuario y bloqueo de productos ordenado. Migración 0022 y `fecha_ingreso` de producto para excluir entradas posteriores a la consulta, también en caja. Se rechazan ajustes anteriores al ingreso conocido. [Contrato vigente](../../../../docs/api/contrato-entradas-productos.md); no consume ingredientes ni dispara promociones. Autor Codex para Axel; responsabilidad Vera conservada y coordinación en Cueva.

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

**Integración 30-09-2026:** V01/V02 disponibles desde entrega delegada de Rojas: apertura, lectura, caducidad, cero conocido y ajustes. Migración 0006; misma clave compara lote, delta, tipo, motivo y hora. SQLite no acredita bloqueo concurrente; V02_POSTGRES_TEST=1 verifica PostgreSQL en esquema aislado. V03 pendiente.

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

## Corte vigente · 11-10-2026 · Flujo y promociones

Codex para Axel implementó configuración reutilizable, comprobación de requisitos por interfaces públicas, calendario histórico diario de 1–31 días, modelo/modo conservados y pausa/cancelación/reprogramación de tareas sin despacho. Promociones tienen regla inmutable versionada, reserva transaccional después de cada ajuste nuevo de producto y evaluación idempotente con snapshot/motivo; API y pantalla reales. Se conserva la propiedad de cada dominio.

[Contrato vigente, APIs y límites](../../../../docs/api/contrato-flujo-promociones.md). Aplicar `0015_flujo_promociones` antes de actualizar API/worker/Beat. El diagnóstico no ejecuta inferencia ni envía mensajes; guardar configuración no agenda. Consultas de tareas/evaluaciones admiten paginación real con total. La pausa no recupera horas perdidas: reprogramar antes de reanudar. Deshabilitar promociones afecta ajustes nuevos; tareas ya reservadas conservan su versión. Hora simulada de evaluación avanza por el tiempo real transcurrido desde el ajuste para comprobar frescura.

Las notas fechadas de cortes anteriores son historial; no usar sus pendientes como estado actual. Pruebas y límites finales en los registros Cueva/Vera/Sanchez, incluyendo PostgreSQL/Redis y Telegram real solo si fueron ejecutados. No confundir fixtures QA con datos de operación.


## Recepción y corrección autorizadas · 15-10-2026

Codex para Axel coordina Compras/Inventario/Planificación. Contrato vigente: docs/api/contrato-pedidos.md y frontera de inventario en docs/api/contratos.md. Migración aditiva 0018: corrección enlazada de propuesta bloqueada sin envíos, nuevo plan y modo manual; recepción administrativa parcial/completa sobre pedido ENVIADO, con factor guardado, lotes y movimientos RECEPCION atómicos e idempotentes. UI distingue envío del mensaje y llegada física, muestra pendientes/historial y tabla de cantidades. Inventario etiqueta Recepción y filtra nuevas entradas anteriores a fecha_ingreso. Pruebas test_recepcion_compras.py; CI incluye su corte PostgreSQL. No implementa ventas en vivo ni simulación: solo plan en docs/equipo/plan-ventas-vivo-simulacion.md. Registro transversal y resultados reales en avances/cueva.md.


## Caja presencial · 26-10-2026

`ventas.py` publica disponibilidad/retirada/reintegración para caja presencial: lotes con fecha límite conocida vigente, caducidad informada vigente o aviso; orden de fecha límite/caducidad/ID, bloqueo global por ID y validación del carrito completo. VENTA negativa y ANULA_VENTA positiva de producto; no ingredientes ni producción. El consumidor confirma una única transacción. [Contrato implementado](../../../../docs/api/contrato-caja-presencial.md). Autor de este corte: Codex para Axel; se conservan las responsabilidades de cada dominio. Evidencia y límites en el registro de Cueva.

## Acoplamiento de Bohorquez · 28-10-2026

Backport adaptado 4c2a271: [contrato de operaciones](../../../../docs/api/contrato-operacion-integrada.md). Conserva tienda independiente por HTTP, caja y entradas múltiples de Cueva. Nueva migración 0023 sobre 0022; producción explícita, recepción asistida, avisos/monitor. No publica en tienda ni altera histórico/ML. Evidencia y límites en el registro de Cueva.

## Ampliación vigente · 28-10-2026 · Tienda por API

reservas.py publica el agregado activo/no vencido por lote. ventas.py descuenta reservas de lo vendible para caja y tienda, excluye ingresos futuros y consume asignaciones exactas en confirmar tienda. Ajustes negativos respetan reservas. Reservar/expirar no modifica saldo físico. Coordinación Codex para Axel (A04), conservando dominios Rojas (Tienda), Sanchez (Ventas/UI) y Vera (Inventario/Promociones). La ampliación usa dos proyectos y bases independientes: solo API HTTP, sin importar modelos, montar carpetas ni consultar PostgreSQL desde tienda. Payme solo preproducción y comprador invitado; cuatro botones independientes. Ver docs/api/contrato-integracion-tienda.md desde la raíz y registro Cueva para evidencia y límites.
