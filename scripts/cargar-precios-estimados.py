"""Carga administrativa explícita de estimaciones PEN mediante el servicio de Ventas.

Ejecutar dentro del entorno backend con DATABASE_URL configurada. Sin --aplicar,
solo valida/describe; no modifica precios, stock, tickets ni histórico.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

from app.principal import app  # noqa: F401; registra todos los modelos
from app.core.base_datos import SessionLocal
from app.core.errores import ErrorAPI
from app.modules.autenticacion.modelos import Usuario
from app.modules.ventas.caja import catalogo_caja, guardar_precio
from app.modules.ventas.esquemas_caja import PrecioCrear


def cargar(sesion, archivo, usuario_id, aplicar=False):
    usuario = sesion.get(Usuario, usuario_id)
    if not usuario or not usuario.activo or usuario.rol != "ADMINISTRADOR":
        raise ValueError("Indica el ID de un administrador activo para auditar la carga.")
    contenido = Path(archivo).read_bytes()
    with Path(archivo).open(encoding="utf-8-sig", newline="") as f:
        filas = list(csv.DictReader(f))
    if not filas:
        raise ValueError("El archivo de estimaciones está vacío.")
    por_codigo = {f["codigo"]: f for f in filas}
    if len(por_codigo) != len(filas):
        raise ValueError("Hay códigos repetidos en las estimaciones.")
    catalogo = catalogo_caja(sesion)
    productos = catalogo["productos"]
    if set(por_codigo) != {p["codigo"] for p in productos}:
        raise ValueError("El archivo debe cubrir exactamente el catálogo activo actual.")
    huella = hashlib.sha256(contenido).hexdigest()[:16]
    plan, conservados = [], 0
    # Validar TODO antes de insertar el primer precio. Orden global por producto.
    for p in sorted(productos, key=lambda p: p["id"]):
        fila = por_codigo[p["codigo"]]
        if fila["moneda"] != "PEN" or fila["nombre"] != p["nombre"]:
            raise ValueError(f"Moneda o identidad no coincide: {p['codigo']}")
        entrada = PrecioCrear(clave_idempotencia=f"estimado-{huella}-{p['codigo']}",
                              precio=fila["precio_pen"], version_actual=0)
        if p["precio"] is not None:
            conservados += 1
        else:
            plan.append((p["id"], entrada))
    if aplicar:
        for id_, entrada in plan:
            guardar_precio(sesion, id_, entrada, usuario)
        sesion.flush()
    return {"modo": "APLICAR" if aplicar else "VALIDAR", "moneda": "PEN",
            "productos": len(productos), "precios_a_crear": len(plan),
            "precios_previos_conservados": conservados, "huella_archivo": huella}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archivo", required=True)
    parser.add_argument("--usuario-id", type=int, required=True)
    parser.add_argument("--aplicar", action="store_true")
    args = parser.parse_args()
    try:
        with SessionLocal.begin() as sesion:
            resultado = cargar(sesion, args.archivo, args.usuario_id, args.aplicar)
        print(json.dumps(resultado, ensure_ascii=False))
    except (ValueError, KeyError, ErrorAPI) as error:
        parser.exit(1, f"No se aplicó la carga: {error}\n")


if __name__ == "__main__":
    main()
