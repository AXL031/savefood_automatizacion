"""Reglas puras de vigencia de lotes para una fecha del escenario.

**Producto de pastelería (perecible):** vida máxima de 5 días. La
`fecha_caducidad` del lote es el último día de vida (día 5), así que el día de
vida en `fecha` es `5 - (fecha_caducidad - fecha)`:

- días 1 a 3 → `OPTIMO`: cuenta como stock disponible.
- días 4 y 5 → `PRIORIDAD`: cuenta, pero debe venderse primero.
- día 6 en adelante → `MERMA`: no cuenta.

Un lote que pasó su `fecha_limite_venta` tampoco cuenta (`MERMA`).

**Ingrediente:** cuenta mientras `fecha <= fecha_caducidad` (`VIGENTE`); después
es `VENCIDO` y no cuenta.

Sin fecha de caducidad el lote cuenta con `DESCONOCIDO` y obliga a advertirlo
en el plan: la ausencia de fecha no se trata como vigente ni como vencido.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

VIDA_MAXIMA_PRODUCTO_DIAS = 5
ULTIMO_DIA_OPTIMO = 3

OPTIMO = "OPTIMO"
PRIORIDAD = "PRIORIDAD"
MERMA = "MERMA"
VIGENTE = "VIGENTE"
VENCIDO = "VENCIDO"
DESCONOCIDO = "DESCONOCIDO"


@dataclass(frozen=True)
class Vigencia:
    estado: str
    cuenta: bool
    dia_de_vida: int | None
    motivo: str


def caducidad_maxima_producto(dia_existente: date) -> date:
    """Caducidad más lejana posible para un lote que ya existe en `dia_existente`.

    Si se elaboró ese mismo día (día 1), su día 5 es cuatro días después.
    """
    return dia_existente + timedelta(days=VIDA_MAXIMA_PRODUCTO_DIAS - 1)


def vigencia_producto(fecha: date, fecha_caducidad: date | None, fecha_limite_venta: date | None) -> Vigencia:
    if fecha_limite_venta is not None and fecha > fecha_limite_venta:
        return Vigencia(MERMA, False, _dia(fecha, fecha_caducidad), f"Pasó su límite de venta ({fecha_limite_venta}).")
    if fecha_caducidad is None:
        return Vigencia(DESCONOCIDO, True, None, "Sin fecha de caducidad: vigencia desconocida.")
    dia = _dia(fecha, fecha_caducidad)
    if dia > VIDA_MAXIMA_PRODUCTO_DIAS:
        return Vigencia(MERMA, False, dia, f"Día {dia} de vida: es merma y no se ofrece.")
    if dia > ULTIMO_DIA_OPTIMO:
        return Vigencia(PRIORIDAD, True, dia, f"Día {dia} de {VIDA_MAXIMA_PRODUCTO_DIAS}: vender con prioridad.")
    return Vigencia(OPTIMO, True, dia, f"Día {dia} de {VIDA_MAXIMA_PRODUCTO_DIAS}: óptimo.")


def vigencia_ingrediente(fecha: date, fecha_caducidad: date | None) -> Vigencia:
    if fecha_caducidad is None:
        return Vigencia(DESCONOCIDO, True, None, "Sin fecha de caducidad: vigencia desconocida.")
    if fecha > fecha_caducidad:
        return Vigencia(VENCIDO, False, None, f"Venció el {fecha_caducidad}.")
    return Vigencia(VIGENTE, True, None, f"Vigente hasta {fecha_caducidad}.")


def _dia(fecha: date, fecha_caducidad: date | None) -> int | None:
    if fecha_caducidad is None:
        return None
    # Una fecha anterior a la elaboración no existe en el escenario; se muestra día 1.
    return max(1, VIDA_MAXIMA_PRODUCTO_DIAS - (fecha_caducidad - fecha).days)
