"""Reintentos exclusivos para efectos internos transaccionales."""

from datetime import datetime, timedelta
from random import randint

from sqlalchemy.exc import OperationalError


class ErrorTransitorioInterno(Exception):
    """El adaptador garantiza que falló una operación interna que puede repetirse."""


class ErrorDatos(Exception):
    """Error definitivo. Su mensaje debe ser seguro para mostrar al usuario."""


def es_transitorio(error: Exception) -> bool:
    if isinstance(error, ErrorTransitorioInterno):
        return True
    if isinstance(error, OperationalError):
        codigo = getattr(error.orig, "sqlstate", None) or getattr(error.orig, "pgcode", "") or ""
        return error.connection_invalidated or codigo.startswith("08") or codigo in {
            "40001", "40P01", "53300", "57P01", "57P02", "57P03",
        }
    # Un timeout genérico podría pertenecer a un envío externo incierto.
    return False


def siguiente_intento(numero: int, ahora: datetime) -> datetime | None:
    if numero >= 3:
        return None
    return ahora + timedelta(seconds=60 * 2 ** (numero - 1) + randint(0, 5))
