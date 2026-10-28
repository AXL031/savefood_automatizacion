"""Revisión diez minutos y vencimientos reales. Beat invoca sin depender de visitas web."""
from datetime import datetime, timedelta, timezone
import hashlib
from sqlalchemy import select
from app.modules.inventario.modelos import LoteProducto
from app.modules.inventario.operacion import bloquear_catalogo
from app.modules.promociones.servicio import ultima_regla
from app.modules.promociones.reglas import evaluar_promocion, ReglaPromocion, EstadoProducto, PropuestaPromocion
from app.modules.promociones.esquemas import ConfigurarRegla
from app.modules.compras.modelos import PedidoCompra, LineaPedido
from app.modules.compras.recepciones import resumen_recepciones
from .modelos import SolicitudProveedor, ConfiguracionOperacion, PromocionOperacion
from .servicio import configuracion, utc, aviso


def revisar(s, ahora=None, forzar=False):
    ahora = ahora or datetime.now(timezone.utc)
    c = configuracion(s)
    c = s.scalar(select(ConfiguracionOperacion).where(ConfiguracionOperacion.id == 1).with_for_update())
    # Alertas no envían mensajes: se conservan en la bandeja administrativa.
    referencias=list(s.scalars(select(SolicitudProveedor).where(SolicitudProveedor.estado.in_(['PENDIENTE','ACEPTADO'])).order_by(SolicitudProveedor.pedido_id,SolicitudProveedor.id)))
    for referencia in referencias:
        from app.modules.compras.servicio import _bloquear_pedido
        p,_=_bloquear_pedido(s,referencia.pedido_id)
        r=s.scalar(select(SolicitudProveedor).where(SolicitudProveedor.id==referencia.id).with_for_update().execution_options(populate_existing=True))
        if r.estado == 'PENDIENTE' and utc(r.expira_en) <= ahora and p.estado in {'ENVIADO','PENDIENTE_VERIFICACION'}:
            r.estado = 'SIN_RESPUESTA'
            aviso(s, f'sin-respuesta:{r.id}', f'Proveedor sin respuesta · Pedido #{r.pedido_id}', {'pedido_id': r.pedido_id})
        if r.estado == 'ACEPTADO' and r.respuesta and datetime.fromisoformat(r.respuesta['entrega_comprometida']) <= ahora:
            lineas = list(s.scalars(select(LineaPedido).where(LineaPedido.pedido_id == p.id)))
            resumen = resumen_recepciones(s, p.id, lineas)
            if resumen['recepcion_estado'] != 'RECIBIDO':
                aviso(s, f'entrega-pendiente:{r.id}', f'Entrega pendiente · Pedido #{p.id}', {'pedido_id': p.id, 'cantidades': resumen['cantidades']})
    if not forzar and c.proxima_revision and utc(c.proxima_revision) > ahora: return {'revisada': False}
    c.proxima_revision = ahora + timedelta(minutes=10)
    datos = c.datos
    if not datos['habilitada']: return {'revisada': True, 'evaluadas': 0}
    regla = ultima_regla(s)
    if not regla or not regla.parametros['habilitada']: return {'revisada': True, 'evaluadas': 0}
    from zoneinfo import ZoneInfo
    from app.modules.negocios.servicio import zona_horaria_negocio
    local = ahora.astimezone(ZoneInfo(zona_horaria_negocio(s))).replace(tzinfo=None)
    if datos['reloj'] == 'ESCENARIO': local = datetime.fromisoformat(datos['fecha_escenario']+'T'+datos['hora_escenario'])
    from app.modules.productos.modelos import Producto
    activos=list(s.scalars(select(Producto.id).where(Producto.id.in_(datos['producto_ids']),Producto.activo.is_(True))))
    bloquear_catalogo(s, activos)
    lotes = list(s.scalars(select(LoteProducto).where(LoteProducto.producto_id.in_(activos)).order_by(LoteProducto.id).with_for_update()))
    por_id = {l.id:l for l in lotes}
    for p in s.scalars(select(PromocionOperacion).where(PromocionOperacion.estado.in_(['APROBADA','PENDIENTE']))):
        l = por_id.get(p.lote_id) or s.get(LoteProducto,p.lote_id)
        if l.saldo_disponible <= 0 or not l.fecha_limite_venta or l.fecha_limite_venta < local.date() or not l.fecha_caducidad or l.fecha_caducidad < local.date():
            p.estado = 'FINALIZADA'
    d = ConfigurarRegla(**regla.parametros)
    n = 0
    for l in lotes:
        if s.scalar(select(PromocionOperacion.id).where(PromocionOperacion.lote_id==l.id,
            PromocionOperacion.fecha==local.date(),PromocionOperacion.estado.in_(['PENDIENTE','APROBADA']))):continue
        clave = f'lote:{l.id}:regla:{regla.id}:{local.date()}'
        if s.scalar(select(PromocionOperacion.id).where(PromocionOperacion.clave == clave)): continue
        if l.fecha_ingreso and l.fecha_ingreso > local.date():
            resultado=PropuestaPromocion(False,'El lote aún no ha ingresado en esta fecha.')
        elif not l.fecha_limite_venta or not l.fecha_caducidad:
            resultado=PropuestaPromocion(False,'Falta fecha límite de venta o caducidad del lote.')
        elif l.fecha_caducidad < local.date():
            resultado=PropuestaPromocion(False,'El lote está vencido.')
        else:
            resultado = evaluar_promocion(ReglaPromocion(d.hora_revision,d.hora_cierre,d.stock_umbral,d.descuento_pct,d.descuento_maximo_pct,d.antiguedad_maxima_stock_min),
                EstadoProducto(l.fecha_limite_venta,l.saldo_disponible,local),local)
        if not resultado.proponer:
            clave += ':no:'+hashlib.sha256(resultado.motivo.encode()).hexdigest()[:12]
            if s.scalar(select(PromocionOperacion.id).where(PromocionOperacion.clave == clave)): continue
        p = PromocionOperacion(clave=clave, lote_id=l.id, regla_id=regla.id, estado='PENDIENTE' if resultado.proponer else 'NO_APLICA',
            descuento=resultado.descuento_pct, motivo=resultado.motivo, fecha=local.date())
        s.add(p); s.flush(); n+=1
        if resultado.proponer: aviso(s,f'promocion:{p.id}','Promoción sugerida pendiente de aprobación',{'promocion_id':p.id,'lote_id':l.id})
    return {'revisada':True,'evaluadas':n}
