# Guía de desarrollo — Identidad, sesiones y configuración común

**Carpeta:** `backend/app/core`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contratos.md](../../../docs/api/contratos.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `__init__.py`, `base.py`, `base_datos.py`, `crear_admin.py`, `identidad.py`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

**A01 disponible:** `identidad_actual` devuelve 401 ante ausencia, invalidez o usuario inactivo; `requiere_administrador` devuelve 403 al Operador. `errores.py` registra el sobre HTTP uniforme y detalles de validación 422. Los módulos nuevos deben lanzar `ErrorAPI` para códigos propios y compartir `obtener_sesion` cuando una operación abarque varios servicios.

1. Mantener Base, motor SQLAlchemy y ciclo de sesión.
2. Validar configuración requerida al iniciar sin imprimir secretos.
3. Exponer identidad y requiere_administrador como dependencias públicas.
4. Permitir la unidad de trabajo compartida de inicialización y errores uniformes.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Una operación revertida no deja cambios parciales; permisos se validan en servidor.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
