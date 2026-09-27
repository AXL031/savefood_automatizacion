# Guía de desarrollo — Pedidos, aprobación y envío

**Carpeta:** `frontend/src/features/compras`.

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

1. Listar pedidos por plan/proveedor y detallar líneas, conversión y modo.
2. Mostrar aprobación solo a Administrador y solo en estado permitido.
3. Distinguir envío, fallo e incertidumbre; construir conciliación con evidencia según contrato.

## Organización de implementación

Agrupar aquí formularios, hooks y vistas específicos del dominio. Consumir `src/services` y `src/types`; reutilizar layout y componentes de Edu. Las fórmulas y decisiones definitivas viven en el backend, no se duplican en el navegador.

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
