# Automatización

> Guía vigente: [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md). Responsable de coordinación: **Axel Cueva**. Tareas, dependencias y avances se detallan en la guía local.

**Para hacer diagramas de flujo:** [flujos implementados al 20-10-2026](flujos-implementados.md). Incluye disparadores, entradas, decisiones, salidas y ocho diagramas Mermaid: cinco tareas de negocio, envío Telegram, motor común y recepción manual. La [conexión del bot y API Telegram](../api/configurar-telegram.md) añade su propio diagrama de configuración.

Contratos de [flujos](flujos.md), [programación](programacion.md) y [reintentos](politica-de-reintentos.md) del prototipo universitario. Beat despacha la propuesta (pronóstico → plan → pedidos) y la evaluación que **sugiere** promoción; los pedidos se envían por Telegram a un chat de pruebas según el modo de aprobación ([ADR-008](../arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md)) y no se activan descuentos. Véase el [alcance vigente](../guia-inicio-desarrollo.md).

