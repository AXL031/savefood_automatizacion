"""Gestión administrativa de cuentas; el llamador confirma la transacción."""
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.core.identidad import requiere_administrador
from app.modules.autenticacion.modelos import Usuario

Rol = Literal["ADMINISTRADOR", "OPERADOR"]
router = APIRouter(prefix="/usuarios", tags=["usuarios"])
_password = PasswordHash.recommended()


class CrearUsuario(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str = Field(min_length=1, max_length=160)
    correo: EmailStr = Field(max_length=254)
    contrasena: str = Field(min_length=8, max_length=128)
    rol: Rol

    @field_validator("nombre", "correo")
    @classmethod
    def limpiar(cls, valor):
        valor = valor.strip()
        if not valor:
            raise ValueError("El campo es obligatorio.")
        return valor

    @field_validator("contrasena")
    @classmethod
    def clave_no_vacia(cls, valor):
        if not valor.strip():
            raise ValueError("La contraseña no puede contener solo espacios.")
        return valor


class EditarUsuario(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str | None = Field(None, min_length=1, max_length=160)
    correo: EmailStr | None = Field(None, max_length=254)
    rol: Rol | None = None
    activo: bool | None = None

    @model_validator(mode="after")
    def cambios_validos(self):
        if not self.model_fields_set or any(getattr(self, campo) is None for campo in self.model_fields_set):
            raise ValueError("Indica al menos un cambio; no se admiten valores nulos.")
        if "nombre" in self.model_fields_set:
            self.nombre = self.nombre.strip()
            if not self.nombre:
                raise ValueError("El nombre no puede quedar vacío.")
        return self


def _vista(usuario):
    return {"id": usuario.id, "nombre": usuario.nombre, "correo": usuario.correo,
            "rol": usuario.rol, "activo": usuario.activo,
            "creado_en": usuario.creado_en.isoformat()}


def _bloquear_y_autorizar(sesion, actor_id):
    # Todos los cambios de roles/estado toman los mismos locks en el mismo orden.
    usuarios = list(sesion.scalars(select(Usuario).order_by(Usuario.id).with_for_update()
                                  .execution_options(populate_existing=True)))
    actor = next((u for u in usuarios if u.id == actor_id), None)
    if actor is None or not actor.activo or actor.rol != "ADMINISTRADOR":
        raise ErrorAPI(403, "PERMISO_DENEGADO", "Se requiere un administrador activo.")
    return usuarios


def crear_usuario(sesion: Session, actor_id: int, entrada: CrearUsuario) -> dict:
    _bloquear_y_autorizar(sesion, actor_id)
    try:
        with sesion.begin_nested():
            usuario = Usuario(nombre=entrada.nombre, correo=str(entrada.correo).lower(),
                              hash_contrasena=_password.hash(entrada.contrasena), rol=entrada.rol, activo=True)
            sesion.add(usuario)
            sesion.flush()
    except IntegrityError:
        raise ErrorAPI(409, "CORREO_DUPLICADO", "Ya existe una cuenta con ese correo.") from None
    return _vista(usuario)


def editar_usuario(sesion: Session, actor_id: int, usuario_id: int, entrada: EditarUsuario) -> dict:
    usuarios = _bloquear_y_autorizar(sesion, actor_id)
    usuario = next((u for u in usuarios if u.id == usuario_id), None)
    if usuario is None:
        raise ErrorAPI(404, "USUARIO_NO_ENCONTRADO", "El usuario no existe.")
    cambios = entrada.model_dump(exclude_unset=True)
    if "correo" in cambios:
        cambios["correo"] = str(cambios["correo"]).lower()
    activo, rol = cambios.get("activo", usuario.activo), cambios.get("rol", usuario.rol)
    if usuario.activo and usuario.rol == "ADMINISTRADOR" and (not activo or rol != "ADMINISTRADOR"):
        if not any(u.id != usuario.id and u.activo and u.rol == "ADMINISTRADOR" for u in usuarios):
            raise ErrorAPI(409, "ULTIMO_ADMINISTRADOR", "Debe permanecer al menos un administrador activo.")
    try:
        with sesion.begin_nested():
            for campo, valor in cambios.items():
                setattr(usuario, campo, valor)
            sesion.flush()
    except IntegrityError:
        raise ErrorAPI(409, "CORREO_DUPLICADO", "Ya existe una cuenta con ese correo.") from None
    return _vista(usuario)


@router.get("")
def listar(_admin: Usuario = Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    return {"datos": [_vista(u) for u in sesion.scalars(select(Usuario).order_by(Usuario.id))]}


@router.post("", status_code=201)
def crear(entrada: CrearUsuario, admin: Usuario = Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    vista = crear_usuario(sesion, admin.id, entrada)
    sesion.commit()
    return {"datos": vista}


@router.patch("/{usuario_id}")
def editar(usuario_id: int, entrada: EditarUsuario, admin: Usuario = Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    vista = editar_usuario(sesion, admin.id, usuario_id, entrada)
    sesion.commit()
    return {"datos": vista}
