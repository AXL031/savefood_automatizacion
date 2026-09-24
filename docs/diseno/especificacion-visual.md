# Especificación integral de diseño de FoodSave

## Identidad y propósito de la interfaz

FoodSave es una aplicación de gestión operativa para un negocio de alimentos. Su interfaz presenta el estado de la operación, las decisiones automáticas, sus resultados y los problemas que requieren intervención. El diseño debe ser sobrio, amplio y fácil de recorrer: superficies claras, pocos acentos de color, jerarquía tipográfica definida y datos agrupados en tarjetas. La pantalla debe responder rápidamente a cuatro preguntas: **qué ocurre, qué hará el sistema, cómo se verificó y qué debe hacer la persona usuaria**.

El idioma de la interfaz es español. El negocio activo y el rol aparecen en el encabezado. Los importes se muestran en soles con el prefijo `S/`, las horas en formato de 24 horas y las cantidades con su unidad (`u.`, `kg`, `L` o `%`). Los datos de ejemplo de una pantalla no constituyen valores globales del producto.

## Sistema de color

| Función | Valor | Aplicación |
|---|---|---|
| Primario | `#0F766E` | Botones principales, texto destacado y acciones |
| Primario suave | `#CCFBF1` | Elemento de navegación activo, iconos y superficies informativas |
| Acento | `#14B8A6` | Barras de progreso y énfasis gráfico |
| Éxito | `#16A34A` | Confirmaciones, resultados positivos y completados |
| Advertencia | `#F59E0B` | Pendientes, riesgos moderados y verificación |
| Error | `#DC2626` | Fallos, riesgo alto y acción requerida |
| Texto principal | `#111827` | Títulos, números y contenido principal |
| Texto secundario | `#6B7280` | Descripciones, unidades, detalles auxiliares |
| Fondo | `#F8FAFC` | Área de trabajo |
| Borde | `#E5E7EB` | Tarjetas, campos, tablas y separadores |

El blanco se reserva para barra lateral, encabezado, tarjetas y campos. Las insignias usan una versión clara del color de estado y texto legible del mismo grupo. Una alerta de error o advertencia puede ocupar una superficie tintada de borde suave. El color nunca es el único indicador de estado: debe acompañarse de una palabra como «Fallida» o «En control».

## Tipografía y jerarquía

La familia tipográfica es **Inter**. La escala base es: título grande de 30 px en negrita; título de pantalla o sección principal de 21 px en negrita; título de tarjeta de 15 px en seminegrita; cuerpo de 13 px normal; etiqueta de 11 px peso medio; texto auxiliar de 10 px seminegrita. Los números de indicadores se presentan con mayor peso y tamaño que su etiqueta. Las etiquetas de tabla son pequeñas, discretas y consistentes; los datos siguen siendo el elemento principal.

La jerarquía de contenido es: navegación contextual → título de página → descripción o fecha → indicadores → zona de trabajo → detalles y trazabilidad. Un aviso crítico se coloca antes de los indicadores para no esconder la excepción.

## Estructura de escritorio

La composición de referencia usa un lienzo de **1440 px de ancho**. A la izquierda hay una barra lateral blanca de alrededor de 248 px con el logotipo arriba y los grupos **Operación, Abastecimiento, Prevención y Sistema**. El elemento seleccionado tiene fondo verde agua claro, icono y texto primario. El área restante contiene encabezado blanco y superficie de trabajo gris muy clara.

El encabezado incluye miga de navegación, icono contextual sobre un cuadro suave, título, subtítulo, identificación del negocio y rol, y un botón principal a la derecha. Debajo suele aparecer una fila de cuatro indicadores. El contenido usa una columna principal amplia para tablas o tarjetas de trabajo y una columna secundaria más estrecha para detalle, estado o siguiente acción. Los componentes dejan espacio en blanco suficiente para separar bloques sin sombras pronunciadas.

Se usan tarjetas blancas con borde de 1 px `#E5E7EB` y radio de **14 px**. Los botones tienen radio de **8 px**. Las insignias son ovaladas. Una escala regular de separación, en torno a 8, 16, 24 y 32 px, mantiene orden entre controles, tarjetas y secciones. La aplicación móvil y los puntos de ruptura aún no tienen composición definida en esta especificación; deberán diseñarse sin perder indicadores críticos, causas de fallo ni acciones de recuperación.

## Componentes obligatorios

| Componente | Estructura y comportamiento visual |
|---|---|
| Navegación lateral | Logotipo, grupos rotulados, icono y nombre por opción, estado activo inequívoco. |
| Encabezado de página | Miga, icono, título, descripción, negocio/rol y acción principal. |
| Tarjeta de indicador | Etiqueta, cifra dominante, unidad o periodo y nota de estado en insignia. |
| Tabla | Encabezados breves, separadores finos, datos alineados y estados textuales. Los importes y cantidades se leen junto con su unidad. |
| Tarjeta de detalle | Identifica el registro seleccionado, resume sus atributos y muestra resultado o siguiente paso. |
| Insignia de estado | Píldora de texto corto, con color semántico y contraste suficiente. |
| Aviso | Mensaje concreto que explica evento, consecuencia y posible acción. |
| Barra de progreso | Representa una relación entre avance real y meta, con cifras visibles. |
| Línea de tiempo | Hora, fase, resultado y color de estado por evento. |
| Interruptor | Etiqueta explícita y estado activado o desactivado claramente perceptible. |
| Campo de configuración | Etiqueta sobre el valor, unidad cuando corresponde y agrupación por tema. |
| Botón | Primario oscuro para la acción de mayor prioridad; secundario blanco con borde para alternativas. |

Los controles deben mostrar estados de foco, carga, deshabilitado, éxito y error. Las tablas y paneles necesitan estados vacíos y de fallo que expliquen si no hay información o si no se pudo obtener. Un contador nunca debe aparecer sin contexto temporal cuando este cambie su significado, por ejemplo «hoy», «esta semana» o «últimos 14 días».

## Especificación por pantalla

### Panel principal

La primera fila resume demanda prevista, producción planificada, unidades con riesgo de excedente y pérdida económica evitada. El área principal contiene producción del día por producto y avance frente a meta, aviso preventivo, pedidos a proveedores y actividad automática. La columna de contexto informa estados recientes e impacto acumulado. La acción de cabecera abre automatizaciones.

### Planificación de producción

Presenta precisión reciente, demanda prevista, margen de seguridad y número de insumos faltantes. Una tabla ordena producto, demanda, existencias, cantidad a producir y confianza. Una explicación breve aclara cómo se obtuvo el plan. A la derecha se listan insumos faltantes, proveedor sugerido y cantidad, con acción para generar pedidos. La cabecera permite aprobar el plan; un bloque informa el siguiente paso automático.

### Compras y abastecimiento

Resume pedidos generados, enviados, pendientes y total estimado. Cada pedido muestra proveedor, número, hora, importe, estado, insumos, origen y regla aplicada. Al seleccionar uno, se ve su historial de control y resultado. Un aviso destaca pedidos sin confirmación. La acción principal permite crear un pedido.

### Riesgo de excedentes

Resume productos en riesgo, unidades, valor potencial perdido y acciones activas. La tabla distingue producto, stock, venta estimada, excedente, nivel de riesgo y acción. El detalle preventivo compara el estado anterior, la promoción aplicada y la medición posterior; permite mantener la acción o recalcular. La secuencia visual del control es detectar, decidir, actuar, verificar y corregir.

### Promociones

Resume promociones activas, unidades recuperadas, descuento medio y pérdida evitada. La tabla presenta producto, descuento, inicio, fin, origen y estado. El detalle muestra duración, origen, decisión y confirmación de aplicación. Una tarjeta compara excedente inicial, ventas durante el periodo de medición, excedente estimado posterior y pérdida evitada. La cabecera permite crear una promoción.

### Automatizaciones

Resume ejecuciones del día, completadas, en control y fallidas. Cada automatización muestra nombre, frecuencia o disparador, entradas, acción y estado de activación. En una columna se explican las fases detectar, decidir, actuar, verificar, corregir y notificar. Debajo aparecen las últimas ejecuciones con hora, duración y estado. La cabecera permite crear una automatización.

### Ejecución y control

Cuando ocurre un fallo, un aviso superior explica el problema y el número de intentos. Cuatro indicadores resumen estado, intentos, duración e impacto. La línea de tiempo registra detección, decisión, acción, verificación, corrección y notificación con hora y resultado. Una columna muestra la notificación enviada y las acciones de recuperación: reintentar, cambiar proveedor o registrar pedido manual. Se explican el impacto en el plan y las reglas aplicadas.

### Configuración

Agrupa datos del negocio, automatizaciones activas, límites y reglas de control, notificaciones y estado del sistema. Presenta interruptores para activar reglas y avisos, campos para nombre, cierre, zona horaria y límites, y una acción única de guardar cambios. El estado del sistema informa integraciones, sincronización y cobertura de proveedores.

## Estados y lenguaje

Los estados que se muestran deben preservar sus diferencias: **programada** indica acción futura; **activa**, una acción vigente; **en control**, una acción cuyo efecto se mide; **enviada**, una comunicación emitida; **confirmada**, una respuesta recibida; **completada**, un proceso terminado satisfactoriamente; **pendiente**, una espera o intervención; **fallida**, una ejecución que requiere revisión. La redacción evita llamar «confirmado» a algo solamente enviado.

Los títulos y opciones de navegación se expresan en español, incluido **Panel principal** e **Informes**. Los avisos dicen qué pasó y qué puede hacerse. Los resultados estimados se distinguen de los observados. Las cifras monetarias y porcentajes deben conservar criterio y periodo para no inducir una lectura incorrecta.

## Accesibilidad

Los iconos llevan etiqueta textual o nombre accesible. Los interruptores exponen su estado. Foco visible y navegación por teclado alcanzan menús, botones, campos, tablas y opciones de recuperación. Los avisos críticos se anuncian sin depender únicamente de color. El contraste de texto secundario, insignias y estados debe verificarse al implementar, especialmente en tamaños de 10 y 11 px.
