# Guía de desarrollo — Planificación y necesidades de ingredientes

**Carpeta:** `backend/app/modules/planificacion`.

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

1. Consumir pronóstico de Kevin y stock por fecha de Vera mediante interfaces públicas.
2. Calcular producción con margen cero y guardar receta/stock/pronóstico de referencia.
3. Sumar necesidades por ingrediente antes del redondeo final y calcular faltantes.
4. Entregar plan y necesidades a Compras; mantener los planes anteriores cuando cambien entradas.
5. Construir detalle de cantidades, avisos y enlaces a corrida/pedidos.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `plan_produccion`, `elemento_plan`, `necesidad_ingrediente`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

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

## Corte M02–M04 · 06-10-2026

M02–M04 implementados: `generar_plan`, `obtener_plan`, `obtener_necesidades`, rutas `/planes` y handler `GENERAR_PROPUESTA`. Snapshots de recetas, pronósticos y lotes; omisiones explícitas y necesidades con null si falta stock. Una clave recupera el mismo resultado; otra conserva un recálculo. No hace commit ni modifica inventario. Migración `0009_m02_planes`. Compras siguen pendientes.
