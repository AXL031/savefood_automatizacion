"""Outbox del dominio de compras. Ningún retry interno repite sendMessage."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from app.core.base_datos import SessionLocal
from app.modules.autenticacion.modelos import Usuario  # noqa: F401; FK en proceso worker sin FastAPI
from app.integrations.proveedores.telegram import ClienteTelegram, ErrorTelegram, ResultadoEnvio
from app.modules.proveedores.servicio import ServicioProveedores
from .modelos import EnvioPedido, PedidoCompra
from .servicio import _bloquear_pedido

LEASE_SEGUNDOS = 120


def _fallar(envio, pedido, estado, codigo, detalle, ahora):
    envio.estado = pedido.estado = estado
    envio.codigo_error, envio.detalle_error = codigo, detalle
    envio.fin_en = ahora
    envio.lease_hasta = None


def despachar_envios(publicar, *, sesiones=SessionLocal, ahora=None) -> dict:
    ahora = ahora or datetime.now(timezone.utc)
    mensajes, inciertos = [], 0
    with sesiones.begin() as sesion:
        candidatos = sesion.execute(select(EnvioPedido.id, EnvioPedido.pedido_id).where(
            EnvioPedido.estado.in_(["PENDIENTE_ENVIO", "ENVIANDO"]),
            or_(EnvioPedido.lease_hasta.is_(None), EnvioPedido.lease_hasta <= ahora)
        ).order_by(EnvioPedido.id).limit(50)).all()
        for envio_id, pedido_id in candidatos:
            pedido, _ = _bloquear_pedido(sesion, pedido_id)
            envio = sesion.scalar(select(EnvioPedido).where(EnvioPedido.id == envio_id)
                .with_for_update().execution_options(populate_existing=True))
            lease = envio.lease_hasta
            if lease and lease.tzinfo is None:
                lease = lease.replace(tzinfo=timezone.utc)
            if envio.estado not in {"PENDIENTE_ENVIO", "ENVIANDO"} or (lease and lease > ahora):
                continue
            if envio.estado == "ENVIANDO":
                _fallar(envio, pedido, "PENDIENTE_VERIFICACION", "WORKER_INTERRUMPIDO",
                        "El worker no confirmó el resultado. Revisa el chat; no se reenviará automáticamente.", ahora)
                inciertos += 1
                continue
            token = str(uuid4())
            envio.token_despacho = token
            envio.despachado_en = envio.despachado_en or ahora
            envio.lease_hasta = ahora + timedelta(seconds=LEASE_SEGUNDOS)
            mensajes.append((envio.id, token))
    publicados, fallos = 0, 0
    for id_, token in mensajes:
        try:
            publicar(id_, token)
            publicados += 1
        except Exception:
            # El lease permite republicar SOLO un envío aún no iniciado.
            fallos += 1
    return {"publicados": publicados, "publicaciones_fallidas": fallos, "inciertos": inciertos}


def ejecutar_envio(envio_id: int, token: str, *, sesiones=SessionLocal, cliente=None) -> dict:
    error_configuracion = None
    if cliente is None:
        try:
            cliente = ClienteTelegram.desde_configuracion()
        except ErrorTelegram as error:
            error_configuracion = error
    # Reclamar y confirmar antes del primer efecto externo. Una segunda entrega
    # nunca vuelve a llamar a Telegram, incluso después de perder el resultado.
    with sesiones.begin() as sesion:
        pedido_id = sesion.scalar(select(EnvioPedido.pedido_id).where(EnvioPedido.id == envio_id))
        if pedido_id is None:
            return {"estado": "OMITIDO"}
        pedido, propuesta = _bloquear_pedido(sesion, pedido_id)
        envio = sesion.scalar(select(EnvioPedido).where(EnvioPedido.id == envio_id).with_for_update())
        if envio is None or envio.token_despacho != token or envio.estado != "PENDIENTE_ENVIO":
            return {"estado": "OMITIDO"}
        ahora = datetime.now(timezone.utc)
        if error_configuracion:
            _fallar(envio, pedido, "FALLIDO", error_configuracion.codigo, str(error_configuracion), ahora)
            return {"estado": "FALLIDO"}
        destino = ServicioProveedores(sesion, cliente).consultar_destino(pedido.proveedor_id, bloquear=True)
        autorizacion_manual = (pedido.modo_envio == "REQUIERE_APROBACION" and
                               pedido.decision_json and pedido.decision_json.get("accion") == "APROBAR")
        autorizacion_automatica = (pedido.modo_envio == propuesta.modo_envio == "AUTOMATICO" and
                                   pedido.decision_json is None)
        autorizado = (propuesta.activa and propuesta.estado == "GENERADA" and not propuesta.incidencias_json and
                      not pedido.bloqueos_json and pedido.estado == "PENDIENTE_ENVIO" and
                      (autorizacion_manual or autorizacion_automatica) and destino.activo and
                      destino.destino_verificado and destino.chat_id_pruebas == envio.chat_id and
                      cliente.huella == envio.credencial_huella)
        if not autorizado:
            _fallar(envio, pedido, "FALLIDO", "DESTINO_O_CREDENCIAL_CAMBIO",
                    "El proveedor, chat o credencial cambió después de autorizar el envío. El mensaje no se transmitió.", ahora)
            return {"estado": "FALLIDO"}
        envio.estado = pedido.estado = "ENVIANDO"
        envio.inicio_en = ahora
        envio.lease_hasta = ahora + timedelta(seconds=LEASE_SEGUNDOS)
        chat_id, texto = envio.chat_id, envio.texto
    try:
        resultado = cliente.enviar_mensaje(chat_id, texto)
        if not isinstance(resultado, ResultadoEnvio) or resultado.estado not in {"ENVIADO", "FALLIDO", "PENDIENTE_VERIFICACION"}:
            raise ValueError
        if resultado.estado == "ENVIADO" and (type(resultado.message_id) is not int or resultado.message_id <= 0):
            raise ValueError
    except Exception:
        resultado = ResultadoEnvio("PENDIENTE_VERIFICACION", "RESULTADO_NO_CONFIRMADO",
                                   "No se pudo confirmar el resultado. Revisa el chat antes de cualquier nuevo envío.")
    with sesiones.begin() as sesion:
        pedido, _ = _bloquear_pedido(sesion, pedido_id)
        envio = sesion.scalar(select(EnvioPedido).where(EnvioPedido.id == envio_id).with_for_update())
        if envio.token_despacho != token or envio.estado not in {"ENVIANDO", "PENDIENTE_VERIFICACION"}:
            return {"estado": "OMITIDO"}
        try:
            with sesion.begin_nested():
                envio.estado = pedido.estado = resultado.estado
                envio.fin_en = datetime.now(timezone.utc)
                envio.message_id = resultado.message_id if resultado.estado == "ENVIADO" else None
                envio.fecha_telegram = resultado.fecha_telegram
                envio.codigo_error, envio.detalle_error = resultado.codigo, resultado.detalle
                envio.lease_hasta = None
                sesion.flush()
        except IntegrityError:
            _fallar(envio, pedido, "PENDIENTE_VERIFICACION", "EVIDENCIA_TELEGRAM_REUTILIZADA",
                    "La respuesta identifica un mensaje ya registrado en otro intento. Revisa la evidencia del chat.", datetime.now(timezone.utc))
            return {"estado": "PENDIENTE_VERIFICACION"}
    return {"estado": resultado.estado}
