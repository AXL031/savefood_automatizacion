import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.core.identidad import identidad_actual
from app.modules.autenticacion.modelos import Usuario

router = APIRouter(prefix="/autenticacion", tags=["autenticacion"])
password_hash = PasswordHash.recommended()


class Credenciales(BaseModel):
    correo: EmailStr
    contrasena: str


class Perfil(BaseModel):
    id: int
    correo: str
    nombre: str
    rol: str


@router.post("/iniciar-sesion")
def iniciar_sesion(datos: Credenciales, sesion: Session = Depends(obtener_sesion)):
    usuario = sesion.scalar(select(Usuario).where(Usuario.correo == datos.correo.lower()))
    if not usuario or not usuario.activo or not password_hash.verify(datos.contrasena, usuario.hash_contrasena):
        raise ErrorAPI(status.HTTP_401_UNAUTHORIZED, "CREDENCIALES_INVALIDAS", "Credenciales inválidas")
    expira = datetime.now(timezone.utc) + timedelta(minutes=30)
    token = jwt.encode({"sub": str(usuario.id), "exp": expira}, os.environ["JWT_SECRET"], algorithm="HS256")
    return {"datos": {"token_acceso": token, "tipo": "bearer", "expira_en": expira.isoformat()}}


@router.get("/mi-perfil")
def mi_perfil(usuario: Usuario = Depends(identidad_actual)):
    return {"datos": Perfil.model_validate(usuario, from_attributes=True).model_dump()}
