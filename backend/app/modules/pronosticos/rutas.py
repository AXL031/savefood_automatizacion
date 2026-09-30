"""API de modelo, corridas y evaluación histórica."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.core.identidad import identidad_actual, requiere_administrador
from app.modules.autenticacion.modelos import Usuario
from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion
from app.modules.productos.servicio import nombres_productos
from app.modules.pronosticos.esquemas import SolicitarEntrenamiento
from app.modules.pronosticos.evaluacion import detalle_evaluacion, resumen_evaluacion
from app.modules.pronosticos.modelos import ArtefactoModelo, CorridaPronostico
from app.modules.pronosticos.servicio import obtener_pronosticos

router = APIRouter(prefix="/pronosticos", tags=["pronosticos"])


def _modelo(modelo: ArtefactoModelo) -> dict:
    return {
        "id": modelo.id, "version_modelo": modelo.version_modelo, "estado": modelo.estado,
        "sha256": modelo.sha256, "fecha_corte_entrenamiento": modelo.fecha_corte_entrenamiento.isoformat(),
        "particion": modelo.particion_json, "metricas": modelo.metricas_json,
        "entrenado_en": modelo.entrenado_en.isoformat(),
    }


def _corrida(sesion: Session, corrida: CorridaPronostico, incluir_productos: bool = False) -> dict:
    modelo = sesion.get(ArtefactoModelo, corrida.modelo_id)
    respuesta = {
        "id": corrida.id, "ejecucion_id": corrida.ejecucion_id, "tipo": corrida.tipo,
        "clave_ejecucion": corrida.clave_ejecucion, "fecha_objetivo": corrida.fecha_objetivo.isoformat(),
        "estado": corrida.estado, "modelo_id": modelo.id, "version_modelo": modelo.version_modelo,
        "creado_en": corrida.creado_en.isoformat(),
    }
    if incluir_productos:
        pronosticos = obtener_pronosticos(sesion, corrida.id)
        nombres = nombres_productos(sesion, [p.producto_id for p in pronosticos])
        respuesta["pronosticos"] = [
            {"id": p.id, "producto_id": p.producto_id, "producto": nombres.get(p.producto_id, "Producto"),
             "cantidad_pronosticada": p.cantidad_pronosticada, "estado": p.estado}
            for p in pronosticos
        ]
    return respuesta


@router.get("/modelos")
def listar_modelos(
    _usuario: Usuario = Depends(identidad_actual), sesion: Session = Depends(obtener_sesion),
):
    modelos = sesion.scalars(select(ArtefactoModelo).order_by(ArtefactoModelo.id.desc()).limit(50)).all()
    return {"datos": [_modelo(modelo) for modelo in modelos]}


@router.post("/preparar-modelo", status_code=202)
def solicitar_preparacion(
    entrada: SolicitarEntrenamiento, _admin: Usuario = Depends(requiere_administrador),
    sesion: Session = Depends(obtener_sesion),
):
    ejecucion = crear_o_recuperar_ejecucion(
        sesion, "PREPARAR_MODELO", entrada.clave_idempotencia,
        {"version_modelo": entrada.version_modelo},
    )
    sesion.commit()
    return {"datos": {"ejecucion_id": ejecucion.id, "estado": ejecucion.estado}}


@router.get("/corridas")
def listar_corridas(
    modelo_id: int | None = Query(default=None, gt=0),
    _usuario: Usuario = Depends(identidad_actual), sesion: Session = Depends(obtener_sesion),
):
    consulta = select(CorridaPronostico)
    if modelo_id is not None:
        consulta = consulta.where(CorridaPronostico.modelo_id == modelo_id)
    corridas = sesion.scalars(consulta.order_by(CorridaPronostico.id.desc()).limit(50)).all()
    return {"datos": [_corrida(sesion, corrida) for corrida in corridas]}


@router.get("/corridas/{corrida_id}")
def obtener_corrida(
    corrida_id: int, _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    corrida = sesion.get(CorridaPronostico, corrida_id)
    if corrida is None:
        raise ErrorAPI(404, "CORRIDA_NO_ENCONTRADA", "La corrida no existe.")
    return {"datos": _corrida(sesion, corrida, True)}


@router.get("/evaluacion")
def obtener_evaluacion(
    modelo_id: int | None = Query(default=None, gt=0),
    _usuario: Usuario = Depends(identidad_actual), sesion: Session = Depends(obtener_sesion),
):
    return {"datos": resumen_evaluacion(sesion, modelo_id)}


@router.get("/corridas/{corrida_id}/evaluacion")
def obtener_detalle_evaluacion(
    corrida_id: int, _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    corrida = sesion.get(CorridaPronostico, corrida_id)
    if corrida is None:
        raise ErrorAPI(404, "CORRIDA_NO_ENCONTRADA", "La corrida no existe.")
    return {"datos": detalle_evaluacion(sesion, corrida)}
