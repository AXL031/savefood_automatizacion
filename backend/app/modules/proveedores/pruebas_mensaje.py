"""Prueba explícita del canal, sin pedidos ni reintentos de efectos inciertos."""
from sqlalchemy import select

from app.modules.negocios.servicio import nombre_negocio
from .esquemas import MensajePruebaCrear
from .modelos import PruebaMensajeProveedor
from .servicio import ServicioProveedores, Conflicto


def listar_pruebas(servicio: ServicioProveedores, proveedor_id: int):
    servicio.consultar_destino(proveedor_id)
    return list(servicio.db.scalars(select(PruebaMensajeProveedor).where(
        PruebaMensajeProveedor.proveedor_id == proveedor_id).order_by(PruebaMensajeProveedor.id.desc()).limit(10)))


def reservar_prueba(servicio: ServicioProveedores, proveedor_id: int, usuario_id: int, datos: MensajePruebaCrear):
    # Serializa también dos claves diferentes del mismo proveedor.
    destino = servicio.consultar_destino(proveedor_id, bloquear=True)
    anterior = servicio.db.scalar(select(PruebaMensajeProveedor).where(
        PruebaMensajeProveedor.clave_idempotencia == datos.clave_idempotencia))
    if anterior:
        if (anterior.proveedor_id, anterior.usuario_id, anterior.chat_id, anterior.revision_chat_confirmada) != (
                proveedor_id, usuario_id, datos.chat_id_revisado, datos.confirmar_revision_chat):
            raise Conflicto("La clave de esta prueba ya se usó con otra solicitud.")
        return anterior, False
    if not destino.activo or not destino.destino_verificado or destino.chat_id_pruebas != datos.chat_id_revisado:
        raise Conflicto("Activa el proveedor, vincula y verifica el chat que vas a probar.")
    ultima = servicio.db.scalar(select(PruebaMensajeProveedor).where(
        PruebaMensajeProveedor.proveedor_id == proveedor_id).order_by(PruebaMensajeProveedor.id.desc()).limit(1))
    if ultima and ultima.estado == "PENDIENTE_VERIFICACION" and not datos.confirmar_revision_chat:
        raise Conflicto("El último envío no está confirmado. Revisa el chat y confirma su revisión antes de autorizar otra prueba.")
    prueba = PruebaMensajeProveedor(
        proveedor_id=proveedor_id, usuario_id=usuario_id, clave_idempotencia=datos.clave_idempotencia,
        chat_id=destino.chat_id_pruebas, credencial_huella=servicio.telegram.huella,
        revision_chat_confirmada=datos.confirmar_revision_chat,
        texto=f"{nombre_negocio(servicio.db)} · Mensaje de prueba de FoodSave.\n"
              "Este mensaje comprueba la conexión de Telegram. No corresponde a un pedido.")
    servicio.db.add(prueba)
    servicio.db.flush()
    return prueba, True


def transmitir_prueba(servicio: ServicioProveedores, prueba: PruebaMensajeProveedor):
    """Solo HTTP, una vez confirmada una reserva NUEVA. Sin commits internos."""
    destino = servicio.consultar_destino(prueba.proveedor_id, bloquear=True)
    if not (destino.activo and destino.destino_verificado and destino.chat_id_pruebas == prueba.chat_id
            and servicio.telegram and servicio.telegram.huella == prueba.credencial_huella):
        prueba.estado = "FALLIDO"
        prueba.detalle = "El destino o la credencial cambió antes de enviar. Vincula y verifica el chat nuevamente."
        return
    try:
        resultado = servicio.telegram.enviar_mensaje(prueba.chat_id, prueba.texto)
        if (resultado.estado == "ENVIADO" and type(resultado.message_id) is int and resultado.message_id > 0
                and resultado.fecha_telegram and resultado.fecha_telegram.tzinfo):
            prueba.estado = "ENVIADO"
            prueba.message_id = resultado.message_id
            prueba.fecha_telegram = resultado.fecha_telegram
            prueba.detalle = "Telegram confirmó el envío. Comprueba la recepción en tu chat."
        elif resultado.estado == "FALLIDO":
            prueba.estado = "FALLIDO"
            prueba.detalle = "Telegram rechazó el envío. Revisa la configuración del bot, el chat y sus permisos."
        # Nunca guardar texto de excepciones/respuestas externas.
    except Exception:
        pass  # La reserva durable sigue incierta y no se retransmite.
    servicio.db.flush()
