# Guía de desarrollo — Programaciones, ejecuciones e intentos

**Carpeta:** `backend/app/modules/automatizaciones`.

**Responsable:** Axel Cueva. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Acceso, configuración y motor de automatizaciones. **Tareas:** A02, A03.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/automatizacion/programacion.md](../../../../docs/automatizacion/programacion.md).
- [docs/automatizacion/politica-de-reintentos.md](../../../../docs/automatizacion/politica-de-reintentos.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](../../../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Crear consultas/acciones de programación y detalle con clave y huella de entrada.
2. Reclamar trabajos mediante transición atómica y lease recuperable.
3. Persistir intentos, tiempos, salidas y errores; encargar cálculo a cada módulo público.
4. Separar reintentos internos de la política especial de envíos de Aguirre.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `programacion_demo`, `ejecucion_automatizacion`, `intento_automatizacion`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Eventos de carga, planes, ajustes y horarios reales con escenario histórico.
- **Entrega:** Ejecuciones trazables y despacho recuperable para los servicios de dominio.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Reentrega no duplica efectos locales.
- Caída tras commit y antes de publicar no pierde la acción.
- UI muestra intentos y ambas referencias temporales.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
