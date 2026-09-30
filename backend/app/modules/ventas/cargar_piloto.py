"""Carga explícita de productos y ventas bakery para desarrollo local.

Ejemplo desde backend/: python -m app.modules.ventas.cargar_piloto
  --productos ../foodsave-ml/lista_productos_precios_limpia.md
  --ventas ../foodsave-ml/bakery_sales_limpio_final.csv
  --clave piloto-bakery-v1
"""

import argparse
from pathlib import Path

from app.core.base_datos import SessionLocal
from app.modules.productos.servicio import cargar_catalogo_bakery
from app.modules.ventas.servicio import importar_bakery


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga local explícita del historial bakery")
    parser.add_argument("--productos", type=Path, required=True)
    parser.add_argument("--ventas", type=Path, required=True)
    parser.add_argument("--clave", required=True)
    args = parser.parse_args()
    with SessionLocal.begin() as sesion:
        productos = cargar_catalogo_bakery(sesion, args.productos)
        resultado = importar_bakery(sesion, args.ventas, args.clave)
    print(f"Productos: {productos}; importación: {resultado.importacion_id}; "
          f"filas aceptadas: {resultado.filas_aceptadas}; "
          f"negativas excluidas: {resultado.filas_negativas_excluidas}; "
          f"ventas diarias creadas: {resultado.ventas_diarias}")


if __name__ == "__main__":
    main()
