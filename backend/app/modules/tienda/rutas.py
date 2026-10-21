"""Rutas del cliente de la tienda: /api/v1/tienda/*."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.modules.tienda.autenticacion import (
    VerificadorGoogle, cliente_actual, emitir_token_cliente, iniciar_sesion_google, obtener_verificador,
)
from app.modules.tienda.modelos import ClienteTienda

router = APIRouter(prefix="/tienda", tags=["tienda"])


class EntradaGoogle(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_token: str = Field(min_length=20, max_length=4096)


def _cliente(cliente: ClienteTienda) -> dict:
    return {"id": cliente.id, "correo": cliente.correo, "nombre": cliente.nombre}


@router.post("/sesion/google")
def sesion_google(entrada: EntradaGoogle, verificar: VerificadorGoogle = Depends(obtener_verificador),
                  sesion: Session = Depends(obtener_sesion)):
    claims = verificar(entrada.id_token)
    try:
        cliente = iniciar_sesion_google(sesion, claims)
        sesion.commit()
    except IntegrityError:
        # Dos primeros accesos simultáneos de la misma cuenta: el segundo reutiliza el registro.
        sesion.rollback()
        cliente = iniciar_sesion_google(sesion, claims)
        sesion.commit()
    return {"datos": {"token": emitir_token_cliente(cliente), "cliente": _cliente(cliente)}}


@router.get("/sesion")
def sesion_actual(cliente: ClienteTienda = Depends(cliente_actual)):
    return {"datos": _cliente(cliente)}
