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

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Edu Sanchez](../../../../docs/equipo/avances/sanchez.md) para el último estado.

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
