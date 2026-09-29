"""HTTP. AJUSTAR get_db y el adaptador Telegram a los del proyecto."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .esquemas import (OfertaCrear, OfertaPreferidaCompras, OfertaSalida,
                       ProveedorCrear, ProveedorSalida, VerificacionDestino)
from .servicio import Conflicto, NoEncontrado, ServicioProveedores

try:
    from app.db.session import get_db  # AJUSTAR
except ImportError:  # pragma: no cover
    def get_db():
        raise RuntimeError("Conectar get_db del proyecto")

router = APIRouter(prefix="/proveedores", tags=["proveedores"])


def get_servicio(db: Session = Depends(get_db)) -> ServicioProveedores:
    # AJUSTAR: inyectar aquí el adaptador Telegram real.
    return ServicioProveedores(db, telegram=None)


def _http(e: Exception) -> HTTPException:
    return HTTPException(404 if isinstance(e, NoEncontrado) else 409, str(e))


@router.post("", response_model=ProveedorSalida, status_code=201)
def crear(datos: ProveedorCrear, s: ServicioProveedores = Depends(get_servicio)):
    try:
        return s.crear_proveedor(datos)
    except Conflicto as e:
        raise _http(e)


@router.get("", response_model=list[ProveedorSalida])
def listar(s: ServicioProveedores = Depends(get_servicio)):
    return s.repo.listar_proveedores()


@router.patch("/{proveedor_id}/estado", response_model=ProveedorSalida)
def estado(proveedor_id: int, activo: bool, s: ServicioProveedores = Depends(get_servicio)):
    try:
        return s.cambiar_estado(proveedor_id, activo)
    except NoEncontrado as e:
        raise _http(e)


@router.put("/{proveedor_id}/chat", response_model=ProveedorSalida)
def vincular_chat(proveedor_id: int, chat_id: str, s: ServicioProveedores = Depends(get_servicio)):
    try:
        return s.vincular_chat(proveedor_id, chat_id)
    except NoEncontrado as e:
        raise _http(e)


@router.post("/{proveedor_id}/verificar-destino", response_model=VerificacionDestino)
def verificar(proveedor_id: int, s: ServicioProveedores = Depends(get_servicio)):
    try:
        return s.verificar_destino(proveedor_id)
    except NoEncontrado as e:
        raise _http(e)


@router.post("/{proveedor_id}/ofertas", response_model=OfertaSalida, status_code=201)
def crear_oferta(proveedor_id: int, datos: OfertaCrear, s: ServicioProveedores = Depends(get_servicio)):
    try:
        return s.crear_oferta(proveedor_id, datos)
    except (NoEncontrado, Conflicto) as e:
        raise _http(e)


@router.post("/ofertas/{oferta_id}/preferida", response_model=OfertaSalida)
def preferida(oferta_id: int, s: ServicioProveedores = Depends(get_servicio)):
    try:
        return s.marcar_preferida(oferta_id)
    except (NoEncontrado, Conflicto) as e:
        raise _http(e)


@router.get("/ofertas/preferida/{ingrediente_id}", response_model=OfertaPreferidaCompras)
def consulta_compras(ingrediente_id: int, s: ServicioProveedores = Depends(get_servicio)):
    r = s.oferta_preferida_para_compras(ingrediente_id)
    if not r:
        raise HTTPException(404, "Sin oferta preferida activa")
    return r
