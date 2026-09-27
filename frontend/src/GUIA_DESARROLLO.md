# Guía de desarrollo — Código TypeScript de interfaz

**Carpeta:** `frontend/src`.

**Responsable:** Edu Sanchez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida.

## Leer antes de trabajar

- [Instrucciones para IA](../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../docs/guia-inicio-desarrollo.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Edu Sanchez](../../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

1. Separar rutas app, funciones de dominio features, servicios HTTP y componentes comunes.
2. Mantener aliases/imports coherentes con tsconfig.
3. Respetar propietarios locales; evitar lógica de stock o compras en layout global.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Cada cambio de dominio se ubica en su carpeta y consume un contrato API.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
