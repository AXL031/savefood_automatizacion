# Guía de desarrollo — Adaptador Telegram de proveedores

**Carpeta:** `backend/app/integrations/proveedores`.

**Responsable:** Leonardo Aguirre. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Proveedores, pedidos y Telegram.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-pedidos.md](../../../../docs/api/contrato-pedidos.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Leonardo Aguirre](../../../../docs/equipo/avances/aguirre.md) para el último estado.

## Trabajo en esta carpeta

1. Implementar cliente con token de entorno, timeout y destino chat_id verificado.
2. Construir mensaje de pedido con código, líneas, fecha histórica y aviso de demostración.
3. Devolver message_id en éxito y distinguir rechazo inequívoco de timeout incierto.
4. No hacer commits ni cambiar estados de Compras dentro del cliente; devolver un resultado tipado.
5. Usar cliente falso para CI y prueba real solo en el chat autorizado.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

Una respuesta perdida se reporta incierta; no contiene reintento oculto que duplique mensaje.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/aguirre.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
