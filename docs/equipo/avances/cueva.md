# Avances — Axel Cueva

**Responsable:** Axel Cueva. **Bloque:** Acceso, configuración y motor de automatizaciones. **Rama prevista:** `cueva`.

Leer [dependencias](../dependencias.md) y [reglas del registro](README.md). Este archivo se actualiza al terminar cada avance significativo.

## Resumen vigente

- **Estado:** reparto, guías y seguimiento documental entregados; implementación A01–A04 por verificar/completar.
- **Punto de partida observado:** Existen rutas de autenticación y negocio, identidad pública, Compose, CI y una tarea Celery de prueba. Falta comprobar/completar las tareas A01–A04 contra el contrato vigente; esta bitácora no certifica su integración.
- **Contrato disponible:** [reparto y tareas](../responsabilidades.md); las guías de [mapa-carpetas](../mapa-carpetas.md) enlazan contratos de dominio.
- **Entrega a consumidores:** los seis pueden consultar tareas, guías locales y dependencias; no se certifica una nueva API integrada en este registro.
- **Bloqueos:** consultar las entregas necesarias en [dependencias](../dependencias.md); registrar aquí el ID exacto cuando se materialice una espera.
- **Siguiente paso:** cerrar cuerpos de API, tipos/restricciones y ejemplos del primer corte del bloque; después implementar contra esos contratos.

| Tarea | Estado de seguimiento |
|---|---|
| A01 · Completar identidad, roles y configuración | PENDIENTE DE VERIFICAR / COMPLETAR |
| A02 · Construir programaciones y ejecuciones durables | PENDIENTE DE VERIFICAR / COMPLETAR |
| A03 · Implementar Beat y recuperación | PENDIENTE DE VERIFICAR / COMPLETAR |
| A04 · Preparar infraestructura común | PENDIENTE DE VERIFICAR / COMPLETAR |

## Bitácora

### 2026-09-26 20:31 America/Lima — reparto, guías y registro de avances

- **Autor:** IA de la sesión, preparando documentación transversal para el equipo. Axel figura como coordinador, no como autor de implementación de los otros cinco bloques.
- **Estado de esta entrega:** LISTO_PARA_INTEGRAR, cambios locales sin commit. A01–A04 no se marcan completas por este trabajo documental.
- **Qué cambió:** se aplicó el reparto aprobado en el README, asignaciones de tablas y especificación funcional. Se añadieron 115 guías de carpeta, 24 tareas principales con aceptación y seis registros de avance. Nueve carpetas nuevas contienen únicamente documentación de funciones que no tenían ubicación.
- **Archivos clave:** [README principal](../../../README.md), [responsabilidades](../responsabilidades.md), [mapa de carpetas](../mapa-carpetas.md), [dependencias](../dependencias.md), [instrucciones IA](../../../AGENTS.md) y [plantilla de registro](README.md).
- **Contrato entregado:** cada carpeta identifica responsable, alcance, tareas, entradas/salidas, aceptación y registro. Las dependencias identifican proveedor, consumidor, trabajo adelantable y bloqueo real. Cada avance significativo debe actualizar resumen vigente y bitácora antes de entregarse.
- **Ejemplo para el siguiente integrante:** Max abre rojas.md, consulta M02 en responsabilidades, revisa los registros bohorquez.md y vera.md, y usa la guía de backend/app/modules/planificacion. Al entregar su servicio, registra contrato, archivos y prueba para Aguirre.
- **Verificación:** comprobación local con Node de cobertura 115/115, dueños válidos, presencia de instrucciones de seguimiento y enlaces Markdown locales sin destinos rotos; 24 IDs de tareas presentes en el reparto. Revisión de whitespace mediante `git -c core.safecrlf=false diff --check`. Se corrigieron enlaces de responsables antiguos y un salto final sobrante. No se modificó lógica Python/TypeScript ni se ejecutaron pruebas de aplicación para esta entrega documental.
- **Configuración/migración:** ninguna nueva para usar estas guías. Conservar los cambios de alcance/pedidos y configuración que ya estaban en la sesión.
- **Pendientes:** los cuerpos exactos de API, restricciones finales de 0002 y la política de recompra entre planes siguen como trabajo de definición asignado; no confundir guías completas con backend implementado.
- **Siguiente paso:** cada integrante toma su primer ID, entrega contrato y fixture al consumidor y documenta el primer corte funcional en su registro.

### Preparación del registro

- **Autor:** IA que preparó el reparto y guías, sin atribuir implementación a Axel Cueva.
- **Cambio:** se definieron las tareas y el lugar de documentación; no se implementó lógica de este bloque en esta entrega documental.
- **Pruebas:** la revisión de documentación comprueba enlaces, cobertura de carpetas y coherencia del reparto; no acredita funcionamiento del módulo.
- **Próximo autor:** registrar el primer avance con la [plantilla](README.md) y actualizar el resumen vigente.

