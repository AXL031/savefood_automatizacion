# Guía de desarrollo — Rutas y navegación

04-11-2026 · Lighthouse Desktop: layout.tsx precarga las variantes latinas locales de Manrope y Bricolage mediante next/font/local, conservando los imports Fontsource como respaldo para los demás alfabetos. Las variables de estilos priorizan esas fuentes precargadas. Los enlaces de las tarjetas de Inicio mantienen al menos 24px de alto para evitar objetivos contiguos demasiado próximos. No generalizar esta regla a todo enlace de la aplicación.

Inicio reserva con `.home-next-step-slot` la altura de escritorio del siguiente paso durante la consulta (114px observados); es un mínimo, permite crecer al texto y no fija la altura móvil. El aviso de carga sigue siendo un estado accesible y se conserva la condición original que muestra el siguiente paso. Esta reserva evita que el dashboard salte cuando llega el resumen.

`body` usa `display: flow-root` para contener el margen vertical de `.access-state` durante la carga de sesión. No sustituirlo por un contenedor con overflow: la navegación lateral conserva su posicionamiento sticky y la página debe seguir desplazándose normalmente.

04-11-2026 · Segunda revisión de controles a partir de captura de Notificaciones: además de `.field` y `.operation-form`, `styles.css` protege controles nativos dentro de formularios con selectores `:where` de baja especificidad. Etiquetas encima del control, textareas112px y texto/selects48px; casillas/rango/archivo y paginadores se excluyen de reglas de texto. Avisos, recepción y conciliación incorporan estructura compartida explícita. Mantener guía de Forms y pruebas de los consumidores; no afirmar cobertura solo por revisar formularios que ya usan clases comunes.

04-11-2026 · Estilo de Resultados extendido a FoodSave administrativo por solicitud de Axel: `ProtectedShell` usa `layout/MarcoPagina.tsx`, portada verde/pestañas por sección y superficies/jerarquía comunes en `.workspace-page`. Inicio y las tres vistas de Resultados conservan sus portadas existentes. Textos, formularios y lógica siguen perteneciendo a cada módulo. Tienda independiente conserva su diseño; el login administrativo adopta el fondo verde de la referencia. Mantener correcciones de campos de48px y comprobar escritorio/móvil al añadir estilos. [Especificación visual vigente](../../../docs/diseno/especificacion-visual.md).

04-11-2026 · Formularios compartidos: `styles.css` alinea `.form-grid` al inicio y evita que `.field` estire sus filas por ayuda/error del vecino. Inputs/selects comunes y de operaciones mantienen 48px; textareas conservan altura propia. Ayuda/error de campo sin margen externo, controles con min-width0, acciones con separación/gap y casillas de 18px fuera de reglas de texto. Fieldsets de operaciones usan cuadrícula/espaciado explícitos. No fijar altura de toda la fila ni añadir márgenes compensatorios por pantalla. En móviles estrechos el mínimo del body se ajusta al ancho disponible, sin imponer desbordamiento de 320px. Ver evidencia/alcance en avances de Cueva; no cambia API ni datos.

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

Menú por etapas con desplegable móvil; Inicio destaca la siguiente acción. Los textos visibles se redactan como producto en funcionamiento: sin «demostración», «escenario», «piloto», «local» ni guías tipo manual. No usar mensajes de funciones pendientes si la ruta/API ya está implementada. Labels técnicos en detalles. Tablas anchas con scroll horizontal. Ver especificacion-visual.md y registro Sanchez.


## Navegación, páginas y detalles · 30-09-2026

AppShell se monta en layout.tsx: mantiene sesión, sidebar y encabezado entre rutas. ProtectedShell aporta título/guía/contenido de cada pantalla. Navegar con Link no vuelve a consultar perfil/negocio; 401 y cerrar sesión limpian el contexto. Tablas disponibles consumen TablaPaginada/TablaDatos; detalles y edición de registros usan PanelDetalle.

## Dashboard y Reportes de lectura · 01-10-2026

Ampliación expresa: Inicio con ventas diarias, ranking y pedidos; `/informes` con períodos inclusivos, versión del modelo, tablas paginadas, detalle en diálogo y CSV completo del período. [Contrato](../../../docs/api/contrato-informes.md). Ventas publica `resumen_ventas`/`periodo_ventas`; Compras `resumen_pedidos`/`periodo_propuestas` cuenta pedidos sin multiplicar intentos; K03 admite filtros `desde`/`hasta` opcionales conservando la consulta anterior sin filtros. Informes coordina únicamente interfaces públicas. No migra, entrena, modifica stock ni envía mensajes. Fechas ausentes no se rellenan con cero. Registro/evidencia en Bohorquez y coordinación Cueva.

## Corte vigente · 11-10-2026 · Flujo y promociones

Codex para Axel implementó configuración reutilizable, comprobación de requisitos por interfaces públicas, calendario histórico diario de 1–31 días, modelo/modo conservados y pausa/cancelación/reprogramación de tareas sin despacho. Promociones tienen regla inmutable versionada, reserva transaccional después de cada ajuste nuevo de producto y evaluación idempotente con snapshot/motivo; API y pantalla reales. Se conserva la propiedad de cada dominio.

[Contrato vigente, APIs y límites](../../../docs/api/contrato-flujo-promociones.md). Aplicar `0015_flujo_promociones` antes de actualizar API/worker/Beat. El diagnóstico no ejecuta inferencia ni envía mensajes; guardar configuración no agenda. Consultas de tareas/evaluaciones admiten paginación real con total. La pausa no recupera horas perdidas: reprogramar antes de reanudar. Deshabilitar promociones afecta ajustes nuevos; tareas ya reservadas conservan su versión. Hora simulada de evaluación avanza por el tiempo real transcurrido desde el ajuste para comprobar frescura.

Las notas fechadas de cortes anteriores son historial; no usar sus pendientes como estado actual. Pruebas y límites finales en los registros Cueva/Vera/Sanchez, incluyendo PostgreSQL/Redis y Telegram real solo si fueron ejecutados. No confundir fixtures QA con datos de operación.


## Gestión y avisos · 14-10-2026 · Codex para Axel

Patrón de gestión solicitado por Axel: listar registros primero y abrir creación/edición con botón y PanelDetalle. Aplicado a Proveedores, Ingredientes, Usuarios, Planes, Ajustes de inventario y Entrenamiento. Recetas ya abre su gestión desde la tabla. Configuración singular, importación y asistente conservan su recorrido propio.

## Avance K03/K04 y E01/E02 · 20-10-2026

Codex a solicitud del usuario; se conserva la responsabilidad de los dominios. Inicio, Pronósticos, Evaluación y Reportes comparten cabecera/navegación analítica, paleta hoja/yema e indicadores de datos reales. Estilos en styles.css; grid con minmax(0,1fr) y mínimos contenidos evita desbordamiento en móvil. No añade métricas económicas ni tareas externas.

[Contrato y ejemplos vigentes](../../../docs/api/contratos.md#k03k04-y-frontera-e01--20-10-2026). [Pruebas, consumidores y límites del corte](../../../docs/equipo/avances/bohorquez.md). Sin migraciones nuevas; no se acredita PostgreSQL/Redis, CI remoto ni envío real por la QA visual.


## Entradas de productos · 28-10-2026

styles.css añade fieldsets entry-line para agrupar lotes, mínimos contenidos y controles sin desbordamiento. /inventario contiene la entrada de productos y consulta el día actual del negocio, con fecha histórica seleccionable. [Contrato implementado](../../../docs/api/contrato-entradas-productos.md). Autor Codex para Axel; dominio Inventario de Vera y responsabilidades de los demás integrantes conservados. Evidencia en avances/cueva.md.

## Ampliación vigente · 28-10-2026 · Tienda por API

/tienda-admin administra ficha/publicación/entregas/reservas. /tienda/* sigue redirigiendo al proyecto independiente. /ventas presenta ambos canales; cierre/ML no se deducen de tickets. Coordinación Codex para Axel (A04), conservando dominios Rojas (Tienda), Sanchez (Ventas/UI) y Vera (Inventario/Promociones). La ampliación usa dos proyectos y bases independientes: solo API HTTP, sin importar modelos, montar carpetas ni consultar PostgreSQL desde tienda. Payme solo preproducción y comprador invitado; cuatro botones independientes. Ver docs/api/contrato-integracion-tienda.md desde la raíz y registro Cueva para evidencia y límites.
