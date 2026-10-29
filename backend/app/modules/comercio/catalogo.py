"""Catálogo público a partir de precio canónico y publicaciones aprobadas."""
import hashlib
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4
from sqlalchemy import select, text
from app.core.errores import ErrorAPI
from app.modules.productos.servicio import catalogo_para_ventas
from app.modules.ventas.caja import contexto_comercial, precios_comerciales
from app.modules.inventario.ventas import lotes_para_comercio, lote_vendible, disponibilidad_para_venta
from app.modules.inventario.reservas import cantidades_reservadas
from app.modules.operaciones.modelos import PromocionOperacion
from .modelos import ConfiguracionComercio, PublicacionProducto

CATEGORIAS = {'panes':'Panes y hojaldres','tortas':'Tortas clásicas','kekes':'Kekes caseros',
              'postres-personales':'Postres personales','postres-enteros':'Postres para compartir',
              'bocados':'Bocados salados','otros':'Otros productos'}


def dinero(n):
    return f"{Decimal(n).quantize(Decimal('.01'),rounding=ROUND_HALF_UP):.2f}"


def huella(datos):
    return hashlib.sha256(json.dumps(datos,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def configuracion(s, crear=False):
    if crear and s.get_bind().dialect.name == 'postgresql':
        s.execute(text('SELECT pg_advisory_xact_lock(2810202602)'))
    c=s.get(ConfiguracionComercio,1)
    if not c and crear:
        c=ConfiguracionComercio(id=1,origen=str(uuid4()),version=0)
        s.add(c);s.flush()
    return c


def validar_origen(s,origen):
    c=configuracion(s)
    if not c or c.origen != str(origen):
        raise ErrorAPI(409,'CATALOGO_ORIGEN_DISTINTO','El catálogo corresponde a otra instalación; actualiza la tienda.')
    return c


def estado_stock(n):
    return 'AGOTADO' if n<=0 else 'ULTIMAS_UNIDADES' if n<=5 else 'DISPONIBLE'


def promociones_vigentes(s,lotes,fecha):
    ids={l.id for l in lotes if lote_vendible(l,fecha)}
    if not ids:return {}
    return {p.lote_id:p for p in s.scalars(select(PromocionOperacion).where(
        PromocionOperacion.lote_id.in_(ids),PromocionOperacion.estado=='APROBADA',
        PromocionOperacion.fecha==fecha).order_by(PromocionOperacion.id))}


def guardar_ficha(s,id_,entrada,usuario):
    productos=catalogo_para_ventas(s,[id_],bloquear=True)
    if not productos or not productos[0]['activo']:
        raise ErrorAPI(409,'PRODUCTO_NO_DISPONIBLE','Selecciona un producto activo del catálogo.')
    if entrada.publicado and id_ not in precios_comerciales(s,[id_]):
        raise ErrorAPI(409,'PRECIO_NO_DISPONIBLE','Configura primero el precio en Ventas.')
    f=s.get(PublicacionProducto,id_)
    if (f.version if f else 0) != entrada.version_actual:
        raise ErrorAPI(409,'PUBLICACION_MODIFICADA','Otra persona modificó la ficha; actualiza antes de guardar.')
    datos=entrada.model_dump(exclude={'version_actual','publicado'})
    if f and f.publicado==entrada.publicado and f.datos==datos:return f
    if not f:
        f=PublicacionProducto(producto_id=id_,version=0);s.add(f)
    f.version+=1;f.publicado=entrada.publicado;f.datos=datos;f.usuario_id=usuario.id
    f.actualizado_en=contexto_comercial(s)[0]
    s.flush()
    return f


def catalogo_publicado(s):
    c=configuracion(s)
    _,local,_,moneda=contexto_comercial(s)
    productos=catalogo_para_ventas(s)
    ids=[p['id'] for p in productos if p['activo']]
    precios=precios_comerciales(s,ids)
    fichas={f.producto_id:f for f in s.scalars(select(PublicacionProducto).where(PublicacionProducto.publicado.is_(True)))}
    stock=disponibilidad_para_venta(s,ids,local.date())
    lotes=lotes_para_comercio(s,ids);reservas=cantidades_reservadas(s,[l.id for l in lotes])
    promos=promociones_vigentes(s,lotes,local.date())
    salida=[];categorias=set()
    for p in productos:
        id_=p['id'];f=fichas.get(id_);precio=precios.get(id_)
        if not p['activo'] or not f or not precio:continue
        categorias.add(f.datos['categoria']);promo=None
        for lote in sorted((l for l in lotes if l.producto_id==id_),key=lambda l:(l.fecha_limite_venta or datetime.max.date(),l.id)):
            r=promos.get(lote.id)
            if r and lote.saldo_disponible-reservas.get(lote.id,0)>0:
                promo={'id':r.id,'producto_id':id_,'descuento_pct':r.descuento,'precio_normal':precio['precio'],
                       'precio_promocional':dinero(Decimal(precio['precio'])*(100-r.descuento)/100),
                       'vigente_hasta':f'{local.date()}T23:59:59'}
                break
        salida.append({**{k:p[k] for k in ('id','codigo','nombre')},**f.datos,'precio':precio['precio'],
                       'version_precio':precio['version'],'version_publicacion':f.version,'moneda':moneda,
                       'estado_stock':estado_stock(stock[id_]['disponible']),'promocion':promo})
    return {'origen':c.origen if c else None,'fecha_local':local.date().isoformat(),'moneda':moneda,
            'categorias':[{'codigo':k,'nombre':CATEGORIAS[k],'descripcion':'',
                           'imagen':f'/tienda/categorias/{k}.jpg' if k!='otros' else ''} for k in CATEGORIAS if k in categorias],
            'productos':salida}


def cotizar(s,entrada,*,bloquear=False):
    c=validar_origen(s,entrada.origen)
    _,local,_,moneda=contexto_comercial(s)
    cantidades={l.producto_id:l.cantidad for l in entrada.lineas}
    productos={p['id']:p for p in catalogo_para_ventas(s,sorted(cantidades),bloquear=bloquear)}
    precios=precios_comerciales(s,list(cantidades))
    lotes=lotes_para_comercio(s,list(cantidades),bloquear=bloquear)
    reservadas=cantidades_reservadas(s,[l.id for l in lotes])
    promos=promociones_vigentes(s,lotes,local.date());publicas=[];internas=[]
    for id_,n in sorted(cantidades.items()):
        f=s.get(PublicacionProducto,id_);p=productos.get(id_);precio=precios.get(id_)
        if not p or not p['activo'] or not f or not f.publicado or not precio:
            raise ErrorAPI(409,'PRODUCTO_NO_PUBLICADO','Uno de los productos ya no está publicado con precio vigente.')
        restantes=n;segmentos=[];asignaciones=[];subtotal=Decimal(0);con_promo=0
        elegibles=sorted([l for l in lotes if l.producto_id==id_ and lote_vendible(l,local.date())],
                          key=lambda l:(l.fecha_limite_venta,l.fecha_caducidad or datetime.max.date(),l.id))
        for lote in elegibles:
            tomar=min(restantes,max(0,lote.saldo_disponible-reservadas.get(lote.id,0)))
            if not tomar:continue
            r=promos.get(lote.id)
            unitario=Decimal(dinero(Decimal(precio['precio'])*(100-r.descuento)/100)) if r else Decimal(precio['precio'])
            tramo={'cantidad':tomar,'precio_unitario':dinero(unitario),'promocion_id':r.id if r else None}
            grupo=next((x for x in segmentos if x['precio_unitario']==tramo['precio_unitario'] and x['promocion_id']==tramo['promocion_id']),None)
            if grupo:grupo['cantidad']+=tomar
            else:segmentos.append(tramo)
            asignaciones.append({'producto_id':id_,'lote_id':lote.id,'cantidad':tomar,**{k:tramo[k] for k in ('precio_unitario','promocion_id')}})
            subtotal+=tomar*unitario;restantes-=tomar;con_promo+=tomar if r else 0
            if not restantes:break
        if restantes:subtotal+=restantes*Decimal(precio['precio'])
        valores_promo={x['precio_unitario'] for x in segmentos if x['promocion_id']}
        linea={'producto_id':id_,'nombre':p['nombre'],'codigo':p['codigo'],'cantidad':n,'precio_id':precio['id'],
               'version_precio':precio['version'],'version_publicacion':f.version,'precio_unitario_base':precio['precio'],
               'subtotal':dinero(subtotal),'unidades_con_promocion':con_promo,
               'precio_promocional':next(iter(valores_promo)) if len(valores_promo)==1 else None,
               'disponible':restantes==0,'estado_stock':estado_stock(sum(max(0,l.saldo_disponible-reservadas.get(l.id,0)) for l in elegibles)),
               'segmentos':segmentos}
        publicas.append(linea);internas.append({**linea,'asignaciones':asignaciones})
    total=sum(Decimal(l['subtotal']) for l in publicas)
    if not Decimal('0')<total<=Decimal('999999.99'):
        raise ErrorAPI(422,'IMPORTE_NO_ADMITIDO','El total debe ser mayor que cero y no superar S/ 999999.99.')
    datos={'origen':c.origen,'fecha_local':local.date().isoformat(),'lineas':publicas,'total':dinero(total),'moneda':moneda}
    return {**datos,'huella':huella(datos)},internas
