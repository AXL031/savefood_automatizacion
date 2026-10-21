# Guía de desarrollo — Pronósticos y evaluación histórica

**Carpeta:** `frontend/src/app/panel`.

**Responsable:** Kevin Bohorquez. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Modelo predictivo, evaluación histórica y dashboard. **Tareas:** K01, K02, K03, K04.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md](../../../../foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md).
- [foodsave-ml/POLITICA_EVALUACION.md](../../../../foodsave-ml/POLITICA_EVALUACION.md).
- [docs/api/contratos.md](../../../../docs/api/contratos.md).

## Punto de partida

`page.tsx` consulta el backtest persistido por versión, compone serie, métricas y desglose por fecha, y conserva los valores indefinidos como tales. `SerieHistorica` se encuentra en `components/charts`. Consultar el resumen vigente de [Kevin Bohorquez](../../../../docs/equipo/avances/bohorquez.md).

## Trabajo en esta carpeta

1. Mostrar estado del modelo, versión, partición y pronósticos por fecha/producto.
2. Construir dashboard de evaluación histórica, cobertura, MAE/WAPE y serie temporal.
3. Mostrar null y métricas indefinidas como desconocidas, con enlace a la corrida.

## Organización de implementación

La ruta compone `page.tsx` y componentes del feature correspondiente. Usar layout protegido y cliente HTTP común. Resolver carga, vacío, error, permisos y sesión vencida. Tener una carpeta y una guía no hace que la página exista: conectarla solo cuando su contrato esté publicado.

## Dependencias y contrato de entrega

- **Recibe:** Historial de Edu, modelo/partición y fecha histórica de la programación.
- **Entrega:** Pronósticos para Max y evaluaciones para el panel de Kevin.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Cambiar venta objetivo no cambia características de ese objetivo.
- Predicción desconocida queda null; real ausente no equivale a cero.
- Métricas agregadas se calculan con los mismos pares evaluables.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/bohorquez.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.


## Ajustes de interfaz · 30-09-2026

Tablas con paginador común y tamaños 10/25/50/100. Sesión/marco persistentes en AppShell; no usar recarga del documento para navegar.


## Avance K03/K04 y E01/E02 · 20-10-2026

Codex a solicitud del usuario; se conserva la responsabilidad de los dominios. Evaluación rediseñada con navegación analítica, filtros de modelo/fechas, MAE/WAPE/±20/cobertura, pares pendientes y gráfico accesible con selector diario. Desglose con búsqueda y filtro de errores; partición temporal visible. Carga/error/ausencia sin cifras inventadas; diseño móvil verificado en QA.

[Contrato y ejemplos vigentes](../../../../docs/api/contratos.md#k03k04-y-frontera-e01--20-10-2026). [Pruebas, consumidores y límites del corte](../../../../docs/equipo/avances/bohorquez.md). Sin migraciones nuevas; no se acredita PostgreSQL/Redis, CI remoto ni envío real por la QA visual.
