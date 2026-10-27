# Guía de desarrollo — Aplicación backend y dependencias

**Carpeta:** `backend`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../AGENTS.md).
- [Reparto vigente y criterios de entrega](../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../docs/equipo/dependencias.md).
- [Alcance de la demo](../docs/guia-inicio-desarrollo.md).
- [docs/arquitectura/vision_general.md](../docs/arquitectura/vision_general.md).

## Punto de partida

**30-09-2026 · Paso 5: cryptography es dependencia de runtime para cifrar token Telegram configurable desde Proveedores. API/worker comparten volumen telegram_secrets; clave derivada del JWT_SECRET de instalación. Token no se incorpora a imágenes, base de negocio o logs.**

Archivos técnicos observados al preparar esta guía: `.dockerignore`, `Dockerfile`, `alembic.ini`, `pyproject.toml`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

**A01:** `pyproject.toml` incluye `tzdata` para que la validación IANA del negocio funcione también en entornos Windows sin base horaria del sistema. La prueba del contrato HTTP de acceso/configuración está incorporada al paso Python de CI.

**A02:** el paso Python de CI incluye `test_programaciones_a02.py`; requiere aplicar `0001b_automatizaciones` para usar las rutas en PostgreSQL.

**A03:** Compose aplica `0001c_motor` antes de levantar API, worker y Beat. `test_motor_a03.py` ejecuta política local en la suite Python y casos reales de PostgreSQL/Redis en un paso Docker separado. Los manejadores de dominio aún no están registrados.

**A04:** `pyproject.toml` publica el extra `ml` de runtime (pandas, NumPy, scikit-learn, CatBoost) y la imagen lo instala. `MODEL_ARTIFACT_DIR` apunta al volumen de modelos que comparten API (solo lectura) y worker (escritura). Kevin entrega lógica de entrenamiento, metadatos y pruebas; Aguirre entrega el adaptador y configuración final de Telegram. No añadir sus handlers sin contrato y prueba de consumo.

1. Mantener pyproject.toml y Dockerfile consistentes y reproducibles.
2. Incorporar dependencias ML propuestas por Kevin y lector de archivos de Edu.
3. Acordar configuración y acceso a artefactos entre API y worker.
4. Cada dueño implementa y prueba su módulo completo bajo app/modules.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

La imagen arranca y los módulos registrados respetan las mismas convenciones.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Corte vigente · 11-10-2026 · Flujo y promociones

Codex para Axel implementó configuración reutilizable, comprobación de requisitos por interfaces públicas, calendario histórico diario de 1–31 días, modelo/modo conservados y pausa/cancelación/reprogramación de tareas sin despacho. Promociones tienen regla inmutable versionada, reserva transaccional después de cada ajuste nuevo de producto y evaluación idempotente con snapshot/motivo; API y pantalla reales. Se conserva la propiedad de cada dominio.

[Contrato vigente, APIs y límites](../docs/api/contrato-flujo-promociones.md). Aplicar `0015_flujo_promociones` antes de actualizar API/worker/Beat. El diagnóstico no ejecuta inferencia ni envía mensajes; guardar configuración no agenda. Consultas de tareas/evaluaciones admiten paginación real con total. La pausa no recupera horas perdidas: reprogramar antes de reanudar. Deshabilitar promociones afecta ajustes nuevos; tareas ya reservadas conservan su versión. Hora simulada de evaluación avanza por el tiempo real transcurrido desde el ajuste para comprobar frescura.

Las notas fechadas de cortes anteriores son historial; no usar sus pendientes como estado actual. Pruebas y límites finales en los registros Cueva/Vera/Sanchez, incluyendo PostgreSQL/Redis y Telegram real solo si fueron ejecutados. No confundir fixtures QA con datos de operación.

## Operación integrada · 27-10-2026

Ampliación expresa del usuario, implementada por Codex; responsabilidades conservadas. [Contrato](../docs/api/contrato-operacion-integrada.md) y [guía de reproducción/variables](../docs/operacion-integrada.md). Migración aditiva 0020: producción por tandas, venta interna/tienda con movimientos, respuesta del proveedor de una hora, recepción asistida/avisos y monitor cada diez minutos con aprobación. Código en operaciones y fronteras públicas de inventario/ventas. No hay reposición ni pagos reales automáticos. Docker separado para pruebas; túnel gratuito y Render opcional de pago. Credenciales privadas fuera de Git. Consultar bitácora Cueva para pruebas realmente ejecutadas y límites.
