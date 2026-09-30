"""Entrada HTTP del catálogo de ingredientes."""

from pydantic import BaseModel, Field


class CrearIngrediente(BaseModel):
    codigo: str = Field(min_length=1, max_length=160)
    nombre: str = Field(min_length=1, max_length=160)
    unidad_base: str


class CambiarIngrediente(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=160)
    unidad_base: str | None = None
    activo: bool | None = None
