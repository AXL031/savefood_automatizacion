"""Vector de inferencia basado exclusivamente en los 28 días anteriores."""

from datetime import date, timedelta
from statistics import mean

from app.modules.ventas.servicio import VentaHistorica

FEATURES = [
    "article", "dia_semana", "mes", "dia_mes", "fin_semana", "ventas_ayer",
    "ventas_hace_7_dias", "promedio_7_dias", "promedio_14_dias", "promedio_28_dias",
    "conteo_7_dias", "conteo_14_dias", "conteo_28_dias",
]


def construir_vector(sku: str, objetivo: date, historial: list[VentaHistorica]) -> dict:
    """No lee ni utiliza la venta del objetivo aunque el llamador la incluya."""
    conocidos = {venta.fecha_local: venta.unidades_vendidas for venta in historial if venta.fecha_local < objetivo}

    def ventana(dias: int) -> list[int]:
        return [conocidos[objetivo - timedelta(days=paso)]
                for paso in range(1, dias + 1) if objetivo - timedelta(days=paso) in conocidos]

    siete, catorce, veintiocho = ventana(7), ventana(14), ventana(28)
    return {
        "article": sku,
        "dia_semana": objetivo.weekday(),
        "mes": objetivo.month,
        "dia_mes": objetivo.day,
        "fin_semana": int(objetivo.weekday() >= 5),
        "ventas_ayer": conocidos.get(objetivo - timedelta(days=1)),
        "ventas_hace_7_dias": conocidos.get(objetivo - timedelta(days=7)),
        "promedio_7_dias": mean(siete) if siete else None,
        "promedio_14_dias": mean(catorce) if catorce else None,
        "promedio_28_dias": mean(veintiocho) if veintiocho else None,
        "conteo_7_dias": len(siete),
        "conteo_14_dias": len(catorce),
        "conteo_28_dias": len(veintiocho),
    }
