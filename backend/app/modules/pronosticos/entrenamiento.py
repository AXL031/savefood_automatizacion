"""Entrenamiento sobre ventas confirmadas en PostgreSQL, sin leer el CSV original."""

import csv
import hashlib
import json
import os
import re
import tempfile
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion
from app.modules.productos.servicio import listar_skus_bakery
from app.modules.pronosticos.ml_runtime import preparar_ruta_ml
from app.modules.pronosticos.modelos import ArtefactoModelo
from app.modules.ventas.servicio import leer_historial, limites_historial
from app.workers.retry.politica import ErrorDatos


def _identidad() -> tuple[str, str]:
    return os.getenv("ML_COMERCIO_ID", "piloto"), os.getenv("ML_SUCURSAL_ID", "principal")


def _directorio_modelos() -> Path:
    ruta = Path(os.environ["MODEL_ARTIFACT_DIR"]).resolve()
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta


def _ventas_para_entrenamiento(sesion: Session):
    ids = list(listar_skus_bakery(sesion))
    limites = limites_historial(sesion, ids)
    if not ids or limites[0] is None:
        raise ErrorDatos("No hay ventas locales para entrenar el modelo.")
    return leer_historial(sesion, ids, limites[0], limites[1] + timedelta(days=1))


def preparar_modelo(sesion: Session, *, version: str, ejecucion_id: int, clave_evaluacion: str | None = None) -> ArtefactoModelo:
    """Registra un CBM versionado y agenda su evaluación; no hace commit."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", version):
        raise ErrorDatos("La versión del modelo contiene caracteres no válidos.")
    ventas = _ventas_para_entrenamiento(sesion)
    comercio, sucursal = _identidad()
    huella = hashlib.sha256(json.dumps(
        [(v.producto_id, v.sku_externo, v.fecha_local.isoformat(), v.unidades_vendidas, v.revision_venta_id)
         for v in ventas], separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()
    existente = sesion.scalar(select(ArtefactoModelo).where(ArtefactoModelo.version_modelo == version))
    if existente is not None:
        if existente.huella_datos_entrenamiento != huella:
            raise ErrorDatos("La versión del modelo ya corresponde a otro historial.")
        if clave_evaluacion:
            crear_o_recuperar_ejecucion(sesion, "EVALUAR_MODELO", clave_evaluacion, {"modelo_id": existente.id})
        return existente

    preparar_ruta_ml()
    from artefacto import entrenar_y_exportar
    from metadata import verificar_artefacto_completo
    from particion import calcular_particion

    raiz = _directorio_modelos()
    nombre = f"{version}-{huella[:12]}"
    destino = raiz / nombre
    with tempfile.TemporaryDirectory(prefix="foodsave-ml-") as temporal:
        csv_path = Path(temporal) / "ventas.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["comercio_id", "sucursal_id", "fecha_local", "producto_id", "unidades_vendidas"])
            escritor.writerows((comercio, sucursal, v.fecha_local.isoformat(), v.sku_externo, v.unidades_vendidas) for v in ventas)
        if not destino.exists():
            try:
                particion = calcular_particion(csv_path, comercio, sucursal)
            except ValueError as exc:
                raise ErrorDatos(str(exc)) from exc
            staging = raiz / f".staging-{version}-{huella[:12]}-{uuid4().hex}"
            staging.mkdir()
            try:
                entrenar_y_exportar(csv_path, comercio, sucursal, particion, staging, version)
                metadata_path = staging / "metadata.json"
                meta = json.loads(metadata_path.read_text(encoding="utf-8"))
                meta["huella_datos_entrenamiento"] = huella
                metadata_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                staging.rename(destino)
            except Exception:
                # Se conserva staging para diagnosticar una interrupción; no se publica como modelo listo.
                raise
    meta = verificar_artefacto_completo(destino, comercio, sucursal)
    if meta.get("huella_datos_entrenamiento") != huella:
        raise ErrorDatos("El artefacto existente no corresponde al historial actual.")
    artefacto = ArtefactoModelo(
        version_modelo=version, ruta_local=nombre, sha256=meta["sha256_artefacto"],
        huella_datos_entrenamiento=huella,
        fecha_corte_entrenamiento=date.fromisoformat(meta["fecha_corte_entrenamiento"]),
        particion_json=meta["particion"], estado="LISTO_DEMO",
    )
    sesion.add(artefacto)
    sesion.flush()
    crear_o_recuperar_ejecucion(
        sesion, "EVALUAR_MODELO", clave_evaluacion or f"evaluar-modelo-{version}-{huella[:12]}",
        {"modelo_id": artefacto.id},
    )
    return artefacto
