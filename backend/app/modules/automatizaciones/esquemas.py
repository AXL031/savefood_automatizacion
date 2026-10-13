"""Entradas públicas de las programaciones demostrativas."""

from datetime import date, datetime, time, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator, model_validator


class ProgramarPropuesta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo: Literal["GENERAR_PROPUESTA"]
    ejecutar_desde_utc: datetime
    fecha_hora_simulada_local: datetime
    fecha_objetivo_demo: date
    producto_ids: list[PositiveInt] = Field(min_length=1, max_length=5)
    modo_envio_pedidos: Literal["REQUIERE_APROBACION", "AUTOMATICO"] | None = None
    modelo_id: PositiveInt | None = None
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


class ConfigurarFlujo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    producto_ids: list[PositiveInt] = Field(min_length=1, max_length=5)
    modelo_id: PositiveInt | None = None
    fecha_objetivo_demo: date
    hora_simulada: time = time(10)
    primera_ejecucion_local: datetime
    dias: int = Field(default=1, ge=1, le=31)
    modo_envio_pedidos: Literal["REQUIERE_APROBACION", "AUTOMATICO"] = "REQUIERE_APROBACION"

    @model_validator(mode="after")
    def validar(self):
        if len(set(self.producto_ids)) != len(self.producto_ids):
            raise ValueError("No repitas productos.")
        self.producto_ids = sorted(self.producto_ids)
        if self.primera_ejecucion_local.tzinfo or self.hora_simulada.tzinfo:
            raise ValueError("Usa horarios locales del negocio sin zona.")
        return self


class ProgramarFlujo(ConfigurarFlujo):
    clave_idempotencia: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]+$")
    autorizar_envio: bool = False


class GestionarProgramacion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    accion: Literal["PAUSAR", "REANUDAR", "CANCELAR"]
    motivo: str = Field(min_length=3, max_length=300)


class Reprogramar(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ejecutar_desde_utc: datetime
    motivo: str = Field(min_length=3, max_length=300)

    @field_validator("ejecutar_desde_utc")
    @classmethod
    def validar_fecha(cls, valor):
        if valor.tzinfo is None or valor.utcoffset() != timedelta(0):
            raise ValueError("Usa una hora UTC.")
        return valor
