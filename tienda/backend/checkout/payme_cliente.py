"""Payme Flex, SOLO preproducción. No recibe PAN/CVV ni ejecuta POST /charges."""
import base64
import hashlib
import os
import threading
import time
from dataclasses import dataclass
from urllib.parse import quote

import httpx
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from .errores import ErrorAPI

AUTH = "https://auth.preprod.alignet.io"
API = "https://api.preprod.alignet.io/"
SDK_JS = "https://flex.dev.pay-me.cloud/flex-payment-forms.min.js"
SDK_CSS = "https://flex.dev.pay-me.cloud/main-flex-payment-forms.css"
VERSION = "1709847567"
METODOS = ("CARD", "YAPE", "QR", "PAGOEFECTIVO")
# Llave PÚBLICA de preproducción publicada en /payin/notificaciones (21-10-2026).
LLAVE_PREPROD = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkmpsqcJzjQ45u0K7JOQJ
tfjXGeMXNwsaU6JDGSdKwSDGGXt1m551p2mlG0oGkmn9FPbp4E0lOQzkL/qhHB1Y
pTP2MqecJ7pMTonEeXOv0P6uwR9yvV5lxK17nE3+xgfcpFfxT5GAI/wZsQJ3+Lsv
qh3+IcRG2Hb2BUdM5pYZFOUBGGSZWc/ULPtsFx2DSjI9peJ9kYibpaokphP+Cypz
/LgKV7Yiv/TUufPiUk5gFYIad5VhRU822sTMRQ7BgS2CY4t49jqFkIiRnmPwM8fF
KjPD4wvzssrqbAQvkk56XOcE9ML0iJhcIY1/xgNSiHqij0Ql1UTU5nAIJR5/paOn
hQIDAQAB
-----END PUBLIC KEY-----"""


@dataclass(frozen=True)
class ConfigPayme:
    habilitado: bool
    client_id: str
    client_secret: str
    merchant_code: str

    @property
    def listo(self):
        return self.habilitado and all((self.client_id, self.client_secret, self.merchant_code))

    def exigir(self):
        if not self.listo:
            raise ErrorAPI(503, "PAYME_NO_CONFIGURADO", "Los pagos de prueba todavía no están configurados.")


def configuracion():
    return ConfigPayme(os.getenv("PAYME_HABILITADO", "false").lower() == "true",
                       os.getenv("PAYME_CLIENT_ID", "").strip(), os.getenv("PAYME_CLIENT_SECRET", "").strip(),
                       os.getenv("PAYME_MERCHANT_CODE", "").strip())


_lock = threading.Lock()
_cache = {"identidad": None, "token": None, "hasta": 0}


class ClientePayme:
    def __init__(self, config: ConfigPayme, transporte=None):
        self.config, self.transporte = config, transporte

    def _request(self, metodo, url, **kwargs):
        try:
            with httpx.Client(timeout=httpx.Timeout(10, connect=5), follow_redirects=False,
                              trust_env=False, transport=self.transporte) as cliente:
                respuesta = cliente.request(metodo, url, **kwargs)
                respuesta.raise_for_status()
                datos = respuesta.json()
            if not isinstance(datos, dict):
                raise ValueError("Respuesta inválida")
            return datos
        except (httpx.HTTPError, ValueError):
            # Nunca propagar cuerpo, URL de error, Authorization o credenciales.
            raise ErrorAPI(502, "PAYME_NO_DISPONIBLE", "No se pudo completar la comunicación con Payme de pruebas. Revisa el estado antes de volver a pagar.") from None

    def token(self):
        self.config.exigir()
        identidad = hashlib.sha256((self.config.client_id + "\0" + self.config.client_secret).encode()).hexdigest()
        with _lock:
            if _cache["identidad"] == identidad and _cache["hasta"] > time.monotonic():
                return _cache["token"]
            datos = self._request("POST", AUTH + "/token", headers={"ALG-API-VERSION": VERSION}, json={
                "action": "authorize", "grant_type": "client_credentials", "audience": API,
                "client_id": self.config.client_id, "client_secret": self.config.client_secret,
                "scope": "create:token post:charges get:charges"})
            if datos.get("success") not in (True, "true") or not isinstance(datos.get("access_token"), str):
                raise ErrorAPI(502, "PAYME_AUTENTICACION", "Payme no aceptó las credenciales de pruebas.")
            try:
                duracion = max(0, min(int(datos.get("expires_in", 0)) - 30, 3600))
            except (TypeError, ValueError):
                duracion = 0
            _cache.update(identidad=identidad, token=datos["access_token"], hasta=time.monotonic() + duracion)
            return datos["access_token"]

    def headers(self):
        return {"Authorization": "Bearer " + self.token(), "ALG-API-VERSION": VERSION}

    def nonce(self):
        datos = self._request("POST", AUTH + "/nonce", headers=self.headers(), json={
            "action": "create.nonce", "audience": API, "client_id": self.config.client_id, "scope": "post:charges"})
        if datos.get("success") not in (True, "true") or not isinstance(datos.get("nonce"), str) or not datos["nonce"]:
            raise ErrorAPI(502, "PAYME_NONCE", "No se pudo preparar el formulario de Payme de pruebas.")
        return datos["nonce"]

    def consultar(self, merchant, operacion, transaction_id):
        ruta = "/".join(quote(str(x), safe="") for x in (merchant, operacion, transaction_id))
        return self._request("GET", API + "charges/" + ruta, headers=self.headers())


def obtener_cliente_payme():
    return ClientePayme(configuracion())


def verificar_firma(raw: bytes, firma: str):
    try:
        pem = os.getenv("PAYME_WEBHOOK_PUBLIC_KEY", "").replace("\\n", "\n").strip() or LLAVE_PREPROD
        llave = serialization.load_pem_public_key(pem.encode())
        if not isinstance(llave, rsa.RSAPublicKey):
            raise ValueError("Llave inválida")
        llave.verify(base64.b64decode(firma, validate=True), raw, padding.PKCS1v15(), hashes.SHA512())
    except (ValueError, TypeError, InvalidSignature):
        raise ErrorAPI(401, "PAYME_FIRMA_INVALIDA", "La firma de la notificación no es válida.") from None
