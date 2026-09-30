"""Registro explícito de servicios internos; cada autor entrega su adaptador."""

from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.workers.retry.politica import ErrorDatos


@dataclass(frozen=True)
class ContextoEjecucion:
    id: int
    tipo: str
    clave_idempotencia: str
    datos_entrada: dict


Manejador = Callable[[Session, ContextoEjecucion], dict]
# Añadir aquí únicamente adaptadores entregados y probados por su responsable.
# Usan la sesión recibida, sin commit/rollback y sin envío externo de Telegram.
MANEJADORES: dict[str, Manejador] = {}


def _registrar_pronosticos() -> None:
    from app.modules.pronosticos.manejadores import preparar, backtest, evaluacion_programada

    MANEJADORES.update({
        "PREPARAR_MODELO": preparar,
        "EVALUAR_MODELO": backtest,
        "EVALUAR_PRONOSTICO": evaluacion_programada,
    })


_registrar_pronosticos()


def obtener_manejador(tipo: str) -> Manejador:
    try:
        return MANEJADORES[tipo]
    except KeyError:
        raise ErrorDatos(f"El servicio {tipo} está pendiente de integración.") from None
