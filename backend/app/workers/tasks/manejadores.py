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
    from app.modules.pronosticos.manejadores import preparar, backtest, evaluacion_programada
    from app.modules.inicializacion.preparacion import iniciar_preparacion, fallar_preparacion

    MANEJADORES.update({
        "PREPARAR_MODELO": preparar,
        "EVALUAR_MODELO": backtest,
        "EVALUAR_PRONOSTICO": evaluacion_programada,
    })
    AL_INICIAR["PREPARAR_MODELO"] = iniciar_preparacion
    AL_FALLAR["PREPARAR_MODELO"] = fallar_preparacion


def contexto_ejecucion(ejecucion) -> ContextoEjecucion:
    return ContextoEjecucion(ejecucion.id, ejecucion.tipo, ejecucion.clave_idempotencia,
                            ejecucion.datos_entrada_json)


def notificar_inicio(sesion, ejecucion):
    callback = AL_INICIAR.get(ejecucion.tipo)
    if callback is not None:
        callback(sesion, contexto_ejecucion(ejecucion))


def notificar_fallo(sesion, ejecucion, mensaje):
    callback = AL_FALLAR.get(ejecucion.tipo)
    if callback is not None:
        callback(sesion, contexto_ejecucion(ejecucion), mensaje)


_registrar_pronosticos()


def _registrar_planificacion():
    from app.modules.planificacion.manejadores import generar_propuesta
    MANEJADORES["GENERAR_PROPUESTA"] = generar_propuesta


_registrar_planificacion()


def obtener_manejador(tipo: str) -> Manejador:
    try:
        return MANEJADORES[tipo]
    except KeyError:
        raise ErrorDatos(f"El servicio {tipo} está pendiente de integración.") from None
