"""Caja presencial. Precios, cotizaciones, tickets y compensaciones sin commits internos."""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4
from zoneinfo import ZoneInfo
from sqlalchemy import func, select, text
from app.core.errores import ErrorAPI
from app.modules.negocios.servicio import zona_horaria_negocio, moneda_negocio
from app.modules.productos.servicio import catalogo_para_ventas
from app.modules.inventario.ventas import disponibilidad_para_venta, retirar_productos_por_venta, reintegrar_venta
from .modelos_caja import PrecioVenta, CotizacionVenta, TicketVenta, LineaTicketVenta, SalidaLoteVenta


def ahora():
    return datetime.now(timezone.utc)


def _utc(v):
    return v.replace(tzinfo=timezone.utc) if v.tzinfo is None else v.astimezone(timezone.utc)


def _dinero(v):
    return f"{Decimal(v):.2f}"


def _huella(datos):
    return hashlib.sha256(json.dumps(datos, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _bloquear_clave(s, operacion, uid, clave):
    if s.get_bind().dialect.name == "postgresql":
        numero = int.from_bytes(hashlib.sha256(f"caja:{operacion}:{uid}:{clave}".encode()).digest()[:8], signed=True)
        s.execute(text("SELECT pg_advisory_xact_lock(:clave)"), {"clave": numero})


def _repeticion(anterior, huella):
    if anterior.huella != huella:
        raise ErrorAPI(409, "CLAVE_REUTILIZADA", "Esta clave corresponde a otro contenido. Revisa la operación original.")


def _contexto(s):
    zona = zona_horaria_negocio(s)
    moneda = moneda_negocio(s)
    if moneda != "PEN":
        raise ErrorAPI(409, "MONEDA_NO_ADMITIDA", "La caja inicial trabaja en PEN.")
    instante = ahora()
    return instante, instante.astimezone(ZoneInfo(zona)).replace(tzinfo=None), zona, moneda


def _precios(s, ids):
    maximos = select(PrecioVenta.producto_id, func.max(PrecioVenta.version).label("v")).where(
        PrecioVenta.producto_id.in_(ids)).group_by(PrecioVenta.producto_id).subquery()
    return {p.producto_id: p for p in s.scalars(select(PrecioVenta).join(maximos,
        (PrecioVenta.producto_id == maximos.c.producto_id) & (PrecioVenta.version == maximos.c.v)))}


def contexto_comercial(s):
    """Reloj/moneda públicos compartidos por caja e integración HTTP."""
    return _contexto(s)


def precios_comerciales(s, ids):
    """Snapshots públicos del precio vigente; escribir sigue pasando por guardar_precio."""
    return {id_: {'id':p.id,'version':p.version,'precio':_dinero(p.precio)} for id_,p in _precios(s,ids).items()}


def bloquear_clave_comercial(s, operacion, identidad, clave):
    return _bloquear_clave(s, operacion, identidad, clave)


def guardar_precio(s, producto_id, entrada, usuario):
    datos = {"producto_id": producto_id, **entrada.model_dump(exclude={"clave_idempotencia"})}
    h = _huella(datos)
    _bloquear_clave(s, "precio", usuario.id, entrada.clave_idempotencia)
    anterior = s.scalar(select(PrecioVenta).where(PrecioVenta.usuario_id == usuario.id, PrecioVenta.clave == entrada.clave_idempotencia))
    if anterior:
        _repeticion(anterior, h)
        return anterior, True
    productos = catalogo_para_ventas(s, [producto_id], bloquear=True)
    if not productos or not productos[0]["activo"]:
        raise ErrorAPI(409, "PRODUCTO_NO_VENDIBLE", "El producto debe existir y estar activo.")
    vigente = _precios(s, [producto_id]).get(producto_id)
    version = vigente.version if vigente else 0
    if version != entrada.version_actual:
        raise ErrorAPI(409, "PRECIO_MODIFICADO", "Otro administrador modificó el precio. Actualiza el catálogo.")
    nuevo = PrecioVenta(producto_id=producto_id, version=version+1, precio=Decimal(entrada.precio), usuario_id=usuario.id,
                        clave=entrada.clave_idempotencia, huella=h)
    s.add(nuevo); s.flush()
    return nuevo, False


def catalogo_caja(s):
    _, local, zona, moneda = _contexto(s)
    productos = [p for p in catalogo_para_ventas(s) if p["activo"]]
    ids = [p["id"] for p in productos]
    precios, stock = _precios(s, ids), disponibilidad_para_venta(s, ids, local.date())
    return {"fecha_local": local.date().isoformat(), "zona_horaria": zona, "moneda": moneda,
            "productos": [{**p, "precio": _dinero(precios[p["id"]].precio) if p["id"] in precios else None,
                "version_precio": precios[p["id"]].version if p["id"] in precios else 0,
                **stock[p["id"]], "disponible": stock[p["id"]]["disponible"] if stock[p["id"]]["stock_conocido"] else None}
                for p in productos]}


def _lineas(s, cantidades, *, bloquear=False):
    productos = {p["id"]: p for p in catalogo_para_ventas(s, list(cantidades), bloquear=bloquear)}
    precios = _precios(s, list(cantidades))
    resultado = []
    for id_, cantidad in sorted(cantidades.items()):
        p, precio = productos.get(id_), precios.get(id_)
        if not p or not p["activo"]:
            raise ErrorAPI(409, "PRODUCTO_NO_VENDIBLE", f"Producto #{id_} no disponible para venta.")
        if not precio:
            raise ErrorAPI(409, "PRECIO_NO_DISPONIBLE", f"Configura el precio de {p['nombre']}.")
        resultado.append({"producto_id": id_, "nombre": p["nombre"], "codigo": p["codigo"], "cantidad": cantidad,
            "precio_id": precio.id, "version_precio": precio.version, "precio": _dinero(precio.precio),
            "subtotal": _dinero(precio.precio*cantidad)})
    if sum(Decimal(l["subtotal"]) for l in resultado) > Decimal("999999.99"):
        raise ErrorAPI(422, "IMPORTE_FUERA_DE_RANGO", "El total supera el máximo de PEN 999999.99.")
    return resultado


def cotizar(s, entrada, usuario):
    h = _huella(entrada.model_dump(exclude={"clave_idempotencia"}))
    _bloquear_clave(s, "cotizacion", usuario.id, entrada.clave_idempotencia)
    anterior = s.scalar(select(CotizacionVenta).where(CotizacionVenta.usuario_id == usuario.id, CotizacionVenta.clave == entrada.clave_idempotencia))
    if anterior:
        _repeticion(anterior, h)
        return anterior, True
    instante, local, _, moneda = _contexto(s)
    cantidades = {l.producto_id: l.cantidad for l in entrada.lineas}
    lineas = _lineas(s, cantidades, bloquear=True)
    stock = disponibilidad_para_venta(s, list(cantidades), local.date())
    for id_, cantidad in cantidades.items():
        if not stock[id_]["stock_conocido"] or stock[id_]["disponible"] < cantidad:
            raise ErrorAPI(409, "STOCK_INSUFICIENTE" if stock[id_]["stock_conocido"] else "STOCK_DESCONOCIDO",
                           f"No hay {cantidad} unidades vendibles del producto #{id_}. Revisa Inventario.")
    cot = CotizacionVenta(id=str(uuid4()), usuario_id=usuario.id, clave=entrada.clave_idempotencia, huella=h,
                         lineas=lineas, total=sum(Decimal(l["subtotal"]) for l in lineas), moneda=moneda,
                         creado_en=instante, vence_en=instante+timedelta(minutes=5))
    s.add(cot); s.flush()
    return cot, False


def registrar_ticket(s, entrada, usuario):
    h = _huella(entrada.model_dump(exclude={"clave_idempotencia"}))
    _bloquear_clave(s, "ticket", usuario.id, entrada.clave_idempotencia)
    anterior = s.scalar(select(TicketVenta).where(TicketVenta.usuario_id == usuario.id, TicketVenta.clave == entrada.clave_idempotencia))
    if anterior:
        _repeticion(anterior, h)
        return anterior, True
    cot = s.scalar(select(CotizacionVenta).where(CotizacionVenta.id == entrada.cotizacion_id)
                   .with_for_update().execution_options(populate_existing=True))
    if not cot or cot.usuario_id != usuario.id:
        raise ErrorAPI(404, "COTIZACION_NO_ENCONTRADA", "La cotización no existe para tu usuario.")
    if s.scalar(select(TicketVenta.id).where(TicketVenta.cotizacion_id == cot.id)):
        raise ErrorAPI(409, "COTIZACION_USADA", "Esta cotización ya tiene una venta. Consulta el historial.")
    instante, local, zona, moneda = _contexto(s)
    if _utc(cot.vence_en) <= instante:
        raise ErrorAPI(409, "COTIZACION_VENCIDA", "Vuelve a cotizar y revisa la venta.")
    if moneda != cot.moneda or Decimal(entrada.total_revisado) != cot.total:
        raise ErrorAPI(409, "COTIZACION_CAMBIO", "El importe o la moneda no coincide con lo cotizado.")
    cantidades = {l["producto_id"]: l["cantidad"] for l in cot.lineas}
    if _lineas(s, cantidades, bloquear=True) != cot.lineas:
        raise ErrorAPI(409, "COTIZACION_CAMBIO", "Cambió el catálogo o precio. Vuelve a cotizar antes de confirmar.")
    cobro = entrada.cobro_presencial.model_dump()
    recibido = Decimal(cobro["importe_recibido"])
    if recibido < cot.total or (cobro["medio"] != "EFECTIVO" and recibido != cot.total):
        raise ErrorAPI(422, "COBRO_INVALIDO", "Efectivo debe cubrir el total; los demás medios deben igualarlo.")
    cobro["vuelto"] = _dinero(recibido-cot.total)
    ticket = TicketVenta(cotizacion_id=cot.id, usuario_id=usuario.id, nombre_usuario=usuario.nombre,
        clave=entrada.clave_idempotencia, huella=h, total=cot.total, moneda=moneda, cobro=cobro, anulacion=None,
        vendida_en=instante, fecha_local=local.date(), zona_horaria=zona)
    s.add(ticket); s.flush()
    salidas = retirar_productos_por_venta(s, cantidades, ticket_id=ticket.id, usuario_id=usuario.id, efectivo=local)
    for l in cot.lineas:
        linea = LineaTicketVenta(ticket_id=ticket.id, **{k: l[k] for k in
            ("producto_id", "precio_id", "nombre", "codigo", "cantidad", "precio")}, subtotal=Decimal(l["subtotal"]))
        s.add(linea); s.flush()
        s.add_all(SalidaLoteVenta(linea_id=linea.id, **{k: a[k] for k in ("lote_id", "cantidad", "movimiento_id")})
                  for a in salidas if a["producto_id"] == l["producto_id"])
    s.flush()
    return ticket, False


def anular_ticket(s, id_, entrada, usuario):
    _bloquear_clave(s, "anulacion", usuario.id, entrada.clave_idempotencia)
    otra = s.scalar(select(TicketVenta.id).where(TicketVenta.anulado_por == usuario.id, TicketVenta.clave_anulacion == entrada.clave_idempotencia))
    if otra and otra != id_:
        raise ErrorAPI(409, "CLAVE_REUTILIZADA", "Esta clave de anulación pertenece a otra venta.")
    ticket = s.scalar(select(TicketVenta).where(TicketVenta.id == id_).with_for_update().execution_options(populate_existing=True))
    if not ticket:
        raise ErrorAPI(404, "VENTA_NO_ENCONTRADA", "La venta no existe.")
    if ticket.canal == 'TIENDA':
        raise ErrorAPI(409,'ANULACION_TIENDA_NO_ADMITIDA','La venta online requiere revisión de pedido y pago; esta acción solo anula caja presencial.')
    h = _huella(entrada.model_dump())
    if ticket.anulacion:
        if ticket.anulacion["huella"] != h or ticket.anulacion["usuario_id"] != usuario.id:
            raise ErrorAPI(409, "VENTA_YA_ANULADA", "La venta ya se anuló con otra solicitud.")
        return ticket
    _, local, _, _ = _contexto(s)
    salidas = list(s.scalars(select(SalidaLoteVenta).join(LineaTicketVenta, LineaTicketVenta.id == SalidaLoteVenta.linea_id)
                            .where(LineaTicketVenta.ticket_id == ticket.id)))
    compensaciones = reintegrar_venta(s, [a.movimiento_id for a in salidas], ticket_id=ticket.id, usuario_id=usuario.id, efectivo=local)
    for a in salidas:
        a.compensacion_id = compensaciones[a.movimiento_id]
    ticket.estado = "ANULADA"
    ticket.anulado_por, ticket.clave_anulacion = usuario.id, entrada.clave_idempotencia
    ticket.anulacion = {**entrada.model_dump(), "huella": h, "usuario_id": usuario.id,
                        "nombre_usuario": usuario.nombre, "creado_en": ahora().isoformat()}
    s.flush()
    return ticket


def resumen_ticket(t):
    return {"id": t.id, "numero": f"V-{t.id:08d}", "canal": t.canal, "estado": t.estado, "total": _dinero(t.total),
        "moneda": t.moneda, "fecha_local": t.fecha_local.isoformat(), "vendida_en": _utc(t.vendida_en).isoformat(),
        "zona_horaria": t.zona_horaria, "nombre_usuario": t.nombre_usuario, "usuario_id": t.usuario_id,
        "pedido_externo":t.pedido_externo,"integracion_id":t.integracion_id,
        "cobro":t.cobro if t.canal=='PRESENCIAL' else {**t.cobro,'medio':'TARJETA' if t.cobro['metodo']=='CARD' else t.cobro['metodo'],
                                                    'importe_recibido':_dinero(t.total),'vuelto':'0.00'}}


def detalle_ticket(s, id_):
    t = s.get(TicketVenta, id_)
    if not t:
        raise ErrorAPI(404, "VENTA_NO_ENCONTRADA", "La venta no existe.")
    lineas = list(s.scalars(select(LineaTicketVenta).where(LineaTicketVenta.ticket_id == t.id).order_by(LineaTicketVenta.id)))
    salidas = list(s.scalars(select(SalidaLoteVenta).where(SalidaLoteVenta.linea_id.in_([l.id for l in lineas]))))
    return {**resumen_ticket(t), "cotizacion_id": t.cotizacion_id, "anulacion": t.anulacion,
        "lineas": [{"id": l.id, "producto_id": l.producto_id, "nombre": l.nombre, "codigo": l.codigo,
            "cantidad": l.cantidad, "precio": _dinero(l.precio), "subtotal": _dinero(l.subtotal), "precio_id": l.precio_id,
            "segmentos": l.segmentos,
            "salidas": [{"lote_id": a.lote_id, "cantidad": a.cantidad, "movimiento_id": a.movimiento_id, "compensacion_id": a.compensacion_id}
                        for a in salidas if a.linea_id == l.id]} for l in lineas]}
