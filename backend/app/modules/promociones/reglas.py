"""Reglas puras para proponer promociones de productos perecibles.

Las fechas y horas se reciben en la hora local de la sucursal. Este módulo
propone una acción; no cambia precios ni publica promociones en el POS.
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


@dataclass(frozen=True)
class ReglaPromocion:
    hora_revision: time
    hora_cierre: time
    stock_umbral: int
    descuento_pct: int
    descuento_maximo_pct: int
    antiguedad_maxima_stock_min: int = 30

    def __post_init__(self) -> None:
        if self.hora_revision >= self.hora_cierre:
            raise ValueError("La revisión debe ocurrir antes del cierre")
        if self.stock_umbral < 0:
            raise ValueError("El umbral de stock no puede ser negativo")
        if not 1 <= self.descuento_pct <= self.descuento_maximo_pct <= 100:
            raise ValueError("El descuento debe respetar el máximo configurado")
        if self.antiguedad_maxima_stock_min <= 0:
            raise ValueError("La antigüedad máxima del stock debe ser positiva")


@dataclass(frozen=True)
class EstadoProducto:
    fecha_limite_venta: date
    stock_actual: int | None
    stock_actualizado_en: datetime | None
    promocion_activa: bool = False


@dataclass(frozen=True)
class PropuestaPromocion:
    proponer: bool
    motivo: str
    descuento_pct: int | None = None


def evaluar_promocion(
    regla: ReglaPromocion, estado: EstadoProducto, ahora_local: datetime
) -> PropuestaPromocion:
    """Propone descuento solo con stock reciente y excedente sobre el umbral."""
    if ahora_local.tzinfo is not None or (
        estado.stock_actualizado_en is not None
        and estado.stock_actualizado_en.tzinfo is not None
    ):
        raise ValueError("Usa horas locales sin zona horaria para ambos valores")
    if estado.fecha_limite_venta != ahora_local.date():
        return PropuestaPromocion(False, "El producto no vence hoy")
    if not regla.hora_revision <= ahora_local.time() < regla.hora_cierre:
        return PropuestaPromocion(False, "Fuera de la ventana de promoción")
    if estado.promocion_activa:
        return PropuestaPromocion(False, "Ya existe una promoción activa")
    if estado.stock_actual is None or estado.stock_actualizado_en is None:
        return PropuestaPromocion(False, "Falta una lectura de stock")
    if estado.stock_actual < 0:
        raise ValueError("El stock no puede ser negativo")
    antiguedad = ahora_local - estado.stock_actualizado_en
    if not timedelta(0) <= antiguedad <= timedelta(
        minutes=regla.antiguedad_maxima_stock_min
    ):
        return PropuestaPromocion(False, "La lectura de stock no está vigente")
    if estado.stock_actual <= regla.stock_umbral:
        return PropuestaPromocion(False, "El stock no supera el umbral")
    return PropuestaPromocion(
        True,
        f"Vence hoy y quedan {estado.stock_actual} unidades, más de "
        f"{regla.stock_umbral}",
        regla.descuento_pct,
    )
