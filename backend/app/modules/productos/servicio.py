"""Interfaz pública del catálogo para carga y pronósticos."""

import hashlib
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.productos.modelos import Producto, SkuProducto

ORIGEN_BAKERY = "bakery"


def leer_nombres_bakery(lista: Path) -> list[str]:
    """Lee solo la columna Producto de la lista curada; precios no son parte de E01."""
    nombres = []
    for linea in lista.read_text(encoding="utf-8-sig").splitlines():
        match = re.fullmatch(r"\|\s*(.*?)\s*\|\s*(.*?)\s*\|", linea)
        if match and match.group(1) != "Producto" and not set(match.group(1)) <= {"-", " ", ":"}:
            nombres.append(match.group(1).strip())
    if not nombres or len(nombres) != len(set(nombres)):
        raise ErrorAPI(422, "CATALOGO_INVALIDO", "La lista de productos está vacía o contiene SKU repetidos.")
    return nombres


def cargar_catalogo_bakery(sesion: Session, lista: Path) -> int:
    """Registra el catálogo explícito en la sesión del importador; no confirma."""
    nombres = leer_nombres_bakery(lista)
    existentes = {
        sku: (producto_id, activo)
        for sku, producto_id, activo in sesion.execute(
            select(SkuProducto.sku_externo, SkuProducto.producto_id, SkuProducto.activo)
            .where(SkuProducto.origen == ORIGEN_BAKERY)
        )
    }
    if existentes and set(existentes) != set(nombres):
        raise ErrorAPI(409, "CATALOGO_DIFERENTE", "El catálogo bakery existente no coincide con la lista entregada.")
    if existentes:
        if not all(activo for _, activo in existentes.values()):
            raise ErrorAPI(409, "SKU_INACTIVO", "La lista contiene SKU inactivos.")
        if len({producto_id for producto_id, _ in existentes.values()}) != len(existentes):
            raise ErrorAPI(409, "MAPEO_AMBIGUO", "Dos SKU bakery apuntan al mismo producto.")
        return len(existentes)

    for nombre in nombres:
        codigo = "bakery-" + hashlib.sha256(nombre.encode("utf-8")).hexdigest()[:20]
        if sesion.scalar(select(Producto.id).where(Producto.codigo == codigo)) is not None:
            raise ErrorAPI(409, "CODIGO_DUPLICADO", f"El código del producto {nombre!r} ya existe.")
        producto = Producto(codigo=codigo, nombre=nombre, demostrar=False)
        sesion.add(producto)
        sesion.flush()
        sesion.add(SkuProducto(producto_id=producto.id, origen=ORIGEN_BAKERY, sku_externo=nombre))
    sesion.flush()
    return len(nombres)


def resolver_sku(sesion: Session, origen: str, sku_externo: str) -> int:
    """Devuelve el ID local o rechaza el SKU sin crearlo implícitamente."""
    producto_id = sesion.scalar(
        select(Producto.id)
        .join(SkuProducto, SkuProducto.producto_id == Producto.id)
        .where(SkuProducto.origen == origen, SkuProducto.sku_externo == sku_externo,
               SkuProducto.activo.is_(True), Producto.activo.is_(True))
    )
    if producto_id is None:
        raise ErrorAPI(422, "SKU_DESCONOCIDO", f"No hay producto activo para {origen}/{sku_externo}.")
    return producto_id


def listar_skus_bakery(sesion: Session) -> dict[int, str]:
    """Frontera pública: producto activo -> único SKU bakery activo."""
    filas = sesion.execute(
        select(Producto.id, SkuProducto.sku_externo)
        .join(SkuProducto, SkuProducto.producto_id == Producto.id)
        .where(SkuProducto.origen == ORIGEN_BAKERY,
               SkuProducto.activo.is_(True), Producto.activo.is_(True))
    ).all()
    resultado = dict(filas)
    if len(resultado) != len(filas):
        raise ErrorAPI(409, "MAPEO_AMBIGUO", "Un producto tiene varios SKU bakery activos.")
    return resultado


def nombres_productos(sesion: Session, producto_ids: list[int]) -> dict[int, str]:
    """Nombres para vistas de otros dominios, sin exponer el modelo privado."""
    if not producto_ids:
        return {}
    return dict(sesion.execute(
        select(Producto.id, Producto.nombre).where(Producto.id.in_(producto_ids))
    ).all())
