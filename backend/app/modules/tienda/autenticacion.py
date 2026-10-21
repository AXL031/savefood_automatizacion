"""T02: verificación del ID token de Google y token propio de cliente.

El token de cliente usa una clave distinta de la administrativa y la audiencia
`tienda`: no sirve en rutas del administrador y un token administrativo no sirve aquí.
"""

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Callable

import jwt
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.modules.tienda.modelos import ClienteTienda

AUDIENCIA = "tienda"
DURACION = timedelta(hours=8)
EMISORES_GOOGLE = ("https://accounts.google.com", "accounts.google.com")
CLAVES_GOOGLE = "https://www.googleapis.com/oauth2/v3/certs"

VerificadorGoogle = Callable[[str], dict]


def _clave_tienda() -> str:
    explicita = os.getenv("TIENDA_JWT_SECRET")
    if explicita:
        return explicita
    # Derivada de JWT_SECRET para no exigir otra variable; nunca igual a la administrativa.
    return hmac.new(os.environ["JWT_SECRET"].encode(), b"foodsave-tienda-clientes", hashlib.sha256).hexdigest()


@lru_cache(maxsize=1)
def _cliente_jwks() -> jwt.PyJWKClient:
    return jwt.PyJWKClient(CLAVES_GOOGLE, cache_keys=True, lifespan=3600, timeout=10)


def verificar_con_google(id_token: str) -> dict:
    """Valida firma, audiencia, emisor y vigencia con las claves públicas de Google."""
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    if not client_id:
        raise ErrorAPI(status.HTTP_503_SERVICE_UNAVAILABLE, "GOOGLE_NO_CONFIGURADO", "El inicio de sesión con Google no está configurado.")
    try:
        clave = _cliente_jwks().get_signing_key_from_jwt(id_token).key
    except jwt.PyJWKClientConnectionError:
        raise ErrorAPI(status.HTTP_503_SERVICE_UNAVAILABLE, "GOOGLE_NO_DISPONIBLE", "No pudimos comunicarnos con Google. Inténtalo otra vez.") from None
    except jwt.PyJWTError:
        raise ErrorAPI(status.HTTP_401_UNAUTHORIZED, "GOOGLE_TOKEN_INVALIDO", "La credencial de Google no es válida.") from None
    try:
        return jwt.decode(id_token, clave, algorithms=["RS256"], audience=client_id, issuer=EMISORES_GOOGLE,
                          options={"require": ["exp", "iat", "sub", "aud", "iss"]})
    except jwt.PyJWTError:
        raise ErrorAPI(status.HTTP_401_UNAUTHORIZED, "GOOGLE_TOKEN_INVALIDO", "La credencial de Google no es válida o venció.") from None


def obtener_verificador() -> VerificadorGoogle:
    """Dependencia sustituible en pruebas; producción siempre consulta a Google."""
    return verificar_con_google


def iniciar_sesion_google(sesion: Session, claims: dict) -> ClienteTienda:
    """Crea o actualiza el cliente por `sub`. No confirma la sesión."""
    if claims.get("email_verified") is not True:
        raise ErrorAPI(status.HTTP_403_FORBIDDEN, "CORREO_NO_VERIFICADO", "Tu cuenta de Google no tiene el correo verificado.")
    correo = str(claims.get("email", "")).strip().lower()
    if not correo:
        raise ErrorAPI(status.HTTP_403_FORBIDDEN, "CORREO_NO_VERIFICADO", "Google no compartió tu correo.")
    nombre = (str(claims.get("name") or "").strip() or correo.split("@")[0])[:160]
    cliente = sesion.scalar(select(ClienteTienda).where(ClienteTienda.google_sub == str(claims["sub"])).with_for_update())
    ahora = datetime.now(timezone.utc)
    if cliente is None:
        cliente = ClienteTienda(google_sub=str(claims["sub"]), correo=correo, nombre=nombre, activo=True, creado_en=ahora, ultimo_acceso_en=ahora)
        sesion.add(cliente)
    else:
        if not cliente.activo:
            raise ErrorAPI(status.HTTP_403_FORBIDDEN, "CLIENTE_INACTIVO", "Tu cuenta de cliente está desactivada.")
        cliente.correo, cliente.nombre, cliente.ultimo_acceso_en = correo, nombre, ahora
    sesion.flush()
    return cliente


def emitir_token_cliente(cliente: ClienteTienda) -> str:
    ahora = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(cliente.id), "aud": AUDIENCIA, "iat": ahora, "exp": ahora + DURACION}, _clave_tienda(), algorithm="HS256")


_portador = HTTPBearer(auto_error=False)


def cliente_actual(credenciales: HTTPAuthorizationCredentials | None = Depends(_portador),
                   sesion: Session = Depends(obtener_sesion)) -> ClienteTienda:
    if credenciales is None or credenciales.scheme.lower() != "bearer":
        raise ErrorAPI(status.HTTP_401_UNAUTHORIZED, "AUTENTICACION_REQUERIDA", "Inicia sesión con Google para continuar.")
    try:
        datos = jwt.decode(credenciales.credentials, _clave_tienda(), algorithms=["HS256"], audience=AUDIENCIA)
        cliente_id = int(datos["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise ErrorAPI(status.HTTP_401_UNAUTHORIZED, "AUTENTICACION_REQUERIDA", "Tu sesión venció. Vuelve a iniciar sesión.") from None
    cliente = sesion.get(ClienteTienda, cliente_id)
    if cliente is None or not cliente.activo:
        raise ErrorAPI(status.HTTP_401_UNAUTHORIZED, "AUTENTICACION_REQUERIDA", "Tu sesión ya no es válida. Vuelve a iniciar sesión.")
    return cliente
