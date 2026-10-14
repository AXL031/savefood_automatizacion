# Guía de desarrollo — Asistente y primera carga

**Carpeta:** `frontend/src/app/inicializacion`.

**Responsable:** Edu Sanchez. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida. **Tareas:** E02, E03.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-importaciones.md](../../../../docs/api/contrato-importaciones.md).
- [foodsave-ml/CONTRATO_DATOS_COMERCIOS.md](../../../../foodsave-ml/CONTRATO_DATOS_COMERCIOS.md).

## Punto de partida

**Paso 1 · 30-09-2026:** El asistente completo muestra preparación y backtest, refresca cada tres segundos, enlaza ejecución/modelo/panel y ofrece reintento administrativo sin archivos; no vuelve a mostrar carga aceptada. MODELO_LISTO y evaluación COMPLETADA son estados distintos. Servicios y tipos usan el estado ampliado del contrato E03.

`page.tsx` implementa el asistente de primera carga de Sánchez: dos XLSX o cinco CSV, vista previa y confirmación. `piloto/page.tsx` conserva la carga rápida del CSV bakery para la base local existente y reserva la preparación del modelo. Son flujos distintos. La carga completa consume recetas y lotes reales, y reserva entrenamiento. Consultar el resumen vigente de [Edu Sanchez](../../../../docs/equipo/avances/sanchez.md).

## Integración E03/K01

El asistente completo reserva preparación al confirmar y consulta progreso cada tres segundos mientras la ejecución está activa. Muestra enlace a intentos y panel; permite reintentar fallo sin adjuntar archivos. Una carga aceptada deja de mostrar el formulario de importación.

## Trabajo en esta carpeta

1. Construir pasos de archivos, fechas, vista previa, errores y confirmación.
2. Subir multipart mediante servicio común y mostrar conteos/huellas.
3. Consultar estado de preparación y ofrecer reintento ML sin recargar ventas ni lotes.

## Organización de implementación

La ruta compone `page.tsx` y componentes del feature correspondiente. Usar layout protegido y cliente HTTP común. Resolver carga, vacío, error, permisos y sesión vencida. Tener una carpeta y una guía no hace que la página exista: conectarla solo cuando su contrato esté publicado.

## Dependencias y contrato de entrega

- **Recibe:** Archivos, claves de carga y fechas del escenario del Administrador.
- **Entrega:** Datos consistentes, conteos, errores, estado de inicialización y solicitud de entrenamiento.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Un fallo en la última hoja no deja productos, ventas ni stock parciales.
- Carga idéntica devuelve el resultado; clave reutilizada con otro archivo produce conflicto.
- Fallo ML permite reintento sin nueva importación.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Corte vigente · 11-10-2026 · Flujo y promociones

Codex para Axel implementó configuración reutilizable, comprobación de requisitos por interfaces públicas, calendario histórico diario de 1–31 días, modelo/modo conservados y pausa/cancelación/reprogramación de tareas sin despacho. Promociones tienen regla inmutable versionada, reserva transaccional después de cada ajuste nuevo de producto y evaluación idempotente con snapshot/motivo; API y pantalla reales. Se conserva la propiedad de cada dominio.

[Contrato vigente, APIs y límites](../../../../docs/api/contrato-flujo-promociones.md). Aplicar `0015_flujo_promociones` antes de actualizar API/worker/Beat. El diagnóstico no ejecuta inferencia ni envía mensajes; guardar configuración no agenda. Consultas de tareas/evaluaciones admiten paginación real con total. La pausa no recupera horas perdidas: reprogramar antes de reanudar. Deshabilitar promociones afecta ajustes nuevos; tareas ya reservadas conservan su versión. Hora simulada de evaluación avanza por el tiempo real transcurrido desde el ajuste para comprobar frescura.

Las notas fechadas de cortes anteriores son historial; no usar sus pendientes como estado actual. Pruebas y límites finales en los registros Cueva/Vera/Sanchez, incluyendo PostgreSQL/Redis y Telegram real solo si fueron ejecutados. No confundir fixtures QA con datos de operación.

## Corte solicitado · 14-10-2026

Codex para Axel. Tarjeta inicial usa Día que se va a planificar. Las fechas siguen siendo las del contrato/modelo cargado; no altera CSV ni registra carga al cambiar presentación.
