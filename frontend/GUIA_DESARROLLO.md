# Guía de desarrollo — Aplicación web común

> Actualización 21-10-2026 solicitada por Axel: la tienda es el proyecto independiente `tienda/`; solo se comunica con FoodSave por API HTTP. Payme Flex se integra exclusivamente en preproducción con cuatro botones. El inventario real sigue pendiente de T01/T03/T04. Prevalece ADR-010 y el contrato Payme; las ubicaciones y pagos simulados descritos abajo son el corte previo.


**Carpeta:** `frontend`.

**Responsable:** Edu Sanchez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida.

## Leer antes de trabajar

- [Instrucciones para IA](../AGENTS.md).
- [Reparto vigente y criterios de entrega](../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../docs/equipo/dependencias.md).
- [Alcance de la demo](../docs/guia-inicio-desarrollo.md).
- [docs/diseno/especificacion-visual.md](../docs/diseno/especificacion-visual.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `.dockerignore`, `Dockerfile`, `next-env.d.ts`, `next.config.ts`, `package-lock.json`, `package.json`, `tsconfig.json`, `tsconfig.tsbuildinfo`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Edu Sanchez](../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

1. Mantener estructura Next.js/TypeScript, scripts y estilos compartidos.
2. Coordinar navegación y componentes; cada dueño construye sus pantallas completas.
3. Axel mantiene contrato de sesión; Kevin panel/gráficos; Max plan; Vera stock/promoción; Aguirre compras.
4. Verificar typecheck y build cuando cambie código de UI.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Las pantallas usan servicios comunes, no presentan una operación no implementada como completada.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Corte vigente · 11-10-2026 · Flujo y promociones

Codex para Axel implementó configuración reutilizable, comprobación de requisitos por interfaces públicas, calendario histórico diario de 1–31 días, modelo/modo conservados y pausa/cancelación/reprogramación de tareas sin despacho. Promociones tienen regla inmutable versionada, reserva transaccional después de cada ajuste nuevo de producto y evaluación idempotente con snapshot/motivo; API y pantalla reales. Se conserva la propiedad de cada dominio.

[Contrato vigente, APIs y límites](../docs/api/contrato-flujo-promociones.md). Aplicar `0015_flujo_promociones` antes de actualizar API/worker/Beat. El diagnóstico no ejecuta inferencia ni envía mensajes; guardar configuración no agenda. Consultas de tareas/evaluaciones admiten paginación real con total. La pausa no recupera horas perdidas: reprogramar antes de reanudar. Deshabilitar promociones afecta ajustes nuevos; tareas ya reservadas conservan su versión. Hora simulada de evaluación avanza por el tiempo real transcurrido desde el ajuste para comprobar frescura.

Las notas fechadas de cortes anteriores son historial; no usar sus pendientes como estado actual. Pruebas y límites finales en los registros Cueva/Vera/Sanchez, incluyendo PostgreSQL/Redis y Telegram real solo si fueron ejecutados. No confundir fixtures QA con datos de operación.

## Acoplamiento compatible de Bohorquez · 28-10-2026

Operación diaria, portal proveedor, avisos/campana y jerarquía de menú incorporados sin reemplazar nuestra caja/entradas ni tienda externa. Docker mantiene usuario no root y limita chown al caché de Next, adaptación compatible de Bohorquez. Contrato en ../docs/api/contrato-operacion-integrada.md; evidencia en Cueva.

## Ampliación vigente · 28-10-2026 · Tienda por API

Nueva /tienda-admin publica fichas sin precios paralelos, muestra reservas/entregas y usa sesión FoodSave. Ventas filtra ambos canales, conserva anulación solo presencial y distingue cobro verificado. Ningún Bearer privado de integración se añade al navegador. Coordinación Codex para Axel (A04), conservando dominios Rojas (Tienda), Sanchez (Ventas/UI) y Vera (Inventario/Promociones). La ampliación usa dos proyectos y bases independientes: solo API HTTP, sin importar modelos, montar carpetas ni consultar PostgreSQL desde tienda. Payme solo preproducción y comprador invitado; cuatro botones independientes. Ver docs/api/contrato-integracion-tienda.md desde la raíz y registro Cueva para evidencia y límites.
