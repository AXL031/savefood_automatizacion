from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class SolicitarPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    corrida_id: PositiveInt
    clave_ejecucion: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")
