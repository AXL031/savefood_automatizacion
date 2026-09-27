"""Dependencias públicas de identidad y autorización."""

import os

import jwt
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.modules.autenticacion.modelos import Usuario

seguridad = HTTPBearer(auto_error=False)


def identidad_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(seguridad),
    sesion: Session = Depends(obtener_sesion),
) -> Usuario:
    if credenciales is None or credenciales.scheme.lower() != "bearer":
        raise ErrorAPI(status.HTTP_401_UNAUTHORIZED, "AUTENTICACION_REQUERIDA", "Inicia sesión para continuar")
    try:
        payload = jwt.decode(credenciales.credentials, os.environ["JWT_SECRET"], algorithms=["HS256"])
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise ErrorAPI(status.HTTP_401_UNAUTHORIZED, "CREDENCIAL_INVALIDA", "Credencial inválida") from None
    usuario = sesion.get(Usuario, usuario_id)
    if not usuario or not usuario.activo:
        raise ErrorAPI(status.HTTP_401_UNAUTHORIZED, "USUARIO_NO_DISPONIBLE", "Usuario no disponible")
    return usuario


def requiere_administrador(usuario: Usuario = Depends(identidad_actual)) -> Usuario:
    if usuario.rol != "ADMINISTRADOR":
        raise ErrorAPI(status.HTTP_403_FORBIDDEN, "PERMISO_DENEGADO", "Se requiere administrador")
    return usuario
