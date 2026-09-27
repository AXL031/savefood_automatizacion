"""Entradas públicas de las programaciones demostrativas."""

from datetime import date, datetime, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator, model_validator


class ProgramarPropuesta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo: Literal["GENERAR_PROPUESTA"]
    ejecutar_desde_utc: datetime
    fecha_hora_simulada_local: datetime
    fecha_objetivo_demo: date
    producto_ids: list[PositiveInt] = Field(min_length=1, max_length=5)
    clave_idempotencia: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")

    @field_validator("ejecutar_desde_utc")
    @classmethod
    def validar_utc(cls, valor: datetime) -> datetime:
        if valor.tzinfo is None or valor.utcoffset() != timedelta(0):
            raise ValueError("El horario real debe incluir zona UTC")
        return valor

    @field_validator("fecha_hora_simulada_local")
    @classmethod
    def validar_hora_local(cls, valor: datetime) -> datetime:
        if valor.tzinfo is not None:
            raise ValueError("La hora simulada es local y no lleva zona")
        return valor

    @field_validator("producto_ids")
    @classmethod
    def validar_productos(cls, valor: list[int]) -> list[int]:
        if len(valor) != len(set(valor)):
            raise ValueError("No repitas productos en la programación")
        return sorted(valor)

    @model_validator(mode="after")
    def validar_dia_simulado(self):
        if self.fecha_hora_simulada_local.date() != self.fecha_objetivo_demo:
            raise ValueError("La fecha objetivo y el día del reloj simulado deben coincidir")
        return self
