"""Ejecutor de backtest y evaluación histórica del modelo CatBoost según POLITICA_EVALUACION.md.

Automatiza la comprobación histórica:
  1. Carga y valida el artefacto CBM y su metadata.
  2. Lee la partición temporal para identificar el tramo de prueba reservado (inicio_prueba a fin_prueba).
  3. Para cada fecha del tramo de prueba:
     - Realiza un pronóstico un día adelante usando SOLO ventas fechadas antes de ese día.
     - Aplica límite mínimo cero (max(0, pred)) y redondeo al entero más cercano con np.rint.
     - Contrasta la predicción contra la venta real observada si existe.
  4. Consolida métricas completas del tramo y desglose diario para el dashboard K04.

Uso:
  python foodsave-ml/ejecutar_backtest.py \\
      --artefacto-dir /ruta/a/model_artifacts \\
      --csv ventas_diarias_normalizadas.csv \\
      --salida reporte_evaluacion.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

from features import construir_features, FEATURES
from metadata import verificar_artefacto_completo, ErrorArtefacto
from metricas import ParEvaluacion
from evaluador import consolidar_evaluacion_tramo


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--artefacto-dir",
        required=True,
        type=Path,
        help="Directorio con catboost_model.cbm y metadata.json",
    )
    parser.add_argument(
        "--csv",
        required=True,
        type=Path,
        help="CSV con ventas diarias normalizadas",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=None,
        help="Ruta opcional para guardar el JSON con los resultados de la evaluación",
    )
    return parser.parse_args()


def ejecutar_backtest(
    artefacto_dir: Path,
    csv_path: Path,
) -> dict:
    """Ejecuta el backtest completo sobre el tramo de prueba reservado.

    Returns:
        Diccionario serializable con el reporte consolidado de evaluación.
    """
    # 1. Validar e inspeccionar el artefacto
    meta = verificar_artefacto_completo(artefacto_dir)
    comercio_id = meta["comercio_id"]
    sucursal_id = meta["sucursal_id"]
    version_modelo = meta["version_modelo"]
    particion = meta["particion"]
    inicio_prueba = particion["inicio_prueba"]
    fin_prueba = particion["fin_prueba"]

    # 2. Cargar el modelo CBM
    ruta_cbm = artefacto_dir / meta.get("artefacto", "catboost_model.cbm")
    modelo = CatBoostRegressor()
    modelo.load_model(str(ruta_cbm))

    # 3. Construir features para todo el tramo de prueba
    # construir_features asegura ventanas por días calendario y ausencia de fuga temporal
    df_features = construir_features(
        csv_path=csv_path,
        comercio_id=comercio_id,
        sucursal_id=sucursal_id,
        inicio=inicio_prueba,
        fin=fin_prueba,
    )

    # 4. Inferencia con CatBoost
    X_test = df_features[FEATURES]
    predicciones_raw = modelo.predict(X_test)

    # Regla contractual: mínimo cero y redondeo con np.rint (empate al par)
    predicciones = np.rint(np.maximum(0.0, predicciones_raw))

    # 5. Armar pares de evaluación (conservando ausencias como None)
    pares: list[ParEvaluacion] = []
    for idx, fila in df_features.iterrows():
        p_id = str(fila["article"])
        f_local = pd.to_datetime(fila["fecha_objetivo"]).strftime("%Y-%m-%d")
        pred_val = float(predicciones[idx])
        real_val = (
            float(fila["unidades_vendidas"])
            if pd.notna(fila["unidades_vendidas"])
            else None
        )
        pares.append(
            ParEvaluacion(
                producto_id=p_id,
                fecha_local=f_local,
                previsto=pred_val,
                real=real_val,
            )
        )

    # 6. Consolidar evaluación del tramo completo sin promediar porcentajes
    resultado = consolidar_evaluacion_tramo(
        version_modelo=version_modelo,
        fecha_inicio=inicio_prueba,
        fecha_fin=fin_prueba,
        pares_todos=pares,
    )

    return resultado.as_dict()


def main() -> None:
    args = _args()

    if not args.csv.exists():
        print(f"[ERROR] No existe el archivo CSV: {args.csv}", file=sys.stderr)
        sys.exit(1)

    try:
        resultado = ejecutar_backtest(args.artefacto_dir, args.csv)
    except ErrorArtefacto as exc:
        print(f"[ERROR] Artefacto no válido: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"[ERROR] Falló la ejecución del backtest: {exc}", file=sys.stderr)
        sys.exit(1)

    m = resultado["metricas_globales"]
    print("=" * 65)
    print("  RESULTADOS DE EVALUACIÓN HISTÓRICA (K03)")
    print("=" * 65)
    print(f"  Versión modelo:          {resultado['version_modelo']}")
    print(f"  Tramo evaluado:          {resultado['fecha_inicio']} a {resultado['fecha_fin']}")
    print(f"  Fechas evaluadas:        {resultado['fechas_evaluadas']}")
    print(f"  Pares evaluables:        {resultado['total_pares_evaluables']}")
    print(f"  Cobertura:               {m['cobertura_pct']}%")
    print(f"  MAE (unidades):          {m['mae']}")
    print(f"  WAPE (% error):          {m['wape_pct']}%")
    print(f"  Dentro de ±20%:          {m['dentro_mas_menos_20_pct']}%")
    print(f"  Dentro de ±10%:          {m['dentro_mas_menos_10_pct']}%")
    print("=" * 65)

    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        args.salida.write_text(
            json.dumps(resultado, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"[INFO] Reporte exportado a: {args.salida}")


if __name__ == "__main__":
    main()
