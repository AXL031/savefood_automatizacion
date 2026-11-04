# Guía de desarrollo — Planificación y necesidades de ingredientes

## Explorador de ingredientes del plan · 04-11-2026

`DetalleIngredientes.tsx` sustituye la lista repetida de desplegables por una tabla única con búsqueda por nombre/código (sin distinguir tildes), filtros Todos/Con faltantes/Stock sin confirmar y un solo panel seleccionado. Ver detalle está junto al nombre del ingrediente para que pueda abrirse en móvil sin desplazar horizontalmente la tabla. El panel alterna Aportes por producto y Lotes consultados; usa nombres de productos conservados en `elementos`, receta/versiones e importes/unidades del snapshot. No suma ni recalcula cantidades ni consulta inventario actual. Stock/faltante null siguen como No disponible, distintos de cero.

Listas mayores de diez filas usan `TablaPaginada`; listas cortas no muestran paginadores vacíos. Cambiar búsqueda/filtro cierra el detalle, selección nueva vuelve a Aportes y foco pasa al panel; cerrar retorna a la fila o buscador si la fila ya no está montada. La página usa key del plan para limpiar selección al cambiarlo. Mantener lotes incluidos y excluidos/motivo visibles: el detalle muestra la lectura conservada y no la disponibilidad comercial actual. Prueba aislada: `node scripts/verificar-ingredientes-plan.cjs`, complementada con QA interactiva de55 ingredientes y móvil.

**Carpeta:** `frontend/src/features/planificacion`.

**Responsable:** Max Rojas. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Ingredientes, recetas y planificación. **Tareas:** M02, M03, M04.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contratos.md](../../../../docs/api/contratos.md).
- [docs/api/contrato-pedidos.md](../../../../docs/api/contrato-pedidos.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Max Rojas](../../../../docs/equipo/avances/rojas.md) para el último estado.

## Trabajo en esta carpeta

1. Mostrar producción sugerida por producto con pronóstico, stock y receta de origen.
2. Mostrar necesidades agregadas con disponible/faltante/unidad y advertencias.
3. Enlazar corrida y pedidos; nunca cambiar stock desde una acción de consultar/generar plan.

## Organización de implementación

Agrupar aquí formularios, hooks y vistas específicos del dominio. Consumir `src/services` y `src/types`; reutilizar layout y componentes de Edu. Las fórmulas y decisiones definitivas viven en el backend, no se duplican en el navegador.

## Dependencias y contrato de entrega

- **Recibe:** Corrida, recetas versionadas, disponibilidad por fecha y clave de operación.
- **Entrega:** Plan reproducible y necesidades para Aguirre.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- No modifica inventario y no inventa ceros para predicción no disponible.
- Ingrediente compartido por varios productos se suma una vez correctamente.
- Repetir entrada recupera el plan; recálculo conserva el anterior.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/rojas.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
