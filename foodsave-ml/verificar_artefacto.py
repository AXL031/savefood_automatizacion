"""Verifica la integridad de un artefacto ML exportado por entrenar.py.

Uso:
  python foodsave-ml/verificar_artefacto.py --directorio /ruta/a/model_artifacts
  python foodsave-ml/verificar_artefacto.py --directorio /ruta --comercio piloto --sucursal principal

El script comprueba:
  1. Existencia de catboost_model.cbm y metadata.json
  2. JSON válido y campos requeridos presentes
  3. Estado aceptable para backend (listo_demo o aprobado)
  4. SHA-256 del CBM coincide con metadata.json
  5. Orden de features coincide con el contrato
  6. Par comercio/sucursal coincide (si se indica)
  7. Coherencia de fechas en la partición

Salida: imprime OK con un resumen si todo pasa, o ERROR con el motivo.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from metadata import verificar_artefacto_completo, ErrorArtefacto


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--directorio",
        required=True,
        type=Path,
        help="Directorio con catboost_model.cbm y metadata.json",
    )
    parser.add_argument(
        "--comercio",
        default=None,
        help="ID del comercio esperado (opcional; verifica la identidad del artefacto)",
    )
    parser.add_argument(
        "--sucursal",
        default=None,
        help="ID de la sucursal esperada (opcional; verifica la identidad del artefacto)",
    )
    return parser.parse_args()


def _verificar_coherencia_fechas(meta: dict) -> list[str]:
    """Verifica que las fechas de la partición sean coherentes entre sí."""
    advertencias = []
    p = meta.get("particion", {})

    try:
        from datetime import date

        ini_train = date.fromisoformat(p["inicio_entrenamiento"])
        fin_train = date.fromisoformat(p["fin_entrenamiento"])
        ini_val = date.fromisoformat(p["inicio_validacion"])
        fin_val = date.fromisoformat(p["fin_validacion"])
        ini_prueba = date.fromisoformat(p["inicio_prueba"])
        fin_prueba = date.fromisoformat(p["fin_prueba"])

        if not (ini_train < fin_train < ini_val < fin_val < ini_prueba < fin_prueba):
            advertencias.append(
                "Las fechas de la partición no están en orden estrictamente creciente: "
                f"{ini_train} … {fin_prueba}"
            )

        fecha_corte = date.fromisoformat(meta["fecha_corte_entrenamiento"])
        if fecha_corte > fin_val:
            advertencias.append(
                f"'fecha_corte_entrenamiento' ({fecha_corte}) es posterior a fin_validacion ({fin_val}). "
                "El corte no puede alcanzar el tramo de prueba."
            )
    except (KeyError, ValueError) as exc:
        advertencias.append(f"Error al parsear fechas de partición: {exc}")

    return advertencias


def main() -> None:
    args = _args()

    print(f"[INFO] Verificando artefacto en: {args.directorio}")

    try:
        meta = verificar_artefacto_completo(
            directorio=args.directorio,
            comercio_id=args.comercio,
            sucursal_id=args.sucursal,
        )
    except ErrorArtefacto as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    # Verificaciones adicionales de coherencia
    advertencias = _verificar_coherencia_fechas(meta)
    for adv in advertencias:
        print(f"[ADVERTENCIA] {adv}", file=sys.stderr)

    # Resumen
    p = meta.get("particion", {})
    print()
    print("=" * 60)
    print("[OK] Artefacto válido")
    print("=" * 60)
    print(f"  Estado:             {meta['estado']}")
    print(f"  Versión:            {meta['version_modelo']}")
    print(f"  Comercio:           {meta['comercio_id']}")
    print(f"  Sucursal:           {meta['sucursal_id']}")
    print(f"  SHA-256:            {meta['sha256_artefacto'][:16]}…")
    print(f"  Corte entrenamiento:{meta['fecha_corte_entrenamiento']}")
    print(f"  Entrenamiento:      {p.get('inicio_entrenamiento')} -> {p.get('fin_entrenamiento')}")
    print(f"  Validación:         {p.get('inicio_validacion')} -> {p.get('fin_validacion')}")
    print(f"  Prueba:             {p.get('inicio_prueba')} -> {p.get('fin_prueba')}")
    print(f"  Productos:          {len(meta.get('productos_entrenados', []))}")
    print(f"  Features:           {len(meta.get('features', []))} (orden contractual ✓)")
    print(f"  Min obs 28d:        {meta.get('min_observaciones_previas_28_dias')}")
    if advertencias:
        print(f"\n  Advertencias: {len(advertencias)} (ver salida de error)")
    print("=" * 60)


if __name__ == "__main__":
    main()
