# Guía de desarrollo — Tablas comunes

## Exploración de detalles · 04-11-2026

`ExploradorDetalle<T>` recibe filas, idFila, nombre, textoBusqueda, etiquetaBusqueda, columnas y filtros opcionales `{valor,etiqueta,acepta}`. Con `detalle(fila)` agrega una acción junto al nombre y un solo panel, con foco al abrir/cerrar. Sin detalle es una lista de solo lectura con búsqueda/paginación. Normaliza tildes, busca también por código cuando lo entrega el consumidor, cierra selección al filtrar y reinicia página. Usar key de la entidad padre al cambiar plan/ticket. No consulta API, modifica filas ni interpreta números del dominio.

Consumidores reales: productos/trazas de Planificación, líneas/movimientos de Ventas, productos seleccionados de Automatizaciones y exclusiones de aportes del plan. Las trazas largas se consultan desde la tabla, sin otro desplegable por registro. `TablaDatos compacta` omite paginación para hasta10 filas locales; con más filas o paginación remota se conserva el contrato previo. El valor predeterminado no cambia otros consumidores. `node scripts/verificar-trazas.cjs` comprueba139 productos y los paneles con snapshots ficticios.

**Carpeta:** `frontend/src/components/tables`.

**Responsable:** Edu Sanchez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Edu Sanchez](../../../../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

1. Definir tabla con encabezados, paginación, vacío y carga.
2. Mostrar IDs/enlaces, unidades y fechas según datos del dominio.
3. Evitar ordenar texto decimal como si fuera número y distinguir null de cero.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Tabla larga y vacía siguen siendo utilizables; acción por fila identifica la entidad correcta.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.


## Navegación, páginas y detalles · 30-09-2026

TablaPaginada recibe thead/tbody y pagina filas por clave; tamaños 10/25/50/100, extremos, anterior/siguiente y salto accesible. Cambio de lista/filtro reinicia página; sondeo con mismos IDs la conserva. TablaDatos comparte el paginador. Props remota/paginacion reciben pagina, tamano, total, cargando y onCambio para listas servidas por API; Ventas usa ese contrato. No presentar el tamaño de una lista reciente limitada como total histórico.
