# Guía de desarrollo — Rutas y navegación

**Carpeta:** `frontend/src/app`.

**Responsable:** Edu Sanchez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../docs/guia-inicio-desarrollo.md).
- [docs/api/rutas-api.md](../../../docs/api/rutas-api.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `layout.tsx`, `page.tsx`, `styles.css`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Edu Sanchez](../../../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

1. Mantener layout, estilos y entrada raíz según estado de sesión/inicialización.
2. Cada dueño implementa page.tsx de su dominio usando ProtectedShell y componentes comunes.
3. Mostrar carga, vacío, error y falta de backend; proteger escrituras también en servidor.
4. Las carpetas nuevas de rutas documentales no son páginas disponibles hasta añadir implementación.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Navegación identifica correctamente funciones disponibles y estado de la demo.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Inicio y navegación · 30-09-2026

Ruta / implementada como página principal protegida con bienvenida y consultas reales de inicialización/modelo, últimos planes y pedidos pendientes de las últimas 50 propuestas; errores parciales se muestran sin sustituirlos por cero. Accesos a inventario, recetas, Proveedores/Telegram, Compras, evaluación y automatizaciones. Login exitoso y marca FoodSave enlazan a /. La página /panel conserva la evaluación histórica de Kevin.

Menú de escritorio dentro de sidebar-menu: altura disponible, min-height:0, overflow-y:auto, teclado y scroll independientes; marca/cierre de sesión permanecen visibles. En móvil se mantiene navegación horizontal por grupo y desplazamiento normal de página. Usuarios solo visible a Administrador. Implementación por Codex para Axel en coordinación E04 de Edu; no añade datos simulados al producto.

## Claridad y flujo completo · 30-09-2026

Todas las rutas disponibles consumen GuiaPantalla. Menú por etapas con desplegable móvil; Inicio orienta el recorrido. No usar mensajes de funciones pendientes si la ruta/API ya está implementada. Labels técnicos en detalles. Tablas anchas con scroll horizontal. Ver especificacion-visual.md y registro Sanchez.


## Navegación, páginas y detalles · 30-09-2026

AppShell se monta en layout.tsx: mantiene sesión, sidebar y encabezado entre rutas. ProtectedShell aporta título/guía/contenido de cada pantalla. Navegar con Link no vuelve a consultar perfil/negocio; 401 y cerrar sesión limpian el contexto. Tablas disponibles consumen TablaPaginada/TablaDatos; detalles y edición de registros usan PanelDetalle.
