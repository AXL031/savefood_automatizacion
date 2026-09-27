# Guía de desarrollo — Programaciones, ejecuciones e intentos

**Carpeta:** `frontend/src/app/automatizaciones/ejecuciones/[id]`.

**Responsable:** Axel Cueva. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Acceso, configuración y motor de automatizaciones. **Tareas:** A02, A03.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../../../docs/guia-inicio-desarrollo.md).
- [docs/automatizacion/programacion.md](../../../../../../docs/automatizacion/programacion.md).
- [docs/automatizacion/politica-de-reintentos.md](../../../../../../docs/automatizacion/politica-de-reintentos.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `page.tsx`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../../../../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

**A02 disponible:** `page.tsx` consulta el ID real, muestra estado, horas e intentos registrados y explica la espera de A03 cuando está pendiente. No ofrece reintento manual ni afirma efectos externos.

1. Obtener ejecución por ID de la URL y distinguir ID inválido, no encontrado y falta de permisos.
2. Mostrar tipo, estado, horas reales, escenario histórico, intentos y efectos relacionados.
3. Enlazar corrida, plan, pedido o evaluación sin inventar resultados; acciones de recuperación siguen contrato de Axel/Aguirre.

## Organización de implementación

La ruta compone `page.tsx` y componentes del feature correspondiente. Usar layout protegido y cliente HTTP común. Resolver carga, vacío, error, permisos y sesión vencida. Tener una carpeta y una guía no hace que la página exista: conectarla solo cuando su contrato esté publicado.

## Dependencias y contrato de entrega

- **Recibe:** Eventos de carga, planes, ajustes y horarios reales con escenario histórico.
- **Entrega:** Ejecuciones trazables y despacho recuperable para los servicios de dominio.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Reentrega no duplica efectos locales.
- Caída tras commit y antes de publicar no pierde la acción.
- UI muestra intentos y ambas referencias temporales.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
