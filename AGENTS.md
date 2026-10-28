# Instrucciones de trabajo para FoodSave

## Tienda independiente (instrucción de Axel, 21-10-2026)

La web de tienda vive en `tienda/`, con dependencias, Compose, backend de pagos y almacenamiento propios. Solo comunica con FoodSave mediante API HTTP; no importar servicios/modelos, montar sus archivos ni acceder a su PostgreSQL. Payme Flex solo preproducción, cuatro botones independientes. Credenciales en `tienda/.env`. ADR-010 y `docs/api/contrato-payme-pruebas.md` actualizan ADR-009. Pruebas de pago sobre catálogo de ejemplo no descuentan inventario real.


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
- Max Rojas: ingredientes, recetas, planificación, necesidades de insumos y tienda del cliente (T01–T05).

Cada persona implementa interfaz, backend, API, datos y pruebas de su bloque. La propiedad de una carpeta compartida indica coordinación; la lógica de dominio sigue perteneciendo a su autor. No trasladar toda la integración ni todas las pruebas a Axel.

## Contratos y alcance

- Prototipo local: una instalación, un comercio y una sucursal; PostgreSQL es la fuente después de la primera carga.
- Ausencia de venta no es cero. Pronóstico usa solo historia anterior al objetivo. Modelo/receta/plan conservan versiones.
- Un plan o pedido a proveedor no cambia stock. Solo apertura, ajustes explícitos, recepción de compras y, cuando se implemente, la compra confirmada de la tienda del cliente ([ADR-009](docs/arquitectura/decisiones/ADR-009-tienda-cliente.md)) producen movimientos.
- Tienda del cliente: pago siempre simulado (la interfaz puede pedir datos de tarjeta para validarlos en el navegador, pero nunca se envían a la API, ni se guardan ni se registran), promociones visibles solo tras aprobación administrativa y compras de tienda fuera de Ventas/ML.
- Pedidos por faltantes, aprobación configurable y Telegram real a un chat propio de pruebas. Mensajes históricos rotulados como demostración. No enviar mensajes externos sin autorización expresa de la tarea en curso.
- Un envío incierto no se reintenta a ciegas. Cerrar la regla entre planes de la misma fecha antes de habilitar compras automáticas.
- No implementar producción física, pagos reales o informes de impacto a partir de carpetas futuras o maquetas. Recepción y tienda del cliente siguen sus ampliaciones expresas y contratos.
- El alcance vigente (`docs/guia-inicio-desarrollo.md`) y los ADR prevalecen; `docs/vision-futura.md` no es contrato. Para responsables prevalece `docs/equipo/responsabilidades.md`.

## Implementación y entrega

Usar interfaces públicas entre módulos y transacciones coherentes. El importador coordina una sesión compartida; los servicios participantes no confirman por separado. Acordar campos, estados, errores, tipos y restricciones antes de conectar consumidores. Actualizar contrato, guía y pruebas con el cambio.

No reescribir migraciones ya aplicadas por el equipo. Respetar las ramas personales documentadas en `docs/equipo/flujo-git.md`; no cambiar de rama, publicar o integrar cambios sin una tarea que lo requiera. Verificar lo apropiado al cambio y registrar límites del entorno sin declarar pruebas no ejecutadas.

Las instrucciones del usuario en la sesión prevalecen. Si crea una carpeta fuente nueva, añadir su GUIA_DESARROLLO.md e incorporarla al mapa. Omitir guías dentro de `.git`, dependencias, entornos virtuales, cachés y salidas generadas.

## Documentar cada avance

Al finalizar un avance significativo, antes de entregar al usuario o abrir PR, actualizar `docs/equipo/avances/<apellido>.md`: resumen vigente y nueva entrada de bitácora. Registrar tareas, comportamiento disponible, archivos clave, contrato/ejemplo, configuración/migraciones, pruebas realmente ejecutadas, dependencias, siguiente paso y commit/PR si existe. Si no terminó, dejar estado parcial y bloqueo concreto. Seguir la plantilla en `docs/equipo/avances/README.md`.

Actualizar también el contrato y la guía de carpeta si cambiaron. Indicar si una entrega es real, parcial o simulada. No sustituir este registro por la respuesta del chat ni marcar un bloque integrado sin verificar su consumidor. Una tarea transversal registra avance en el bloque que la coordina y enlaza los otros afectados, sin inventar autoría de los integrantes.

## Acoplamiento autorizado · 28-10-2026

Axel autoriza integrar lo compatible de Bohorquez con prioridad de Cueva. Producción explícita por tandas se incorpora conforme a docs/api/contrato-operacion-integrada.md; sustituye la exclusión anterior únicamente para esa operación. Se conservan caja/entradas de lotes y tienda independiente por API HTTP. No habilitar checkout compartido, semillas automáticas ni escritura inmediata de tickets al histórico/ML.

## Ampliación vigente · 28-10-2026 · Tienda por API

Ampliación expresa autorizada por Axel: implementar etapas 1–3 del análisis de Bohorquez. Catálogo/promociones aprobadas publicados por HTTP; cotización/reserva autoritativas y pago verificado generan ticket TIENDA y salida en el servicio canónico. La exclusión de tienda de Ventas de los cortes anteriores queda sustituida para tickets operativos, no para venta_diaria/ML. Modo ejemplo sigue sin tocar inventario. Nunca sembrar la base habitual para demostrarlo. Coordinación Codex para Axel (A04), conservando dominios Rojas (Tienda), Sanchez (Ventas/UI) y Vera (Inventario/Promociones). La ampliación usa dos proyectos y bases independientes: solo API HTTP, sin importar modelos, montar carpetas ni consultar PostgreSQL desde tienda. Payme solo preproducción y comprador invitado; cuatro botones independientes. Ver docs/api/contrato-integracion-tienda.md desde la raíz y registro Cueva para evidencia y límites.

## Jornada en la aplicación actual · 28-10-2026

Aclaración expresa de Axel: usar la instalación existente (FoodSave 3100, tienda 3101 y Telegram real configurado) para la exposición. Se autoriza preparar puntualmente ventas sintéticas del 27, continuidad histórica identificada, lotes recientes, ajustes auditados de insumos y modelo/flujo del 28, con respaldo previo y conservación de la carga/configuración anterior. No crear otra instalación ni un receptor ficticio para reemplazar los módulos actuales. El código de preparación separado anterior fue retirado y sus servicios quedaron detenidos. Guion: docs/equipo/guion-prueba-2026-10-28.md.
