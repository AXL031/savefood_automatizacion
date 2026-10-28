"""Enlaces de respuesta y recepción asistida; sin envío externo ni commit."""
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import select
from app.core.errores import ErrorAPI
from app.modules.compras.modelos import PedidoCompra, LineaPedido, PropuestaCompra
from app.modules.compras.servicio import _bloquear_pedido
from .modelos import SolicitudProveedor
from .servicio import aviso, utc, previo, nuevo


def crear_enlace(s, pedido_id):
    pedido, propuesta = _bloquear_pedido(s, pedido_id)
    if not propuesta.activa or pedido.estado in {'BLOQUEADO','CANCELADO','RECHAZADO'}:
        raise ErrorAPI(409, 'PEDIDO_NO_DISPONIBLE', 'El pedido no admite respuesta del proveedor.')
    anteriores = list(s.scalars(select(SolicitudProveedor).where(SolicitudProveedor.pedido_id == pedido_id).with_for_update()))
    if any(a.estado == 'ACEPTADO' for a in anteriores):
        raise ErrorAPI(409, 'PEDIDO_YA_ACEPTADO', 'El pedido ya fue aceptado; consulta su recepción.')
    for a in anteriores:
        if a.estado == 'PENDIENTE': a.estado = 'REVOCADO'
    token = secrets.token_urlsafe(32)
    r = SolicitudProveedor(pedido_id=pedido_id, token_hash=hashlib.sha256(token.encode()).hexdigest(),
        estado='PENDIENTE', expira_en=datetime.now(timezone.utc)+timedelta(hours=1))
    s.add(r); s.flush()
    base = (os.getenv('PUBLIC_BASE_URL') or os.getenv('FRONTEND_ORIGIN', 'http://localhost:3100')).rstrip('/')
    return {'url': f'{base}/proveedor/pedido/{token}', 'expira_en': r.expira_en.isoformat(), 'solicitud_id': r.id}


def buscar(s, token, bloquear=False):
    if not 30 <= len(token) <= 100: raise ErrorAPI(404, 'ENLACE_INVALIDO', 'El enlace no existe.')
    q = select(SolicitudProveedor).where(SolicitudProveedor.token_hash == hashlib.sha256(token.encode()).hexdigest())
    r = s.scalar(q.with_for_update() if bloquear else q)
    if not r: raise ErrorAPI(404, 'ENLACE_INVALIDO', 'El enlace no existe.')
    return r


def detalle_publico(s, token):
    r = buscar(s, token)
    p = s.get(PedidoCompra, r.pedido_id)
    propuesta = s.get(PropuestaCompra, p.propuesta_id)
    if r.estado in {'REVOCADO', 'SIN_RESPUESTA'} or (r.estado == 'PENDIENTE' and utc(r.expira_en) <= datetime.now(timezone.utc)):
        raise ErrorAPI(410, 'ENLACE_VENCIDO', 'El plazo de una hora terminó. Contacta al comercio.')
    if not propuesta.activa or p.estado in {'CANCELADO','RECHAZADO','BLOQUEADO'}:
        raise ErrorAPI(410, 'PEDIDO_NO_DISPONIBLE', 'El pedido dejó de estar disponible.')
    return {'pedido_id': p.id, 'proveedor': p.proveedor_json['nombre'], 'estado': r.estado, 'fecha_objetivo':propuesta.fecha_objetivo.isoformat(),
        'expira_en': utc(r.expira_en).isoformat(), 'respuesta': r.respuesta,
        'lineas': [{'nombre': l.ingrediente_json['stock']['nombre'], 'cantidad': str(l.cantidad_compra), 'unidad': l.unidad_compra}
            for l in s.scalars(select(LineaPedido).where(LineaPedido.pedido_id == p.id).order_by(LineaPedido.id))]}


def responder(s, token, entrada):
    # Mismo orden de bloqueo que compra/recepción: pedido antes del enlace.
    referencia = buscar(s, token)
    p, propuesta = _bloquear_pedido(s, referencia.pedido_id)
    r = buscar(s, token, True)
    detalle_publico(s, token)
    if r.estado != 'PENDIENTE':
        if r.respuesta and {k:r.respuesta.get(k) for k in entrada} == entrada: return r
        raise ErrorAPI(409, 'RESPUESTA_REGISTRADA', 'Ya se registró una decisión distinta.')
    if entrada['accion'] == 'ACEPTAR':
        entrega = datetime.fromisoformat(entrada['entrega_comprometida'])
        if entrega.tzinfo is None or entrega <= datetime.now(timezone.utc):
            raise ErrorAPI(422, 'ENTREGA_INVALIDA', 'Indica una fecha y hora futura con zona horaria.')
    r.estado = 'ACEPTADO' if entrada['accion'] == 'ACEPTAR' else 'RECHAZADO'
    r.respuesta = {**entrada,'respondido_en':datetime.now(timezone.utc).isoformat()}
    aviso(s, f'proveedor-respuesta:{r.id}', f'Proveedor: pedido #{p.id} {r.estado.lower()}', {'pedido_id': p.id, 'respuesta': entrada})
    s.flush(); return r


def recibir_asistido(s, pedido_id, entrada, usuario):
    from app.modules.compras.recepciones import registrar_recepcion, RecepcionCrear, resumen_recepciones
    pedido, _ = _bloquear_pedido(s, pedido_id)
    if p := previo(s, entrada['clave_idempotencia'], 'RECEPCION', entrada, usuario.id): return p
    aceptado = s.scalar(select(SolicitudProveedor.id).where(SolicitudProveedor.pedido_id == pedido_id, SolicitudProveedor.estado == 'ACEPTADO'))
    if not aceptado: raise ErrorAPI(409, 'ACEPTACION_PENDIENTE', 'El proveedor debe aceptar el pedido antes de recibirlo.')
    lineas = list(s.scalars(select(LineaPedido).where(LineaPedido.pedido_id == pedido_id).order_by(LineaPedido.id)))
    cantidades = resumen_recepciones(s, pedido_id, lineas)['cantidades']
    if not any(Decimal(x['cantidad_pendiente'])>0 for x in cantidades.values()):
        raise ErrorAPI(409,'RECEPCION_COMPLETA','El pedido ya se recibió completamente.')
    if set(cantidades) != {l['linea_pedido_id'] for l in entrada['lineas']}:
        raise ErrorAPI(422, 'LINEAS_INVALIDAS', 'Revisa todas las líneas del pedido una sola vez.')
    if len(entrada['lineas']) != len(lineas): raise ErrorAPI(422, 'LINEAS_INVALIDAS', 'No repitas ingredientes.')
    diferencias, positivas = [], []
    for l in entrada['lineas']:
        cantidad = Decimal(l['cantidad_compra'])
        pendiente = Decimal(cantidades[l['linea_pedido_id']]['cantidad_pendiente'])
        if cantidad < 0 or cantidad > pendiente: raise ErrorAPI(409, 'EXCEDE_PENDIENTE', 'Acepta entre cero y la cantidad pendiente.')
        if cantidad < pendiente: diferencias.append({'linea_pedido_id': l['linea_pedido_id'], 'pendiente': str(pendiente), 'aceptada': str(cantidad)})
        if cantidad > 0: positivas.append(l)
    if diferencias and len(entrada['motivo'].strip()) < 10:
        raise ErrorAPI(422, 'DESCRIPCION_REQUERIDA', 'Describe el defecto o faltante (al menos diez caracteres).')
    from datetime import date
    r = nuevo(s, entrada['clave_idempotencia'], 'RECEPCION', entrada, date.fromisoformat(entrada['fecha_recepcion']), usuario.id)
    if positivas:
        datos = RecepcionCrear(**{k:v for k,v in entrada.items() if k != 'lineas'}, lineas=positivas)
        rec = registrar_recepcion(s, pedido_id, datos, usuario.id, usuario.nombre)
        rid = rec.id
    else:
        if pedido.estado != 'ENVIADO': raise ErrorAPI(409, 'PEDIDO_NO_RECEPCIONABLE', 'Se requiere un pedido enviado.')
        from app.modules.negocios.servicio import zona_horaria_negocio
        from zoneinfo import ZoneInfo
        fecha = date.fromisoformat(entrada['fecha_recepcion'])
        if not s.get(PropuestaCompra,pedido.propuesta_id).fecha_objetivo <= fecha <= datetime.now(ZoneInfo(zona_horaria_negocio(s))).date():
            raise ErrorAPI(422,'FECHA_RECEPCION_INVALIDA','Fecha de recepción inválida.')
        rid = None
    if diferencias:
        aviso(s, f'recepcion:{r.id}', f'Recepción con diferencias · Pedido #{pedido_id}',
            {'pedido_id': pedido_id, 'recepcion_id': rid, 'trabajador': usuario.nombre, 'descripcion': entrada['motivo'], 'diferencias': diferencias})
    r.resultado = {'pedido_id': pedido_id, 'recepcion_id': rid, 'diferencias': diferencias}
    s.flush(); return r
