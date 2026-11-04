# Lighthouse de FoodSave — 04-11-2026

Auditoría de escritorio completada en `vera` sobre localhost:3000: **23 rutas**, tres mediciones iniciales y tres finales por ruta. Las 23 alcanzan **100 en accesibilidad**; 22 alcanzan **100 en rendimiento** y Automatización pasa de **81 a 88**. Las puntuaciones corresponden a la instalación y sus datos existentes, incluidos estados vacíos o de error; no certifican todos los flujos de negocio ni sustituyen una auditoría manual completa de accesibilidad.

## Método y evidencia

Lighthouse 13.6.0, preset Desktop, Performance y Accessibility, viewport de 1350×940, RTT de 40ms, 10Mbps y CPU×1. Sesión administrativa conservada con disableStorageReset; credenciales y tokens excluidos de los archivos. Herramientas temporales fuera del proyecto, sin dependencias nuevas de FoodSave. Build de producción Next 15.5.26. No se ejecutaron builds durante las mediciones comparadas.

[JSON con las tres ejecuciones de cada corte, métricas y hallazgos](lighthouse-2026-11-04.json). La tabla usa medianas; FCP/LCP/TBT se expresan en milisegundos y CLS no tiene unidad. Las revalidaciones de Tienda administrativa e Inicialización sustituyen su resultado previo tras dos correcciones de enlaces acotadas a esas páginas; el resto conserva la medición completa de la misma implementación compartida. Las series intermedias interrumpidas no forman parte de esta comparación.

| Ruta | Rendimiento antes → final | Accesibilidad antes → final | FCP final | LCP final | CLS final | TBT final |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `/` | 95 → 100 | 92 → 100 | 173.3 | 299.0 | 0.0257 | 0.0 |
| `/automatizaciones` | 81 → 88 | 97 → 100 | 170.3 | 292.1 | 0.2395 | 0.0 |
| `/compras` | 97 → 100 | 96 → 100 | 170.6 | 289.6 | 0.0000 | 0.0 |
| `/ingredientes` | 97 → 100 | 96 → 100 | 174.8 | 291.9 | 0.0002 | 0.0 |
| `/iniciar-sesion` | 100 → 100 | 100 → 100 | 189.4 | 189.4 | 0.0000 | 0.0 |
| `/inventario` | 96 → 100 | 96 → 100 | 174.3 | 288.8 | 0.0138 | 0.0 |
| `/operaciones` | 97 → 100 | 96 → 100 | 174.0 | 286.5 | 0.0000 | 0.0 |
| `/planificacion` | 97 → 100 | 96 → 100 | 170.0 | 291.9 | 0.0000 | 0.0 |
| `/productos` | 97 → 100 | 96 → 100 | 174.4 | 327.8 | 0.0002 | 0.0 |
| `/promociones` | 94 → 100 | 96 → 100 | 170.3 | 289.4 | 0.0486 | 5.0 |
| `/proveedores` | 97 → 100 | 96 → 100 | 174.1 | 290.7 | 0.0000 | 0.0 |
| `/recetas` | 97 → 100 | 96 → 100 | 170.9 | 304.0 | 0.0002 | 0.0 |
| `/tienda-admin` | 97 → 100 | 96 → 100 | 170.3 | 287.6 | 0.0040 | 0.0 |
| `/ventas` | 96 → 100 | 96 → 100 | 174.6 | 292.0 | 0.0103 | 0.0 |
| `/configuracion` | 97 → 100 | 96 → 100 | 170.8 | 283.3 | 0.0000 | 0.0 |
| `/informes` | 97 → 100 | 96 → 100 | 170.4 | 291.0 | 0.0000 | 0.0 |
| `/panel` | 97 → 100 | 96 → 100 | 172.1 | 304.0 | 0.0084 | 0.0 |
| `/pronosticos` | 95 → 100 | 96 → 100 | 170.5 | 307.5 | 0.0284 | 0.0 |
| `/usuarios` | 97 → 100 | 96 → 100 | 170.3 | 287.2 | 0.0000 | 0.0 |
| `/inicializacion` | 97 → 100 | 96 → 100 | 175.9 | 317.3 | 0.0000 | 0.0 |
| `/inicializacion/piloto` | 96 → 100 | 96 → 100 | 170.5 | 292.6 | 0.0232 | 0.0 |
| `/notificaciones` | 97 → 100 | 96 → 100 | 173.7 | 289.3 | 0.0069 | 0.0 |
| `/automatizaciones/ejecuciones/2` | 97 → 100 | 96 → 100 | 170.5 | 325.7 | 0.0002 | 0.0 |

## Cambios y comprobaciones

- Avisos conserva el texto visible y contador en su nombre accesible, compatible con control por voz.
- Enlaces dentro de frases subrayados en cabecera, asistente, tienda administrativa y estados de preparación/evaluación. Enlaces de tarjetas de Inicio con altura mínima de 24px.
- Precarga de las fuentes latinas locales de Manrope y Bricolage; imports de Fontsource conservados. No se cambian tipografías ni dependencias.
- Body con flow-root para contener el margen de la carga de sesión; reserva flexible de 114px para el siguiente paso de Inicio mientras consulta. Se conservan los mensajes, las consultas y las condiciones originales.
- Build de 25 rutas y `npm run typecheck -- --incremental false` correctos. El intento incremental inicial falló solo por permisos al escribir tsconfig.tsbuildinfo en el contenedor no root.
- Regresiones existentes de marco/navegación, notificaciones y asistente correctas con React real y APIs falsas; el asistente comprueba ocho estados/escenarios.
- Ocho comprobaciones de navegador correctas: abrir diálogos de Ingredientes/Inventario con teclado, foco contenido, Tab, Escape y retorno; filtro y restauración en Inventario; paginación de Productos; navegación contextual; etiquetas/precargas y enlaces subrayados. Sin errores JavaScript. No se confirmaron operaciones ni se enviaron mensajes.

## Cobertura y límites

- Portal `/proveedor/pedido/[token]` sin propuestas/enlaces existentes: no se crearon pedidos para auditarlo. `/tienda/*` redirige al proyecto independiente, fuera del alcance.
- La API instalada devuelve 404 en `/operaciones/avisos`, `/inventario/entradas-productos`, `/inventario/entradas-productos/contexto`, `/tienda-admin/estado`, `/tienda-admin/productos` y `/tienda-admin/reservas` bajo `/api/v1`. En esas secciones se verificó la presentación disponible, no una integración funcional completa. Se mantuvo el backend instalado.
- Automatización conserva CLS durante la recuperación del asistente; su mediana mejora de 81→88. Se conserva su gestión de foco y navegación entre pasos; no se rediseña el asistente para alcanzar una puntuación artificial.
- El primer diagnóstico de la instalación anterior midió una redirección al login (97/100, CLS 0,10444). Al actualizar solo frontend a la rama actual, el login directo dio 100/100. Esos recorridos/versiones diferentes no son una comparación atribuible a las correcciones; la tabla anterior sí usa la rama actual en ambos cortes.
- Evidencia privada adicional en `.tmp/lighthouse/`. APIs, tipos de negocio, migraciones, datos, stock, pagos y tienda independiente sin cambios en este trabajo.
