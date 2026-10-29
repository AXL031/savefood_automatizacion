"""Contratos sandbox sin enviar peticiones a Payme ni conectar con FoodSave."""
import base64
import json
from uuid import uuid4
import httpx
import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from checkout.base_datos import obtener_sesion
from checkout.errores import ErrorAPI, configurar_errores
from checkout.esquemas_pagos import CrearPago
from checkout.modelos import Base, PagoTiendaPrueba, TransaccionPaymePrueba
from checkout.pagos import aplicar_resultado, crear_pago, vista_pago
from checkout.payme_cliente import ConfigPayme, ClientePayme, obtener_cliente_payme, verificar_firma, LLAVE_PREPROD, _cache
from checkout.rutas_pagos import router

CONFIG = ConfigPayme(True, "id-prueba", "secreto-prueba", "comercio-prueba")

def entrada(metodo="CARD"):
    return {"clave_checkout": str(uuid4()), "metodo": metodo, "lineas": [{"producto_id": 1, "cantidad": 2}],
        "comprador": {"nombres": "Axel", "apellidos": "Prueba", "correo": "prueba@example.com"},
        "entrega": {"nombre_receptor": "Axel Prueba", "celular": "987654321", "direccion": "Calle Prueba 123", "distrito": "Lima", "referencia": ""}}

def resultado(pago, estado="AUTORIZADO", tid="tx-prueba"):
    return {"success": True, "merchant_code": pago.merchant_code, "merchant_operation_number": pago.operacion,
        "transaction": {"transaction_id": tid, "state": estado, "amount": str(pago.monto_centimos), "currency": "604",
                        "payment_method": {"method_name": pago.metodo}}}

@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()

@pytest.fixture
def api(db, monkeypatch):
    monkeypatch.setenv("PAYME_HABILITADO", "true")
    monkeypatch.setenv("PAYME_CLIENT_ID", CONFIG.client_id)
    monkeypatch.setenv("PAYME_CLIENT_SECRET", CONFIG.client_secret)
    monkeypatch.setenv("PAYME_MERCHANT_CODE", CONFIG.merchant_code)
    class Proveedor:
        config = CONFIG
        llamadas = 0
        fallo_nonce = False
        estado = "AUTORIZADO"
        def nonce(self):
            if self.fallo_nonce: raise ErrorAPI(502, "PAYME_NO_DISPONIBLE", "Payme no disponible.")
            return "nonce-de-pruebas"
        def consultar(self, merchant, operacion, tid):
            self.llamadas += 1
            pago = db.scalar(select(PagoTiendaPrueba).where(PagoTiendaPrueba.operacion == operacion))
            r = resultado(pago, self.estado, tid)
            return {"success": True, "merchant_code": merchant, "operation": {
                "merchant_operation_number": operacion, "amount": str(pago.monto_centimos), "currency": "604", "transactions": [r["transaction"]]}}
    proveedor = Proveedor()
    app = FastAPI(); configurar_errores(app); app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[obtener_sesion] = lambda: db
    app.dependency_overrides[obtener_cliente_payme] = lambda: proveedor
    with TestClient(app) as c:
        yield c, proveedor

@pytest.mark.parametrize("metodo", ["CARD", "YAPE", "QR", "PAGOEFECTIVO"])
def test_checkout_metodo_total_servidor_y_repeticion(api, db, metodo):
    c, proveedor = api; body = entrada(metodo)
    uno = c.post("/api/v1/pagos", json=body)
    assert uno.status_code == 200, uno.text
    datos = uno.json()["datos"]; pago = datos["pago"]
    assert datos["flex"]["metodo"] == metodo
    assert datos["flex"]["payload"]["payment_method"] == {}
    # Dos croissants a S/6.50, promoción del 30% del catálogo: S/9.10.
    assert datos["flex"]["payload"]["payment_details"]["amount"] == "910"
    assert pago["total"] == "9.10" and pago["estado"] == "CREADO" and not pago["pagado"]
    assert "secreto" not in uno.text and "clave_hash" not in uno.text
    dos = c.post("/api/v1/pagos", json=body).json()["datos"]
    assert dos["pago"]["id"] == pago["id"]
    assert db.scalar(select(func.count()).select_from(PagoTiendaPrueba)) == 1
    body["lineas"][0]["cantidad"] = 3
    assert c.post("/api/v1/pagos", json=body).status_code == 409

def test_sin_credenciales_ninguna_llamada(api, monkeypatch):
    c, proveedor = api
    monkeypatch.setenv("PAYME_HABILITADO", "false")
    assert not c.get("/api/v1/pagos/configuracion").json()["datos"]["configurado"]
    proveedor.config = ConfigPayme(False, "", "", "")
    assert c.post("/api/v1/pagos", json=entrada()).status_code == 503
    assert proveedor.llamadas == 0

@pytest.mark.parametrize("cambio", ["precio", "duplicado", "cantidad", "metodo", "producto"])
def test_rechaza_carrito_manipulado(api, cambio):
    c, _ = api; body = entrada()
    if cambio == "precio": body["total"] = "0.01"
    if cambio == "duplicado": body["lineas"] *= 2
    if cambio == "cantidad": body["lineas"][0]["cantidad"] = -1
    if cambio == "metodo": body["metodo"] = "PLIN"
    if cambio == "producto": body["lineas"][0]["producto_id"] = 99999
    assert c.post("/api/v1/pagos", json=body).status_code == 422

def test_capacidad_y_verificacion_real_en_backend(api):
    c, proveedor = api; body = entrada()
    pago = c.post("/api/v1/pagos", json=body).json()["datos"]["pago"]
    ruta = "/api/v1/pagos/" + pago["id"]
    assert c.get(ruta).status_code == 404
    assert c.get(ruta, headers={"Authorization": "Bearer " + str(uuid4())}).status_code == 404
    headers = {"Authorization": "Bearer " + body["clave_checkout"]}
    assert c.post(ruta+"/verificar", json={"state": "AUTORIZADO"}, headers=headers).status_code == 422
    proveedor.estado = "PENDIENTE"
    respuesta = c.post(ruta+"/verificar", json={"transaction_id": "tx-prueba"}, headers=headers)
    assert not respuesta.json()["datos"]["pagado"]
    proveedor.estado = "AUTORIZADO"
    respuesta = c.post(ruta+"/verificar", json={}, headers=headers)
    assert respuesta.json()["datos"]["pagado"] and proveedor.llamadas == 2

def test_timeout_nonce_conserva_operacion(api, db):
    c, proveedor = api; body = entrada(); proveedor.fallo_nonce = True
    assert c.post("/api/v1/pagos", json=body).status_code == 502
    id = db.scalar(select(PagoTiendaPrueba.id))
    proveedor.fallo_nonce = False
    assert c.post("/api/v1/pagos", json=body).json()["datos"]["pago"]["id"] == id


def test_cambiar_metodos_sin_transaccion_conserva_operacion(api, db):
    c, proveedor = api; body = entrada()
    primero = c.post("/api/v1/pagos", json=body).json()["datos"]["pago"]
    for metodo in ["YAPE", "QR", "PAGOEFECTIVO", "CARD", "YAPE"]:
        body["metodo"] = metodo
        respuesta = c.post("/api/v1/pagos", json=body)
        assert respuesta.status_code == 200, respuesta.text
        datos = respuesta.json()["datos"]
        assert datos["pago"]["id"] == primero["id"]
        assert datos["pago"]["operacion"] == primero["operacion"]
        assert datos["pago"]["total"] == primero["total"]
        assert datos["flex"]["metodo"] == metodo
    assert db.scalar(select(func.count()).select_from(PagoTiendaPrueba)) == 1
    assert proveedor.llamadas == 0  # Preparar formularios no consulta ni ejecuta cobros.
    body["comprador"]["correo"] = "otro@example.com"
    assert c.post("/api/v1/pagos", json=body).status_code == 409


@pytest.mark.parametrize("estado", ["REGISTRADO", "PENDIENTE", "AUTORIZADO", "CANCELADO", "DENEGADO"])
def test_no_cambiar_metodo_si_payme_ya_registro_transaccion(api, db, estado):
    c, _ = api; body = entrada()
    c.post("/api/v1/pagos", json=body)
    pago = db.scalar(select(PagoTiendaPrueba))
    aplicar_resultado(db, pago, resultado(pago, estado)); db.commit()
    body["metodo"] = "YAPE"
    respuesta = c.post("/api/v1/pagos", json=body)
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "PAYME_PAGO_EN_CURSO"
    assert pago.metodo == "CARD"


def test_respuesta_tardia_del_formulario_previo_no_se_pierde(api, db):
    c, _ = api; body = entrada()
    c.post("/api/v1/pagos", json=body)
    pago = db.scalar(select(PagoTiendaPrueba))
    tardia = resultado(pago, "AUTORIZADO", "tx-tardia-card")
    body["metodo"] = "YAPE"
    assert c.post("/api/v1/pagos", json=body).status_code == 200
    assert pago.metodo == "YAPE"
    aplicar_resultado(db, pago, tardia); db.commit()
    assert vista_pago(db, pago)["pagado"] and pago.metodo == "CARD"
    # Se preserva la comparación del cuerpo aunque el resultado haya usado el método anterior.
    respuesta = c.post("/api/v1/pagos", json=body)
    assert respuesta.status_code == 409 and respuesta.json()["error"]["codigo"] == "PAYME_PAGO_EN_CURSO"


def test_no_acepta_metodo_nunca_preparado_despues_de_cambiar(api, db):
    c, _ = api; body = entrada()
    c.post("/api/v1/pagos", json=body)
    body["metodo"] = "YAPE"; c.post("/api/v1/pagos", json=body)
    pago = db.scalar(select(PagoTiendaPrueba)); r = resultado(pago)
    r["transaction"]["payment_method"]["method_name"] = "QR"
    with pytest.raises(ErrorAPI): aplicar_resultado(db, pago, r)

@pytest.mark.parametrize("campo,valor", [("merchant_code", "otro"), ("merchant_operation_number", "123456"), ("amount", "1"), ("currency", "840"), ("method_name", "YAPE")])
def test_no_acepta_resultado_ajeno(db, campo, valor):
    pago = crear_pago(db, CrearPago(**entrada()), CONFIG); r = resultado(pago)
    if campo in ("merchant_code", "merchant_operation_number"): r[campo] = valor
    elif campo == "method_name": r["transaction"]["payment_method"][campo] = valor
    else: r["transaction"][campo] = valor
    with pytest.raises(ErrorAPI): aplicar_resultado(db, pago, r)
    assert not vista_pago(db, pago)["pagado"]

def test_cip_pendiente_y_eventos_fuera_de_orden(db):
    pago = crear_pago(db, CrearPago(**entrada("PAGOEFECTIVO")), CONFIG)
    r = resultado(pago, "PENDIENTE"); r["transaction"]["processor_response"] = {"cip": "123456789", "cip_url": "https://sandbox.example/cip"}
    aplicar_resultado(db, pago, r); assert not vista_pago(db, pago)["pagado"]
    assert vista_pago(db, pago)["continuacion"]["cip"] == "123456789"
    aplicar_resultado(db, pago, resultado(pago)); aplicar_resultado(db, pago, r)
    assert vista_pago(db, pago)["pagado"]
    aplicar_resultado(db, pago, resultado(pago, "EXTORNADO"))
    aplicar_resultado(db, pago, resultado(pago))
    assert pago.estado == "EXTORNADO" and not vista_pago(db, pago)["pagado"]
    assert db.scalar(select(func.count()).select_from(TransaccionPaymePrueba)) == 1

def test_firma_cruda_y_webhook_idempotente(api, db, monkeypatch):
    llave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = llave.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    monkeypatch.setenv("PAYME_WEBHOOK_PUBLIC_KEY", pem)
    c, _ = api; body = entrada()
    c.post("/api/v1/pagos", json=body)
    pago = db.scalar(select(PagoTiendaPrueba)); raw = json.dumps(resultado(pago), indent=2).encode()
    firma = base64.b64encode(llave.sign(raw, padding.PKCS1v15(), hashes.SHA512())).decode()
    for _ in range(2):
        r = c.post("/api/v1/pagos/notificaciones", content=raw, headers={"signature": firma})
        assert r.status_code == 200, r.text
    assert vista_pago(db, pago)["pagado"]
    assert db.scalar(select(func.count()).select_from(TransaccionPaymePrueba)) == 1
    assert c.post("/api/v1/pagos/notificaciones", content=raw+b" ", headers={"signature": firma}).status_code == 401
    assert c.post("/api/v1/pagos/notificaciones", content=raw).status_code == 401

def test_llave_publicada_valida_y_firma_invalida(monkeypatch):
    monkeypatch.delenv("PAYME_WEBHOOK_PUBLIC_KEY", raising=False)
    assert serialization.load_pem_public_key(LLAVE_PREPROD.encode()).key_size == 2048
    with pytest.raises(ErrorAPI): verificar_firma(b"{}", "???")

def test_cliente_http_solo_preproduccion_y_cache():
    _cache.update(identidad=None, token=None, hasta=0)
    llamadas = []
    def responder(request):
        llamadas.append(request)
        assert request.headers["ALG-API-VERSION"] == "1709847567"
        if request.url.path == "/token":
            body = json.loads(request.content); assert body["client_secret"] == CONFIG.client_secret
            assert body["audience"] == "https://api.preprod.alignet.io/"
            return httpx.Response(200, json={"success": "true", "access_token": "token-privado", "expires_in": 3600})
        assert request.headers["Authorization"] == "Bearer token-privado"
        if request.url.path == "/nonce": return httpx.Response(200, json={"success": True, "nonce": "nonce"})
        return httpx.Response(200, json={"success": True})
    cliente = ClientePayme(CONFIG, httpx.MockTransport(responder))
    assert cliente.nonce() == "nonce"; assert cliente.nonce() == "nonce"
    cliente.consultar("merchant", "123456", "tx-1")
    assert sum(r.url.path == "/token" for r in llamadas) == 1
    assert {r.url.host for r in llamadas} == {"auth.preprod.alignet.io", "api.preprod.alignet.io"}
    assert all(r.url.path != "/charges" for r in llamadas)

def test_error_proveedor_no_filtra_secretos():
    cliente = ClientePayme(CONFIG, httpx.MockTransport(lambda r: httpx.Response(500, text="token-privado secreto-prueba")))
    with pytest.raises(ErrorAPI) as e: cliente._request("POST", "https://auth.preprod.alignet.io/token")
    assert "secreto-prueba" not in str(e.value) and "token-privado" not in str(e.value)
