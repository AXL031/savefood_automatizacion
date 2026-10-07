# Instrucciones de trabajo para FoodSave

## Antes de editar

1. Leer `docs/equipo/responsabilidades.md`: es la fuente vigente de responsables y tareas A01–M04.
2. Leer `GUIA_DESARROLLO.md` en la carpeta objetivo y las guías de sus carpetas padre. El índice está en `docs/equipo/mapa-carpetas.md`.
3. Leer `docs/guia-inicio-desarrollo.md` y los contratos enlazados desde la guía local. Distinguir diseño pendiente de código implementado.
4. Revisar el estado de Git y conservar cambios existentes. El reparto de tareas no autoriza revertir trabajo de otra persona.
5. Leer `docs/equipo/dependencias.md`, el resumen vigente del integrante en `docs/equipo/avances/` y el registro de quien entrega la dependencia. Usar esos enlaces para localizar el contrato y los archivos clave.

## Reparto vigente

- Axel Cueva: acceso, negocio, configuración, motor de automatización e infraestructura común.
- Edu Sanchez: inicialización, productos, ventas, archivos de entrada y estructura visual compartida.
- Kevin Bohorquez: entrenamiento, inferencia, evaluación histórica y dashboard.
- Leonardo Vera: inventario por lotes y promociones sugeridas.
- Leonardo Aguirre: proveedores, ofertas, pedidos, aprobación y adaptador Telegram.
- Max Rojas: ingredientes, recetas, planificación y necesidades de insumos.

Cada persona implementa interfaz, backend, API, datos y pruebas de su bloque. La propiedad de una carpeta compartida indica coordinación; la lógica de dominio sigue perteneciendo a su autor. No trasladar toda la integración ni todas las pruebas a Axel.

## Contratos y alcance

- Prototipo local: una instalación, un comercio y una sucursal; PostgreSQL es la fuente después de la primera carga.
- Ausencia de venta no es cero. Pronóstico usa solo historia anterior al objetivo. Modelo/receta/plan conservan versiones.
- Un plan o pedido no cambia stock. Solo apertura y ajustes explícitos producen movimientos en esta demo.
- Pedidos por faltantes, aprobación configurable y Telegram real a un chat propio de pruebas. Mensajes históricos rotulados como demostración. No enviar mensajes externos sin autorización expresa de la tarea en curso.
- Un envío incierto no se reintenta a ciegas. Cerrar la regla entre planes de la misma fecha antes de habilitar compras automáticas.
- No implementar producción física, pagos, recepción, promoción publicada o informes de impacto a partir de carpetas futuras o maquetas.
- El alcance vigente (`docs/guia-inicio-desarrollo.md`) y los ADR prevalecen; `docs/vision-futura.md` no es contrato. Para responsables prevalece `docs/equipo/responsabilidades.md`.

## Implementación y entrega

Usar interfaces públicas entre módulos y transacciones coherentes. El importador coordina una sesión compartida; los servicios participantes no confirman por separado. Acordar campos, estados, errores, tipos y restricciones antes de conectar consumidores. Actualizar contrato, guía y pruebas con el cambio.

No reescribir migraciones ya aplicadas por el equipo. Respetar las ramas personales documentadas en `docs/equipo/flujo-git.md`; no cambiar de rama, publicar o integrar cambios sin una tarea que lo requiera. Verificar lo apropiado al cambio y registrar límites del entorno sin declarar pruebas no ejecutadas.

Las instrucciones del usuario en la sesión prevalecen. Si crea una carpeta fuente nueva, añadir su GUIA_DESARROLLO.md e incorporarla al mapa. Omitir guías dentro de `.git`, dependencias, entornos virtuales, cachés y salidas generadas.

## Documentar cada avance

Al finalizar un avance significativo, antes de entregar al usuario o abrir PR, actualizar `docs/equipo/avances/<apellido>.md`: resumen vigente y nueva entrada de bitácora. Registrar tareas, comportamiento disponible, archivos clave, contrato/ejemplo, configuración/migraciones, pruebas realmente ejecutadas, dependencias, siguiente paso y commit/PR si existe. Si no terminó, dejar estado parcial y bloqueo concreto. Seguir la plantilla en `docs/equipo/avances/README.md`.

Actualizar también el contrato y la guía de carpeta si cambiaron. Indicar si una entrega es real, parcial o simulada. No sustituir este registro por la respuesta del chat ni marcar un bloque integrado sin verificar su consumidor. Una tarea transversal registra avance en el bloque que la coordina y enlaza los otros afectados, sin inventar autoría de los integrantes.
