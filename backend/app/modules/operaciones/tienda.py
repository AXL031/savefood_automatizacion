"""Catálogo y compra real con pago simulado; nunca recibe datos de tarjeta."""
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import select
from app.core.errores import ErrorAPI
from app.modules.productos.modelos import Producto
from app.modules.inventario.operacion import bloquear_catalogo, lotes_vendibles, retirar_productos
from .modelos import FichaTienda, PromocionOperacion, RegistroOperacion
from .servicio import fecha_operativa, previo, nuevo


def dinero(n): return str(Decimal(n).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))


def estado_stock(n): return 'AGOTADO' if n <= 0 else 'ULTIMAS_UNIDADES' if n <= 5 else 'DISPONIBLE'


def promo_lote(s,lote,fecha):
    if lote.saldo_disponible <= 0 or not lote.fecha_limite_venta or lote.fecha_limite_venta < fecha: return None
    return s.scalar(select(PromocionOperacion).where(PromocionOperacion.lote_id == lote.id,
        PromocionOperacion.estado == 'APROBADA', PromocionOperacion.fecha == fecha).order_by(PromocionOperacion.id.desc()).limit(1))


def catalogo(s):
    fecha = fecha_operativa(s)
    productos, categorias = [], {}
    for f,p in s.execute(select(FichaTienda,Producto).join(Producto,Producto.id==FichaTienda.producto_id).where(Producto.activo.is_(True)).order_by(Producto.id)):
        if not f.datos.get('publicado'): continue
        lotes = lotes_vendibles(s,p.id,fecha)
        promocion = None
        for lote in lotes:
            promo = promo_lote(s,lote,fecha)
            if promo:
                promocion = {'id':promo.id,'producto_id':p.id,'descuento_pct':promo.descuento,'precio_normal':dinero(f.precio),
                    'precio_promocional':dinero(f.precio*(100-promo.descuento)/100),'vigente_hasta':f'{fecha}T23:59:59'}
                break
        categoria = f.datos.get('categoria','panes')
        categorias[categoria] = {'codigo':categoria,'nombre':categoria.replace('-',' ').capitalize(),'descripcion':'','imagen':'/tienda/categorias/panes.jpg'}
        productos.append({'id':p.id,'codigo':p.codigo,'nombre':p.nombre,'precio':dinero(f.precio),'moneda':'PEN',
            **{k:f.datos.get(k,'') for k in ['categoria','descripcion','presentacion','imagen']},
            'estado_stock':estado_stock(sum(l.saldo_disponible for l in lotes)),'promocion':promocion})
    return {'categorias':list(categorias.values()),'productos':productos}


def cotizar(s,lineas):
    fecha = fecha_operativa(s); salida=[]
    for l in lineas:
        f = s.get(FichaTienda,l['producto_id']); p=s.get(Producto,l['producto_id'])
        if not f or not f.datos.get('publicado') or not p or not p.activo:
            raise ErrorAPI(409,'PRODUCTO_NO_PUBLICADO','El producto no está disponible en el catálogo.')
        lotes = lotes_vendibles(s,p.id,fecha)
        stock = sum(x.saldo_disponible for x in lotes)
        restante, subtotal, con_promo, precio_promo = l['cantidad'],Decimal(0),0,None
        for lote in lotes:
            tomar=min(restante,lote.saldo_disponible)
            promo=promo_lote(s,lote,fecha)
            precio=Decimal(dinero(f.precio*(100-promo.descuento)/100)) if promo else f.precio
            subtotal+=precio*tomar
            if promo: con_promo+=tomar; precio_promo=dinero(precio)
            restante-=tomar
            if not restante:break
        subtotal+=restante*f.precio
        salida.append({**l,'precio_unitario_base':dinero(f.precio),'unidades_con_promocion':con_promo,
            'precio_promocional':precio_promo,'subtotal':dinero(subtotal),'disponible':stock>=l['cantidad'],'estado_stock':estado_stock(stock)})
    return {'lineas':salida,'total':dinero(sum(Decimal(l['subtotal']) for l in salida)),'moneda':'PEN'}


def comprar(s,entrada,cliente):
    bloquear_catalogo(s,[l['producto_id'] for l in entrada['lineas']])
    clave=f'cliente:{cliente.id}:{entrada["clave_idempotencia"]}'
    if p:=previo(s,clave,'VENTA_TIENDA',entrada,cliente_id=cliente.id):return p.resultado
    # Congelar los lotes antes de cotizar: un ajuste antiguo solo bloquea lote,
    # no catálogo. Releer al adquirir lock evita sobrescribir su saldo reciente.
    fecha=fecha_operativa(s)
    for producto_id in sorted(l['producto_id'] for l in entrada['lineas']):
        lotes_vendibles(s,producto_id,fecha,bloquear=True)
    cotizacion=cotizar(s,[{k:l[k] for k in ['producto_id','cantidad']} for l in entrada['lineas']])
    if any(not l['disponible'] for l in cotizacion['lineas']): raise ErrorAPI(409,'STOCK_INSUFICIENTE','Uno de los productos ya no tiene stock suficiente.')
    if any(Decimal(l['subtotal']) != Decimal(e['subtotal_esperado']) for l,e in zip(cotizacion['lineas'],entrada['lineas'])):
        raise ErrorAPI(409,'PRECIO_CAMBIADO','El precio cambió. Revisa y confirma nuevamente la cotización.')
    r=nuevo(s,clave,'VENTA_TIENDA',entrada,fecha,cliente_id=cliente.id)
    lineas=[]
    for l in cotizacion['lineas']:
        asignaciones=retirar_productos(s,l['producto_id'],l['cantidad'],fecha,f'tienda:{r.id}:{l["producto_id"]}',None,'VENTA_TIENDA')
        lineas.append({'producto_id':l['producto_id'],'nombre':s.get(Producto,l['producto_id']).nombre,'cantidad':l['cantidad'],
            'precio_unitario':l['precio_unitario_base'],'subtotal':l['subtotal'],'asignaciones':asignaciones})
    from datetime import timezone
    pedido={'id':r.id,'estado':'CONFIRMADO','creado_en':datetime.now(timezone.utc).isoformat(),'total':cotizacion['total'],
        'moneda':'PEN','lineas':lineas,'entrega':entrada['entrega'],
        'pago':{'metodo':entrada['metodo_pago_simulado'],'estado':'APROBADO','referencia':f'SIM-{r.id}','monto':cotizacion['total']}}
    r.resultado=pedido
    # El monitor transaccional periódico conserva la sugerencia con la lectura más reciente.
    # La compra no se agrega a Ventas/ML conforme ADR-009.
    for p in s.scalars(select(PromocionOperacion).where(PromocionOperacion.estado=='APROBADA')):
        from app.modules.inventario.modelos import LoteProducto
        lote=s.get(LoteProducto,p.lote_id)
        if lote.saldo_disponible<=0 or not lote.fecha_limite_venta or lote.fecha_limite_venta<fecha:p.estado='FINALIZADA'
    s.flush();return pedido
