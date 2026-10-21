"""Mercancía recibida y auditoría atómicas; nunca equivale al envío de un mensaje."""
from datetime import date, datetime
from decimal import Decimal, localcontext
from zoneinfo import ZoneInfo
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from app.core.errores import ErrorAPI
from app.modules.negocios.servicio import zona_horaria_negocio
from app.modules.inventario.servicio import registrar_recepcion_ingrediente
from .modelos import RecepcionPedido, LineaRecepcionPedido, LineaPedido


class LineaRecepcionCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")
    linea_pedido_id: int = Field(gt=0)
    cantidad_compra: Decimal = Field(gt=0, max_digits=20, decimal_places=4)
    codigo_lote: str | None = Field(default=None, max_length=80)
    fecha_caducidad: date | None = None

    @field_validator("codigo_lote")
    @classmethod
    def limpiar(cls, valor):
        return valor.strip() or None if valor is not None else None


class RecepcionCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")
    clave_idempotencia: str = Field(min_length=8, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    fecha_recepcion: date
    motivo: str = Field(min_length=3, max_length=300)
    lineas: list[LineaRecepcionCrear] = Field(min_length=1)

    @field_validator("motivo")
    @classmethod
    def limpiar(cls, valor):
        if len(valor.strip()) < 3:
            raise ValueError("Indica el motivo de la recepción")
        return valor.strip()


def resumen_recepciones(sesion, pedido_id, lineas):
    recibidas = {}
    historial = []
    for recepcion in sesion.scalars(select(RecepcionPedido).where(RecepcionPedido.pedido_id == pedido_id).order_by(RecepcionPedido.id)):
        detalle = []
        for linea in sesion.scalars(select(LineaRecepcionPedido).where(LineaRecepcionPedido.recepcion_id == recepcion.id).order_by(LineaRecepcionPedido.id)):
            recibidas[linea.linea_pedido_id] = recibidas.get(linea.linea_pedido_id, Decimal(0)) + linea.cantidad_compra
            detalle.append({"linea_pedido_id": linea.linea_pedido_id, "cantidad_compra": str(linea.cantidad_compra),
                "cantidad_base": str(linea.cantidad_base), "lote_id": linea.lote_id, "movimiento_id": linea.movimiento_id,
                "codigo_lote": linea.codigo_lote, "fecha_caducidad": linea.fecha_caducidad.isoformat() if linea.fecha_caducidad else None})
        historial.append({"id": recepcion.id, "fecha_recepcion": recepcion.fecha_recepcion.isoformat(),
            "creado_en": recepcion.creado_en.isoformat(), "usuario_id": recepcion.usuario_id,
            "nombre_usuario": recepcion.nombre_usuario, "motivo": recepcion.motivo, "lineas": detalle})
    cantidades = {l.id: {"cantidad_recibida": str(recibidas.get(l.id, Decimal(0))),
        "cantidad_pendiente": str(l.cantidad_compra - recibidas.get(l.id, Decimal(0)))} for l in lineas}
    completo = bool(lineas) and all(Decimal(cantidades[l.id]["cantidad_pendiente"]) == 0 for l in lineas)
    return {"recepcion_estado": "RECIBIDO" if completo else "PARCIAL" if historial else "PENDIENTE",
        "recepciones": historial, "cantidades": cantidades}


def registrar_recepcion(sesion, pedido_id, datos: RecepcionCrear, usuario_id, nombre_usuario):
    from .servicio import _bloquear_pedido
    pedido, propuesta = _bloquear_pedido(sesion, pedido_id)
    solicitud = datos.model_dump(mode="json", exclude={"clave_idempotencia"})
    solicitud["lineas"] = sorted(solicitud["lineas"], key=lambda l: l["linea_pedido_id"])
    previa = sesion.scalar(select(RecepcionPedido).where(RecepcionPedido.clave_idempotencia == datos.clave_idempotencia))
    if previa:
        if (previa.pedido_id, previa.usuario_id, previa.solicitud_json) != (pedido_id, usuario_id, solicitud):
            raise ErrorAPI(409, "CLAVE_REUTILIZADA", "La clave de recepción ya se utilizó con otro contenido o usuario.")
        return previa
    if pedido.estado != "ENVIADO" or not propuesta.activa:
        raise ErrorAPI(409, "PEDIDO_NO_RECEPCIONABLE", "Solo se recibe mercancía de un pedido enviado y vigente.")
    hoy = datetime.now(ZoneInfo(zona_horaria_negocio(sesion))).date()
    if not propuesta.fecha_objetivo <= datos.fecha_recepcion <= hoy:
        raise ErrorAPI(422, "FECHA_RECEPCION_INVALIDA", "La recepción no puede ser futura ni anterior al día del pedido.")
    lineas = list(sesion.scalars(select(LineaPedido).where(LineaPedido.pedido_id == pedido_id).order_by(LineaPedido.id)))
    por_id = {l.id: l for l in lineas}
    ids = [l.linea_pedido_id for l in datos.lineas]
    if len(ids) != len(set(ids)) or not set(ids) <= set(por_id):
        raise ErrorAPI(422, "LINEAS_RECEPCION_INVALIDAS", "Cada línea debe pertenecer al pedido y aparecer una sola vez.")
    resumen = resumen_recepciones(sesion, pedido_id, lineas)
    recepcion = RecepcionPedido(pedido_id=pedido_id, clave_idempotencia=datos.clave_idempotencia,
        usuario_id=usuario_id, nombre_usuario=nombre_usuario, fecha_recepcion=datos.fecha_recepcion,
        motivo=datos.motivo, solicitud_json=solicitud)
    sesion.add(recepcion); sesion.flush()
    # Orden por ingrediente: todos los consumidores bloquean en el mismo orden.
    for dato in sorted(datos.lineas, key=lambda l: por_id[l.linea_pedido_id].ingrediente_id):
        linea = por_id[dato.linea_pedido_id]
        if dato.cantidad_compra > Decimal(resumen["cantidades"][linea.id]["cantidad_pendiente"]):
            raise ErrorAPI(409, "EXCEDE_PENDIENTE", "La cantidad recibida supera lo pendiente del pedido.")
        with localcontext() as contexto:
            contexto.prec = 60
            base = dato.cantidad_compra * Decimal(linea.oferta_json["factor_conversion"])
            exacta = base.quantize(Decimal("0.001"))
            if exacta != base or base >= Decimal("100000000000"):
                raise ErrorAPI(422, "PRECISION_RECEPCION", "El contenido recibido debe caber en inventario con hasta tres decimales exactos.")
        codigo_lote = dato.codigo_lote or f"REC-{recepcion.id}-{linea.id}"
        movimiento = registrar_recepcion_ingrediente(sesion, ingrediente_id=linea.ingrediente_id, cantidad_base=exacta,
            codigo_lote=codigo_lote, lote_informado=bool(dato.codigo_lote), fecha_ingreso=datos.fecha_recepcion,
            fecha_caducidad=dato.fecha_caducidad, clave=f"recepcion:{recepcion.id}:{linea.id}",
            motivo=f"Pedido #{pedido_id}: {datos.motivo}"[:300], usuario_id=usuario_id)
        sesion.add(LineaRecepcionPedido(recepcion_id=recepcion.id, linea_pedido_id=linea.id,
            cantidad_compra=dato.cantidad_compra, cantidad_base=exacta, lote_id=movimiento.lote_id,
            movimiento_id=movimiento.movimiento_id, codigo_lote=codigo_lote, fecha_caducidad=dato.fecha_caducidad))
    sesion.flush()
    return recepcion
