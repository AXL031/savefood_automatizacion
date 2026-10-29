# Guía de desarrollo — Herramientas de desarrollo y verificación

## Operaciones compatibles · 28-10-2026

`node scripts/verificar-operaciones.cjs` ejecuta el componente React real con API falsa y sin red: enlace a caja existente, ausencia de segunda caja/tienda acoplada, respuesta perdida tras confirmar, remontaje, recuperación con la misma clave y nueva tanda con clave nueva. No sustituye la prueba de stock/concurrencia PostgreSQL de `test_operacion_integrada.py`.

## Precios estimados de Ventas · 26-10-2026

`cargar-precios-estimados.py` se ejecuta en el entorno backend con `DATABASE_URL`, `--archivo` y `--usuario-id` de administrador activo; sin `--aplicar` valida sin escribir. Comprueba cobertura/identidad/moneda y formato de todo el CSV antes de guardar precios faltantes por `ventas.caja.guardar_precio`, en una única transacción. Clave derivada de SHA-256/código; conserva precios previos y ediciones manuales. [Referencia y ejemplos](../datos_carga/referencias/precios_estimados_ventas_pen.md). No modificar saldos ni insertar tickets como parte de esta carga. `verificar-caja.cjs` comprueba también diálogo con cero elegibles, motivo visible y acción para abrir catálogo.

**Carpeta:** `scripts`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../AGENTS.md).
- [Reparto vigente y criterios de entrega](../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../docs/equipo/dependencias.md).
- [Alcance de la demo](../docs/guia-inicio-desarrollo.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

`verificar-flujo-automatizacion.cjs` (Axel/A03) requiere dependencias instaladas en `frontend` y Node.js; verifica estados y renderizado SSR de ocho escenarios sin APIs ni efectos operativos. Salida OK/exit 0 o error/exit 1. `--preview` añade HTML de fixtures en `.tmp/automatizacion-preview`; abrir mediante servidor estático local para revisar estilos. No sustituye la verificación de polling en navegador ni la integración de servicios de dominio.

1. Agregar solo scripts reproducibles que apoyen arranque, fixtures o verificación.
2. Edu aporta generación de plantillas, Kevin verificación ML; cada script identifica su dueño.
3. Usar rutas explícitas y no borrar volúmenes/datos por defecto.
4. Documentar requisitos, entradas, salida y código de error.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Otra persona ejecuta el script con instrucciones y obtiene un resultado verificable.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.


## Caja presencial · 26-10-2026

`node scripts/verificar-caja.cjs` monta el componente real con React/jsdom y API falsa, sin red: medio intercambiable, permisos, doble clic, confirmación y recuperación tras respuesta perdida/remontaje. Requiere `npm ci --prefix frontend`; jsdom 26.1.0 está fijado como dependencia de desarrollo. [Contrato implementado](../docs/api/contrato-caja-presencial.md). Autor de este corte: Codex para Axel; se conservan las responsabilidades de cada dominio. Evidencia y límites en el registro de Cueva.


## Entradas de productos · 28-10-2026

node scripts/verificar-entradas.cjs monta EntradasProductos real con React/jsdom y API falsa sin red: dos productos/cantidades, revisión, fecha actual, doble clic, recuperación tras respuesta perdida/remontaje y permisos. Requiere npm ci --prefix frontend. [Contrato implementado](../docs/api/contrato-entradas-productos.md). Autor Codex para Axel; dominio Inventario de Vera y responsabilidades de los demás integrantes conservados. Evidencia en avances/cueva.md.

## Ampliación vigente · 28-10-2026 · Tienda por API

configurar-integracion-tienda.cjs se ejecuta con Node desde la raíz; respalda ambos .env en .tmp, conserva credenciales ajenas y reutiliza tokens válidos concordantes. Rechaza tokens débiles/divergentes en vez de sobrescribirlos. Habilita API comercial y TIENDA_MODO=api; requiere recrear API/comercio de FoodSave y API/conciliador de tienda. No hace migración, semillas, publicaciones de SKU ni pagos.

## Preparación de jornada · 28-10-2026

preparar-jornada-actual.cjs orquesta respaldo, preparación y ensayo sobre la aplicación actual. preparar-jornada.py agrega solo la jornada autorizada; verificar-jornada.py revierte pronóstico/plan/pedidos y guarda mensajes previstos. aprobar-promocion-jornada.py comprueba publicación administrativa sin pago ni Telegram. Guardas PREPARAR_JORNADA_AUTORIZADA=2026-10-28/base foodsave; no crea otro Compose, cuentas o .env. Historial/stock añadidos son sintéticos y trazables; ajustes de insumos expresamente autorizados. Reejecución conserva el marcador/avances. Guion y límites en ../docs/equipo/guion-prueba-2026-10-28.md.
