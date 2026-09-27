# Guía de desarrollo — Pronósticos y evaluación histórica

**Carpeta:** `frontend/src/app/pronosticos`.

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

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Kevin Bohorquez](../../../../docs/equipo/avances/bohorquez.md) para el último estado.

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
