"""T02: sesión de clientes con Google. Ninguna prueba llama a Google."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from test_api_inicializacion_ventas import cabecera, cliente, token  # noqa: F401

from app.core.errores import ErrorAPI
from app.modules.tienda import autenticacion
from app.modules.tienda.autenticacion import obtener_verificador, verificar_con_google

RUTA = "/api/v1/tienda/sesion"
TOKEN_FALSO = "x" * 40


def claims(**cambios):
    return {"sub": "google-123", "email": "Maria.Rojas@gmail.com", "email_verified": True, "name": "María Rojas", **cambios}


def con_claims(cliente_http, valor):
    cliente_http.app.dependency_overrides[obtener_verificador] = lambda: (lambda _token: valor)


def test_login_crea_cliente_y_token_solo_vale_en_la_tienda(cliente):
    con_claims(cliente, claims())
    respuesta = cliente.post(f"{RUTA}/google", json={"id_token": TOKEN_FALSO})
    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()["datos"]
    assert datos["cliente"]["correo"] == "maria.rojas@gmail.com" and datos["cliente"]["nombre"] == "María Rojas"
    tienda = cabecera(datos["token"])
    assert cliente.get(RUTA, headers=tienda).json()["datos"]["id"] == datos["cliente"]["id"]
    # El token de cliente no abre rutas administrativas y el administrativo no abre la tienda.
    assert cliente.get("/api/v1/usuarios", headers=tienda).status_code == 401
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    assert cliente.get(RUTA, headers=admin).status_code == 401
    assert cliente.get(RUTA).status_code == 401

    # Segundo acceso: mismo cliente, datos actualizados, sin duplicar.
    con_claims(cliente, claims(name="María E. Rojas"))
    otra = cliente.post(f"{RUTA}/google", json={"id_token": TOKEN_FALSO}).json()["datos"]
    assert otra["cliente"]["id"] == datos["cliente"]["id"] and otra["cliente"]["nombre"] == "María E. Rojas"
    cliente.app.dependency_overrides.pop(obtener_verificador)


def test_rechaza_correo_no_verificado_y_entrada_extra(cliente):
    con_claims(cliente, claims(email_verified=False))
    fallo = cliente.post(f"{RUTA}/google", json={"id_token": TOKEN_FALSO})
    assert fallo.status_code == 403 and fallo.json()["error"]["codigo"] == "CORREO_NO_VERIFICADO"
    assert cliente.post(f"{RUTA}/google", json={"id_token": TOKEN_FALSO, "correo": "x@gmail.com"}).status_code == 422
    cliente.app.dependency_overrides.pop(obtener_verificador)


def test_sin_client_id_responde_no_configurado(cliente, monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    fallo = cliente.post(f"{RUTA}/google", json={"id_token": TOKEN_FALSO})
    assert fallo.status_code == 503 and fallo.json()["error"]["codigo"] == "GOOGLE_NO_CONFIGURADO"


@pytest.fixture
def google_local(monkeypatch):
    """Claves RSA locales en lugar de las públicas de Google."""
    privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cliente-de-prueba.apps.googleusercontent.com")
    monkeypatch.setattr(autenticacion, "_cliente_jwks", lambda: SimpleNamespace(
        get_signing_key_from_jwt=lambda _t: SimpleNamespace(key=privada.public_key())))

    def firmar(**cambios):
        ahora = datetime.now(timezone.utc)
        datos = {"iss": "https://accounts.google.com", "aud": "cliente-de-prueba.apps.googleusercontent.com",
                 "iat": ahora, "exp": ahora + timedelta(minutes=5), **claims(), **cambios}
        return jwt.encode(datos, privada, algorithm="RS256")
    return firmar


def test_verificacion_de_firma_audiencia_emisor_y_vigencia(google_local):
    assert verificar_con_google(google_local())["sub"] == "google-123"
    for invalido in (google_local(aud="otra-app"), google_local(iss="https://otro.example"),
                     google_local(exp=datetime.now(timezone.utc) - timedelta(minutes=1))):
        with pytest.raises(ErrorAPI) as error:
            verificar_con_google(invalido)
        assert error.value.codigo == "GOOGLE_TOKEN_INVALIDO"


def test_cors_tienda_independiente(cliente):
    respuesta = cliente.options(RUTA + "/google", headers={
        "Origin": "http://localhost:3101", "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type"})
    assert respuesta.status_code == 200
    assert respuesta.headers["access-control-allow-origin"] == "http://localhost:3101"
    assert "access-control-allow-credentials" not in respuesta.headers
    ajeno = cliente.options(RUTA + "/google", headers={
        "Origin": "https://ajeno.example", "Access-Control-Request-Method": "POST"})
    assert ajeno.status_code == 400
