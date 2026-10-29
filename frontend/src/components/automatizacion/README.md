# Automatización

> Guía vigente: [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md). Responsable de coordinación: **Axel Cueva**. Tareas, dependencias y avances se detallan en la guía local.

Componentes visuales de estados y ejecuciones automáticas.

`FlujoEjecucion.tsx` muestra espera, despacho, procesamiento y resultado con datos de la API. `estadoFlujo.ts` proyecta los estados canónicos sin simular porcentajes ni fases internas. Se reutiliza en el historial y el detalle protegido; los enlaces de resultado usan IDs positivos reales.

Verificación reproducible sin APIs: `node scripts/verificar-flujo-automatizacion.cjs`. Con `--preview` genera HTML de ocho escenarios ficticios en `.tmp/automatizacion-preview`, sin programar tareas ni enviar mensajes.
