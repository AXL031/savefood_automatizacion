from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.core.identidad import identidad_actual, requiere_administrador
from app.modules.negocios.modelos import Negocio
from app.modules.negocios.servicio import ModoEnvio

router = APIRouter(prefix="/negocios", tags=["negocios"])


class CambioNegocio(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, min_length=1, max_length=160)
    zona_horaria: str | None = Field(default=None, min_length=1, max_length=80)
    moneda: str | None = Field(default=None, min_length=3, max_length=3)
    modo_envio_pedidos: ModoEnvio | None = None

    @field_validator("nombre", "zona_horaria", "moneda", mode="before")
    @classmethod
    def limpiar_texto(cls, valor: str | None) -> str | None:
        return valor.strip() if isinstance(valor, str) else valor

    @field_validator("zona_horaria")
    @classmethod
    def validar_zona_horaria(cls, valor: str | None) -> str | None:
        if valor is not None:
            try:
                ZoneInfo(valor)
            except (ZoneInfoNotFoundError, ValueError) as exc:
                raise ValueError("Usa una zona horaria IANA válida, por ejemplo America/Lima") from exc
        return valor

    @field_validator("moneda")
    @classmethod
    def validar_moneda(cls, valor: str | None) -> str | None:
        if valor is not None and (len(valor) != 3 or not valor.isascii() or not valor.isalpha() or not valor.isupper()):
            raise ValueError("Usa un código de moneda de tres letras mayúsculas, por ejemplo PEN")
        return valor

    @model_validator(mode="after")
    def validar_cambios(self):
        if not self.model_fields_set or any(getattr(self, campo) is None for campo in self.model_fields_set):
            raise ValueError("Envía al menos un campo y no uses valores nulos")
        return self


def serializar(negocio: Negocio):
    return {
        "id": negocio.id,
        "nombre": negocio.nombre,
        "zona_horaria": negocio.zona_horaria,
        "moneda": negocio.moneda,
        "modo_envio_pedidos": negocio.modo_envio_pedidos,
    }


@router.get("/actual")
def negocio_actual(_usuario=Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    negocio = sesion.get(Negocio, 1)
    if not negocio:
        raise ErrorAPI(503, "NEGOCIO_NO_CONFIGURADO", "Falta aplicar la migración inicial")
    return {"datos": serializar(negocio)}


@router.patch("/actual")
def actualizar_negocio(
    datos: CambioNegocio,
    _usuario=Depends(requiere_administrador),
    sesion: Session = Depends(obtener_sesion),
):
    negocio = sesion.get(Negocio, 1)
    if not negocio:
        raise ErrorAPI(503, "NEGOCIO_NO_CONFIGURADO", "Falta aplicar la migración inicial")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(negocio, campo, valor)
    sesion.commit()
    return {"datos": serializar(negocio)}
