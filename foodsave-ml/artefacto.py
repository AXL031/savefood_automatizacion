"""Entrenamiento CatBoost y exportación atómica del artefacto ML.

Produce:
  <salida>/catboost_model.cbm   — modelo entrenado
  <salida>/metadata.json        — metadatos exigidos por el contrato

La escritura es atómica: se guarda primero en archivos temporales dentro
del mismo directorio y luego se hace rename() para que nunca quede un
estado intermedio visible en caso de interrupción.

Ver: foodsave-ml/CONTRATO_ARTEFACTO_INFERENCIA.md
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor, Pool

from features import construir_features, FEATURES, CAT_FEATURES
from particion import Particion

# Mínimo de observaciones en los 28 días anteriores para incluir una fila en entrenamiento
MIN_OBSERVACIONES_28_DIAS = 7

# Objetivo de entrenamiento (Quantile:alpha=0.65 según EXPERIMENTOS_CATBOOST.md)
OBJETIVO = "Quantile:alpha=0.65"


def _filtrar_entrenables(df: pd.DataFrame) -> pd.DataFrame:
    """Conserva solo filas con suficiente historial y venta real conocida."""
    mask = (
        df["conteo_28_dias"] >= MIN_OBSERVACIONES_28_DIAS
    ) & df["unidades_vendidas"].notna()
    return df.loc[mask].copy()


def _sha256(ruta: Path) -> str:
    """Calcula SHA-256 del archivo en `ruta`."""
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def entrenar_y_exportar(
    csv_path: Path,
    comercio_id: str,
    sucursal_id: str,
    particion: Particion,
    salida: Path,
    version: str = "1.0.0",
) -> tuple[Path, Path]:
    """Entrena CatBoost con los datos de entrenamiento/validación y exporta el artefacto.

    Args:
        csv_path: CSV normalizado.
        comercio_id: ID del comercio.
        sucursal_id: ID de la sucursal.
        particion: Partición temporal calculada por calcular_particion().
        salida: Directorio destino para catboost_model.cbm y metadata.json.
        version: Cadena de versión del modelo (ej. "1.0.0").

    Returns:
        Tupla (ruta_cbm, ruta_metadata).

    Raises:
        ValueError: Si no hay filas entrenables tras aplicar los filtros.
    """
    print("[INFO] Construyendo features de entrenamiento…")
    df_train = construir_features(
        csv_path, comercio_id, sucursal_id,
        inicio=particion.inicio_entrenamiento,
        fin=particion.fin_entrenamiento,
    )

    print("[INFO] Construyendo features de validación…")
    df_val = construir_features(
        csv_path, comercio_id, sucursal_id,
        inicio=particion.inicio_validacion,
        fin=particion.fin_validacion,
    )

    df_train_f = _filtrar_entrenables(df_train)
    df_val_f = _filtrar_entrenables(df_val)

    if df_train_f.empty:
        raise ValueError(
            "No hay filas entrenables en el tramo de entrenamiento. "
            f"Verifica que haya productos con al menos {MIN_OBSERVACIONES_28_DIAS} "
            "observaciones en 28 días."
        )

    X_train = df_train_f[FEATURES]
    y_train = df_train_f["unidades_vendidas"].values

    cat_idxs = [FEATURES.index(c) for c in CAT_FEATURES]

    pool_train = Pool(data=X_train, label=y_train, cat_features=cat_idxs)

    eval_set = None
    if not df_val_f.empty:
        X_val = df_val_f[FEATURES]
        y_val = df_val_f["unidades_vendidas"].values
        eval_set = Pool(data=X_val, label=y_val, cat_features=cat_idxs)

    print(f"[INFO] Entrenando CatBoost (objetivo={OBJETIVO}, "
          f"filas_train={len(df_train_f)}, filas_val={len(df_val_f)})…")

    modelo = CatBoostRegressor(
        loss_function=OBJETIVO,
        eval_metric="MAE",
        iterations=1000,
        learning_rate=0.05,
        depth=6,
        early_stopping_rounds=50,
        verbose=100,
        random_seed=42,
    )
    modelo.fit(pool_train, eval_set=eval_set, use_best_model=(eval_set is not None))

    # Verificar que el orden de features grabado en el CBM coincide con el contrato
    features_en_modelo = list(modelo.feature_names_)
    if features_en_modelo != FEATURES:
        raise RuntimeError(
            f"El modelo grabó features en orden diferente al contrato.\n"
            f"  Modelo: {features_en_modelo}\n"
            f"Contrato: {FEATURES}"
        )

    # Exportar CBM de forma atómica
    salida.mkdir(parents=True, exist_ok=True)
    ruta_cbm_final = salida / "catboost_model.cbm"

    with tempfile.NamedTemporaryFile(
        dir=salida, suffix=".cbm", delete=False
    ) as tmp_cbm:
        ruta_tmp_cbm = Path(tmp_cbm.name)

    try:
        modelo.save_model(str(ruta_tmp_cbm))
        ruta_tmp_cbm.replace(ruta_cbm_final)  # atómico en mismo filesystem
    except Exception:
        ruta_tmp_cbm.unlink(missing_ok=True)
        raise

    print(f"[INFO] CBM exportado → {ruta_cbm_final}")

    # Calcular huella SHA-256
    sha256 = _sha256(ruta_cbm_final)

    # SKUs conocidos por el modelo
    productos_entrenados = sorted(df_train_f["article"].unique().tolist())

    # Metadata completa según contrato
    metadata = {
        "estado": "listo_demo",
        "version_modelo": version,
        "comercio_id": comercio_id,
        "sucursal_id": sucursal_id,
        "artefacto": "catboost_model.cbm",
        "sha256_artefacto": sha256,
        "fecha_corte_entrenamiento": particion.fin_validacion,
        "particion": particion.as_dict(),
        "features": FEATURES,
        "cat_features": CAT_FEATURES,
        "productos_entrenados": productos_entrenados,
        "min_observaciones_previas_28_dias": MIN_OBSERVACIONES_28_DIAS,
        "horizonte": "un_dia_con_historial_real",
        "politica_ausencias": "desconocido",
        "objetivo_entrenamiento": OBJETIVO,
        "nota": (
            "Artefacto para demostración histórica local. "
            "No equivale a aprobación comercial."
        ),
    }

    # Exportar metadata de forma atómica
    ruta_meta_final = salida / "metadata.json"
    with tempfile.NamedTemporaryFile(
        dir=salida, suffix=".json", delete=False, mode="w", encoding="utf-8"
    ) as tmp_meta:
        ruta_tmp_meta = Path(tmp_meta.name)
        json.dump(metadata, tmp_meta, ensure_ascii=False, indent=2)
        tmp_meta.write("\n")

    try:
        ruta_tmp_meta.replace(ruta_meta_final)
    except Exception:
        ruta_tmp_meta.unlink(missing_ok=True)
        raise

    print(f"[INFO] Metadata exportada → {ruta_meta_final}")
    print(f"[INFO] SHA-256: {sha256}")
    print(f"[INFO] Productos entrenados: {len(productos_entrenados)}")

    return ruta_cbm_final, ruta_meta_final
