# Guía de desarrollo — Experimento y contrato de ML

**Carpeta:** `foodsave-ml`.

**Responsable:** Kevin Bohorquez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Modelo predictivo, evaluación histórica y dashboard.

## Leer antes de trabajar

- [Instrucciones para IA](../AGENTS.md).
- [Reparto vigente y criterios de entrega](../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../docs/equipo/dependencias.md).
- [Alcance de la demo](../docs/guia-inicio-desarrollo.md).
- [foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md](CONTRATO_ARTEFACTO_INFERENCIA.md).
- [foodsave-ml/POLITICA_EVALUACION.md](POLITICA_EVALUACION.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `.gitignore`, `bakery_sales_limpio.csv`, `normalizar_ventas.py`, `requirements.txt`, `verificar_notebook.py`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Kevin Bohorquez](../docs/equipo/avances/bohorquez.md) para el último estado.

Kevin coordina la carpeta; normalizar_ventas.py corresponde a Edu por su frontera de importación.

## Trabajo en esta carpeta

1. Extraer funciones de entrenamiento/inferencia y conservar notebook como experimento reproducible.
2. Aplicar política temporal vigente, no copiar automáticamente los cortes experimentales antiguos.
3. Versionar artefacto y validar features/huella/cobertura antes de integrarlo con backend.
4. Edu mantiene adaptador de archivos normalizar_ventas.py y sus pruebas coordinando salida con Kevin.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

El backend puede usar el contrato ML sin ejecutar Colab; ventas reales objetivo no alimentan características.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../docs/equipo/avances/bohorquez.md) siguiendo [la plantilla](../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
