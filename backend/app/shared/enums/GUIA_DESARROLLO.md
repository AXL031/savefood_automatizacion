# Guía de desarrollo — Estados compartidos

**Carpeta:** `backend/app/shared/enums`.

**Responsable:** Axel Cueva. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Acceso, configuración y motor de automatizaciones.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/base_de_datos/esquema-objetivo-mvp.md](../../../../docs/base_de_datos/esquema-objetivo-mvp.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Axel Cueva](../../../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Definir estados canónicos de ejecución y programación con Axel.
2. Publicar estados de compras propuestos por Aguirre y de modelo por Kevin solo si hay consumidores compartidos.
3. Actualizar tipos TypeScript y documentación cuando cambie un valor.
4. Evitar confundir COMPLETADA de ejecución con ENVIADO de pedido.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Servidor, cliente y contrato usan exactamente los mismos valores.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
