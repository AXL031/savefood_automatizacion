"""Inferencia diaria persistida y contrato público para planificación."""

import hashlib
import json
import math
from datetime import date, datetime, timedelta, timezone
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.productos.servicio import listar_skus_bakery
from app.modules.pronosticos.caracteristicas import FEATURES, construir_vector
from app.modules.pronosticos.entrenamiento import _directorio_modelos, _identidad
from app.modules.pronosticos.ml_runtime import preparar_ruta_ml
from app.modules.pronosticos.modelos import ArtefactoModelo, CorridaPronostico, Pronostico
from app.modules.ventas.servicio import leer_historial
from app.workers.retry.politica import ErrorDatos


def modelo_listo(sesion: Session, modelo_id: int | None = None) -> ArtefactoModelo:
    modelo = (sesion.get(ArtefactoModelo, modelo_id) if modelo_id is not None else
              sesion.scalar(select(ArtefactoModelo).where(ArtefactoModelo.estado == "LISTO_DEMO")
                            .order_by(ArtefactoModelo.id.desc()).limit(1)))
    if modelo is None or modelo.estado != "LISTO_DEMO":
        raise ErrorAPI(503, "MODELO_NO_LISTO", "No hay un modelo listo para inferencia.")
    return modelo


def _cargar_cbm(modelo: ArtefactoModelo):
    preparar_ruta_ml()
    from catboost import CatBoostRegressor
    from metadata import ErrorArtefacto, verificar_artefacto_completo

    raiz = _directorio_modelos()
    directorio = (raiz / modelo.ruta_local).resolve()
    if not directorio.is_relative_to(raiz) or directorio == raiz:
        raise ErrorDatos("Ruta de modelo no válida.")
    comercio, sucursal = _identidad()
    try:
        meta = verificar_artefacto_completo(directorio, comercio, sucursal)
        if meta["sha256_artefacto"] != modelo.sha256 or meta["version_modelo"] != modelo.version_modelo:
            raise ErrorArtefacto("La versión o huella no coincide con el registro del modelo.")
        if meta["features"] != FEATURES:
            raise ErrorArtefacto("El orden de características no coincide con el contrato.")
        cbm = CatBoostRegressor()
        cbm.load_model(str(directorio / meta["artefacto"]))
        if list(cbm.feature_names_) != FEATURES:
            raise ErrorArtefacto("El CBM tiene características distintas de sus metadatos.")
    except (ErrorArtefacto, OSError, ValueError) as exc:
        raise ErrorDatos(f"Artefacto no utilizable: {exc}") from exc
    return cbm, meta


def generar_corrida(
    sesion: Session, *, ejecucion_id: int, clave_ejecucion: str, fecha_objetivo: date,
    producto_ids: list[int], tipo: str = "DEMO_PROGRAMADA", modelo_id: int | None = None,
) -> CorridaPronostico:
    """Genera pronósticos o motivos de ausencia; no hace commit ni crea plan."""
    if tipo not in ("BACKTEST", "DEMO_PROGRAMADA") or not producto_ids or len(set(producto_ids)) != len(producto_ids):
        raise ErrorAPI(422, "CORRIDA_INVALIDA", "Tipo o lista de productos inválidos.")
    if not clave_ejecucion or len(clave_ejecucion) > 128:
        raise ErrorAPI(422, "CLAVE_INVALIDA", "Clave de corrida inválida.")
    modelo = modelo_listo(sesion, modelo_id)
    if fecha_objetivo <= modelo.fecha_corte_entrenamiento:
        raise ErrorAPI(422, "FECHA_FUERA_DE_PRUEBA", "La fecha objetivo debe ser posterior al corte del modelo.")
    particion = modelo.particion_json
    if not (date.fromisoformat(particion["inicio_prueba"]) <= fecha_objetivo <= date.fromisoformat(particion["fin_prueba"])):
        raise ErrorAPI(422, "FECHA_FUERA_DE_PRUEBA", "La fecha objetivo debe estar en la prueba reservada.")
    catalogo = listar_skus_bakery(sesion)
    sku_por_id = {producto_id: catalogo[producto_id] for producto_id in producto_ids if producto_id in catalogo}
    if len(sku_por_id) != len(producto_ids):
        raise ErrorAPI(422, "SKU_NO_RESUELTO", "Cada producto debe tener un único SKU bakery activo.")
    historial = leer_historial(sesion, producto_ids, fecha_objetivo - timedelta(days=28), fecha_objetivo)
    por_producto: dict[int, list] = {id_: [] for id_ in producto_ids}
    for venta in historial:
        por_producto[venta.producto_id].append(venta)
    huella = hashlib.sha256(json.dumps({
        "modelo": modelo.id, "fecha": fecha_objetivo.isoformat(), "productos": sorted(producto_ids),
        "ventas": [(v.producto_id, v.fecha_local.isoformat(), v.unidades_vendidas, v.revision_venta_id)
                   for v in historial],
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    anterior = sesion.scalar(select(CorridaPronostico).where(CorridaPronostico.clave_ejecucion == clave_ejecucion))
    if anterior is not None:
        if anterior.huella_datos_entrada != huella or anterior.ejecucion_id != ejecucion_id or anterior.tipo != tipo:
            raise ErrorAPI(409, "CLAVE_REUTILIZADA", "La clave de corrida corresponde a otra entrada.")
        return anterior

    cbm, meta = _cargar_cbm(modelo)
    import numpy as np
    import pandas as pd

    resultados = []
    for producto_id in sorted(producto_ids):
        sku = sku_por_id[producto_id]
        vector = construir_vector(sku, fecha_objetivo, por_producto[producto_id])
        if sku not in meta["productos_entrenados"]:
            estado, cantidad = "PRODUCTO_NO_CUBIERTO", None
        elif vector["conteo_28_dias"] < meta["min_observaciones_previas_28_dias"]:
            estado, cantidad = "HISTORIAL_INSUFICIENTE", None
        else:
            tabla = pd.DataFrame([{clave: np.nan if valor is None else valor
                                   for clave, valor in vector.items()}])[FEATURES]
            prediccion = float(cbm.predict(tabla)[0])
            if not math.isfinite(prediccion):
                raise ErrorDatos("El modelo produjo una predicción no finita.")
            cantidad = int(np.rint(max(0.0, prediccion)))
            if cantidad > 2_147_483_647:
                raise ErrorDatos("El modelo produjo una cantidad fuera de rango.")
            estado = "DISPONIBLE"
        resultados.append((producto_id, estado, cantidad))

    corrida = CorridaPronostico(
        ejecucion_id=ejecucion_id, tipo=tipo, clave_ejecucion=clave_ejecucion,
        huella_datos_entrada=huella, fecha_objetivo=fecha_objetivo, modelo_id=modelo.id,
        estado="COMPLETADA" if any(r[1] == "DISPONIBLE" for r in resultados) else "SIN_COBERTURA",
        finalizado_en=datetime.now(timezone.utc),
    )
    sesion.add(corrida)
    sesion.flush()
    sesion.add_all(Pronostico(
        corrida_id=corrida.id, producto_id=producto_id, estado=estado,
        cantidad_pronosticada=cantidad,
    ) for producto_id, estado, cantidad in resultados)
    sesion.flush()
    return corrida


def obtener_pronosticos(sesion: Session, corrida_id: int) -> list[Pronostico]:
    """Frontera pública para Max: cantidad nullable y motivo por producto."""
    return list(sesion.scalars(select(Pronostico).where(Pronostico.corrida_id == corrida_id)
                               .order_by(Pronostico.producto_id)))


@dataclass(frozen=True)
class CorridaLeida:
    id: int
    ejecucion_id: int
    fecha_objetivo: date
    modelo_id: int
    version_modelo: str
    huella_datos_entrada: str
    tipo: str
    estado: str


def consultar_corrida(sesion: Session, corrida_id: int, *, bloquear: bool = False) -> CorridaLeida:
    """Lectura pública M02; bloqueo opcional serializa los planes de la corrida."""
    consulta = select(CorridaPronostico).where(CorridaPronostico.id == corrida_id)
    if bloquear:
        consulta = consulta.with_for_update()
    corrida = sesion.scalar(consulta)
    if corrida is None:
        raise ErrorAPI(404, "CORRIDA_NO_ENCONTRADA", "La corrida no existe.")
    modelo = sesion.get(ArtefactoModelo, corrida.modelo_id)
    return CorridaLeida(corrida.id, corrida.ejecucion_id, corrida.fecha_objetivo,
                       modelo.id, modelo.version_modelo, corrida.huella_datos_entrada,
                       corrida.tipo, corrida.estado)
