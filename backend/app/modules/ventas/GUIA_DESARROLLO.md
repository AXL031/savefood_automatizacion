# Guía de desarrollo — Ventas diarias e historial

**26-10-2026 · Precios estimados autorizados:** `scripts/cargar-precios-estimados.py` consume `guardar_precio` con administrador activo, validación completa y una transacción. [139 estimaciones PEN, fuentes y presentaciones](../../../../datos_carga/referencias/precios_estimados_ventas_pen.md). Conserva precios existentes y no modifica stock, catálogo, histórico o tickets. No constituye publicación a tienda ni amplía la API.

**Carpeta:** `backend/app/modules/ventas`.

**Responsable:** Edu Sanchez. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida. **Tareas:** E01, E02.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-importaciones.md](../../../../docs/api/contrato-importaciones.md).
- [foodsave-ml/CONTRATO_DATOS_COMERCIOS.md](../../../../foodsave-ml/CONTRATO_DATOS_COMERCIOS.md).

## Punto de partida

**30-09-2026 · Completar piloto:** `registrar_ventas_diarias(..., reutilizar_identicas=True)` es la opción explícita de E03 para conservar pares conocidos idénticos e insertar solo filas nuevas del archivo. Cambiar u omitir un par conocido en el periodo provoca HISTORIAL_DIFERENTE; se bloquean ventas consultadas y se conservan IDs/importaciones/revisiones anteriores. El modo habitual mantiene VENTA_DUPLICADA. Cada carga nueva conserva clave/huella propia y reporta filas creadas; no genera ceros por ausencia. Sin commit ni migración.

E01 parcial implementa tablas `importacion_venta`, `venta_diaria` y `revision_venta` en `0002_e01_ventas`. `importar_bakery` agrega tickets a día/SKU, exige catálogo previo, excluye y cuenta líneas negativas y conserva revisiones iniciales; `leer_historial` devuelve filas conocidas con revisión vigente para Kevin y usa fin exclusivo, por lo que la fecha objetivo no entra en sus características. `limites_historial` devuelve el rango observado. `corregir_venta` conserva revisiones anteriores. Todas las funciones reciben la sesión del consumidor y no hacen commit. El CLI `python -m app.modules.ventas.cargar_piloto` sigue disponible; la carga web piloto usa el mismo servicio. La subida y su repetición se probaron con el CSV real en PostgreSQL. La API general y pantalla de ventas, y el asistente completo, siguen pendientes. Consultar el resumen vigente de [Edu Sanchez](../../../../docs/equipo/avances/sanchez.md).

## Trabajo en esta carpeta

1. Adaptar bakery a agregado diario sin convertir ausencias en cero.
2. Persistir importación y revisión inicial; permitir corrección con motivo y revisión nueva.
3. Publicar consulta paginada y lectura temporal que Kevin consume.
4. Definir con Kevin cómo una corrección marca evaluaciones previas como históricas sin borrarlas.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `importacion_venta`, `venta_diaria`, `revision_venta`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Ventas normalizadas con SKU resuelto y correcciones administrativas.
- **Entrega:** Historial y revisiones por producto/fecha para ML y auditoría.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- No se aceptan dos sucursales ni filas diarias duplicadas.
- Corrección conserva revisión anterior y no descuenta inventario.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.


## Historial paginado E01/E04 · 30-09-2026

GET /ventas añade desplazamiento>=0 y metadatos.total filtrado, conservando datos y limite (1–500). Orden fecha descendente/producto/id; cuenta antes de recortar. No agrega fechas ausentes ni modifica revisiones/stock; sin migración. Ventas UI consume el sobre para recorrer todo el historial.

## Dashboard y Reportes de lectura · 01-10-2026

Ampliación expresa: Inicio con ventas diarias, ranking y pedidos; `/informes` con períodos inclusivos, versión del modelo, tablas paginadas, detalle en diálogo y CSV completo del período. [Contrato](../../../../docs/api/contrato-informes.md). Ventas publica `resumen_ventas`/`periodo_ventas`; Compras `resumen_pedidos`/`periodo_propuestas` cuenta pedidos sin multiplicar intentos; K03 admite filtros `desde`/`hasta` opcionales conservando la consulta anterior sin filtros. Informes coordina únicamente interfaces públicas. No migra, entrena, modifica stock ni envía mensajes. Fechas ausentes no se rellenan con cero. Registro/evidencia en Bohorquez y coordinación Cueva.


## Avance K03/K04 y E01/E02 · 20-10-2026

Codex a solicitud del usuario; se conserva la responsabilidad de los dominios. leer_revisiones publica versiones inmutables. PATCH coordina corregir_venta y solicitar_reevaluaciones_venta en la misma sesión antes del commit; añade reevaluaciones a la respuesta. La reserva fallida revierte la corrección; repetición conserva IDs. No recalcula planes/pedidos ni stock.

[Contrato y ejemplos vigentes](../../../../docs/api/contratos.md#k03k04-y-frontera-e01--20-10-2026). [Pruebas, consumidores y límites del corte](../../../../docs/equipo/avances/bohorquez.md). Sin migraciones nuevas; no se acredita PostgreSQL/Redis, CI remoto ni envío real por la QA visual.


## Caja presencial · 26-10-2026

`modelos_caja.py`, `esquemas_caja.py`, `caja.py` y `rutas_caja.py` implementan precios/cotizaciones/tickets presenciales; migración 0021. Sesión compartida, sin commits internos; stock por interfaz pública de Inventario. El histórico/revisiones se mantiene separado, sin agregación de tickets a ML. Tienda/cierre/promociones comerciales/simuladores pendientes. [Contrato implementado](../../../../docs/api/contrato-caja-presencial.md). Autor de este corte: Codex para Axel; se conservan las responsabilidades de cada dominio. Evidencia y límites en el registro de Cueva.

## Ampliación vigente · 28-10-2026 · Tienda por API

tienda.py amplía los tickets canónicos con canal TIENDA, identidad limitada de integración, pedido/evento/transacción únicos y segmentos por promoción/lote. No usa usuario ficticio ni inserta venta_diaria. Anulación presencial no reembolsa compras online y se bloquea para TIENDA. Coordinación Codex para Axel (A04), conservando dominios Rojas (Tienda), Sanchez (Ventas/UI) y Vera (Inventario/Promociones). La ampliación usa dos proyectos y bases independientes: solo API HTTP, sin importar modelos, montar carpetas ni consultar PostgreSQL desde tienda. Payme solo preproducción y comprador invitado; cuatro botones independientes. Ver docs/api/contrato-integracion-tienda.md desde la raíz y registro Cueva para evidencia y límites.
