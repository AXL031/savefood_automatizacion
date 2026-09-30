"""API de inventario por lotes: disponibilidad, movimientos y ajustes (V01/V02)."""

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.core.identidad import identidad_actual, requiere_administrador
from app.modules.autenticacion.modelos import Usuario
from app.modules.inventario import vigencia
from app.modules.inventario.esquemas import AjusteEntrada
from app.modules.inventario.servicio import (
    INGREDIENTE,
    PRODUCTO,
    ResultadoMovimiento,
    SolicitudAjuste,
    consultar_disponibilidad,
    listar_movimientos,
    registrar_ajuste,
)

router = APIRouter(prefix="/inventario", tags=["inventario"])


def _num(tipo: str, valor: Decimal | None) -> str | None:
    if valor is None:
        return None
    return str(int(valor)) if tipo == PRODUCTO else f"{valor:.3f}"


def _fecha(valor: date | None) -> str | None:
    return valor.isoformat() if valor else None


def _movimiento(resultado: ResultadoMovimiento) -> dict:
    return {
        "movimiento_id": resultado.movimiento_id,
        "tipo": resultado.tipo_item,
        "lote_id": resultado.lote_id,
        "tipo_movimiento": resultado.tipo_movimiento,
        "delta": _num(resultado.tipo_item, resultado.delta),
        "saldo_resultante": _num(resultado.tipo_item, resultado.saldo_resultante),
        "efectivo_en_demo": resultado.efectivo_en_demo.isoformat(),
        "repetido": resultado.repetido,
    }


@router.get("/disponibilidad")
def disponibilidad(
    fecha: date = Query(..., description="Fecha local del escenario, YYYY-MM-DD."),
    tipo: str | None = Query(None, pattern="^(producto|ingrediente)$"),
    _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    lectura = consultar_disponibilidad(sesion, fecha, tipo=tipo)
    return {
        "datos": [
            {
                "tipo": item.tipo,
                "item_id": item.item_id,
                "codigo": item.codigo,
                "nombre": item.nombre,
                "unidad": item.unidad,
                "stock_conocido": item.stock_conocido,
                "cantidad_disponible": _num(item.tipo, item.cantidad_disponible),
                "cantidad_prioridad": _num(item.tipo, item.cantidad_prioridad),
                "cantidad_excluida": _num(item.tipo, item.cantidad_excluida),
                "vigencia_desconocida": item.vigencia_desconocida,
                "lotes": [
                    {
                        "lote_id": lote.lote_id,
                        "codigo_lote": lote.codigo_lote,
                        "lote_informado": lote.lote_informado,
                        "fecha_caducidad": _fecha(lote.fecha_caducidad),
                        "fecha_limite_venta": _fecha(lote.fecha_limite_venta),
                        "saldo": _num(item.tipo, lote.saldo),
                        "estado": lote.estado,
                        "dia_de_vida": lote.dia_de_vida,
                        "cuenta": lote.cuenta,
                        "motivo": lote.motivo,
                    }
                    for lote in item.lotes
                ],
            }
            for item in lectura.items
        ],
        "metadatos": {
            "fecha": lectura.fecha.isoformat(),
            "leido_en": lectura.leido_en.isoformat(),
            "huella": lectura.huella,
            "vida_maxima_producto_dias": vigencia.VIDA_MAXIMA_PRODUCTO_DIAS,
            "ultimo_dia_optimo": vigencia.ULTIMO_DIA_OPTIMO,
        },
    }


@router.get("/movimientos")
def movimientos(
    tipo: str | None = Query(None, pattern="^(producto|ingrediente)$"),
    lote_id: int | None = Query(None),
    limite: int = Query(100, ge=1, le=500),
    _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    filas = listar_movimientos(sesion, tipo=tipo, lote_id=lote_id, limite=limite)
    return {
        "datos": [
            {
                "id": fila.id,
                "tipo": fila.tipo_item,
                "lote_id": fila.lote_id,
                "codigo_lote": fila.codigo_lote,
                "item_nombre": fila.item_nombre,
                "tipo_movimiento": fila.tipo_movimiento,
                "delta": _num(fila.tipo_item, fila.delta),
                "saldo_resultante": _num(fila.tipo_item, fila.saldo_resultante),
                "motivo": fila.motivo,
                "clave_operacion": fila.clave_operacion,
                "usuario_id": fila.usuario_id,
                "efectivo_en_demo": fila.efectivo_en_demo.isoformat(),
                "creado_en": fila.creado_en.isoformat() if fila.creado_en else None,
            }
            for fila in filas
        ],
        "metadatos": {"limite": limite, "total_devuelto": len(filas)},
    }


@router.post("/ajustes", status_code=201)
def ajustar(
    cuerpo: AjusteEntrada,
    response: Response,
    admin: Usuario = Depends(requiere_administrador),
    sesion: Session = Depends(obtener_sesion),
):
    """Registra un ajuste. 201 si es nuevo; 200 si la clave ya se aplicó igual."""
    solicitud = SolicitudAjuste(
        tipo_item=cuerpo.tipo,
        lote_id=cuerpo.lote_id,
        delta=cuerpo.delta,
        motivo=cuerpo.motivo,
        clave_operacion=cuerpo.clave_operacion,
        efectivo_en_demo=cuerpo.efectivo_en_demo,
    )
    try:
        resultado = registrar_ajuste(sesion, solicitud, admin.id)
        sesion.commit()
    except IntegrityError:
        # Carrera entre dos solicitudes con la misma clave sobre lotes distintos:
        # la restricción única decide y la segunda recibe conflicto.
        sesion.rollback()
        raise ErrorAPI(409, "CLAVE_REUTILIZADA", "La clave de operación ya se usó en otra operación.") from None
    if resultado.repetido:
        response.status_code = 200
    return {"datos": _movimiento(resultado)}
