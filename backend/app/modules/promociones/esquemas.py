from datetime import time
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ConfigurarRegla(BaseModel):
    model_config = ConfigDict(extra="forbid")
    habilitada: bool = False
    hora_revision: time = time(17)
    hora_cierre: time = time(20)
    stock_umbral: int = Field(default=5, ge=0, le=1000000)
    descuento_pct: int = Field(default=20, ge=1, le=100)
    descuento_maximo_pct: int = Field(default=30, ge=1, le=100)
    antiguedad_maxima_stock_min: int = Field(default=30, ge=1, le=1440)
    demora_segundos: int = Field(default=5, ge=5, le=3600)

    @model_validator(mode="after")
    def validar(self):
        if self.hora_revision.tzinfo or self.hora_cierre.tzinfo or self.hora_revision >= self.hora_cierre:
            raise ValueError("La revisión debe ser anterior al cierre, con horas locales sin zona.")
        if self.descuento_pct > self.descuento_maximo_pct:
            raise ValueError("El descuento supera el máximo permitido.")
        return self
