"""Entrada HTTP de recetas."""

from decimal import Decimal

from pydantic import BaseModel, Field


class LineaEntrada(BaseModel):
    ingrediente_id: int
    # Se recibe como texto o número; el servicio valida >0 y hasta 3 decimales.
    cantidad_por_unidad: Decimal


class NuevaVersion(BaseModel):
    motivo: str = Field(min_length=3, max_length=300)
    lineas: list[LineaEntrada] = Field(min_length=1, max_length=100)
