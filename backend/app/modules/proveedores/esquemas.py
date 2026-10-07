"""Entrada/salida y validación."""
from decimal import Decimal
from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProveedorCrear(BaseModel):
    codigo: str = Field(min_length=1, max_length=30)
    nombre: str = Field(min_length=1, max_length=120)
    chat_id_pruebas: str | None = Field(default=None, min_length=1, max_length=64)
    activo: bool = True

    @field_validator("chat_id_pruebas")
    @classmethod
    def _chat_numerico(cls, valor: str | None) -> str | None:
        if valor is None:
            return valor
        valor = valor.strip()
        if not re.fullmatch(r"-?[1-9][0-9]{0,18}", valor):
            raise ValueError("usa el identificador numérico del chat de pruebas")
        return valor

    @field_validator("codigo", "nombre")
    @classmethod
    def _sin_espacios(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("no puede estar vacío")
        return v


class ProveedorSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    nombre: str
    activo: bool
    chat_id_pruebas: str | None
    destino_verificado: bool
    destino_verificado_en: datetime | None


class OfertaCrear(BaseModel):
    """factor_conversion es obligatorio: nunca se infiere del nombre de la unidad."""
    ingrediente_id: int = Field(gt=0)
    descripcion: str = Field(min_length=1, max_length=120)
    unidad_compra: str = Field(min_length=1, max_length=30)
    factor_conversion: Decimal = Field(gt=0, max_digits=14, decimal_places=4)
    minimo: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=4)
    multiplo: Decimal = Field(default=Decimal("1"), gt=0, max_digits=14, decimal_places=4)
    preferida: bool = False

    @field_validator("descripcion", "unidad_compra")
    @classmethod
    def _texto_oferta(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("no puede estar vacío")
        return valor


class OfertaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    proveedor_id: int
    ingrediente_id: int
    descripcion: str
    unidad_compra: str
    factor_conversion: Decimal
    minimo: Decimal
    multiplo: Decimal
    activa: bool
    preferida: bool


class OfertaPreferidaCompras(BaseModel):
    """Contrato publicado para Compras."""
    oferta_id: int
    proveedor_id: int
    proveedor_codigo: str
    proveedor_nombre: str
    proveedor_activo: bool
    chat_id_pruebas: str | None
    destino_verificado: bool
    ingrediente_id: int
    unidad_compra: str
    factor_conversion: Decimal
    minimo: Decimal
    multiplo: Decimal
    compra_automatica_habilitada: bool
    motivo_bloqueo: str | None = None


class VerificacionDestino(BaseModel):
    verificado: bool
    detalle: str
    codigo: str = "DESTINO_NO_VERIFICADO"
