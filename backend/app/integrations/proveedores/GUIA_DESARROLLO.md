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

**30-09-2026 · Paso 5: telegram.py implementa Fernet sobre bot.enc en TELEGRAM_CONFIG_DIR, clave derivada de JWT_SECRET con dominio propio. Token ingresado desde UI por petición administrativa; nunca se devuelve ni registra. urllib HTTPS fijo, timeout 8s, sin redirects ni retry. getMe/getChat/getChatMember; búsqueda de /start con getWebhookInfo/getUpdates sin offset ni cambios de webhook. No implementa sendMessage. Volumen cifrado persistente API rw/worker ro. Guardar de nuevo si cambia JWT_SECRET. Pruebas con transporte falso; sin bot propio para prueba real.**

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

## Paso 6 local · L03 · 30-09-2026

Aprobación/rechazo administrativos con clave idempotente, responsable, nombre y fecha; rechazo motivado de pendiente/bloqueado sin exigir canal. Aprobar exige modo manual, propuesta válida y chat revisado/verificado con credencial vigente. Congela texto/chat/huella y reserva envio_pedido en la misma transacción. Consultas/UI incluyen decisión, destino actual separado de snapshots, mensaje DEMOSTRACIÓN — NO SURTIR e intento/evidencia de Telegram. Aprobar no confirma envío; Beat/worker lo ejecutan y guardan message_id/fecha solo con respuesta válida.

Outbox con lease y token de despacho: revalida antes de transmitir y confirma ENVIANDO antes del efecto externo. Reentrega no vuelve a enviar; timeout, respuesta inválida o worker interrumpido quedan PENDIENTE_VERIFICACION sin retry. Cambiar destino/credencial bloquea antes de red. Ninguna acción mueve stock ni libera por sí sola la reserva de fecha. AUTOMATICO, conciliación y nuevos intentos humanos siguen en paso 7. Migración aditiva 0013; downgrade bloqueado si existen decisiones para no borrar evidencia. Contrato vigente: docs/api/contrato-pedidos.md; prueba test_aprobacion_envio_l03.py. Implementación local por Codex para Axel, responsabilidad de Aguirre, sin commit ni remoto; bot real pendiente del usuario.
