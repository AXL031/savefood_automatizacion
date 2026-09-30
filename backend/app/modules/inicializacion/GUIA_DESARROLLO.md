# Guía de desarrollo — Asistente y primera carga

**Carpeta:** `backend/app/modules/inicializacion`.

**Responsable:** Edu Sanchez. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida. **Tareas:** E02, E03.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-importaciones.md](../../../../docs/api/contrato-importaciones.md).
- [foodsave-ml/CONTRATO_DATOS_COMERCIOS.md](../../../../foodsave-ml/CONTRATO_DATOS_COMERCIOS.md).

## Punto de partida

**Paso 1 · 30-09-2026:** E03→ML disponible en este corte: confirmación reserva preparación automática, estado enlaza ejecución/modelo/evaluación y POST reintentar-preparacion reutiliza una reserva activa o crea otra tras fallo sin importar. ENTRENANDO se confirma al iniciar el intento; ver contrato E03 en docs/api/contrato-importaciones.md. PostgreSQL/Redis/CatBoost y Beat real verificados.

**Integración 30-09-2026:** La ruta completa ya pasa ServicioRecetasM01 y ServicioInventarioV01 en una sola sesión: DATOS_CARGADOS sin pendientes de esos puertos. Rollback de stock verificado. El piloto se conserva separado. Entrenamiento automático integrado en el paso 1.

**E02 y E03 implementados (29-09-2026), verificados en SQLite; `0004` aplicado en PostgreSQL local.** La confirmación completa y su preparación ML pasaron PostgreSQL/Redis en el paso 1 de cueva. Consultar el resumen vigente de [Edu Sanchez](../../../../docs/equipo/avances/sanchez.md) para el último estado.

| Archivo | Responsabilidad |
|---|---|
| `lectores.py` | Lee los dos XLSX o los cinco CSV con encabezados exactos y calcula las huellas. No interpreta tipos. |
| `adaptador_bakery.py` | Convierte el CSV de tickets del piloto a la forma diaria del contrato, validando contra la lista curada. |
| `validacion.py` | Reúne todos los errores por archivo y fila. Un error rechaza el lote completo. |
| `modelos.py` | Fila única `configuracion_inicial` con sus cinco estados. |
| `puertos.py` | `ServicioRecetas` (Max) y `ServicioInventario` (Vera), invocados con la misma sesión. |
| `servicio.py` | Vista previa sin escritura, carga atómica y transiciones de estado. |
| `rutas.py` | `GET /inicializacion/estado`, `POST /inicializacion/vista-previa` y `POST /inicializacion/confirmar`. |
| `piloto.py` | Carga rápida del CSV bakery en `POST /inicializacion/piloto-bakery` y reserva `PREPARAR_MODELO`; flujo separado del asistente completo. |

Migración `0004_e03_inicializacion`, sucesora de `0003_pronosticos`. La ruta completa consume los puertos reales de Max/Vera; compatibilidad sin puertos queda solo para pruebas parciales y nunca agenda ML. El CSV piloto usa su propio contrato y no altera esta fila. La lista curada se localiza desde el repositorio o `/code` en Docker.

## Trabajo en esta carpeta

1. Validar dos XLSX o cinco CSV con errores por archivo/hoja/fila y vista previa.
2. Calcular huellas y aplicar idempotencia antes de confirmar la carga.
3. Orquestar productos/ventas propios y servicios públicos de recetas de Max y apertura de Vera en una transacción.
4. Persistir estado y solicitar preparación ML al motor de Axel; exponer transición que Kevin usa al terminar.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `configuracion_inicial`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Archivos, claves de carga y fechas del escenario del Administrador.
- **Entrega:** Datos consistentes, conteos, errores, estado de inicialización y solicitud de entrenamiento.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Un fallo en la última hoja no deja productos, ventas ni stock parciales.
- Carga idéntica devuelve el resultado; clave reutilizada con otro archivo produce conflicto.
- Fallo ML permite reintento sin nueva importación.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
