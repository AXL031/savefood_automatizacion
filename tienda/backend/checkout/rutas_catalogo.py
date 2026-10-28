"""El navegador siempre usa la API propia; origen y cotización permanecen juntos."""
import json
from pathlib import Path
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .base_datos import obtener_sesion
from .integracion import modo, catalogo_con_disponibilidad

router=APIRouter(tags=['catalogo-tienda'])


def catalogo_ejemplo():
    c=json.loads(Path(__file__).with_name('catalogo_prueba.json').read_text(encoding='utf8'))
    promos={p['producto_id']:p for p in c['promociones']};productos=[]
    for p in c['productos']:
        promo=promos.get(p['id']);n=p['stock']
        productos.append({**{k:v for k,v in p.items() if k!='stock'},'moneda':'PEN',
            'estado_stock':'AGOTADO' if n<=0 else 'ULTIMAS_UNIDADES' if n<=5 else 'DISPONIBLE',
            'promocion':{'id':promo['id'],'producto_id':p['id'],'descuento_pct':promo['descuento_pct'],
                'precio_normal':p['precio'],'precio_promocional':f"{(Decimal(p['precio'])*(100-promo['descuento_pct'])/100).quantize(Decimal('.01')):.2f}",
                'vigente_hasta':promo['vigente_hasta']} if promo and n>0 else None})
    return {'origen':'ejemplo:'+c['version'],'version':c['version'],'modo':'ejemplo','disponibilidad_actualizada':True,
            'categorias':c.get('categorias',[]),'productos':productos}


@router.get('/catalogo')
def catalogo(s:Session=Depends(obtener_sesion)):
    return {'datos':catalogo_con_disponibilidad(s) if modo()=='api' else catalogo_ejemplo()}


@router.get('/stock')
def stock(s:Session=Depends(obtener_sesion)):
    c=catalogo_con_disponibilidad(s) if modo()=='api' else catalogo_ejemplo()
    return {'datos':{'origen':c['origen'],'version':c['version'],'actualizada':c['disponibilidad_actualizada'],
        'items':[{'producto_id':p['id'],'estado_stock':p['estado_stock'],'promocion_id':p['promocion']['id'] if p['promocion'] else None} for p in c['productos']]}}
