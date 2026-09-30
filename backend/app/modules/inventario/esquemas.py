"""Entrada HTTP del inventario."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class AjusteEntrada(BaseModel):
    tipo: Literal["producto", "ingrediente"]
    lote_id: int
    # Positivo suma, negativo resta. Producto: entero; ingrediente: hasta 3 decimales.
    delta: Decimal
    motivo: str = Field(min_length=3, max_length=300)
    clave_operacion: str = Field(min_length=1, max_length=200)
    # Hora local del escenario simulado, sin zona: p. ej. "2022-08-24T17:45:00".
    efectivo_en_demo: datetime
