"""Entradas públicas del checkout de Payme; nunca reciben tarjetas ni montos libres."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, UUID4, model_validator

MetodoPayme = Literal["CARD", "YAPE", "QR", "PAGOEFECTIVO"]


class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class LineaPago(Entrada):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(strict=True, ge=1, le=20)


class CotizarPago(Entrada):
    lineas: list[LineaPago] = Field(min_length=1, max_length=30)
    origen_catalogo: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def sin_repetidos(self):
        if len({l.producto_id for l in self.lineas}) != len(self.lineas):
            raise ValueError("No repitas productos en la canasta.")
        return self


class CompradorPago(Entrada):
    nombres: str = Field(min_length=2, max_length=80)
    apellidos: str = Field(min_length=2, max_length=80)
    correo: EmailStr


class EntregaPago(Entrada):
    nombre_receptor: str = Field(min_length=3, max_length=120)
    celular: str = Field(pattern=r"^9\d{8}$")
    direccion: str = Field(min_length=5, max_length=200)
    distrito: str = Field(min_length=2, max_length=80)
    referencia: str = Field(default="", max_length=200)


class CrearPago(CotizarPago):
    clave_checkout: UUID4
    metodo: MetodoPayme
    comprador: CompradorPago
    entrega: EntregaPago
    cotizacion_hash: str | None = Field(default=None, pattern=r'^[a-f0-9]{64}$')
    total_revisado: str | None = Field(default=None, pattern=r'^\d{1,6}\.\d{2}$')


class VerificarPago(Entrada):
    transaction_id: str | None = Field(default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")
