# Guía de desarrollo — Pedidos, aprobación y envío

**Carpeta:** `backend/app/modules/compras`.

**Responsable:** Leonardo Aguirre. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Proveedores, pedidos y Telegram. **Tareas:** L02, L03, L04.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-pedidos.md](../../../../docs/api/contrato-pedidos.md).
- [docs/arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md](../../../../docs/arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Leonardo Aguirre](../../../../docs/equipo/avances/aguirre.md) para el último estado.

## Trabajo en esta carpeta

1. Agrupar necesidades de Max por proveedor y copiar cálculo de conversión/cantidades.
2. Cerrar política de recompra entre planes de una misma fecha con Max antes de habilitar automático.
3. Guardar modo de aprobación y estados; aprobación requiere rol Administrador.
4. Invocar adaptador Telegram desde tarea de dominio y persistir evidencia.
5. Conciliar resultado incierto; no dejar que reintentos genéricos repitan envíos.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `pedido_compra`, `linea_pedido`, `envio_pedido`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Plan/necesidades de Max, ofertas propias y modo de negocio de Axel.
- **Entrega:** Pedidos trazables, estado de aprobación y resultado real del canal.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Repetir plan no duplica pedido; plan nuevo de misma fecha pasa control de recompra.
- Modo manual espera aprobación; automático usa datos/destino validados.
- Timeout después de transmitir queda PENDIENTE_VERIFICACION.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/aguirre.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
