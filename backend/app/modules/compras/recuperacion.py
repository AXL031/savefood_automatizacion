"""Conciliación y nuevo intento explícitos. No llama Telegram ni hace commit."""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.errores import ErrorAPI
from .modelos import EnvioPedido, RecuperacionEnvio
from .servicio import _bloquear_pedido, _preparar_envio


def recuperar_envio(sesion, pedido_id, *, accion, clave, envio_id, chat_id_revisado,
                    evidencia, usuario_id, nombre_usuario, message_id=None, fecha_telegram=None):
    clave, evidencia = clave.strip(), evidencia.strip()
    if not 1 <= len(clave) <= 80 or not 10 <= len(evidencia) <= 1500:
        raise ErrorAPI(422, "EVIDENCIA_INVALIDA", "Indica una clave y evidencia de 10 a 1500 caracteres.")
    if accion not in {"CONFIRMAR_ENVIO", "CONFIRMAR_NO_ENVIO", "REINTENTAR"}:
        raise ErrorAPI(422, "RECUPERACION_INVALIDA", "Acción de recuperación no admitida.")
    ahora = datetime.now(timezone.utc)
    if accion == "CONFIRMAR_ENVIO":
        if (type(message_id) is not int or not 0 < message_id <= 9223372036854775807 or
                fecha_telegram is None or fecha_telegram.utcoffset() is None):
            raise ErrorAPI(422, "EVIDENCIA_INVALIDA", "Indica identificador positivo y fecha de Telegram con zona horaria.")
        fecha_telegram = fecha_telegram.astimezone(timezone.utc)
        if fecha_telegram > ahora:
            raise ErrorAPI(422, "EVIDENCIA_INVALIDA", "La fecha del mensaje no puede estar en el futuro.")
    elif message_id is not None or fecha_telegram is not None:
        raise ErrorAPI(422, "EVIDENCIA_INVALIDA", "Esta acción no admite evidencia de un mensaje enviado.")

    # El mismo orden se usa en despacho y ambos lados de la llamada externa.
    pedido, propuesta = _bloquear_pedido(sesion, pedido_id)
    solicitud = {"pedido_id": pedido_id, "envio_id": envio_id, "accion": accion,
                 "chat_id_revisado": chat_id_revisado, "evidencia": evidencia,
                 "message_id": message_id,
                 "fecha_telegram": fecha_telegram.isoformat() if fecha_telegram else None}
    previa = sesion.scalar(select(RecuperacionEnvio).where(RecuperacionEnvio.clave_idempotencia == clave))
    if previa:
        if previa.usuario_id != usuario_id or previa.solicitud_json != solicitud:
            raise ErrorAPI(409, "CLAVE_RECUPERACION_REUTILIZADA", "Esta clave ya corresponde a otra acción, evidencia o responsable.")
        return previa
    envio = sesion.scalar(select(EnvioPedido).where(EnvioPedido.pedido_id == pedido_id)
                          .order_by(EnvioPedido.numero_intento.desc()).limit(1)
                          .with_for_update().execution_options(populate_existing=True))
    if envio is None or envio.id != envio_id:
        raise ErrorAPI(409, "INTENTO_CAMBIO", "Actualiza el pedido y revisa su último intento antes de actuar.")
    if pedido.estado != envio.estado or not propuesta.activa or propuesta.estado != "GENERADA":
        raise ErrorAPI(409, "RECUPERACION_NO_PERMITIDA", "El estado de la propuesta o del pedido no permite esta acción.")
    if accion == "REINTENTAR":
        if envio.estado != "FALLIDO":
            raise ErrorAPI(409, "RECUPERACION_NO_PERMITIDA", "Solo se puede reintentar un fallo definitivo o conciliado como no enviado.")
        manual = pedido.modo_envio == "REQUIERE_APROBACION" and pedido.decision_json and pedido.decision_json.get("accion") == "APROBAR"
        automatico = pedido.modo_envio == propuesta.modo_envio == "AUTOMATICO" and pedido.decision_json is None
        if not (manual or automatico) or pedido.bloqueos_json or propuesta.incidencias_json:
            raise ErrorAPI(409, "RECUPERACION_NO_PERMITIDA", "Falta la autorización original o hay bloqueos en el pedido.")
        nuevo = _preparar_envio(sesion, pedido, chat_id_revisado=chat_id_revisado)
        # Conservar el texto autorizado, aunque cambie el formateador en el futuro.
        nuevo.texto = envio.texto
        if len(nuevo.texto.encode("utf-16-le")) // 2 > 4096:
            raise ErrorAPI(422, "MENSAJE_FUERA_DE_RANGO", "El mensaje conservado supera el tamaño permitido.")
        nuevo.numero_intento = envio.numero_intento + 1
    else:
        nuevo = None
        if envio.estado != "PENDIENTE_VERIFICACION":
            raise ErrorAPI(409, "RECUPERACION_NO_PERMITIDA", "Solo se concilia un resultado incierto; espera a que finalice un envío en curso.")
        if chat_id_revisado != envio.chat_id:
            raise ErrorAPI(409, "DESTINO_CAMBIO", "Revisa el chat conservado del intento, aunque el proveedor tenga otro destino ahora.")
        creado = envio.creado_en.replace(tzinfo=timezone.utc) if envio.creado_en.tzinfo is None else envio.creado_en
        if fecha_telegram and fecha_telegram < creado - timedelta(minutes=1):
            raise ErrorAPI(422, "EVIDENCIA_INVALIDA", "La fecha del mensaje es anterior a este intento.")

    try:
        with sesion.begin_nested():
            registro = RecuperacionEnvio(envio_id=envio.id, clave_idempotencia=clave, accion=accion,
                usuario_id=usuario_id, nombre_usuario=nombre_usuario, evidencia=evidencia,
                solicitud_json=solicitud, creado_en=ahora,
                resultado_anterior_json={"estado": envio.estado, "codigo_error": envio.codigo_error,
                    "detalle_error": envio.detalle_error, "message_id": envio.message_id,
                    "fin_en": envio.fin_en.isoformat() if envio.fin_en else None})
            if nuevo:
                sesion.add(nuevo)
                sesion.flush()
                registro.nuevo_envio_id = nuevo.id
                pedido.estado = "PENDIENTE_ENVIO"
            else:
                envio.estado = pedido.estado = "ENVIADO" if accion == "CONFIRMAR_ENVIO" else "FALLIDO"
                envio.message_id, envio.fecha_telegram = message_id, fecha_telegram
                envio.fin_en, envio.lease_hasta, envio.token_despacho = ahora, None, None
                # El error original del intento sigue visible; el resultado humano
                # se distingue por la auditoría y nunca finge una respuesta del bot.
                if accion == "CONFIRMAR_NO_ENVIO":
                    envio.codigo_error = "CONCILIADO_NO_ENVIADO"
                    envio.detalle_error = "El administrador registró evidencia de no envío. No se reintenta automáticamente."
            sesion.add(registro)
            sesion.flush()
    except IntegrityError:
        raise ErrorAPI(409, "EVIDENCIA_O_CLAVE_REUTILIZADA", "La clave o la evidencia chat/mensaje ya fue registrada. Actualiza el pedido.") from None
    return registro
