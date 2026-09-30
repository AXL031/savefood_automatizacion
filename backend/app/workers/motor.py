"""Publicación recuperable y ejecución de efectos locales en PostgreSQL."""

import logging
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.exc import DBAPIError

from app.core.base_datos import SessionLocal
# Las FK de automatizaciones necesitan los metadatos del núcleo en el worker.
from app.modules.autenticacion.modelos import Usuario  # noqa: F401
from app.modules.negocios.modelos import Negocio  # noqa: F401
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion, IntentoAutomatizacion, ProgramacionDemo
from app.modules.automatizaciones.servicio import finalizar_intento, iniciar_intento
from app.workers.retry.politica import ErrorDatos, es_transitorio, siguiente_intento
from app.workers.tasks.manejadores import ContextoEjecucion, obtener_manejador, notificar_inicio, notificar_fallo

logger = logging.getLogger(__name__)
LEASE_SEGUNDOS = 120


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def _liberar(sesion, ejecucion):
    ejecucion.lease_hasta = None
    ejecucion.token_despacho = None
    if ejecucion.programacion_id is not None:
        sesion.get(ProgramacionDemo, ejecucion.programacion_id).lease_hasta = None


def _contexto(ejecucion):
    return ContextoEjecucion(ejecucion.id, ejecucion.tipo, ejecucion.clave_idempotencia, ejecucion.datos_entrada_json)


def _cerrar_fallo(sesion, intento, mensaje: str, transitorio: bool, ahora: datetime):
    proximo = siguiente_intento(intento.numero_intento, ahora) if transitorio else None
    ejecucion = finalizar_intento(
        sesion, intento.id, "REINTENTANDO" if proximo else "FALLIDA",
        mensaje_error=mensaje, proximo_intento_en=proximo,
    )
    notificar_fallo(sesion, _contexto(ejecucion), mensaje)
    _liberar(sesion, ejecucion)


def despachar_pendientes(publicar: Callable[[int, str], None], *, ahora: datetime | None = None) -> dict:
    """Confirma los reclamos antes de publicar; un fallo conserva el lease para recuperar."""
    ahora = ahora or _ahora()
    mensajes: list[tuple[int, str]] = []
    recuperadas = 0
    with SessionLocal.begin() as sesion:
        candidatas = sesion.scalars(
            select(EjecucionAutomatizacion)
            .outerjoin(ProgramacionDemo, ProgramacionDemo.id == EjecucionAutomatizacion.programacion_id)
            .where(
                EjecucionAutomatizacion.estado.in_(["PENDIENTE", "REINTENTANDO", "EN_EJECUCION"]),
                or_(EjecucionAutomatizacion.lease_hasta.is_(None), EjecucionAutomatizacion.lease_hasta <= ahora),
                or_(EjecucionAutomatizacion.proximo_intento_en.is_(None), EjecucionAutomatizacion.proximo_intento_en <= ahora),
                or_(
                    EjecucionAutomatizacion.programacion_id.is_(None),
                    (ProgramacionDemo.estado != "CANCELADA") & (ProgramacionDemo.ejecutar_desde_utc <= ahora),
                ),
            )
            .order_by(EjecucionAutomatizacion.id)
            .limit(50)
            .with_for_update(of=EjecucionAutomatizacion, skip_locked=True)
        ).all()
        for ejecucion in candidatas:
            if ejecucion.estado == "EN_EJECUCION":
                intento = sesion.scalar(select(IntentoAutomatizacion).where(
                    IntentoAutomatizacion.ejecucion_id == ejecucion.id,
                    IntentoAutomatizacion.estado == "EN_EJECUCION",
                ))
                if intento is None:
                    ejecucion.estado = "FALLIDA"
                    ejecucion.fin_en = ahora
                    ejecucion.mensaje_error = "Ejecución inconsistente: no existe intento activo."
                    notificar_fallo(sesion, _contexto(ejecucion), ejecucion.mensaje_error)
                    _liberar(sesion, ejecucion)
                else:
                    _cerrar_fallo(sesion, intento, "El worker se interrumpió antes de confirmar el resultado.", True, ahora)
                recuperadas += 1
                continue
            token = str(uuid4())
            ejecucion.token_despacho = token
            ejecucion.lease_hasta = ahora + timedelta(seconds=LEASE_SEGUNDOS)
            ejecucion.despachada_en = ejecucion.despachada_en or ahora
            if ejecucion.programacion_id is not None:
                programacion = sesion.get(ProgramacionDemo, ejecucion.programacion_id)
                programacion.estado = "DESPACHADA"
                programacion.despachada_en = programacion.despachada_en or ahora
                programacion.lease_hasta = ejecucion.lease_hasta
            mensajes.append((ejecucion.id, token))
    publicados = 0
    for ejecucion_id, token in mensajes:
        try:
            publicar(ejecucion_id, token)
            publicados += 1
        except Exception:
            # No registrar credenciales, parámetros ni excepciones del transporte.
            logger.warning("No se confirmó la publicación de ejecución %s; se recuperará por lease", ejecucion_id)
    return {"reclamadas": len(mensajes), "publicadas": publicados, "recuperadas": recuperadas}


def _bloquear(sesion, ejecucion_id: int):
    return sesion.scalar(select(EjecucionAutomatizacion).where(
        EjecucionAutomatizacion.id == ejecucion_id,
    ).with_for_update(skip_locked=True).execution_options(populate_existing=True))


def ejecutar(ejecucion_id: int, token: str) -> dict:
    """Conserva un intento durable y confirma efecto local + resultado en una transacción."""
    with SessionLocal.begin() as sesion:
        ejecucion = _bloquear(sesion, ejecucion_id)
        if ejecucion is None or ejecucion.token_despacho != token or ejecucion.estado not in ("PENDIENTE", "REINTENTANDO"):
            return {"resultado": "IGNORADA"}
        ahora = _ahora()
        if ejecucion.proximo_intento_en is not None and ejecucion.proximo_intento_en > ahora:
            return {"resultado": "NO_VENCIDA"}
        if ejecucion.programacion_id is not None:
            programacion = sesion.get(ProgramacionDemo, ejecucion.programacion_id)
            if programacion.estado == "CANCELADA" or programacion.ejecutar_desde_utc > ahora:
                return {"resultado": "NO_VENCIDA"}
        intento = iniciar_intento(sesion, ejecucion_id)
        intento_id = intento.id
        try:
            with sesion.begin_nested():
                notificar_inicio(sesion, _contexto(ejecucion))
        except Exception as error:
            mensaje = str(error) if isinstance(error, ErrorDatos) else "No se pudo iniciar la preparación del servicio."
            _cerrar_fallo(sesion, intento, mensaje, es_transitorio(error), ahora)
            return {"resultado": ejecucion.estado, "ejecucion_id": ejecucion_id}
        ejecucion.lease_hasta = ahora + timedelta(seconds=LEASE_SEGUNDOS)
        if ejecucion.programacion_id is not None:
            programacion.lease_hasta = ejecucion.lease_hasta
    # Si el proceso muere aquí, el intento permanece visible y el lease lo recupera.
    try:
        with SessionLocal.begin() as sesion:
            ejecucion = _bloquear(sesion, ejecucion_id)
            if ejecucion is None or ejecucion.token_despacho != token or ejecucion.estado != "EN_EJECUCION":
                return {"resultado": "IGNORADA"}
            intento = sesion.get(IntentoAutomatizacion, intento_id)
            contexto = ContextoEjecucion(ejecucion.id, ejecucion.tipo, ejecucion.clave_idempotencia, ejecucion.datos_entrada_json)
            try:
                # El bloqueo se mantiene durante el handler. El despachador omite esa fila,
                # incluso si vence el lease durante un cálculo largo.
                with sesion.begin_nested():
                    salida = obtener_manejador(ejecucion.tipo)(sesion, contexto)
                    if not isinstance(salida, dict):
                        raise ErrorDatos("El servicio debe devolver un objeto de resultado.")
                    finalizar_intento(sesion, intento_id, "COMPLETADA", datos_salida=salida)
            except Exception as error:
                mensaje = str(error) if isinstance(error, ErrorDatos) else (
                    "Fallo transitorio de infraestructura interna." if es_transitorio(error)
                    else "El servicio falló; revisa su implementación y los datos de entrada."
                )
                _cerrar_fallo(sesion, intento, mensaje, es_transitorio(error), _ahora())
            else:
                _liberar(sesion, ejecucion)
            estado = ejecucion.estado
        return {"resultado": estado, "ejecucion_id": ejecucion_id}
    except DBAPIError:
        # Si la conexión se perdió, no se puede confirmar ni el efecto ni su traza.
        # PostgreSQL revierte el efecto y Beat recupera el intento durable al vencer.
        logger.warning("Se perdió la transacción de ejecución %s; pendiente de recuperación", ejecucion_id)
        raise
