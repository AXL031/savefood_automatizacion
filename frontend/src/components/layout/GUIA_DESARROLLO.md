# Guía de desarrollo — Layout y navegación protegida

**Carpeta:** `frontend/src/components/layout`.

**Responsable:** Edu Sanchez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `ProtectedShell.tsx`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Edu Sanchez](../../../../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

1. Mantener ProtectedShell, menú y contexto visible del comercio.
2. Consumir sesión/perfil/configuración definidos por Axel.
3. Añadir rutas activas de cada dueño sin mostrar futuras como implementadas.
4. Mantener experiencia de sesión vencida consistente.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Usuario sin sesión vuelve al acceso y quien entra encuentra su pantalla sin duplicar layout.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
