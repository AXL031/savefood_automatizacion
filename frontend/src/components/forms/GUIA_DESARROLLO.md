# Guía de desarrollo — Controles de formularios

04-11-2026 · Cobertura nativa: `styles.css` incluye una base de baja especificidad con `:where` para labels/controles HTML dentro de formularios, aunque no usen Campo o una clase particular. Etiqueta arriba, ancho disponible, controles48px y textareas112px; estilos de componentes conservan prioridad. Excluir checkbox/radio/hidden/range/color/file/botones de reglas de texto y excluir descendientes de `.pagination` del tamaño de campo de formulario. Paginación conserva38px y anchos propios. No incluir textareas en reglas posteriores de min-height44px, porque anulaba su altura mínima. Preferir Campo para ayuda/error/asociación de etiqueta y usar la base como protección, no como sustituto de estructura semántica.

04-11-2026 · Alineación: `Campo` admite ayuda/error opcionales sin estirar el input vecino. Los estilos comunes en `app/styles.css` fijan inputs/selects a 48px y contenido de `.field` al inicio; ayuda/error no heredan el margen de párrafos. Textareas crecen por separado, checkboxes/radios no usan el ancho/padding de inputs de texto. Mantener min-width0 y la cuadrícula móvil; no añadir alturas/márgenes por formulario para compensar campos con distinta cantidad de descripciones. Verificación visual con los componentes reales y datos ficticios; registro transversal en Cueva.

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
