# Guía de desarrollo — Ventas diarias e historial

**Carpeta:** `frontend/src/app/ventas`.

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

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Edu Sanchez](../../../../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

1. Listar ventas por fecha/producto con paginación.
2. Construir corrección con motivo y revisión; mostrar ausencia distinta de cantidad cero.

## Organización de implementación

La ruta compone `page.tsx` y componentes del feature correspondiente. Usar layout protegido y cliente HTTP común. Resolver carga, vacío, error, permisos y sesión vencida. Tener una carpeta y una guía no hace que la página exista: conectarla solo cuando su contrato esté publicado.

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
