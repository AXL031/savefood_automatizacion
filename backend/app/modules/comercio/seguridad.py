import hmac
import os
from fastapi import Header
from app.core.errores import ErrorAPI


def integracion(authorization: str = Header(default='')):
    esperado = os.getenv('TIENDA_INTEGRACION_TOKEN', '')
    if os.getenv('TIENDA_INTEGRACION_HABILITADA') != '1' or len(esperado) < 32:
        raise ErrorAPI(503, 'INTEGRACION_NO_CONFIGURADA', 'La integración de tienda está deshabilitada.')
    recibido = authorization[7:] if authorization.startswith('Bearer ') else ''
    if not hmac.compare_digest(recibido, esperado):
        raise ErrorAPI(401, 'INTEGRACION_NO_AUTORIZADA', 'La integración no está autorizada.')
    return os.getenv('TIENDA_INTEGRACION_ID', 'tienda-local')
