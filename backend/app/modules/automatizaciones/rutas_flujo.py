from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.core.identidad import identidad_actual, requiere_administrador
from app.modules.automatizaciones.esquemas import ConfigurarFlujo, ProgramarFlujo, GestionarProgramacion, Reprogramar
from app.modules.automatizaciones.modelos import ConfiguracionFlujo
from app.modules.automatizaciones.flujo import comprobar, guardar_configuracion, programar_flujo, gestionar
from app.modules.automatizaciones.rutas import serializar_programacion, router_programaciones

router = APIRouter(prefix="/flujo-automatizacion", tags=["flujo-automatizacion"])


@router.get("/configuracion")
def leer(_usuario=Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    config = sesion.get(ConfiguracionFlujo, 1)
    return {"datos": config.parametros if config else None}


@router.put("/configuracion")
def guardar(datos: ConfigurarFlujo, usuario=Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    try:
        resultado = guardar_configuracion(sesion, datos, usuario.id)
        sesion.commit()
    except IntegrityError:
        sesion.rollback()
        raise ErrorAPI(409, "CONFIGURACION_MODIFICADA", "Otro administrador guardó la configuración. Actualiza antes de continuar.") from None
    return {"datos": resultado}


@router.post("/comprobar")
def revisar(datos: ConfigurarFlujo, _usuario=Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    return {"datos": comprobar(sesion, datos)}


@router.post("/programar")
def programar(datos: ProgramarFlujo, usuario=Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    try:
        resultado = programar_flujo(sesion, datos, usuario.id)
        sesion.commit()
    except IntegrityError:
        sesion.rollback()
        resultado = programar_flujo(sesion, datos, usuario.id)
        sesion.commit()
    return {"datos": [serializar_programacion(sesion, p) for p in resultado]}


@router_programaciones.post("/{programacion_id}/gestionar")
def controlar(programacion_id: int, datos: GestionarProgramacion, usuario=Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    resultado = gestionar(sesion, programacion_id, usuario.id, datos.motivo, accion=datos.accion)
    sesion.commit()
    return {"datos": serializar_programacion(sesion, resultado)}


@router_programaciones.patch("/{programacion_id}")
def cambiar_hora(programacion_id: int, datos: Reprogramar, usuario=Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    resultado = gestionar(sesion, programacion_id, usuario.id, datos.motivo, horario=datos.ejecutar_desde_utc)
    sesion.commit()
    return {"datos": serializar_programacion(sesion, resultado)}
