"""Entrena el modelo CatBoost fuera de Colab y exporta el artefacto listo para el backend.

Uso:
  python foodsave-ml/entrenar.py --csv ventas_diarias_normalizadas.csv \\
      --comercio piloto --sucursal principal \\
      --salida /ruta/a/model_artifacts

El CSV de entrada debe estar normalizado con normalizar_ventas.py (columnas:
comercio_id, sucursal_id, fecha_local, producto_id, unidades_vendidas).

El script escribe de forma atómica:
  <salida>/catboost_model.cbm
  <salida>/metadata.json

La escritura es atómica: primero a archivos temporales y luego rename,
de modo que el directorio no queda en estado intermedio si se interrumpe.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from particion import calcular_particion
from features import construir_features, FEATURES
from artefacto import entrenar_y_exportar


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--csv",
        required=True,
        type=Path,
        help="CSV normalizado con columnas: comercio_id, sucursal_id, "
             "fecha_local, producto_id, unidades_vendidas",
    )
    parser.add_argument(
        "--comercio",
        required=True,
        help="ID del comercio a entrenar (debe existir en el CSV)",
    )
    parser.add_argument(
        "--sucursal",
        required=True,
        help="ID de la sucursal a entrenar (debe existir en el CSV)",
    )
    parser.add_argument(
        "--salida",
        required=True,
        type=Path,
        help="Directorio de salida donde se escriben catboost_model.cbm y metadata.json",
    )
    parser.add_argument(
        "--version",
        default="1.0.0",
        help="Versión del modelo (por defecto: 1.0.0)",
    )
    return parser.parse_args()


def main() -> None:
    args = _args()

    if not args.csv.exists():
        print(f"[ERROR] No se encontró el CSV: {args.csv}", file=sys.stderr)
        sys.exit(1)

    args.salida.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Cargando ventas desde: {args.csv}")
    print(f"[INFO] Comercio: {args.comercio} | Sucursal: {args.sucursal}")
    print(f"[INFO] Directorio de salida: {args.salida}")

    # 1. Calcular partición temporal según POLITICA_EVALUACION.md
    particion = calcular_particion(
        csv_path=args.csv,
        comercio_id=args.comercio,
        sucursal_id=args.sucursal,
    )
    print(f"[INFO] Partición calculada: {particion}")

    # 2. Construir features y entrenar
    ruta_cbm, ruta_metadata = entrenar_y_exportar(
        csv_path=args.csv,
        comercio_id=args.comercio,
        sucursal_id=args.sucursal,
        particion=particion,
        salida=args.salida,
        version=args.version,
    )

    print(f"[OK] Artefacto exportado:")
    print(f"     CBM:      {ruta_cbm}")
    print(f"     Metadata: {ruta_metadata}")


if __name__ == "__main__":
    main()
