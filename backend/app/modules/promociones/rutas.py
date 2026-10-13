from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.base_datos import obtener_sesion
from app.core.identidad import identidad_actual, requiere_administrador
from app.core.errores import ErrorAPI
from app.modules.promociones.esquemas import ConfigurarRegla
from app.modules.promociones.modelos import EvaluacionPromocion
from app.modules.promociones.servicio import guardar_regla, ultima_regla, serializar_regla, serializar_evaluacion

router = APIRouter(prefix="/promociones", tags=["promociones"])


@router.get("/regla")
def regla(_usuario=Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    return {"datos": serializar_regla(ultima_regla(sesion))}


@router.put("/regla")
def configurar(datos: ConfigurarRegla, usuario=Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    try:
        regla = guardar_regla(sesion, datos, usuario.id)
        sesion.commit()
    except IntegrityError:
        sesion.rollback()
        raise ErrorAPI(409, "REGLA_MODIFICADA", "La regla cambió mientras editabas. Actualiza y vuelve a guardar.") from None
    return {"datos": serializar_regla(regla)}


@router.get("/evaluaciones")
def listar(limite: int = Query(25, ge=1, le=100), desplazamiento: int = Query(0, ge=0),
           _usuario=Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    filas = sesion.scalars(select(EvaluacionPromocion).order_by(EvaluacionPromocion.id.desc()).offset(desplazamiento).limit(limite)).all()
    return {"datos": [serializar_evaluacion(sesion, e) for e in filas],
            "metadatos": {"total": sesion.scalar(select(func.count()).select_from(EvaluacionPromocion))}}


@router.get("/evaluaciones/{evaluacion_id}")
def detalle(evaluacion_id: int, _usuario=Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    evaluacion = sesion.get(EvaluacionPromocion, evaluacion_id)
    if not evaluacion:
        raise ErrorAPI(404, "EVALUACION_NO_ENCONTRADA", "Evaluación no encontrada.")
    return {"datos": serializar_evaluacion(sesion, evaluacion)}
