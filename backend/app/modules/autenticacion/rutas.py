import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.modules.autenticacion.modelos import Usuario

router = APIRouter(prefix="/autenticacion", tags=["autenticacion"])
seguridad = HTTPBearer()
password_hash = PasswordHash.recommended()


class Credenciales(BaseModel):
    correo: EmailStr
    contrasena: str


class Perfil(BaseModel):
    id: int
    correo: str
    nombre: str
    rol: str


def usuario_actual(
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


@router.post("/iniciar-sesion")
def iniciar_sesion(datos: Credenciales, sesion: Session = Depends(obtener_sesion)):
    usuario = sesion.scalar(select(Usuario).where(Usuario.correo == datos.correo.lower()))
    if not usuario or not usuario.activo or not password_hash.verify(datos.contrasena, usuario.hash_contrasena):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    expira = datetime.now(timezone.utc) + timedelta(minutes=30)
    token = jwt.encode({"sub": str(usuario.id), "exp": expira}, os.environ["JWT_SECRET"], algorithm="HS256")
    return {"datos": {"token_acceso": token, "tipo": "bearer", "expira_en": expira.isoformat()}}


@router.get("/mi-perfil")
def mi_perfil(usuario: Usuario = Depends(usuario_actual)):
    return {"datos": Perfil.model_validate(usuario, from_attributes=True).model_dump()}
