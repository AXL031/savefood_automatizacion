# Guía de desarrollo — Ventas diarias e historial

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
