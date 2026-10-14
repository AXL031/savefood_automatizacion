# Guía de desarrollo — Datos de primera carga

**Responsable:** Axel Cueva, coordinación de la entrega solicitada. Los contratos de importación pertenecen a Sanchez; ML a Bohorquez; stock a Vera; ingredientes/recetas/planificación a Rojas.

Leer la [guía raíz](../GUIA_DESARROLLO.md), [responsabilidades](../docs/equipo/responsabilidades.md), [dependencias](../docs/equipo/dependencias.md), [contrato de importaciones](../docs/api/contrato-importaciones.md) y [política ML](../foodsave-ml/POLITICA_EVALUACION.md).

Esta carpeta contiene datos de prueba preparados desde archivos suministrados por Axel, no fixtures de pruebas unitarias ni una carga ya aceptada. [README](README.md) fija los cinco nombres, las fechas que deben introducirse y los ajustes de stock. No cambiar encabezados técnicos, identidades, ceros explícitos ni cantidades de receta para eliminar una etiqueta de interfaz.

Actualización 14-10-2026: productos.csv marca los 139 productos como si a solicitud de Axel; el sistema admite todo el catálogo en carga y programación. La instalación habitual ya aceptó los archivos anteriores y tiene modelo listo; no reimportar para ampliar la selección, usar Automatización. La validación inicial para cinco productos se conserva como historial en Cueva; una segunda verificación cubre los 139 y los 55 ingredientes.

Mantener archivos UTF-8, delimitados por coma y fechas ISO. Los campos de stock vacíos siguen siendo desconocidos. Las ventas ausentes no se convierten en cero. Para cambiar las fechas del escenario, verificar conjuntamente referencia anterior al objetivo, ventana reservada del modelo y límite de vida de todos los lotes de producto, incluidos los no seleccionados.

Validar vista previa y confirmación con el importador público en una base aislada. Cargar la instalación habitual solamente a solicitud del usuario. Registrar resultados reales en [Cueva](../docs/equipo/avances/cueva.md); no atribuir cambios de dominio a sus responsables sin su intervención. No requiere migración ni modifica API.
