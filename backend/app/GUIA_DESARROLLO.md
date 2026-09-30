# Guía de desarrollo — Composición de la API

**Carpeta:** `backend/app`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../docs/guia-inicio-desarrollo.md).
- [docs/api/contratos.md](../../docs/api/contratos.md).

## Punto de partida

**Paso 2 local · 30-09-2026:** principal.py registra /planes (M02) con identidad/error comunes. POST administrativo; consultas con sesión. La generación desde corrida usa snapshots y no mueve stock.

**Integración 30-09-2026:** principal.py registra ingredientes, recetas, inventario y proveedores además del piloto/pronósticos existentes. Proveedores respeta identidad y errores comunes.

Archivos técnicos observados al preparar esta guía: `__init__.py`, `principal.py`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

**A01:** `principal.py` registra `configurar_errores(app)` antes de los routers. Las rutas nuevas reciben el sobre común para errores HTTP, validación 422 y fallos internos; las reglas de dominio permanecen en su módulo.

**A02:** `principal.py` registra las rutas de programaciones y ejecuciones; las reglas de idempotencia y transacción viven en `modules/automatizaciones/servicio.py`.

1. Registrar routers en principal.py con prefijo /api/v1.
2. Homologar errores, CORS y dependencias compartidas sin mezclar reglas de dominio.
3. Distinguir salud de infraestructura y disponibilidad funcional de un módulo.
4. Conectar servicios mediante interfaces públicas y dejar el cálculo en su dueño.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Una ruta de dominio respeta sobre, permisos y errores documentados; salud refleja conexión real.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Gestión de usuarios local · 30-09-2026

A01 ampliado por Codex para Axel: API /usuarios y pantalla administrativa para listado, creación, edición de datos/roles y activación. Contraseñas protegidas y respuestas sin hash; última cuenta administrativa activa protegida con locks ordenados. Sin migración. PostgreSQL: 13 pruebas de usuarios/acceso correctas, incluidas operaciones concurrentes. Typecheck y build correctos. Guía/mapa de /usuarios actualizados; sin publicación remota.
