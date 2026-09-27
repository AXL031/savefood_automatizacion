"""Frontera pública y transaccional del motor de automatizaciones."""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion, IntentoAutomatizacion, ProgramacionDemo

TipoEjecucion = Literal[
    "PREPARAR_MODELO", "EVALUAR_MODELO", "GENERAR_PROPUESTA", "EVALUAR_PRONOSTICO", "EVALUAR_PROMOCION"
]
EstadoFinal = Literal["COMPLETADA", "REINTENTANDO", "FALLIDA"]
TIPOS_EJECUCION = frozenset(TipoEjecucion.__args__)


def _json_normalizado(datos: dict) -> dict:
    try:
        return json.loads(json.dumps(datos, sort_keys=True, ensure_ascii=False, allow_nan=False))
    except (TypeError, ValueError) as exc:
        raise ValueError("Los datos de la ejecución deben ser JSON válido") from exc


def _huella(datos: dict) -> str:
    contenido = json.dumps(datos, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(contenido.encode("utf-8")).hexdigest()


def _instante_utc(valor: datetime) -> str:
    if valor.tzinfo is None or valor.utcoffset() != timedelta(0):
        raise ValueError("El horario real debe incluir zona UTC")
    return valor.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def crear_o_recuperar_ejecucion(
    sesion: Session,
    tipo: TipoEjecucion,
    clave_idempotencia: str,
    datos_entrada: dict,
    programacion_id: int | None = None,
) -> EjecucionAutomatizacion:
    """Crea el sobre de una tarea de dominio sin hacer commit de la sesión recibida."""
    if tipo not in TIPOS_EJECUCION:
        raise ValueError("Tipo de ejecución no admitido")
    if not clave_idempotencia or len(clave_idempotencia) > 128:
        raise ValueError("La clave idempotente debe tener entre 1 y 128 caracteres")
    entrada = _json_normalizado(datos_entrada)
    huella = _huella({"tipo": tipo, "entrada": entrada})
    existente = sesion.scalar(
        select(EjecucionAutomatizacion).where(EjecucionAutomatizacion.clave_idempotencia == clave_idempotencia)
    )
    if existente is not None:
        if existente.huella_entrada != huella or existente.programacion_id != programacion_id:
            raise ErrorAPI(409, "CLAVE_REUTILIZADA", "La clave pertenece a otra entrada")
        return existente
    try:
        with sesion.begin_nested():
            ejecucion = EjecucionAutomatizacion(
                programacion_id=programacion_id,
                tipo=tipo,
                clave_idempotencia=clave_idempotencia,
                huella_entrada=huella,
                datos_entrada_json=entrada,
                estado="PENDIENTE",
            )
            sesion.add(ejecucion)
            sesion.flush()
    except IntegrityError:
        existente = sesion.scalar(
            select(EjecucionAutomatizacion).where(EjecucionAutomatizacion.clave_idempotencia == clave_idempotencia)
        )
        if existente is None or existente.huella_entrada != huella or existente.programacion_id != programacion_id:
            raise ErrorAPI(409, "CLAVE_REUTILIZADA", "La clave pertenece a otra entrada") from None
        return existente
    return ejecucion


def programar_propuesta(
    sesion: Session,
    *,
    ejecutar_desde_utc: datetime,
    fecha_hora_simulada_local: datetime,
    fecha_objetivo_demo: str,
    producto_ids: list[int],
    clave_idempotencia: str,
    creado_por: int,
) -> ProgramacionDemo:
    """Reserva programación y ejecución pendiente en la misma transacción."""
    if fecha_hora_simulada_local.tzinfo is not None:
        raise ValueError("La hora simulada debe ser local y no llevar zona")
    if fecha_hora_simulada_local.date().isoformat() != fecha_objetivo_demo:
        raise ValueError("La fecha objetivo y el reloj simulado deben coincidir")
    if not 1 <= len(producto_ids) <= 5 or len(set(producto_ids)) != len(producto_ids) or any(
        producto_id <= 0 for producto_id in producto_ids
    ):
        raise ValueError("Se requieren entre 1 y 5 productos únicos con IDs positivos")
    parametros = {"fecha_objetivo_demo": fecha_objetivo_demo, "producto_ids": sorted(producto_ids)}
    return programar_ejecucion(
        sesion, tipo="GENERAR_PROPUESTA", ejecutar_desde_utc=ejecutar_desde_utc,
        fecha_hora_simulada_local=fecha_hora_simulada_local, parametros=parametros,
        clave_idempotencia=clave_idempotencia, creado_por=creado_por,
    )


def programar_ejecucion(
    sesion: Session,
    *,
    tipo: Literal["GENERAR_PROPUESTA", "EVALUAR_PROMOCION"],
    ejecutar_desde_utc: datetime,
    fecha_hora_simulada_local: datetime,
    parametros: dict,
    clave_idempotencia: str,
    creado_por: int | None = None,
) -> ProgramacionDemo:
    """Agenda un servicio interno en la transacción del evento que lo originó."""
    if tipo not in ("GENERAR_PROPUESTA", "EVALUAR_PROMOCION"):
        raise ValueError("Tipo de programación no admitido")
    if fecha_hora_simulada_local.tzinfo is not None:
        raise ValueError("La hora simulada debe ser local y no llevar zona")
    if not clave_idempotencia or len(clave_idempotencia) > 128:
        raise ValueError("La clave idempotente debe tener entre 1 y 128 caracteres")
    parametros = _json_normalizado(parametros)
    entrada = {
        "ejecutar_desde_utc": _instante_utc(ejecutar_desde_utc),
        "fecha_hora_simulada_local": fecha_hora_simulada_local.isoformat(),
        "parametros": parametros,
    }
    huella = _huella({"tipo": tipo, **entrada})
    existente = sesion.scalar(select(ProgramacionDemo).where(ProgramacionDemo.clave_idempotencia == clave_idempotencia))
    if existente is not None:
        if existente.huella_entrada != huella:
            raise ErrorAPI(409, "CLAVE_REUTILIZADA", "La clave pertenece a otra programación")
        return existente
    if ejecutar_desde_utc <= datetime.now(timezone.utc):
        raise ErrorAPI(400, "HORA_NO_FUTURA", "El horario real debe ser futuro")
    try:
        with sesion.begin_nested():
            programacion = ProgramacionDemo(
                tipo=tipo,
                ejecutar_desde_utc=ejecutar_desde_utc,
                fecha_hora_simulada_local=fecha_hora_simulada_local,
                parametros_json=parametros,
                clave_idempotencia=clave_idempotencia,
                huella_entrada=huella,
                estado="PROGRAMADA",
                creado_por=creado_por,
            )
            sesion.add(programacion)
            sesion.flush()
            crear_o_recuperar_ejecucion(
                sesion, tipo, clave_idempotencia, entrada, programacion.id
            )
    except IntegrityError:
        existente = sesion.scalar(select(ProgramacionDemo).where(ProgramacionDemo.clave_idempotencia == clave_idempotencia))
        if existente is None or existente.huella_entrada != huella:
            raise ErrorAPI(409, "CLAVE_REUTILIZADA", "La clave pertenece a otra programación") from None
        return existente
    return programacion


def iniciar_intento(sesion: Session, ejecucion_id: int) -> IntentoAutomatizacion:
    """Reserva el siguiente intento; el llamador controla el commit y el efecto de dominio."""
    ejecucion = sesion.scalar(
        select(EjecucionAutomatizacion)
        .where(EjecucionAutomatizacion.id == ejecucion_id)
        .with_for_update()
    )
    if ejecucion is None:
        raise ErrorAPI(404, "EJECUCION_NO_ENCONTRADA", "Ejecución no encontrada")
    if ejecucion.estado == "EN_EJECUCION":
        intento = sesion.scalar(
            select(IntentoAutomatizacion).where(
                IntentoAutomatizacion.ejecucion_id == ejecucion_id,
                IntentoAutomatizacion.estado == "EN_EJECUCION",
            )
        )
        if intento is not None:
            return intento
    if ejecucion.estado not in ("PENDIENTE", "REINTENTANDO"):
        raise ErrorAPI(409, "EJECUCION_NO_INICIABLE", "La ejecución no admite otro intento")
    numero = (sesion.scalar(
        select(func.max(IntentoAutomatizacion.numero_intento))
        .where(IntentoAutomatizacion.ejecucion_id == ejecucion_id)
    ) or 0) + 1
    if numero > 3:
        raise ErrorAPI(409, "INTENTOS_AGOTADOS", "La ejecución agotó sus intentos")
    ahora = datetime.now(timezone.utc)
    intento = IntentoAutomatizacion(
        ejecucion_id=ejecucion_id, numero_intento=numero, inicio_en=ahora, estado="EN_EJECUCION"
    )
    sesion.add(intento)
    ejecucion.estado = "EN_EJECUCION"
    ejecucion.inicio_en = ejecucion.inicio_en or ahora
    ejecucion.proximo_intento_en = None
    sesion.flush()
    return intento


def finalizar_intento(
    sesion: Session,
    intento_id: int,
    estado: EstadoFinal,
    datos_salida: dict | None = None,
    mensaje_error: str | None = None,
    proximo_intento_en: datetime | None = None,
) -> EjecucionAutomatizacion:
    """Registra un resultado; la política de reintento y el commit quedan en el llamador."""
    if estado not in ("COMPLETADA", "REINTENTANDO", "FALLIDA"):
        raise ValueError("Estado final no admitido")
    intento = sesion.get(IntentoAutomatizacion, intento_id)
    if intento is None:
        raise ErrorAPI(404, "INTENTO_NO_ENCONTRADO", "Intento no encontrado")
    ejecucion = sesion.scalar(
        select(EjecucionAutomatizacion)
        .where(EjecucionAutomatizacion.id == intento.ejecucion_id)
        .with_for_update()
    )
    if intento.estado != "EN_EJECUCION" or ejecucion.estado != "EN_EJECUCION":
        raise ErrorAPI(409, "INTENTO_NO_ACTIVO", "El intento ya no está en ejecución")
    if estado == "REINTENTANDO":
        if intento.numero_intento >= 3 or proximo_intento_en is None or proximo_intento_en.tzinfo is None:
            raise ValueError("El reintento requiere cupo y una hora UTC futura")
        if proximo_intento_en.utcoffset().total_seconds() != 0 or proximo_intento_en <= datetime.now(timezone.utc):
            raise ValueError("La hora de reintento debe ser futura")
    if estado != "COMPLETADA" and not mensaje_error:
        raise ValueError("El fallo debe registrar un mensaje")
    ahora = datetime.now(timezone.utc)
    intento.estado = "COMPLETADA" if estado == "COMPLETADA" else "FALLIDA"
    intento.fin_en = ahora
    intento.mensaje_error = None if estado == "COMPLETADA" else mensaje_error
    ejecucion.estado = estado
    ejecucion.fin_en = None if estado == "REINTENTANDO" else ahora
    ejecucion.proximo_intento_en = proximo_intento_en if estado == "REINTENTANDO" else None
    ejecucion.datos_salida_json = _json_normalizado(datos_salida) if datos_salida is not None else None
    ejecucion.mensaje_error = None if estado == "COMPLETADA" else mensaje_error
    sesion.flush()
    return ejecucion
