# Guía de desarrollo — Asistente y primera carga

**Carpeta:** `frontend/src/app/inicializacion`.

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

`page.tsx` implementa el asistente de primera carga de Sánchez: dos XLSX o cinco CSV, vista previa y confirmación. `piloto/page.tsx` conserva la carga rápida del CSV bakery para la base local existente y reserva la preparación del modelo. Son flujos distintos. La carga completa sigue parcialmente pendiente de los servicios de Max y Vera. Consultar el resumen vigente de [Edu Sanchez](../../../../docs/equipo/avances/sanchez.md).

## Integración E03/K01

El asistente completo reserva preparación al confirmar y consulta progreso cada tres segundos mientras la ejecución está activa. Muestra enlace a intentos y panel; permite reintentar fallo sin adjuntar archivos. Una carga aceptada deja de mostrar el formulario de importación.

## Trabajo en esta carpeta

1. Construir pasos de archivos, fechas, vista previa, errores y confirmación.
2. Subir multipart mediante servicio común y mostrar conteos/huellas.
3. Consultar estado de preparación y ofrecer reintento ML sin recargar ventas ni lotes.

## Organización de implementación

La ruta compone `page.tsx` y componentes del feature correspondiente. Usar layout protegido y cliente HTTP común. Resolver carga, vacío, error, permisos y sesión vencida. Tener una carpeta y una guía no hace que la página exista: conectarla solo cuando su contrato esté publicado.

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
