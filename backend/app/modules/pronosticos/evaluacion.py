"""Evaluación posterior a inferencia, con revisión de venta conservada."""

import hashlib
import json
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion
from app.modules.pronosticos.ml_runtime import preparar_ruta_ml
from app.modules.pronosticos.modelos import ArtefactoModelo, CorridaPronostico, EvaluacionPronostico, Pronostico
from app.modules.pronosticos.servicio import generar_corrida, obtener_pronosticos
from app.modules.productos.servicio import listar_skus_bakery, nombres_productos
from app.modules.ventas.servicio import leer_historial


def _reales_actuales(sesion: Session, corrida: CorridaPronostico, ids: list[int]):
    return {v.producto_id: v for v in leer_historial(
        sesion, ids, corrida.fecha_objetivo, corrida.fecha_objetivo + timedelta(days=1)
    )}


def solicitar_evaluacion_corrida(sesion: Session, corrida_id: int):
    """Max llama esto tras guardar su plan, en la misma sesión y sin commit."""
    corrida = sesion.get(CorridaPronostico, corrida_id)
    if corrida is None:
        raise ErrorAPI(404, "CORRIDA_NO_ENCONTRADA", "La corrida no existe.")
    pronosticos = obtener_pronosticos(sesion, corrida_id)
    reales = _reales_actuales(sesion, corrida, [p.producto_id for p in pronosticos])
    revisiones = sorted((id_, venta.revision_venta_id) for id_, venta in reales.items())
    huella = hashlib.sha256(json.dumps(revisiones).encode("utf-8")).hexdigest()[:12]
    return crear_o_recuperar_ejecucion(
        sesion, "EVALUAR_PRONOSTICO", f"evaluar-corrida-{corrida_id}-{huella}",
        {"corrida_id": corrida_id, "revisiones": revisiones},
    )


def evaluar_corrida(sesion: Session, corrida_id: int, ejecucion_id: int) -> dict:
    """Evalúa únicamente pares con pronóstico y venta real conocida."""
    corrida = sesion.get(CorridaPronostico, corrida_id)
    if corrida is None:
        raise ErrorAPI(404, "CORRIDA_NO_ENCONTRADA", "La corrida no existe.")
    pronosticos = obtener_pronosticos(sesion, corrida_id)
    reales = _reales_actuales(sesion, corrida, [p.producto_id for p in pronosticos])
    creadas = 0
    for pronostico in pronosticos:
        real = reales.get(pronostico.producto_id)
        if pronostico.estado != "DISPONIBLE" or real is None:
            continue
        anterior = sesion.scalar(select(EvaluacionPronostico.id).where(
            EvaluacionPronostico.corrida_id == corrida_id,
            EvaluacionPronostico.producto_id == pronostico.producto_id,
            EvaluacionPronostico.revision_venta_id == real.revision_venta_id,
        ))
        if anterior is not None:
            continue
        previsto = pronostico.cantidad_pronosticada
        sesion.add(EvaluacionPronostico(
            ejecucion_id=ejecucion_id, corrida_id=corrida_id, pronostico_id=pronostico.id,
            revision_venta_id=real.revision_venta_id, producto_id=pronostico.producto_id,
            cantidad_pronosticada=previsto, unidades_reales=real.unidades_vendidas,
            error_absoluto=abs(previsto - real.unidades_vendidas),
        ))
        creadas += 1
    sesion.flush()
    return {"corrida_id": corrida_id, "evaluaciones_nuevas": creadas,
            "productos_pronosticados": sum(p.estado == "DISPONIBLE" for p in pronosticos)}


def evaluar_modelo(sesion: Session, modelo_id: int, ejecucion_id: int) -> dict:
    """Backtest cronológico en el tramo reservado, idempotente por fecha."""
    modelo = sesion.get(ArtefactoModelo, modelo_id)
    if modelo is None:
        raise ErrorAPI(404, "MODELO_NO_ENCONTRADO", "El modelo no existe.")
    desde = date.fromisoformat(modelo.particion_json["inicio_prueba"])
    hasta = date.fromisoformat(modelo.particion_json["fin_prueba"])
    productos = list(listar_skus_bakery(sesion))
    if not productos:
        raise ErrorAPI(422, "CATALOGO_FALTANTE", "No hay productos para evaluar.")
    fecha = desde
    corridas = 0
    while fecha <= hasta:
        corrida = generar_corrida(
            sesion, ejecucion_id=ejecucion_id,
            clave_ejecucion=f"backtest-{modelo.id}-{fecha.isoformat()}",
            fecha_objetivo=fecha, producto_ids=productos, tipo="BACKTEST", modelo_id=modelo.id,
        )
        evaluar_corrida(sesion, corrida.id, ejecucion_id)
        corridas += 1
        fecha += timedelta(days=1)
    reporte = resumen_evaluacion(sesion, modelo.id)
    modelo.metricas_json = reporte["metricas_globales"]
    return {"modelo_id": modelo.id, "corridas_backtest": corridas,
            "pares_evaluables": reporte["metricas_globales"]["pares_evaluables"]}


def detalle_evaluacion(sesion: Session, corrida: CorridaPronostico) -> dict:
    preparar_ruta_ml()
    from evaluador import evaluar_dia
    from metricas import ParEvaluacion

    pronosticos = obtener_pronosticos(sesion, corrida.id)
    vigentes = _reales_actuales(sesion, corrida, [p.producto_id for p in pronosticos])
    revisiones = [venta.revision_venta_id for venta in vigentes.values()]
    actuales = dict(sesion.execute(
        select(EvaluacionPronostico.producto_id, EvaluacionPronostico.unidades_reales)
        .where(EvaluacionPronostico.corrida_id == corrida.id,
               EvaluacionPronostico.revision_venta_id.in_(revisiones))
    ).all()) if revisiones else {}
    pares = [ParEvaluacion(str(p.producto_id), corrida.fecha_objetivo.isoformat(),
                           float(p.cantidad_pronosticada),
                           float(actuales[p.producto_id]) if p.producto_id in actuales else None)
             for p in pronosticos if p.estado == "DISPONIBLE"]
    resultado = evaluar_dia(corrida.fecha_objetivo.isoformat(), pares).as_dict()
    nombres = nombres_productos(sesion, [p.producto_id for p in pronosticos])
    for producto in resultado["desglose_productos"]:
        producto_id = int(producto["producto_id"])
        producto["producto"] = nombres.get(producto_id, f"Producto #{producto_id}")
    resultado["corrida_id"] = corrida.id
    resultado["pronosticos_no_disponibles"] = [
        {"producto_id": p.producto_id, "estado": p.estado} for p in pronosticos if p.estado != "DISPONIBLE"
    ]
    return resultado


def resumen_evaluacion(sesion: Session, modelo_id: int | None = None, *,
                       desde: date | None = None, hasta: date | None = None) -> dict:
    preparar_ruta_ml()
    from evaluador import consolidar_evaluacion_tramo
    from metricas import ParEvaluacion

    modelo = (sesion.get(ArtefactoModelo, modelo_id) if modelo_id is not None else
              sesion.scalar(select(ArtefactoModelo).order_by(ArtefactoModelo.id.desc()).limit(1)))
    if modelo is None:
        if modelo_id is not None:
            raise ErrorAPI(404, "MODELO_NO_ENCONTRADO", "El modelo seleccionado no existe.")
        raise ErrorAPI(503, "MODELO_NO_LISTO", "No hay modelo para evaluar.")
    consulta = select(CorridaPronostico).where(
        CorridaPronostico.modelo_id == modelo.id, CorridaPronostico.tipo == "BACKTEST",
        CorridaPronostico.clave_ejecucion.like(f"backtest-{modelo.id}-%"),
    )
    if desde is not None:
        consulta = consulta.where(CorridaPronostico.fecha_objetivo >= desde)
    if hasta is not None:
        consulta = consulta.where(CorridaPronostico.fecha_objetivo <= hasta)
    corridas = list(sesion.scalars(consulta.order_by(CorridaPronostico.fecha_objetivo)))
    pares = []
    dias = []
    trazas = []
    for corrida in corridas:
        detalle = detalle_evaluacion(sesion, corrida)
        dias.append({campo: valor for campo, valor in detalle.items()
                     if campo not in ("corrida_id", "pronosticos_no_disponibles")})
        trazas.append({"fecha_local": detalle["fecha_local"], "corrida_id": corrida.id,
                       "pronosticos_no_disponibles": detalle["pronosticos_no_disponibles"]})
        for producto in detalle["desglose_productos"]:
            pares.append(ParEvaluacion(producto["producto_id"], detalle["fecha_local"],
                                       producto["previsto"], producto["real"]))
    resultado = consolidar_evaluacion_tramo(
        modelo.version_modelo, desde.isoformat() if desde else modelo.particion_json["inicio_prueba"],
        hasta.isoformat() if hasta else modelo.particion_json["fin_prueba"], pares,
    ).as_dict()
    resultado["serie_diaria"] = dias
    resultado["fechas_evaluadas"] = sum(dia["productos_evaluables"] > 0 for dia in dias)
    resultado["modelo_id"] = modelo.id
    resultado["particion"] = modelo.particion_json
    resultado["trazas"] = trazas
    return resultado
