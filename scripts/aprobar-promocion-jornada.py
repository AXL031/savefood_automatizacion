"""Prueba autorizada de publicación en la tienda actual; sin iniciar pagos."""
import json
import os
from pathlib import Path
from datetime import date
from sqlalchemy import select
from sqlalchemy.engine import make_url

if os.getenv('PREPARAR_JORNADA_AUTORIZADA')!='2026-10-28' or make_url(os.environ['DATABASE_URL']).database!='foodsave':
    raise RuntimeError('Requiere la jornada autorizada de la aplicación actual.')

from app.principal import app  # noqa
from app.core.base_datos import SessionLocal
from app.modules.autenticacion.modelos import Usuario
from app.modules.productos.modelos import Producto
from app.modules.inventario.modelos import LoteProducto
from app.modules.operaciones.modelos import PromocionOperacion
from app.modules.operaciones.rutas import decision, Decision
from app.modules.comercio.publicaciones import preparar

with SessionLocal() as s:
    u=s.scalar(select(Usuario).where(Usuario.rol=='ADMINISTRADOR',Usuario.activo.is_(True)).order_by(Usuario.id))
    p=s.scalar(select(PromocionOperacion).join(LoteProducto).join(Producto).where(
        Producto.codigo=='croissant',LoteProducto.codigo_lote.like('DEMO-2026-10-27-%'),
        PromocionOperacion.fecha==date(2026,10,28),PromocionOperacion.estado.in_(['PENDIENTE','APROBADA'])))
    assert p and u,'Primero preparar la jornada.'
    decision(p.id,Decision(aprobar=True),u,s)
    preparar(s);s.commit()
    datos={'promocion_id':p.id,'producto_id':s.get(LoteProducto,p.lote_id).producto_id,'descuento':p.descuento,'estado':p.estado,'sin_pago':True}
    Path('/evidencia/promocion-aprobada.json').write_text(json.dumps(datos,indent=2)+'\n')
    print(json.dumps(datos))
