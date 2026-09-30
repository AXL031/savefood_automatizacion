from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.base_datos import obtener_sesion
from app.core.identidad import identidad_actual, requiere_administrador
from .modelos import PedidoCompra
from .servicio import cancelar_propuesta, decidir_pedido, detalle_pedido, detalle_propuesta, generar_pedidos, listar_propuestas, verificar_destinos_propuesta

router = APIRouter(tags=["compras"])


class GenerarPedidos(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plan_id: int = Field(gt=0)


class CancelarPropuesta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    motivo: str = Field(min_length=1, max_length=500)


class AprobarPedido(BaseModel):
    model_config = ConfigDict(extra="forbid")
    clave_idempotencia: str = Field(min_length=1, max_length=80)
    chat_id_revisado: str = Field(pattern=r"^-?[1-9][0-9]{0,18}$")


class RechazarPedido(BaseModel):
    model_config = ConfigDict(extra="forbid")
    clave_idempotencia: str = Field(min_length=1, max_length=80)
    motivo: str = Field(min_length=1, max_length=500)


@router.post("/pedidos/{pedido_id}/aprobar", status_code=202)
def aprobar(pedido_id: int, datos: AprobarPedido, admin=Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    decidir_pedido(sesion, pedido_id, accion="APROBAR", clave=datos.clave_idempotencia,
                   usuario_id=admin.id, nombre_usuario=admin.nombre, chat_id_revisado=datos.chat_id_revisado)
    sesion.commit()
    return {"datos": detalle_pedido(sesion, pedido_id)}


@router.post("/pedidos/{pedido_id}/rechazar")
def rechazar(pedido_id: int, datos: RechazarPedido, admin=Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    decidir_pedido(sesion, pedido_id, accion="RECHAZAR", clave=datos.clave_idempotencia,
                   usuario_id=admin.id, nombre_usuario=admin.nombre, motivo=datos.motivo)
    sesion.commit()
    return {"datos": detalle_pedido(sesion, pedido_id)}


@router.post("/compras/propuestas/{propuesta_id}/verificar-destinos")
def revisar_destinos(propuesta_id: int, admin=Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    verificar_destinos_propuesta(sesion, propuesta_id)
    sesion.commit()
    return {"datos": detalle_propuesta(sesion, propuesta_id)}


@router.post("/pedidos/generar", status_code=201)
def generar(datos: GenerarPedidos, _admin=Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    propuesta = generar_pedidos(sesion, datos.plan_id)
    sesion.commit()
    return {"datos": detalle_propuesta(sesion, propuesta.id)}


@router.get("/pedidos")
def pedidos(plan_id: int | None = Query(None, gt=0), _usuario=Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    consulta = select(PedidoCompra.id)
    if plan_id is not None:
        consulta = consulta.where(PedidoCompra.plan_id == plan_id)
    return {"datos": [detalle_pedido(sesion, id_) for id_ in sesion.scalars(consulta.order_by(PedidoCompra.id.desc()).limit(100))]}


@router.get("/pedidos/{pedido_id}")
def pedido(pedido_id: int, _usuario=Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    return {"datos": detalle_pedido(sesion, pedido_id)}


@router.get("/compras/propuestas")
def propuestas(plan_id: int | None = Query(None, gt=0), _usuario=Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    return {"datos": listar_propuestas(sesion, plan_id)}


@router.get("/compras/propuestas/{propuesta_id}")
def propuesta(propuesta_id: int, _usuario=Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    return {"datos": detalle_propuesta(sesion, propuesta_id)}


@router.post("/compras/propuestas/{propuesta_id}/cancelar")
def cancelar(propuesta_id: int, datos: CancelarPropuesta, admin=Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    cancelar_propuesta(sesion, propuesta_id, admin.id, datos.motivo)
    sesion.commit()
    return {"datos": detalle_propuesta(sesion, propuesta_id)}
