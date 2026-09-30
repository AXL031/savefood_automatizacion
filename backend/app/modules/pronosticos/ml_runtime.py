"""Importa la implementación ML compartida incluida en la imagen backend."""

import sys
from pathlib import Path


def preparar_ruta_ml() -> None:
    padres = Path(__file__).resolve().parents
    ruta = next((candidato for candidato in
                 (padres[3] / "foodsave-ml", padres[4] / "foodsave-ml") if candidato.is_dir()), None)
    if ruta is None:
        raise RuntimeError("No se encuentra foodsave-ml junto al backend")
    if str(ruta) not in sys.path:
        sys.path.insert(0, str(ruta))
