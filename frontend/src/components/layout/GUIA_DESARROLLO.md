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

**Paso 2 local · 30-09-2026:** el menú Producción enlaza /planificacion, que ya consulta la API real de M02.

**Integración 30-09-2026:** El menú conserva piloto, pronósticos y panel; añade ingredientes, recetas e inventario publicados por Rojas. No se añadió una pantalla ficticia de proveedores.

Archivos técnicos observados al preparar esta guía: `ProtectedShell.tsx`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Edu Sanchez](../../../../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

**A01:** `ProtectedShell` escucha el evento `foodsave:sesion-vencida` del cliente HTTP, limpia el token y vuelve al inicio de sesión ante un 401 de una ruta protegida. Mantener una sola reacción de sesión para las pantallas nuevas.

El menú incluye `/inicializacion` porque la carga CSV del piloto ya tiene página y API reales; esa pantalla identifica el asistente completo como pendiente.

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

## Gestión de usuarios local · 30-09-2026

A01 ampliado por Codex para Axel: API /usuarios y pantalla administrativa para listado, creación, edición de datos/roles y activación. Contraseñas protegidas y respuestas sin hash; última cuenta administrativa activa protegida con locks ordenados. Sin migración. PostgreSQL: 13 pruebas de usuarios/acceso correctas, incluidas operaciones concurrentes. Typecheck y build correctos. Guía/mapa de /usuarios actualizados; sin publicación remota.

## Inicio y navegación · 30-09-2026

Ruta / implementada como página principal protegida con bienvenida y consultas reales de inicialización/modelo, últimos planes y pedidos pendientes de las últimas 50 propuestas; errores parciales se muestran sin sustituirlos por cero. Accesos a inventario, recetas, Proveedores/Telegram, Compras, evaluación y automatizaciones. Login exitoso y marca FoodSave enlazan a /. La página /panel conserva la evaluación histórica de Kevin.

Menú de escritorio dentro de sidebar-menu: altura disponible, min-height:0, overflow-y:auto, teclado y scroll independientes; marca/cierre de sesión permanecen visibles. En móvil se mantiene navegación horizontal por grupo y desplazamiento normal de página. Usuarios solo visible a Administrador. Implementación por Codex para Axel en coordinación E04 de Edu; no añade datos simulados al producto.

## Claridad y flujo completo · 30-09-2026

GuiaPantalla aporta propósito/pasos/términos/enlace según ruta, incluidos detalle de ejecución y piloto. ProtectedShell conserva autenticación/permisos y usa menú agrupado, indicador de ruta y botón móvil con aria-expanded/controls. Piloto se abre desde Datos iniciales; Notificaciones futura no aparece en navegación principal.


## Navegación, páginas y detalles · 30-09-2026

AppShell vive en el layout raíz y conserva el marco y ContextoSesion. ProtectedShell solo presenta la pantalla. actualizarPerfilLocal/actualizarNegocioLocal permiten reflejar cambios sin reload. La sesión se consulta al entrar desde login o al reintentar un error, no en cada ruta. Conservar evento 401 y validación de permisos en servidor.
