"""Cotización de ejemplo y operaciones Payme durables, sin stock real ni commits."""
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session
from .errores import ErrorAPI
from .esquemas_pagos import CotizarPago, CrearPago
from .modelos import PagoTiendaPrueba, TransaccionPaymePrueba

APROBADOS = {"AUTORIZADO", "LIQUIDADO", "DEPOSITADO"}
ESTADOS = {"REGISTRADO", "PENDIENTE", "INVALIDO", "DENEGADO", "CANCELADO", "EXPIRADO", "EXTORNADO", *APROBADOS}


def _hash(valor):
    return hashlib.sha256(valor.encode()).hexdigest()


def _centimos(valor):
    return int((Decimal(str(valor)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def cotizar(datos: CotizarPago):
    catalogo = json.loads(Path(__file__).with_name("catalogo_prueba.json").read_text(encoding="utf-8"))
    productos = {p["id"]: p for p in catalogo["productos"]}
    promos = {p["producto_id"]: p for p in catalogo["promociones"]}
    lineas = []
    for linea in datos.lineas:
        p = productos.get(linea.producto_id)
        if not p:
            raise ErrorAPI(422, "PRODUCTO_NO_PUBLICADO", "Un producto no pertenece al catálogo de prueba.")
        promo = promos.get(p["id"])
        con_promo = min(linea.cantidad, promo["unidades_lote"]) if promo else 0
        base = _centimos(p["precio"])
        rebajado = int((Decimal(base) * (100 - Decimal(str(promo["descuento_pct"]))) / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)) if promo else base
        subtotal = rebajado * con_promo + base * (linea.cantidad - con_promo)
        stock = p["stock"]
        lineas.append({"producto_id": p["id"], "nombre": p["nombre"], "cantidad": linea.cantidad,
                       "precio_unitario_base": f"{Decimal(base)/100:.2f}", "unidades_con_promocion": con_promo,
                       "precio_promocional": f"{Decimal(rebajado)/100:.2f}" if promo else None,
                       "subtotal": f"{Decimal(subtotal)/100:.2f}", "disponible": linea.cantidad <= stock,
                       "estado_stock": "AGOTADO" if not stock else "ULTIMAS_UNIDADES" if stock <= 5 else "DISPONIBLE"})
    total = sum(_centimos(l["subtotal"]) for l in lineas)
    return {"lineas": lineas, "total": f"{Decimal(total)/100:.2f}", "moneda": "PEN", "catalogo": catalogo["version"]}


def crear_pago(sesion: Session, datos: CrearPago, config, cotizacion_comercial=None):
    config.exigir()
    cuerpo = datos.model_dump(mode="json", exclude={"clave_checkout","cotizacion_hash","total_revisado"}, exclude_none=True)
    if datos.origen_catalogo and datos.origen_catalogo.startswith('ejemplo:'):
        cuerpo.pop('origen_catalogo',None)  # Conserva la huella de pagos anteriores a la integración.
    huella = _hash(json.dumps(cuerpo, sort_keys=True, separators=(",", ":")))
    clave = _hash(str(datos.clave_checkout))
    existente = sesion.scalar(select(PagoTiendaPrueba).where(PagoTiendaPrueba.clave_hash == clave).with_for_update())
    if existente:
        # Cambiar la presentación no crea otra compra ni altera líneas/comprador/entrega.
        cuerpo_previo = {**cuerpo, "metodo": existente.snapshot.get("metodo_huella", existente.metodo)}
        huella_previa = _hash(json.dumps(cuerpo_previo, sort_keys=True, separators=(",", ":")))
        if not hmac.compare_digest(existente.huella, huella_previa):
            raise ErrorAPI(409, "CLAVE_REUTILIZADA", "Este checkout ya tiene otros datos. Revisa el pago existente.")
        if existente.metodo != datos.metodo:
            if existente.estado != "CREADO" or sesion.scalar(select(TransaccionPaymePrueba.transaction_id)
                    .where(TransaccionPaymePrueba.pago_id == existente.id).limit(1)):
                raise ErrorAPI(409, "PAYME_PAGO_EN_CURSO", "Payme ya registró una transacción. Consulta su estado antes de cambiar de método.")
            preparados = existente.snapshot.get("metodos_preparados", [existente.metodo])
            existente.snapshot = {**existente.snapshot, "metodos_preparados": sorted(set([*preparados, datos.metodo])),
                                  "metodo_huella": datos.metodo}
            existente.metodo, existente.huella = datos.metodo, huella
            sesion.flush()
        return existente
    if cotizacion_comercial is None:
        if datos.origen_catalogo and not datos.origen_catalogo.startswith('ejemplo:'):
            raise ErrorAPI(409,'CATALOGO_CAMBIO','No se puede pagar un catálogo externo con precios de ejemplo.')
        cotizacion = cotizar(datos)
        cotizacion['origen']='ejemplo:'+cotizacion['catalogo']
    else:
        cotizacion = cotizacion_comercial
        if (datos.cotizacion_hash!=cotizacion['huella'] or datos.total_revisado is None
            or Decimal(datos.total_revisado)!=Decimal(cotizacion['total'])):
            raise ErrorAPI(409,'COTIZACION_CAMBIO','La cotización cambió. Revisa el total antes de pagar.')
    if any(not l["disponible"] for l in cotizacion["lineas"]):
        raise ErrorAPI(409, "STOCK_INSUFICIENTE", "La cantidad supera las existencias del catálogo de prueba.")
    pago = PagoTiendaPrueba(id=str(uuid4()), clave_hash=clave, huella=huella,
                           operacion=str(secrets.randbelow(900_000_000_000) + 100_000_000_000),
                           merchant_code=config.merchant_code, metodo=datos.metodo,
                           monto_centimos=_centimos(cotizacion["total"]), estado="CREADO",
                           snapshot={"cotizacion": cotizacion, "comprador": cuerpo["comprador"], "entrega": cuerpo["entrega"]})
    sesion.add(pago)
    sesion.flush()
    if cotizacion_comercial is not None:
        from .integracion import preparar_vinculo
        preparar_vinculo(sesion,pago,cotizacion)
    return pago


def obtener_pago(sesion, id, capacidad, *, bloquear=False):
    consulta = select(PagoTiendaPrueba).where(PagoTiendaPrueba.id == id)
    pago = sesion.scalar(consulta.with_for_update() if bloquear else consulta)
    if not pago or not capacidad or not hmac.compare_digest(pago.clave_hash, _hash(capacidad)):
        raise ErrorAPI(404, "PAGO_NO_ENCONTRADO", "No se encontró el pago de este navegador.")
    return pago


def payload_flex(pago):
    comprador, entrega = pago.snapshot["comprador"], pago.snapshot["entrega"]
    datos = {"first_name": comprador["nombres"], "last_name": comprador["apellidos"], "email": comprador["correo"],
             "phone": {"country_code": "+51", "subscriber": entrega["celular"]},
             "location": {"line_1": entrega["direccion"], "line_2": entrega["distrito"],
                          "city": "Lima", "state": "Lima", "country": "PE"}}
    return {"action": "authorize", "channel": "ecommerce", "merchant_code": pago.merchant_code,
            "merchant_operation_number": pago.operacion, "payment_method": {},
            "payment_details": {"amount": str(pago.monto_centimos), "currency": "604", "billing": datos,
                                "shipping": datos, "customer": datos, "product_details": []}}


def _url_segura(valor):
    if isinstance(valor, str) and len(valor) <= 2048:
        u = urlparse(valor)
        if u.scheme == "https" and u.hostname and not u.username and not u.password:
            return valor
    return None


def aplicar_resultado(sesion, pago, respuesta, transaction_id=None):
    """Solo aceptar una Consulta backend o un S2S ya autenticado, nunca el callback del navegador."""
    if respuesta.get("success") not in (True, "true") or respuesta.get("merchant_code") != pago.merchant_code:
        raise ErrorAPI(502, "PAYME_RESULTADO_INVALIDO", "Payme no confirmó el comercio de esta operación.")
    operacion = respuesta.get("operation")
    if operacion:
        if (str(operacion.get("merchant_operation_number")) != pago.operacion
                or str(operacion.get("amount")) != str(pago.monto_centimos) or str(operacion.get("currency")) != "604"):
            raise ErrorAPI(502, "PAYME_RESULTADO_INVALIDO", "El importe o la operación no coincide con el checkout.")
        transacciones = operacion.get("transactions", [])
    else:
        if str(respuesta.get("merchant_operation_number")) != pago.operacion:
            raise ErrorAPI(502, "PAYME_RESULTADO_INVALIDO", "La operación no coincide con el checkout.")
        transacciones = [respuesta.get("transaction", {})]
    transaccion = next((t for t in transacciones if isinstance(t, dict) and (not transaction_id or t.get("transaction_id") == transaction_id)), None)
    if not transaccion or not transaccion.get("transaction_id"):
        raise ErrorAPI(502, "PAYME_RESULTADO_INVALIDO", "La consulta no contiene la transacción solicitada.")
    tid = str(transaccion["transaction_id"])
    estado = transaccion.get("state")
    metodo = (transaccion.get("payment_method") or {}).get("method_name")
    # Una respuesta tardía del formulario anterior conserva su correlación con esta operación.
    preparados = pago.snapshot.get("metodos_preparados", [pago.metodo])
    if (len(tid) > 128 or estado not in ESTADOS or metodo not in preparados
            or str(transaccion.get("amount")) != str(pago.monto_centimos) or str(transaccion.get("currency")) != "604"):
        raise ErrorAPI(502, "PAYME_RESULTADO_INVALIDO", "La transacción no coincide con el método, moneda o importe esperado.")
    previo = sesion.get(TransaccionPaymePrueba, tid)
    if previo and previo.pago_id != pago.id:
        raise ErrorAPI(409, "PAYME_TRANSACCION_REUTILIZADA", "La transacción corresponde a otro checkout.")
    # Las entregas tardías no degradan estados terminales a estados iniciales.
    if previo and ((previo.estado == "EXTORNADO" and estado != "EXTORNADO")
                   or (previo.estado in APROBADOS and estado not in APROBADOS | {"EXTORNADO"})
                   or (previo.estado in {"EXTORNADO", "DENEGADO", "CANCELADO", "EXPIRADO", "INVALIDO"} and estado in {"REGISTRADO", "PENDIENTE"})):
        return pago
    procesador = transaccion.get("processor_response") or {}
    detalles = {"cip": str(procesador["cip"])[:128] if procesador.get("cip") else None,
                "cip_url": _url_segura(procesador.get("cip_url")),
                "continue_url": _url_segura(transaccion.get("continue_url")),
                "expira_en": str((transaccion.get("expiration_date") or {}).get("utc_time") or "")[:64] or None}
    ahora = datetime.now(timezone.utc)
    if previo is None:
        previo = TransaccionPaymePrueba(transaction_id=tid, pago_id=pago.id)
        sesion.add(previo)
    previo.estado, previo.detalles = estado, detalles
    previo.huella_evento = _hash(json.dumps(transaccion, sort_keys=True, separators=(",", ":")))
    previo.actualizado_en = ahora
    sesion.flush()
    estados = list(sesion.scalars(select(TransaccionPaymePrueba.estado).where(TransaccionPaymePrueba.pago_id == pago.id)))
    pago.estado = next((e for e in ("DEPOSITADO", "LIQUIDADO", "AUTORIZADO") if e in estados), estado)
    if pago.estado == estado:
        pago.metodo = metodo
    pago.actualizado_en = ahora
    sesion.flush()
    return pago


def vista_pago(sesion, pago):
    ultimo = sesion.scalar(select(TransaccionPaymePrueba).where(TransaccionPaymePrueba.pago_id == pago.id)
                           .order_by(TransaccionPaymePrueba.actualizado_en.desc()).limit(1))
    from .integracion import vista_comercial
    return {"id": pago.id, "ambiente": "pruebas", "operacion": pago.operacion, "metodo": pago.metodo,
            "estado": pago.estado, "pagado": pago.estado in APROBADOS, "total": f"{Decimal(pago.monto_centimos)/100:.2f}",
            "moneda": "PEN", "cotizacion": pago.snapshot["cotizacion"], "creado_en": pago.creado_en.isoformat(),
            "transaction_id": ultimo.transaction_id if ultimo else None, "continuacion": ultimo.detalles if ultimo else {},
            "comercial":vista_comercial(sesion,pago)}
