"""Frontera E03/K01: reserva, progreso y recuperación sin nueva importación."""

import hashlib

from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion, obtener_ejecucion
from app.modules.inicializacion.modelos import ConfiguracionInicial
from app.modules.inicializacion.servicio import (
    leer_estado, marcar_entrenando, marcar_fallo_entrenamiento, marcar_modelo_listo,
)
from app.workers.retry.politica import ErrorDatos


def resumir_preparacion(sesion: Session, estado: ConfiguracionInicial) -> dict | None:
    if estado.preparacion_ejecucion_id is None:
        return None
    ejecucion = obtener_ejecucion(sesion, estado.preparacion_ejecucion_id)
    return {
        "ejecucion_id": ejecucion.id,
        "estado": ejecucion.estado,
        "version_modelo": ejecucion.datos_entrada_json["version_modelo"],
        "modelo_id": (ejecucion.datos_salida_json or {}).get("modelo_id"),
        "mensaje_error": ejecucion.mensaje_error,
    }


def solicitar_preparacion_modelo(sesion: Session, clave_reintento: str | None = None):
    """Reserva dentro de la transacción del llamador; no publica ni confirma."""
    estado = leer_estado(sesion, bloquear=True)
    if not estado.huella_solicitud or estado.estado == "PENDIENTE":
        raise ErrorAPI(409, "INICIALIZACION_NO_PREPARADA", "Primero completa la carga de datos.")
    if estado.preparacion_ejecucion_id is not None:
        actual = obtener_ejecucion(sesion, estado.preparacion_ejecucion_id)
        if clave_reintento is None or actual.estado != "FALLIDA" or estado.estado == "MODELO_LISTO":
            return actual
    clave = "automatica" if clave_reintento is None else clave_reintento
    sufijo = hashlib.sha256(clave.encode()).hexdigest()[:16]
    version = f"inicial-q65v2-{estado.huella_solicitud[:16]}-{sufijo}"
    ejecucion = crear_o_recuperar_ejecucion(
        sesion, "PREPARAR_MODELO", f"modelo-{estado.huella_solicitud}-{sufijo}",
        {"version_modelo": version, "inicializacion_id": estado.id,
         "huella_solicitud": estado.huella_solicitud},
    )
    estado.preparacion_ejecucion_id = ejecucion.id
    if ejecucion.estado != "FALLIDA":
        estado.mensaje_error = None
    sesion.flush()
    return ejecucion


def _estado_del_contexto(sesion, contexto):
    # La preparación del piloto y la preparación a demanda no alteran E03.
    if contexto.datos_entrada.get("inicializacion_id") is None:
        return None
    estado = leer_estado(sesion, bloquear=True)
    if (contexto.datos_entrada.get("inicializacion_id") != estado.id
            or contexto.datos_entrada.get("huella_solicitud") != estado.huella_solicitud
            or estado.preparacion_ejecucion_id != contexto.id):
        raise ErrorDatos("La preparación no corresponde a la inicialización vigente.")
    return estado


def iniciar_preparacion(sesion, contexto):
    if _estado_del_contexto(sesion, contexto) is not None:
        try:
            marcar_entrenando(sesion)
        except ErrorAPI as error:
            raise ErrorDatos(str(error.detail)) from error


def completar_preparacion(sesion, contexto):
    if _estado_del_contexto(sesion, contexto) is not None:
        marcar_modelo_listo(sesion)


def fallar_preparacion(sesion, contexto, mensaje):
    try:
        estado = _estado_del_contexto(sesion, contexto)
    except ErrorDatos:
        return  # Una tarea antigua no puede alterar otra inicialización.
    if estado is not None and estado.estado == "ENTRENANDO":
        marcar_fallo_entrenamiento(sesion, mensaje)
