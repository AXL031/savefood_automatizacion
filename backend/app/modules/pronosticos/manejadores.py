"""Adaptadores de Kevin al motor A03; no confirman la sesión recibida."""

from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.automatizaciones.servicio import consultar_ejecucion_por_clave
from app.modules.inicializacion.servicio import iniciar_preparacion, completar_preparacion, fallar_preparacion
from app.modules.pronosticos.entrenamiento import preparar_modelo
from app.modules.pronosticos.evaluacion import evaluar_corrida, evaluar_modelo
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
    huella = contexto.datos_entrada.get("huella_inicializacion")
    clave_evaluacion = f"evaluar-inicializacion-{contexto.id}" if huella else None
    try:
        artefacto = preparar_modelo(sesion, version=version, ejecucion_id=contexto.id,
                                   clave_evaluacion=clave_evaluacion)
        if huella:
            completar_preparacion(sesion, contexto.id, huella, artefacto.id)
    except ErrorAPI as exc:
        raise ErrorDatos(str(exc.detail)) from exc
    salida = {"modelo_id": artefacto.id, "version_modelo": artefacto.version_modelo}
    if clave_evaluacion:
        evaluacion = consultar_ejecucion_por_clave(sesion, clave_evaluacion)
        salida["evaluacion_ejecucion_id"] = evaluacion.id
    return salida


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


def iniciar(sesion: Session, contexto: ContextoEjecucion) -> None:
    huella = contexto.datos_entrada.get("huella_inicializacion")
    if huella:
        iniciar_preparacion(sesion, contexto.id, huella)


def fallar(sesion: Session, contexto: ContextoEjecucion, mensaje: str) -> None:
    huella = contexto.datos_entrada.get("huella_inicializacion")
    if huella:
        fallar_preparacion(sesion, contexto.id, huella, mensaje)
