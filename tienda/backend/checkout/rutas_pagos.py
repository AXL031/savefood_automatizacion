"""Checkout de pruebas con capacidad privada, Consulta Payme y notificaciones firmadas."""
import json
from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .base_datos import obtener_sesion
from .errores import ErrorAPI
from .esquemas_pagos import CotizarPago, CrearPago, VerificarPago
from .modelos import PagoTiendaPrueba
from .payme_cliente import configuracion, obtener_cliente_payme, verificar_firma, METODOS, SDK_JS, SDK_CSS
from .pagos import aplicar_resultado, cotizar, crear_pago, obtener_pago, payload_flex, vista_pago
from . import integracion

router = APIRouter(prefix="/pagos", tags=["payme-pruebas"])


def capacidad(authorization: str = Header(default="")):
    return authorization[7:] if authorization.startswith("Bearer ") else ""


@router.get("/configuracion")
def estado_configuracion():
    config = configuracion()
    return {"datos": {"ambiente": "pruebas", "configurado": bool(config.listo), "metodos": list(METODOS)}}


@router.post("/cotizar")
def cotizacion(datos: CotizarPago, sesion: Session = Depends(obtener_sesion)):
    if integracion.modo()=='api':return {'datos':integracion.cotizar_comercio(sesion,datos)}
    c=cotizar(datos)
    origen='ejemplo:'+c['catalogo']
    if datos.origen_catalogo and datos.origen_catalogo!=origen:
        raise ErrorAPI(409,'CATALOGO_CAMBIO','El origen del catálogo cambió; vuelve a seleccionar los productos.')
    return {'datos':{**c,'origen':origen}}


@router.post("")
def checkout(datos: CrearPago, sesion: Session = Depends(obtener_sesion), cliente=Depends(obtener_cliente_payme)):
    cliente.config.exigir()
    import hashlib
    existente=sesion.scalar(select(PagoTiendaPrueba).where(
        PagoTiendaPrueba.clave_hash==hashlib.sha256(str(datos.clave_checkout).encode()).hexdigest()))
    sesion.commit()
    comercial=integracion.cotizar_comercio(sesion,datos) if existente is None and integracion.modo()=='api' else None
    try:
        pago = crear_pago(sesion, datos, cliente.config,comercial)
        sesion.commit()  # Reserva durable antes de token/nonce; todavía no se cobra.
    except IntegrityError:
        sesion.rollback()
        pago = crear_pago(sesion, datos, cliente.config,comercial)
        sesion.commit()
    vista = vista_pago(sesion, pago)
    if vista["pagado"]:
        return {"datos": {"pago": vista, "flex": None}}
    if not integracion.asegurar_reserva(sesion,pago.id):
        return {'datos':{'pago':vista_pago(sesion,sesion.get(PagoTiendaPrueba,pago.id)),'flex':None}}
    pago=sesion.get(PagoTiendaPrueba,pago.id)
    vista=vista_pago(sesion,pago)
    if pago.estado != "CREADO":
        raise ErrorAPI(409, "PAYME_PAGO_EN_CURSO", "Este pago ya tiene un resultado o está en curso. Consulta su estado antes de iniciar otro.")
    payload=payload_flex(pago);metodo=pago.metodo;sesion.commit()
    nonce = cliente.nonce()
    return {"datos": {"pago": vista, "flex": {"nonce": nonce, "payload": payload,
                        "metodo": metodo, "script_url": SDK_JS, "css_url": SDK_CSS}}}


@router.post("/notificaciones")
async def notificaciones(request: Request, signature: str = Header(default=""), sesion: Session = Depends(obtener_sesion)):
    raw = bytearray()
    async for fragmento in request.stream():
        raw.extend(fragmento)
        if len(raw) > 65536:
            raise ErrorAPI(413, "PAYME_EVENTO_GRANDE", "La notificación excede el tamaño permitido.")
    if len(signature) > 512:
        raise ErrorAPI(401, "PAYME_FIRMA_INVALIDA", "La firma no es válida.")
    verificar_firma(bytes(raw), signature)
    try:
        datos = json.loads(raw)
        if not isinstance(datos, dict):
            raise ValueError()
    except (ValueError, UnicodeDecodeError):
        raise ErrorAPI(422, "PAYME_EVENTO_INVALIDO", "La notificación no contiene JSON válido.") from None
    pago = sesion.scalar(select(PagoTiendaPrueba).where(PagoTiendaPrueba.operacion == str(datos.get("merchant_operation_number"))).with_for_update())
    if not pago:
        return {"datos": {"recibido": True, "aplicado": False}}
    aplicar_resultado(sesion, pago, datos)
    integracion.preparar_salida(sesion,pago)
    id_=pago.id
    sesion.commit()
    integracion.sincronizar_pago(sesion,id_)
    return {"datos": {"recibido": True, "aplicado": True}}


@router.get('/recuperar')
def recuperar(clave:str=Depends(capacidad),sesion:Session=Depends(obtener_sesion)):
    import hashlib
    if not clave:raise ErrorAPI(404,'PAGO_NO_ENCONTRADO','No se encontró la operación pendiente.')
    pago=sesion.scalar(select(PagoTiendaPrueba).where(PagoTiendaPrueba.clave_hash==hashlib.sha256(clave.encode()).hexdigest()))
    if not pago:raise ErrorAPI(404,'PAGO_NO_ENCONTRADO','No se encontró la operación pendiente.')
    return {'datos':vista_pago(sesion,pago)}


@router.get("/{id}")
def detalle(id: str, clave: str = Depends(capacidad), sesion: Session = Depends(obtener_sesion)):
    return {"datos": vista_pago(sesion, obtener_pago(sesion, id, clave))}


@router.post("/{id}/verificar")
def verificar(id: str, datos: VerificarPago, clave: str = Depends(capacidad), sesion: Session = Depends(obtener_sesion),
              cliente=Depends(obtener_cliente_payme)):
    pago = obtener_pago(sesion, id, clave, bloquear=True)
    vista = vista_pago(sesion, pago)
    tid = datos.transaction_id or vista["transaction_id"]
    if not tid:
        integracion.preparar_salida(sesion,pago);sesion.commit();integracion.sincronizar_pago(sesion,id)
        return {"datos": vista_pago(sesion, sesion.get(PagoTiendaPrueba,id))}
    merchant,operacion=pago.merchant_code,pago.operacion;sesion.commit()
    respuesta = cliente.consultar(merchant, operacion, tid)
    pago=obtener_pago(sesion,id,clave,bloquear=True)
    aplicar_resultado(sesion, pago, respuesta, tid)
    integracion.preparar_salida(sesion,pago)
    sesion.commit()
    integracion.sincronizar_pago(sesion,id)
    return {"datos": vista_pago(sesion, sesion.get(PagoTiendaPrueba,id))}


@router.post('/{id}/sincronizar')
def sincronizar(id:str,clave:str=Depends(capacidad),sesion:Session=Depends(obtener_sesion)):
    pago=obtener_pago(sesion,id,clave,bloquear=True)
    integracion.preparar_salida(sesion,pago);sesion.commit()
    integracion.sincronizar_pago(sesion,id)
    return {'datos':vista_pago(sesion,sesion.get(PagoTiendaPrueba,id))}
