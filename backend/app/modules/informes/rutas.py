"""Lecturas autenticadas, con filtros idénticos en gráficos y exportación."""
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.identidad import identidad_actual
from .servicio import exportar_csv, obtener_resumen

router = APIRouter(prefix="/informes", tags=["informes"], dependencies=[Depends(identidad_actual)])


@router.get("/resumen")
def resumen(desde: date | None = None, hasta: date | None = None,
            modelo_id: int | None = Query(None, ge=1), incluir_evaluacion: bool = True,
            sesion: Session = Depends(obtener_sesion)):
    return {"datos": obtener_resumen(sesion, desde, hasta, modelo_id, incluir_evaluacion)}


@router.get("/exportar")
def exportar(tipo: Literal["ventas", "pronosticos", "pedidos"],
             desde: date | None = None, hasta: date | None = None,
             modelo_id: int | None = Query(None, ge=1), sesion: Session = Depends(obtener_sesion)):
    reporte = obtener_resumen(sesion, desde, hasta, modelo_id, incluir_evaluacion=tipo == "pronosticos")
    nombre = f"foodsave-{tipo}-{reporte['periodo']['desde']}-{reporte['periodo']['hasta']}.csv"
    return Response(exportar_csv(reporte, tipo), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{nombre}"', "Cache-Control": "no-store"})
