"""Programaciones y trazas consultables del corte A02."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.core.identidad import identidad_actual, requiere_administrador
from app.modules.autenticacion.modelos import Usuario
from app.modules.automatizaciones.esquemas import ProgramarPropuesta
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion, IntentoAutomatizacion, ProgramacionDemo
from app.modules.automatizaciones.servicio import programar_propuesta

router_programaciones = APIRouter(prefix="/programaciones-demo", tags=["programaciones-demo"])
router_ejecuciones = APIRouter(prefix="/ejecuciones-automatizacion", tags=["ejecuciones-automatizacion"])


def _utc(valor: datetime | None) -> str | None:
    if valor is None:
        return None
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def serializar_programacion(sesion: Session, programacion: ProgramacionDemo) -> dict:
    ejecucion_id = sesion.scalar(
        select(EjecucionAutomatizacion.id)
        .where(EjecucionAutomatizacion.programacion_id == programacion.id)
    )
    return {
        "id": programacion.id,
        "tipo": programacion.tipo,
        "estado": programacion.estado,
        "ejecutar_desde_utc": _utc(programacion.ejecutar_desde_utc),
        "fecha_hora_simulada_local": programacion.fecha_hora_simulada_local.isoformat(),
        "parametros": programacion.parametros_json,
        "clave_idempotencia": programacion.clave_idempotencia,
        "despachada_en": _utc(programacion.despachada_en),
        "lease_hasta": _utc(programacion.lease_hasta),
        "creado_por": programacion.creado_por,
        "creado_en": _utc(programacion.creado_en),
        "ejecucion_id": ejecucion_id,
    }


def serializar_ejecucion(sesion: Session, ejecucion: EjecucionAutomatizacion) -> dict:
    intentos = sesion.scalars(
        select(IntentoAutomatizacion)
        .where(IntentoAutomatizacion.ejecucion_id == ejecucion.id)
        .order_by(IntentoAutomatizacion.numero_intento)
    ).all()
    return {
        "id": ejecucion.id,
        "programacion_id": ejecucion.programacion_id,
        "tipo": ejecucion.tipo,
        "clave_idempotencia": ejecucion.clave_idempotencia,
        "huella_entrada": ejecucion.huella_entrada,
        "datos_entrada": ejecucion.datos_entrada_json,
        "estado": ejecucion.estado,
        "inicio_en": _utc(ejecucion.inicio_en),
        "fin_en": _utc(ejecucion.fin_en),
        "proximo_intento_en": _utc(ejecucion.proximo_intento_en),
        "despachada_en": _utc(ejecucion.despachada_en),
        "lease_hasta": _utc(ejecucion.lease_hasta),
        "datos_salida": ejecucion.datos_salida_json,
        "mensaje_error": ejecucion.mensaje_error,
        "intentos": [
            {
                "id": intento.id,
                "numero_intento": intento.numero_intento,
                "inicio_en": _utc(intento.inicio_en),
                "fin_en": _utc(intento.fin_en),
                "estado": intento.estado,
                "mensaje_error": intento.mensaje_error,
            }
            for intento in intentos
        ],
    }


@router_programaciones.post("")
def crear_programacion(
    datos: ProgramarPropuesta,
    usuario: Usuario = Depends(requiere_administrador),
    sesion: Session = Depends(obtener_sesion),
):
    programacion = programar_propuesta(
        sesion,
        ejecutar_desde_utc=datos.ejecutar_desde_utc,
        fecha_hora_simulada_local=datos.fecha_hora_simulada_local,
        fecha_objetivo_demo=datos.fecha_objetivo_demo.isoformat(),
        producto_ids=datos.producto_ids,
        clave_idempotencia=datos.clave_idempotencia,
        creado_por=usuario.id,
        modo_envio_pedidos=datos.modo_envio_pedidos,
    )
    sesion.commit()
    return {"datos": serializar_programacion(sesion, programacion)}


@router_programaciones.get("")
def listar_programaciones(_usuario: Usuario = Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    registros = sesion.scalars(select(ProgramacionDemo).order_by(ProgramacionDemo.id.desc()).limit(50)).all()
    return {"datos": [serializar_programacion(sesion, registro) for registro in registros]}


@router_programaciones.get("/{programacion_id}")
def consultar_programacion(
    programacion_id: int,
    _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    programacion = sesion.get(ProgramacionDemo, programacion_id)
    if programacion is None:
        raise ErrorAPI(404, "PROGRAMACION_NO_ENCONTRADA", "Programación no encontrada")
    return {"datos": serializar_programacion(sesion, programacion)}


@router_ejecuciones.get("")
def listar_ejecuciones(_usuario: Usuario = Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    registros = sesion.scalars(select(EjecucionAutomatizacion).order_by(EjecucionAutomatizacion.id.desc()).limit(50)).all()
    return {"datos": [serializar_ejecucion(sesion, registro) for registro in registros]}


@router_ejecuciones.get("/{ejecucion_id}")
def consultar_ejecucion(
    ejecucion_id: int,
    _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    ejecucion = sesion.get(EjecucionAutomatizacion, ejecucion_id)
    if ejecucion is None:
        raise ErrorAPI(404, "EJECUCION_NO_ENCONTRADA", "Ejecución no encontrada")
    return {"datos": serializar_ejecucion(sesion, ejecucion)}
