"""Outbox de snapshots comerciales. HTTP fuera de las transacciones."""
import json
import os
from datetime import timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from sqlalchemy import select
from app.modules.ventas import caja
from .catalogo import configuracion, catalogo_publicado, huella
from .modelos import EventoPublicacion


def ahora():
    return caja.ahora()


def preparar(s):
    c=configuracion(s,crear=True)
    datos=catalogo_publicado(s)
    h=huella(datos)
    anterior=s.scalar(select(EventoPublicacion).order_by(EventoPublicacion.version.desc()).limit(1))
    if anterior and anterior.huella==h:return anterior
    c.version+=1
    e=EventoPublicacion(version=c.version,huella=h,datos={**datos,'version':c.version,'fecha_generacion':ahora().isoformat()},
                       estado='PENDIENTE',intentos=0,proximo_intento=ahora())
    s.add(e);s.flush();return e


def enviar(datos):
    base=os.getenv('TIENDA_API_INTERNA_URL','').rstrip('/')
    token=os.getenv('TIENDA_PUBLICACION_TOKEN','')
    if not base.startswith(('http://','https://')) or len(token)<32:
        raise RuntimeError('PUBLICACION_NO_CONFIGURADA')
    solicitud=Request(base+'/api/v1/integracion/catalogo',data=json.dumps(datos).encode(),method='PUT',
                      headers={'Content-Type':'application/json','Authorization':'Bearer '+token})
    # No reenviar credenciales en una redirección a otro destino.
    from urllib.request import build_opener, HTTPRedirectHandler
    class SinRedireccion(HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):return None
    try:
        with build_opener(SinRedireccion).open(solicitud,timeout=5) as r:
            respuesta=json.loads(r.read(2_000_001))['datos']
        if respuesta.get('origen')!=datos['origen'] or respuesta.get('version')!=datos['version']:
            raise RuntimeError('ACUSE_PUBLICACION_INVALIDO')
    except (HTTPError,URLError,TimeoutError,ValueError,KeyError,OSError):
        raise RuntimeError('TIENDA_NO_CONFIRMÓ_PUBLICACION') from None


def despachar(sesiones,transporte=enviar):
    with sesiones() as s:
        pendientes=[(e.id,e.datos) for e in s.scalars(select(EventoPublicacion).where(
            EventoPublicacion.estado=='PENDIENTE',EventoPublicacion.proximo_intento<=ahora())
            .order_by(EventoPublicacion.version).limit(10))]
    for id_,datos in pendientes:
        error=None
        try:transporte(datos)
        except Exception:error='No se recibió un acuse válido; se reintentará la misma versión.'
        with sesiones.begin() as s:
            e=s.scalar(select(EventoPublicacion).where(EventoPublicacion.id==id_).with_for_update())
            if e.estado=='CONFIRMADO':continue
            e.intentos+=1;e.ultimo_error=error
            if error:e.proximo_intento=ahora()+timedelta(seconds=min(300,5*2**min(e.intentos,6)))
            else:e.estado='CONFIRMADO'
    return len(pendientes)
