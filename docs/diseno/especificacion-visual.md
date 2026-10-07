# Especificación visual de FoodSave

## Implementación de claridad transversal · 30-09-2026

ProtectedShell y GuiaPantalla orientan todas las rutas disponibles con propósito, pasos, términos y enlace siguiente. Menú agrupado en preparación, catálogo/inventario, planificación/compras, resultados y administración; menú móvil desplegable accesible y navegación activa por ruta. Inicio muestra un recorrido de cuatro pasos. No se llama backend futuro desde Notificaciones: ofrece enlaces a pedidos y ejecuciones reales. La carga completa está implementada y no se describe como pendiente.

Las páginas distinguen hora real/escenario, cálculo/pedido/envío, stock desconocido/cero y modelo/evaluación. Etiquetas humanas reemplazan códigos internos; claves/JSON/huellas y acciones de rechazo/cancelación están en detalles desplegables. Programación elige productos por nombre y guarda el modo; compras explica bloqueos y siguiente acción, revisión del chat y evidencia. Proveedores separa conectar bot, vincular/verificar chat y registrar ofertas. Evaluación explica MAE/WAPE/cobertura. Formularios, textos y tablas tienen mayor tamaño; tablas anchas se desplazan horizontalmente sin partir encabezados en letras.

utils/unidades.ts convierte decimales mediante cadenas: >=1000 g/ml → kg/L, entradas kg/g y L/ml en ajustes/ofertas, conservando unidad base/API. No hay migración de unidades ni fórmulas ML nuevas. Esta sección describe código actual; maquetas más amplias que siguen mantienen carácter de referencia.

## Identidad y propósito de la interfaz

Estilo: aplicación de gestión sobria, superficies claras, pocos acentos, datos en tarjetas. Cada pantalla responde **qué pasa, qué hará el sistema, cómo se verificó y qué debe hacer la persona**.

## Tokens

Definirlos como variables CSS en `:root` de `styles.css` y no escribir colores sueltos.

| Token | Valor | Uso |
|---|---|---|
| `--color-primario` | `#0F766E` | Botón principal, enlaces, acción |
| `--color-primario-suave` | `#CCFBF1` | Navegación activa, fondos informativos |
| `--color-acento` | `#14B8A6` | Progreso, foco, énfasis gráfico |
| `--color-exito` | `#16A34A` | Completado, confirmado |
| `--color-advertencia` | `#F59E0B` | Pendiente, verificando, riesgo moderado |
| `--color-error` | `#DC2626` | Fallido, acción requerida |
| `--color-texto` | `#111827` | Títulos, cifras, contenido |
| `--color-texto-secundario` | `#6B7280` | Descripciones, unidades |
| `--color-fondo` | `#F8FAFC` | Área de trabajo |
| `--color-borde` | `#E5E7EB` | Tarjetas, campos, tablas |
| `--color-serie-real` | `#111827` | Serie «real» en gráficos (pronóstico usa primario) |

Blanco solo en barra lateral, encabezado, tarjetas y campos. Insignias: fondo claro del color de estado y texto oscuro del mismo tono. El color nunca es el único indicador: siempre va con texto.

Forma y espacio: tarjeta con borde 1 px y radio **14 px**; botón y campo radio **8 px**; insignia en píldora. Espaciado en múltiplos de 4: 4, 8, 16, 24, 32 px. Sin sombras marcadas.

## Tipografía

**Inter**, cargada con `next/font/google` (pesos 400, 500, 600, 700) y respaldo `system-ui`.

| Nivel | Tamaño / peso | Uso |
|---|---|---|
| H1 | 30 px / 700 | Cifra o título destacado |
| H2 | 21 px / 700 | Título de pantalla |
| H3 | 15 px / 600 | Título de tarjeta |
| Cuerpo | 13 px / 400 | Texto general y celdas |
| Etiqueta | 11 px / 500 | Etiquetas de campos y KPIs |
| Leyenda | 10 px / 600, mayúsculas | Encabezados de tabla, grupos de navegación |

## Formatos

- Números con `Intl.NumberFormat("es-PE")`: miles con coma y decimales con punto (`1,248`; `0.080`). Ingredientes con hasta 3 decimales; productos enteros.
- Unidades: `u.` (la unidad base `unidad` se muestra como `u.`), `g`, `kg`, `ml`, `l`, `%`.
- Fechas `DD/MM/AAAA`; horas de 24 h; siempre en la zona horaria del negocio (`formatearFechaHora`), no la del navegador.
- Fecha del escenario histórico rotulada «Escenario: 24/08/2022»; hora real rotulada «Ejecutado: 06/10/2026 14:05».
- Moneda `S/` (fuera del recorrido de demo).

## Estructura

Lienzo de referencia 1440 px. Barra lateral blanca de **248 px**: logotipo, grupos y opciones con ícono + texto; la opción activa usa fondo primario suave y texto primario. Grupos y pantallas: los de la [especificación funcional](../funcionalidades/especificacion-modulos.md#navegación).

Encabezado de página: miga real (`Grupo / Pantalla`), ícono en cuadro suave, título H2, descripción o fecha, negocio y rol, y a la derecha **una** acción principal si la pantalla la tiene.

Orden del contenido: aviso crítico → fila de 4 indicadores → columna principal (tabla o formulario) + columna lateral (detalle, estado o siguiente paso) en proporción ~2:1.

Puntos de quiebre: ≤1000 px una columna y 2 indicadores por fila; ≤720 px la navegación pasa arriba con desplazamiento horizontal; ≤480 px 1 indicador por fila y formularios en una columna. Nunca se ocultan avisos de error ni acciones de recuperación.

Íconos: un solo conjunto de trazo (Lucide), 16–20 px, siempre con texto o `aria-label`.

## Componentes

| Componente | Regla |
|---|---|
| Indicador (KPI) | Etiqueta, cifra dominante, unidad o periodo, insignia opcional |
| Tabla | Encabezados en leyenda, separadores finos, cifras alineadas a la derecha con unidad, estado como insignia; vacío y error con mensaje |
| Tarjeta de detalle | Registro seleccionado, atributos y siguiente paso |
| Insignia | Texto corto; colores por estado (abajo) |
| Aviso (`EstadoPanel`) | Qué pasó, consecuencia y acción posible |
| Formulario | Etiqueta arriba, unidad junto al campo, error debajo del campo y resumen arriba (`ResumenErrores`); botón con estado de carga |
| Línea de tiempo | Hora, fase, resultado y color de estado |
| Pasos | Asistente numerado (`PasosAsistente`) |
| Botón | Primario relleno para la acción principal; secundario blanco con borde |

Todo control interactivo muestra foco, carga, deshabilitado, éxito y error.

## Estados y su color

| Estado | Insignia |
|---|---|
| Completado, confirmado, disponible | Éxito |
| Pendiente, pendiente de aprobación, verificando, programado, reintentando | Advertencia |
| Fallido, error, saldo insuficiente | Error |
| Enviado, en ejecución, automático | Primario suave |
| Sin dato, inactivo, previsto | Neutro (gris) |

«Enviado» no es «confirmado». «Sugerida» (promoción) no es «activa».

## Diseño por pantalla

| Pantalla | Indicadores | Columna principal | Columna lateral | Acción de cabecera |
|---|---|---|---|---|
| Iniciar sesión | — | Panel izquierdo verde oscuro con marca y frase | Tarjeta con correo, contraseña y error inline | Entrar (en la tarjeta) |
| Primera carga | Estado, archivos, filas válidas, errores | Pasos + zona de archivos + vista previa por entidad + errores por hoja/fila/columna | Estado durable y pendientes | Confirmar carga |
| Productos | Activos, con receta, con SKU, de demo | Tabla código, nombre, SKU, estado | Detalle del producto | — |
| Ventas | Días, productos, último día, revisiones | Filtros + tabla diaria («sin dato» ≠ 0) | Historial de revisiones y corrección | — |
| Ingredientes | Total, activos, en uso, sin lote | Tabla código, nombre, unidad, recetas, lotes, estado | Formulario crear/editar; unidad bloqueada con motivo | Nuevo ingrediente |
| Recetas | Productos, con receta, sin receta, versiones | Lista de productos + líneas de la versión activa | Historial de versiones y editor con motivo obligatorio | Nueva versión |
| Inventario | Lotes, por vencer, vencidos, sin caducidad | Fecha + stock por lote con vida útil | Formulario de ajuste + últimos movimientos | Registrar ajuste |
| Planificación | Productos, a producir (u.), ingredientes con faltante, cobertura | Tabla pronóstico, stock, producir, receta vN, estado; traza «cómo se calculó» | Necesidades: requerido, disponible, faltante; enlace a pedidos | Ver pedidos |
| Proveedores | Activos, con chat, ofertas, ingredientes sin oferta | Tabla proveedor, chat, estado | Ofertas del proveedor | Nuevo proveedor |
| Pedidos | Pendientes de aprobación, enviados, fallidos, sin proveedor | Tabla pedido, proveedor, plan, estado | Líneas e intentos de envío | Aprobar envío |
| Pronósticos | Versión, corte, corridas, cobertura | Corridas persistidas | Partición y preparación de modelo | Preparar modelo |
| Panel histórico | MAE, WAPE, % ±20 %, cobertura | Serie de prueba + barras pronóstico vs. real del día | Día y versión elegidos | — |
| Automatizaciones | Programadas, completadas, fallidas, en curso | Programaciones y ejecuciones | Formulario de programación | Programar propuesta |
| Detalle de ejecución | Estado, intentos, duración, efecto | Línea de tiempo | Entrada, resultado y error | — |
| Promociones sugeridas | Evaluadas, sugeridas, rechazadas, descuento medio | Tabla lote, sugerencia o rechazo, motivo | Detalle de la regla aplicada | — |
| Configuración | — | Datos del comercio y modo de envío | Estado de la instalación | Guardar cambios |

## Accesibilidad

Los iconos llevan etiqueta textual o nombre accesible. Los interruptores exponen su estado. Foco visible y navegación por teclado alcanzan menús, botones, campos, tablas y opciones de recuperación. Los avisos críticos se anuncian sin depender únicamente de color. El contraste de texto secundario, insignias y estados debe verificarse al implementar, especialmente en tamaños de 10 y 11 px.


## Navegación y consulta implementadas · 30-09-2026

Marco/sesión persistentes en layout raíz; Link cambia contenido y conserva menú. Tablas paginadas con rango, tamaño y salto, sin alterar decimales ni orden de dominio. Ventas pagina el historial en servidor; listas recientes de otros contratos se identifican. PanelDetalle sustituye los detalles añadidos al pie en recetas, ventas, inventario, planes, compras, pronósticos y edición de ingredientes/usuarios; foco nativo, Escape, encabezado visible y regreso a lista sin perder página.
