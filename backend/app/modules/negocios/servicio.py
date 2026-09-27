"""Lecturas públicas de configuración para otros módulos."""

from typing import Literal

from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.negocios.modelos import Negocio

ModoEnvio = Literal["REQUIERE_APROBACION", "AUTOMATICO"]


def obtener_modo_envio_pedidos(sesion: Session) -> ModoEnvio:
    """Lee el modo vigente sin confirmar la sesión del consumidor."""
    negocio = sesion.get(Negocio, 1)
    if negocio is None:
        raise ErrorAPI(503, "NEGOCIO_NO_CONFIGURADO", "Falta aplicar la migración inicial")
    return negocio.modo_envio_pedidos
