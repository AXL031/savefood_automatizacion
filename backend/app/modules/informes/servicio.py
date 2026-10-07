"""Agregados y CSV, sin escritura, entrenamiento ni efectos externos."""
import csv
from datetime import date, datetime, timedelta, timezone
from io import StringIO

from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.compras.servicio import periodo_propuestas, resumen_pedidos
from app.modules.pronosticos.evaluacion import resumen_evaluacion
from app.modules.ventas.servicio import periodo_ventas, resumen_ventas

FUENTES = {"ventas": "Ventas diarias conocidas, revisión actual",
           "pedidos": "Fecha objetivo del escenario; estado actual del pedido",
           "evaluacion": "Backtest persistido; pares con revisión vigente evaluada"}

ESTADOS = {"BLOQUEADO": "Bloqueado", "PENDIENTE_APROBACION": "Pendiente de aprobación",
           "CANCELADO": "Cancelado", "RECHAZADO": "Rechazado", "PENDIENTE_ENVIO": "Pendiente de envío",
           "ENVIANDO": "Enviando", "ENVIADO": "Enviado", "FALLIDO": "Fallido",
           "PENDIENTE_VERIFICACION": "Requiere verificar envío", "GENERADA": "Generada",
           "BLOQUEADA": "Bloqueada", "SIN_FALTANTES": "Sin faltantes", "CANCELADA": "Cancelada"}


def obtener_resumen(sesion: Session, desde: date | None = None, hasta: date | None = None,
                    modelo_id: int | None = None, incluir_evaluacion: bool = True) -> dict:
    primera, ultima = periodo_ventas(sesion)
    inicio_pedidos, fin_pedidos = periodo_propuestas(sesion)
    hasta = hasta or (desde + timedelta(days=29) if desde else ultima or fin_pedidos or date.today())
    desde = desde or hasta - timedelta(days=29)
    if desde > hasta or (hasta - desde).days >= 366:
        raise ErrorAPI(422, "RANGO_INVALIDO", "Elige un período ordenado de hasta 366 días, inclusive.")
    evaluacion, aviso = None, None
    if incluir_evaluacion:
        try:
            evaluacion = resumen_evaluacion(sesion, modelo_id, desde=desde, hasta=hasta)
            if not evaluacion["serie_diaria"]:
                aviso = "No hay evaluaciones guardadas para este modelo en el período seleccionado."
        except ErrorAPI as error:
            if error.codigo != "MODELO_NO_LISTO":
                raise
            aviso = "Todavía no hay un modelo guardado para consultar su evaluación."
    return {"generado_en": datetime.now(timezone.utc).isoformat(),
            "periodo": {"desde": desde.isoformat(), "hasta": hasta.isoformat(),
                        "dias_calendario": (hasta - desde).days + 1,
                        "ventas_desde": primera.isoformat() if primera else None,
                        "ventas_hasta": ultima.isoformat() if ultima else None,
                        "pedidos_desde": inicio_pedidos.isoformat() if inicio_pedidos else None,
                        "pedidos_hasta": fin_pedidos.isoformat() if fin_pedidos else None},
            "fuentes": FUENTES, "ventas": resumen_ventas(sesion, desde, hasta),
            "pedidos": resumen_pedidos(sesion, desde, hasta),
            "evaluacion": evaluacion, "aviso_evaluacion": aviso}


def _celda(valor):
    if isinstance(valor, str) and valor.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + valor
    return valor


def exportar_csv(reporte: dict, tipo: str) -> bytes:
    if tipo not in {"ventas", "pronosticos", "pedidos"}:
        raise ErrorAPI(422, "TIPO_INFORME_INVALIDO", "Tipo de reporte no admitido.")
    salida = StringIO(newline="")
    escritor = csv.writer(salida, delimiter=";")

    def fila(*valores):
        escritor.writerow([_celda(valor) for valor in valores])

    fila("FoodSave · Reporte", tipo)
    fila("Generado UTC", reporte["generado_en"])
    fila("Desde", reporte["periodo"]["desde"], "Hasta inclusive", reporte["periodo"]["hasta"])
    fila("Fuente", reporte["fuentes"]["evaluacion" if tipo == "pronosticos" else tipo])
    fila("Datos ausentes", "No equivalen a cero; reales desconocidos se exportan vacíos")
    fila()
    if tipo == "ventas":
        fila("Ventas por día", "Unidades", "Productos observados")
        for dia in reporte["ventas"]["serie_diaria"]:
            fila(dia["fecha"], dia["unidades"], dia["productos_observados"])
        fila()
        fila("Producto ID", "Producto", "Unidades", "Días observados")
        for producto in reporte["ventas"]["por_producto"]:
            fila(producto["producto_id"], producto["producto"], producto["unidades"], producto["dias_observados"])
        fila("Total unidades", reporte["ventas"]["unidades"])
    elif tipo == "pedidos":
        fila("Estado actual", "Pedidos")
        for estado in reporte["pedidos"]["por_estado"]:
            fila(ESTADOS[estado["estado"]], estado["cantidad"])
        fila("Total pedidos", reporte["pedidos"]["total"])
        fila("Propuestas sin pedidos", reporte["pedidos"]["propuestas_sin_pedidos"])
        fila()
        fila("Estado de propuesta", "Propuestas")
        for estado in reporte["pedidos"]["propuestas_por_estado"]:
            fila(ESTADOS[estado["estado"]], estado["cantidad"])
    elif tipo == "pronosticos":
        evaluacion = reporte["evaluacion"]
        if evaluacion:
            fila("Modelo ID", evaluacion["modelo_id"], "Versión", evaluacion["version_modelo"])
            for campo in ("pares_evaluables", "productos_excluidos", "cobertura_pct", "mae", "wape_pct"):
                fila(campo, evaluacion["metricas_globales"][campo])
            fila("Fecha", "Producto ID", "Producto", "Pronóstico", "Venta real", "Error absoluto", "Motivo exclusión")
            for dia in evaluacion["serie_diaria"]:
                for producto in dia["desglose_productos"]:
                    fila(dia["fecha_local"], producto["producto_id"], producto.get("producto", ""),
                         producto["previsto"], producto["real"], producto["diferencia_absoluta"],
                         producto.get("motivo_exclusion", ""))
            fila()
            fila("Fecha", "Producto ID sin pronóstico", "Motivo")
            for traza in evaluacion["trazas"]:
                for producto in traza["pronosticos_no_disponibles"]:
                    fila(traza["fecha_local"], producto["producto_id"], producto["estado"])
        if reporte["aviso_evaluacion"]:
            fila("Aviso", reporte["aviso_evaluacion"])
    else:
        raise ErrorAPI(422, "TIPO_INFORME_INVALIDO", "Tipo de reporte no admitido.")
    return salida.getvalue().encode("utf-8-sig")
