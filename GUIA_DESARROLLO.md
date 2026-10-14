# Guía de desarrollo — Raíz y coordinación del repositorio

**Carpeta:** `.`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](AGENTS.md).
- [Reparto vigente y criterios de entrega](docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](docs/equipo/dependencias.md).
- [Alcance de la demo](docs/guia-inicio-desarrollo.md).
- [docs/base-para-desarrollo.md](docs/base-para-desarrollo.md).

## Punto de partida

**30-09-2026 · Paso 5: Telegram se configura desde Proveedores → Configuración Telegram por Administrador. Token cifrado en volumen telegram_secrets; JWT_SECRET estable (mínimo 32 caracteres). API escribe y worker lee. TELEGRAM_BOT_TOKEN de entorno es fallback opcional. Conservar secreto de instalación/volumen en respaldo privado; rotar JWT_SECRET requiere guardar token de nuevo. Sin aprobación/envío de pedidos en este corte.**

Archivos técnicos observados al preparar esta guía: `.env.example`, `.gitignore`, `compose.yaml`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](docs/equipo/avances/cueva.md) para el último estado.

Axel coordina la raíz; los seis responden por su propio bloque. La revisión documental no declara implementados los módulos.

**A03:** `compose.yaml` aplica Alembic mediante el servicio de una sola ejecución `migraciones` antes de iniciar API, worker y Beat. Beat es único en esta instalación local; revisa ejecuciones cada 30 segundos. Mantener PostgreSQL y Redis saludables antes de las pruebas del motor. Están registrados preparación, backtest y evaluación de pronóstico; plan, necesidades, compras y evaluación programados disponibles; promoción programada sigue pendiente.

**A04:** la imagen backend instala el extra `ml` de ejecución y prepara `/code/model_artifacts`; Compose monta allí un volumen persistente con lectura en API y escritura en worker. El bot usa `TELEGRAM_BOT_TOKEN` opcional; el destino se vinculará en el módulo de Aguirre. CI revisa migración en cabeza, volumen compartido, cola y motor. El modelo y el canal no se declaran integrados hasta recibir las entregas y pruebas de sus dueños.

`iniciar-foodsave.cmd` delega en `iniciar-foodsave.ps1`: evita dos arranques simultáneos del lanzador por instalación, comprueba Docker y espera hasta 120 segundos por API/web antes de abrir Inicio (`/`). Si Docker está apagado, intenta abrir Docker Desktop desde la instalación del CLI y espera hasta 120 segundos por el motor. Aplica el override local `.tmp/compose.rojas.yaml` cuando existe y lee el puerto web publicado de Compose; en el corte local de Rojas abre `http://localhost:3100/`, y sin override usa el puerto de `compose.yaml`. Conserva los volúmenes y muestra el error real de Compose. Usa imágenes ya construidas; tras cambios de código, ejecutar `iniciar-foodsave.cmd -Build` una vez. `-NoBrowser` permite comprobar el arranque sin abrir una pestaña. El primer build sigue requiriendo Docker y descarga de dependencias. El asistente completo está en `/inicializacion`. No ejecutar otro `docker compose up` en paralelo; ante conflicto de nombres, esperar al arranque en curso y volver a intentar, sin borrar volúmenes.

**E03/K01:** primera carga completa conectada al modelo automático, progreso durable y reintento sin reimportar; revisión `0008_e03_preparacion_ml` al final de la cadena. Cinco CSV sintéticos y pruebas PostgreSQL/Redis de carga, entrenamiento, evaluación y recuperación. Ver [evidencia](docs/equipo/avances/cueva.md).

## Trabajo en esta carpeta

**14-10-2026 · Catálogo completo:** solicitud expresa de Axel, posterior al límite inicial de cinco. Carga, programación y manejador permiten todo el catálogo; Automatización consulta todos los activos, los selecciona por defecto y ofrece Seleccionar todos/búsqueda. Productos deja de mostrar el flag heredado como exclusión. CSV actualizado para 139 seleccionados. Instalación habitual ya cargada y modelo listo: ampliar selección sin reimportar ni reentrenar. Contratos de carga/flujo y guías actualizados; evidencia en Cueva.

**14-10-2026 · CSV para primera carga:** [datos_carga](datos_carga/README.md) contiene las copias del usuario con nombres canónicos y stock ajustado a la regla vigente. Objetivo 2026-09-30 y referencia 2026-09-29; ventas originales conservadas. Supuestos de recetas separados de los cinco archivos importables. La instalación habitual sigue pendiente de la confirmación de Axel; evidencia de la validación aislada en el registro de Cueva.

**14-10-2026 · Configuración comercial:** nombre local Pastelería Maria Juanita; presentación y pedidos nuevos sin rótulos de demostración. Migración aditiva `0016_nombre_comercio` conserva nombres configurados y normaliza únicamente el nombre inicial anterior. Automatización mantiene calendario y añade Probar en un minuto / Gestionar → Ejecutar ahora con permisos/auditoría; contratos actualizados. [WhatsApp](docs/api/configurar-whatsapp.md) está pendiente de activos Meta y adaptador; el canal disponible sigue siendo Telegram. CSV y ventanas temporales del modelo no cambian en este corte.

1. Mantener README como entrada al alcance y reparto vigente; enlazar el mapa de carpetas.
2. Integrar manifiestos, Compose y variables de entorno con los requisitos aportados por cada bloque.
3. Mantener una revisión por cambio y evidencia de integración por cada frontera.
4. Preservar datos históricos, cambios locales y secretos fuera de Git.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

README, reparto, diccionario y guías atribuyen el mismo dueño; un compañero puede ubicar su tarea y reproducir el núcleo.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](docs/equipo/avances/cueva.md) siguiendo [la plantilla](docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

**M02–M04:** plan, faltantes y pantalla conectados; `GENERAR_PROPUESTA` hace inferencia real y reserva evaluación. Migración `0009_m02_planificacion`. Compras conectadas con una propuesta activa por fecha y recuperación L04. Consultar el puente de conciliación en la guía de migraciones. Ver avance de coordinación y Rojas.

## Corte vigente · 11-10-2026 · Flujo y promociones

Codex para Axel implementó configuración reutilizable, comprobación de requisitos por interfaces públicas, calendario histórico diario de 1–31 días, modelo/modo conservados y pausa/cancelación/reprogramación de tareas sin despacho. Promociones tienen regla inmutable versionada, reserva transaccional después de cada ajuste nuevo de producto y evaluación idempotente con snapshot/motivo; API y pantalla reales. Se conserva la propiedad de cada dominio.

[Contrato vigente, APIs y límites](docs/api/contrato-flujo-promociones.md). Aplicar `0015_flujo_promociones` antes de actualizar API/worker/Beat. El diagnóstico no ejecuta inferencia ni envía mensajes; guardar configuración no agenda. Consultas de tareas/evaluaciones admiten paginación real con total. La pausa no recupera horas perdidas: reprogramar antes de reanudar. Deshabilitar promociones afecta ajustes nuevos; tareas ya reservadas conservan su versión. Hora simulada de evaluación avanza por el tiempo real transcurrido desde el ajuste para comprobar frescura.

Las notas fechadas de cortes anteriores son historial; no usar sus pendientes como estado actual. Pruebas y límites finales en los registros Cueva/Vera/Sanchez, incluyendo PostgreSQL/Redis y Telegram real solo si fueron ejecutados. No confundir fixtures QA con datos de operación.
