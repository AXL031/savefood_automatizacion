# Guía de desarrollo — Ingredientes y unidades

**Carpeta:** `frontend/src/app/ingredientes`.

**Responsable:** Max Rojas. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Ingredientes, recetas y planificación. **Tareas:** M01.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-importaciones.md](../../../../docs/api/contrato-importaciones.md).

## Punto de partida

**Integración 30-09-2026:** Pantalla /ingredientes disponible desde rojas; consulta y edición administrativas sobre API real, con unidad bloqueada cuando está en uso. Typecheck y build verificados en integración.

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Max Rojas](../../../../docs/equipo/avances/rojas.md) para el último estado.

## Trabajo en esta carpeta

1. Mostrar catálogo y unidad base; presentar validación de códigos y estado activo.
2. Restringir edición de unidad cuando el servidor indique referencias en uso.

## Organización de implementación

La ruta compone `page.tsx` y componentes del feature correspondiente. Usar layout protegido y cliente HTTP común. Resolver carga, vacío, error, permisos y sesión vencida. Tener una carpeta y una guía no hace que la página exista: conectarla solo cuando su contrato esté publicado.

## Dependencias y contrato de entrega

- **Recibe:** Catálogo inicial y consultas del administrador.
- **Entrega:** Ingredientes con unidad inequívoca para receta, lote y compra.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Unidad no permitida se rechaza.
- Referencia utilizada no se elimina en cascada ni cambia de unidad silenciosamente.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/rojas.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
