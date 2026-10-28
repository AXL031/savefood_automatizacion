"""Entradas estrictas para caja. Los importes se reciben como texto decimal exacto."""
import re
from decimal import Decimal
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

Clave = Annotated[str, Field(min_length=8, max_length=80, pattern=r"^[A-Za-z0-9._:-]+$")]
Id = Annotated[int, Field(gt=0, strict=True)]


class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Importes(Entrada):
    @field_validator("*", mode="before")
    @classmethod
    def dinero(cls, v, info):
        if info.field_name in {"precio", "total_revisado", "importe_recibido"}:
            if not isinstance(v, str) or not re.fullmatch(r"\d{1,6}\.\d{2}", v) or Decimal(v) <= 0:
                raise ValueError("Usa un importe positivo con dos decimales, por ejemplo 12.50.")
            return f"{Decimal(v):.2f}"
        return v


class PrecioCrear(Importes):
    clave_idempotencia: Clave
    precio: str
    version_actual: Annotated[int, Field(ge=0, strict=True)]


class LineaCotizar(Entrada):
    producto_id: Id
    cantidad: Annotated[int, Field(ge=1, le=1000, strict=True)]


class CotizarVenta(Entrada):
    clave_idempotencia: Clave
    lineas: list[LineaCotizar] = Field(min_length=1, max_length=100)

    @field_validator("lineas")
    @classmethod
    def unicas(cls, v):
        if len({l.producto_id for l in v}) != len(v):
            raise ValueError("No repitas productos en la venta.")
        return sorted(v, key=lambda l: l.producto_id)


class CobroPresencial(Importes):
    medio: Literal["EFECTIVO", "TARJETA", "YAPE", "QR", "PAGOEFECTIVO"]
    importe_recibido: str


class RegistrarVenta(Importes):
    clave_idempotencia: Clave
    cotizacion_id: Annotated[str, Field(min_length=36, max_length=36)]
    total_revisado: str
    cobro_presencial: CobroPresencial


class AnularVenta(Entrada):
    clave_idempotencia: Clave
    motivo: str = Field(min_length=3, max_length=300)
    mercancia_no_entregada: Literal[True]

    @field_validator("mercancia_no_entregada", mode="before")
    @classmethod
    def confirmar(cls, v):
        if v is not True:
            raise ValueError("Confirma que la mercancía no fue entregada.")
        return v

    @field_validator("motivo")
    @classmethod
    def limpiar(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Indica un motivo de al menos tres caracteres.")
        return v.strip()
