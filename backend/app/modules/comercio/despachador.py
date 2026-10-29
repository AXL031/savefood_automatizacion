"""Proceso local de publicación; no despacha Telegram ni automatizaciones ajenas."""
import os
import time
from app.core.base_datos import SessionLocal
from .publicaciones import preparar, despachar


def ciclo():
    if os.getenv('TIENDA_INTEGRACION_HABILITADA')!='1':return
    with SessionLocal.begin() as s:preparar(s)
    despachar(SessionLocal)


if __name__=='__main__':
    while True:
        try:ciclo()
        except Exception:print('Publicación pendiente: el siguiente ciclo recuperará la entrega.',flush=True)
        time.sleep(10)
