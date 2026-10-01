"""L01: API protegida, sobre común y commit coordinado por HTTP."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import BaseModel, SecretStr, Field
from app.integrations.proveedores.telegram import ClienteTelegram, ConfiguracionTelegram, ErrorTelegram, validar_token
from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.core.identidad import identidad_actual, requiere_administrador
from .esquemas import OfertaCrear, OfertaSalida, ProveedorCrear, ProveedorSalida
from .servicio import Conflicto, NoEncontrado, ServicioProveedores

router = APIRouter(prefix="/proveedores", tags=["proveedores"])


def get_servicio(db: Session = Depends(obtener_sesion)) -> ServicioProveedores:
    return ServicioProveedores(db)


class TokenTelegram(BaseModel):
    token: SecretStr = Field(min_length=1, max_length=256)


def _estado_telegram(comprobar=False, token=None):
    try:
        configuracion = ConfiguracionTelegram()
        cliente = ClienteTelegram(token) if token is not None else ClienteTelegram.desde_configuracion()
        configurado = cliente.huella is not None
        bot = cliente.comprobar_bot() if comprobar else None
        return {"configurado": configurado,
                "origen": "SISTEMA" if token is not None or configuracion.ruta.exists() else "ENTORNO" if configurado else "SIN_CONFIGURAR",
                "codigo": "BOT_VERIFICADO" if bot else "SIN_COMPROBAR" if configurado else "TOKEN_NO_CONFIGURADO",
                "detalle": "Bot verificado con Telegram." if bot else "Comprobar el bot para validar su acceso." if configurado else "Guarda el token de tu bot para comenzar.",
                "bot": bot}
    except ErrorTelegram as error:
        return {"configurado": False if error.codigo in ("CONFIGURACION_ILEGIBLE", "TOKEN_NO_CONFIGURADO") else True,
                "origen": "SISTEMA" if ConfiguracionTelegram().ruta.exists() else "ENTORNO",
                "codigo": error.codigo, "detalle": str(error), "bot": None}


@router.get("/telegram/configuracion")
def configuracion_telegram(_admin=Depends(requiere_administrador)):
    return {"datos": _estado_telegram()}


@router.post("/telegram/configuracion")
def guardar_telegram(datos: TokenTelegram, _admin=Depends(requiere_administrador)):
    try:
        token = SecretStr(validar_token(datos.token.get_secret_value()))
        estado = _estado_telegram(comprobar=True, token=token)
        if estado["bot"] is None:
            actual = _estado_telegram()
            actual.update(codigo=estado["codigo"], detalle=estado["detalle"])
            return {"datos": actual}
        ConfiguracionTelegram().guardar(token)
        return {"datos": estado}
    except ErrorTelegram as error:
        raise ErrorAPI(422 if error.codigo == "TOKEN_INVALIDO" else 503, error.codigo, str(error)) from None


@router.post("/telegram/comprobar")
def comprobar_telegram(_admin=Depends(requiere_administrador)):
    return {"datos": _estado_telegram(comprobar=True)}


@router.post("/telegram/chats-pruebas")
def buscar_chats_telegram(_admin=Depends(requiere_administrador)):
    try:
        return {"datos": ClienteTelegram.desde_configuracion().buscar_chats_pruebas()}
    except ErrorTelegram as error:
        raise ErrorAPI(409 if error.codigo == "BOT_CON_WEBHOOK" else 503, error.codigo, str(error)) from None


@router.delete("/telegram/configuracion")
def deshabilitar_telegram(_admin=Depends(requiere_administrador)):
    try:
        ConfiguracionTelegram().guardar(SecretStr(""))
    except ErrorTelegram as error:
        raise ErrorAPI(503, error.codigo, str(error)) from None
    return {"datos": _estado_telegram()}


def _guardar(s: ServicioProveedores, operacion, esquema=None):
    try:
        resultado = operacion()
        s.db.commit()
        datos = s.salida_proveedor(resultado) if esquema is ProveedorSalida else esquema.model_validate(resultado) if esquema else resultado
        return {"datos": datos}
    except (NoEncontrado, Conflicto) as error:
        s.db.rollback()
        raise ErrorAPI(404 if isinstance(error, NoEncontrado) else 409,
                       "REFERENCIA_NO_ENCONTRADA" if isinstance(error, NoEncontrado) else "CONFLICTO_PROVEEDORES",
                       str(error)) from None
    except IntegrityError:
        s.db.rollback()
        raise ErrorAPI(409, "CONFLICTO_PROVEEDORES", "La operación viola una referencia o unicidad del catálogo.") from None


@router.post("", status_code=201)
def crear(datos: ProveedorCrear, _admin=Depends(requiere_administrador), s=Depends(get_servicio)):
    return _guardar(s, lambda: s.crear_proveedor(datos), ProveedorSalida)


@router.get("")
def listar(_usuario=Depends(identidad_actual), s=Depends(get_servicio)):
    return {"datos": [s.salida_proveedor(p) for p in s.repo.listar_proveedores()]}


@router.patch("/{proveedor_id}/estado")
def estado(proveedor_id: int, activo: bool, _admin=Depends(requiere_administrador), s=Depends(get_servicio)):
    return _guardar(s, lambda: s.cambiar_estado(proveedor_id, activo), ProveedorSalida)


@router.put("/{proveedor_id}/chat")
def vincular_chat(proveedor_id: int, chat_id: str = Query(min_length=1, max_length=64),
                  _admin=Depends(requiere_administrador), s=Depends(get_servicio)):
    if not chat_id.strip():
        raise ErrorAPI(422, "CHAT_INVALIDO", "El identificador del chat no puede estar vacío.")
    return _guardar(s, lambda: s.vincular_chat(proveedor_id, chat_id.strip()), ProveedorSalida)


@router.post("/{proveedor_id}/verificar-destino")
def verificar(proveedor_id: int, _admin=Depends(requiere_administrador), s=Depends(get_servicio)):
    return _guardar(s, lambda: s.verificar_destino(proveedor_id))


@router.get("/{proveedor_id}/ofertas")
def listar_ofertas(proveedor_id: int, _usuario=Depends(identidad_actual), s=Depends(get_servicio)):
    if s.repo.proveedor_por_id(proveedor_id) is None:
        raise ErrorAPI(404, "PROVEEDOR_NO_ENCONTRADO", "Proveedor no encontrado")
    return {"datos": [OfertaSalida.model_validate(o) for o in s.repo.ofertas_de_proveedor(proveedor_id)]}


@router.post("/{proveedor_id}/ofertas", status_code=201)
def crear_oferta(proveedor_id: int, datos: OfertaCrear, _admin=Depends(requiere_administrador), s=Depends(get_servicio)):
    return _guardar(s, lambda: s.crear_oferta(proveedor_id, datos), OfertaSalida)


@router.post("/ofertas/{oferta_id}/preferida")
def preferida(oferta_id: int, _admin=Depends(requiere_administrador), s=Depends(get_servicio)):
    return _guardar(s, lambda: s.marcar_preferida(oferta_id), OfertaSalida)


@router.patch("/ofertas/{oferta_id}/desactivar")
def desactivar(oferta_id: int, _admin=Depends(requiere_administrador), s=Depends(get_servicio)):
    return _guardar(s, lambda: s.desactivar_oferta(oferta_id), OfertaSalida)


@router.get("/ofertas/preferida/{ingrediente_id}")
def consulta_compras(ingrediente_id: int, _usuario=Depends(identidad_actual), s=Depends(get_servicio)):
    resultado = s.oferta_preferida_para_compras(ingrediente_id)
    if resultado is None:
        raise ErrorAPI(404, "OFERTA_NO_ENCONTRADA", "Sin oferta preferida activa")
    return {"datos": resultado}
