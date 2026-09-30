"""Cuerpos de solicitud del módulo de ventas."""

from pydantic import BaseModel, Field


class CorregirVenta(BaseModel):
    """Corrección de una venta diaria. El motivo es obligatorio y queda auditado."""

    unidades_vendidas: int = Field(ge=0)
    motivo: str = Field(min_length=3, max_length=255)
