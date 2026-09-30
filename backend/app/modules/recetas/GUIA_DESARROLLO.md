# Guía de desarrollo — Recetas versionadas

**Carpeta:** `backend/app/modules/recetas`.

**Responsable:** Max Rojas. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Ingredientes, recetas y planificación. **Tareas:** M01.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-importaciones.md](../../../../docs/api/contrato-importaciones.md).
- [docs/base_de_datos/esquema-objetivo-mvp.md](../../../../docs/base_de_datos/esquema-objetivo-mvp.md).

## Punto de partida

**Integración 30-09-2026:** M01 disponible: ServicioRecetasM01 conecta la primera carga; cambios crean versión y conservan la anterior. Migración 0005. API y frontera de carga/versionado verificadas en SQLite.

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Max Rojas](../../../../docs/equipo/avances/rojas.md) para el último estado.

## Trabajo en esta carpeta

1. Relacionar producto de Edu e ingrediente propio con cantidad positiva por unidad.
2. Garantizar una sola versión activa por producto y preservar versiones usadas.
3. Exponer servicio de carga sin commit para Edu y lectura versionada para Planificación.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `receta`, `receta_ingrediente`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Líneas de receta en unidades base y catálogo existente.
- **Entrega:** Composición reproducible por producto para el cálculo de plan.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Referencia rota o pareja duplicada rechaza carga.
- Modificar receta usada crea nueva versión y no cambia planes previos.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/rojas.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
