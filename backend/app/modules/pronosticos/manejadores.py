"""Adaptadores de Kevin al motor A03; no confirman la sesión recibida."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.pronosticos.entrenamiento import preparar_modelo
from app.modules.pronosticos.evaluacion import evaluar_corrida, evaluar_modelo
from app.modules.inicializacion.preparacion import completar_preparacion
from app.workers.retry.politica import ErrorDatos
if TYPE_CHECKING:
    from app.workers.tasks.manejadores import ContextoEjecucion


def _id(entrada: dict, campo: str) -> int:
    valor = entrada.get(campo)
    if type(valor) is not int or valor <= 0:
        raise ErrorDatos(f"Falta {campo} válido en la ejecución.")
    return valor


def preparar(sesion: Session, contexto: ContextoEjecucion) -> dict:
    version = contexto.datos_entrada.get("version_modelo", f"demo-{contexto.id}")
    try:
        artefacto = preparar_modelo(sesion, version=version, ejecucion_id=contexto.id)
    except ErrorAPI as exc:
        raise ErrorDatos(str(exc.detail)) from exc
    except ValueError as exc:
        raise ErrorDatos(str(exc)) from exc
    completar_preparacion(sesion, contexto)
    return {"modelo_id": artefacto.id, "version_modelo": artefacto.version_modelo}


def backtest(sesion: Session, contexto: ContextoEjecucion) -> dict:
    try:
        return evaluar_modelo(sesion, _id(contexto.datos_entrada, "modelo_id"), contexto.id)
    except ErrorAPI as exc:
        raise ErrorDatos(str(exc.detail)) from exc


def evaluacion_programada(sesion: Session, contexto: ContextoEjecucion) -> dict:
    try:
        return evaluar_corrida(sesion, _id(contexto.datos_entrada, "corrida_id"), contexto.id)
    except ErrorAPI as exc:
        raise ErrorDatos(str(exc.detail)) from exc
