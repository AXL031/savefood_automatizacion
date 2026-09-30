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
AL_INICIAR: dict[str, Callable[[Session, ContextoEjecucion], None]] = {}
AL_FALLAR: dict[str, Callable[[Session, ContextoEjecucion, str], None]] = {}


def _registrar_pronosticos() -> None:
    from app.modules.pronosticos.manejadores import preparar, backtest, evaluacion_programada, iniciar, fallar

    AL_INICIAR["PREPARAR_MODELO"] = iniciar
    AL_FALLAR["PREPARAR_MODELO"] = fallar
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


def notificar_inicio(sesion: Session, contexto: ContextoEjecucion) -> None:
    if callback := AL_INICIAR.get(contexto.tipo):
        callback(sesion, contexto)


def notificar_fallo(sesion: Session, contexto: ContextoEjecucion, mensaje: str) -> None:
    if callback := AL_FALLAR.get(contexto.tipo):
        callback(sesion, contexto, mensaje)
