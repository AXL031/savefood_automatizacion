# Guía de desarrollo — Controles de formularios

**Carpeta:** `frontend/src/components/forms`.

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

1. Crear campos y mensajes reutilizables con label y errores por campo.
2. Soportar decimales/unidades sin convertir cantidades con pérdida de precisión.
3. Las validaciones de negocio definitivas siguen en backend del dueño; prevenir doble submit en UI.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Se puede corregir un dato inválido y volver a enviar sin perder el contexto.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.


## Filtros de fecha · 30-09-2026

CampoFecha atiende input y change para que seleccionar/escribir una fecha nativa actualice el estado del consumidor. Ventas vuelve a página 1 al cambiar fecha/producto. En QA, fecha 2022-08-21 devuelve tres ventas y conserva un cero explícito.
