"""Cierre del día: consolida tickets confirmados en el historial diario que usa el modelo ML.

Los tickets de caja (PRESENCIAL) y de la tienda en línea (TIENDA) no escriben
`venta_diaria` en cada venta: una jornada abierta no es una observación diaria
completa. El cierre suma por producto los tickets CONFIRMADOS de una fecha ya
terminada y crea una revisión `CIERRE` auditable. Reglas:

- Una sola procedencia por producto/fecha: si el día ya existe en el historial
  importado o fue corregido a mano, el cierre no lo sobrescribe y lo informa
  como conflicto.
- Repetir el mismo cierre no cambia nada (idempotente por fecha + contenido).
- Si un ticket se anula después del cierre, un nuevo cierre crea otra revisión;
  las anteriores se conservan para las evaluaciones que ya las usaron.
- Reservas de tienda todavía activas impiden cerrar: una venta en curso podría
  quedar fuera del día.
"""
import hashlib
import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.comercio.modelos import ReservaTienda
from app.modules.negocios.servicio import zona_horaria_negocio

from .modelos import ImportacionVenta, RevisionVenta, VentaDiaria
from .modelos_caja import LineaTicketVenta, TicketVenta

ORIGEN_CIERRE = "CIERRE_OPERATIVO"
CANALES = ("PRESENCIAL", "TIENDA")


def ahora() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ResultadoCierre:
    fecha: date
    cierre_id: int | None
    repetido: bool
    unidades: int = 0
    productos: int = 0
    creadas: int = 0
    actualizadas: int = 0
    sin_cambios: int = 0
    conflictos: list[dict] = field(default_factory=list)

    def como_dict(self) -> dict:
        return {
            "fecha": self.fecha.isoformat(), "cierre_id": self.cierre_id, "repetido": self.repetido,
            "unidades": self.unidades, "productos": self.productos, "creadas": self.creadas,
            "actualizadas": self.actualizadas, "sin_cambios": self.sin_cambios, "conflictos": self.conflictos,
        }


def fecha_local_negocio(sesion: Session, instante: datetime | None = None) -> date:
    zona = ZoneInfo(zona_horaria_negocio(sesion))
    return (instante or ahora()).astimezone(zona).date()


def _totales_tickets(sesion: Session, fecha: date) -> dict[int, int]:
    filas = sesion.execute(
        select(LineaTicketVenta.producto_id, func.sum(LineaTicketVenta.cantidad))
        .join(TicketVenta, TicketVenta.id == LineaTicketVenta.ticket_id)
        .where(TicketVenta.fecha_local == fecha, TicketVenta.estado == "CONFIRMADA",
               TicketVenta.canal.in_(CANALES))
        .group_by(LineaTicketVenta.producto_id)
    )
    return {int(producto_id): int(unidades) for producto_id, unidades in filas}


def _reservas_activas(sesion: Session, fecha: date, instante: datetime) -> int:
    return sesion.scalar(select(func.count()).select_from(ReservaTienda).where(
        ReservaTienda.fecha_local == fecha, ReservaTienda.estado == "ACTIVA",
        ReservaTienda.vence_en > instante)) or 0


def _origen_actual(sesion: Session, venta: VentaDiaria) -> str:
    return sesion.scalar(select(RevisionVenta.origen_cambio).where(
        RevisionVenta.venta_id == venta.id, RevisionVenta.numero_revision == venta.revision_actual))


def cerrar_dia(sesion: Session, fecha: date, *, usuario_id: int | None = None,
               jornada_terminada: bool = False, instante: datetime | None = None) -> ResultadoCierre:
    """Consolida los tickets de `fecha` en `venta_diaria`; no hace commit."""
    instante = instante or ahora()
    hoy = fecha_local_negocio(sesion, instante)
    if fecha > hoy:
        raise ErrorAPI(422, "CIERRE_FECHA_FUTURA", "No se puede cerrar un día que todavía no ocurre.")
    if fecha == hoy and not jornada_terminada:
        raise ErrorAPI(409, "JORNADA_ABIERTA",
                       "La jornada de hoy sigue abierta. Confirma que terminó para cerrarla antes de medianoche.")
    if _reservas_activas(sesion, fecha, instante):
        raise ErrorAPI(409, "RESERVAS_PENDIENTES",
                       "Hay compras de la tienda en curso para ese día. Espera a que se paguen o venzan.")

    totales = _totales_tickets(sesion, fecha)
    existentes = {v.producto_id: v for v in sesion.scalars(
        select(VentaDiaria).where(VentaDiaria.fecha_local == fecha).with_for_update())}
    # Productos cerrados antes que ya no tienen tickets confirmados (todos anulados): pasan a 0.
    cerrados_antes = {pid for pid, v in existentes.items() if _origen_actual(sesion, v) == "CIERRE"}
    observados = dict(totales)
    for pid in cerrados_antes - totales.keys():
        observados[pid] = 0

    resultado = ResultadoCierre(fecha=fecha, cierre_id=None, repetido=False,
                                unidades=sum(totales.values()), productos=len(totales))
    if not observados:
        return resultado

    huella = hashlib.sha256(json.dumps(sorted(observados.items()), separators=(",", ":")).encode()).hexdigest()
    clave = f"{fecha.isoformat()}:{huella[:16]}"
    previo = sesion.scalar(select(ImportacionVenta).where(
        ImportacionVenta.origen == ORIGEN_CIERRE, ImportacionVenta.clave_importacion == clave))
    if previo is not None:
        resultado.cierre_id, resultado.repetido = previo.id, True
        resultado.sin_cambios = len(observados)
        return resultado

    registro = ImportacionVenta(origen=ORIGEN_CIERRE, clave_importacion=clave, huella_contenido=huella,
                                filas_aceptadas=len(observados), estado="COMPLETADA")
    sesion.add(registro)
    sesion.flush()
    resultado.cierre_id = registro.id
    motivo = f"Cierre del día {fecha.isoformat()} (caja y tienda)"

    for producto_id, unidades in sorted(observados.items()):
        venta = existentes.get(producto_id)
        if venta is None:
            venta = VentaDiaria(producto_id=producto_id, fecha_local=fecha, unidades_vendidas=unidades,
                                importacion_id=registro.id, revision_actual=1)
            sesion.add(venta)
            sesion.flush()
            sesion.add(RevisionVenta(venta_id=venta.id, numero_revision=1, unidades_vendidas=unidades,
                                     origen_cambio="CIERRE", motivo=motivo, usuario_id=usuario_id,
                                     importacion_id=registro.id))
            resultado.creadas += 1
        elif producto_id not in cerrados_antes:
            resultado.conflictos.append({
                "producto_id": producto_id, "unidades_tickets": unidades,
                "unidades_historial": venta.unidades_vendidas,
                "motivo": "El día ya existe en el historial importado o corregido; no se sobrescribe.",
            })
        elif venta.unidades_vendidas == unidades:
            resultado.sin_cambios += 1
        else:
            venta.revision_actual += 1
            venta.unidades_vendidas = unidades
            venta.actualizado_en = instante
            sesion.add(RevisionVenta(venta_id=venta.id, numero_revision=venta.revision_actual,
                                     unidades_vendidas=unidades, origen_cambio="CIERRE", motivo=motivo,
                                     usuario_id=usuario_id, importacion_id=registro.id))
            resultado.actualizadas += 1
    registro.filas_aceptadas = resultado.creadas + resultado.actualizadas + resultado.sin_cambios
    sesion.flush()
    return resultado


def cerrar_dia_anterior(sesion: Session, instante: datetime | None = None) -> ResultadoCierre | None:
    """Cierre automático del día anterior; sin ventas o con compras en curso no hace nada."""
    instante = instante or ahora()
    ayer = fecha_local_negocio(sesion, instante) - timedelta(days=1)
    try:
        return cerrar_dia(sesion, ayer, instante=instante)
    except ErrorAPI as error:
        if error.codigo == "RESERVAS_PENDIENTES":
            return None
        raise


def listar_cierres(sesion: Session, limite: int = 30) -> list[dict]:
    registros = sesion.scalars(select(ImportacionVenta).where(ImportacionVenta.origen == ORIGEN_CIERRE)
                               .order_by(ImportacionVenta.id.desc()).limit(limite)).all()
    datos = []
    for r in registros:
        fecha, unidades = sesion.execute(
            select(func.min(VentaDiaria.fecha_local), func.sum(RevisionVenta.unidades_vendidas))
            .join(RevisionVenta, RevisionVenta.venta_id == VentaDiaria.id)
            .where(RevisionVenta.importacion_id == r.id)).one()
        datos.append({"id": r.id, "fecha": fecha.isoformat() if fecha else r.clave_importacion[:10],
                      "productos": r.filas_aceptadas, "unidades": int(unidades or 0),
                      "creado_en": r.creado_en.isoformat() if r.creado_en else None})
    return datos
