"""Entrada administrativa para preparar el modelo sin bloquear la solicitud HTTP."""

from pydantic import BaseModel, ConfigDict, Field


class SolicitarEntrenamiento(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_modelo: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    clave_idempotencia: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")
