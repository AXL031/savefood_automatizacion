"""Dependencias públicas de identidad y autorización."""

import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.modules.autenticacion.modelos import Usuario

seguridad = HTTPBearer()


def identidad_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(seguridad),
    sesion: Session = Depends(obtener_sesion),
) -> Usuario:
    try:
        payload = jwt.decode(credenciales.credentials, os.environ["JWT_SECRET"], algorithms=["HS256"])
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credencial inválida") from None
    usuario = sesion.get(Usuario, usuario_id)
    if not usuario or not usuario.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no disponible")
    return usuario


def requiere_administrador(usuario: Usuario = Depends(identidad_actual)) -> Usuario:
    if usuario.rol != "ADMINISTRADOR":
        raise HTTPException(status_code=403, detail="Se requiere administrador")
    return usuario
