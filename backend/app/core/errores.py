"""Formato público de errores para todas las rutas HTTP."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("foodsave.api")

CODIGOS_HTTP = {
    400: "SOLICITUD_INVALIDA",
    401: "AUTENTICACION_REQUERIDA",
    403: "PERMISO_DENEGADO",
    404: "NO_ENCONTRADO",
    405: "METODO_NO_PERMITIDO",
    409: "CONFLICTO",
    503: "SERVICIO_NO_DISPONIBLE",
}


class ErrorAPI(StarletteHTTPException):
    def __init__(self, status_code: int, codigo: str, mensaje: str):
        headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else None
        super().__init__(status_code=status_code, detail=mensaje, headers=headers)
        self.codigo = codigo


def configurar_errores(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def error_http(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        codigo = exc.codigo if isinstance(exc, ErrorAPI) else CODIGOS_HTTP.get(exc.status_code, "ERROR_HTTP")
        mensaje = exc.detail if isinstance(exc.detail, str) else "No se pudo completar la solicitud."
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"codigo": codigo, "mensaje": mensaje}},
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def error_validacion(_request: Request, exc: RequestValidationError) -> JSONResponse:
        detalles = [
            {"campo": ".".join(str(parte) for parte in error["loc"]), "mensaje": error["msg"]}
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={"error": {"codigo": "DATOS_INVALIDOS", "mensaje": "Revisa los datos enviados.", "detalles": detalles}},
        )

    @app.exception_handler(Exception)
    async def error_interno(_request: Request, exc: Exception) -> JSONResponse:
        logger.error("Error interno no controlado: %s", type(exc).__name__)
        return JSONResponse(
            status_code=500,
            content={"error": {"codigo": "ERROR_INTERNO", "mensaje": "No se pudo completar la solicitud."}},
        )
