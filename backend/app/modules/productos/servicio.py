"""Interfaz pública del catálogo para carga y pronósticos."""

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.productos.modelos import Producto, SkuProducto

ORIGEN_BAKERY = "bakery"


@dataclass(frozen=True)
class EntradaCatalogo:
    """Un producto de la hoja `productos` del asistente de primera carga."""

    codigo: str
    nombre: str
    sku_externo: str
    demostrar: bool


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


def registrar_catalogo(
    sesion: Session, entradas: list[EntradaCatalogo], origen: str = ORIGEN_BAKERY,
    *, completar_piloto: bool = False,
) -> dict[str, int]:
    """Registra el catálogo del asistente y devuelve `codigo -> producto_id`.

    No confirma la sesión. Si el catálogo ya existe con los mismos códigos y SKU,
    los reutiliza: repetir la primera carga con el mismo archivo no duplica. Un
    catálogo existente distinto es conflicto. `completar_piloto` permite adoptar
    los códigos y selección de la primera carga sobre el mismo catálogo bakery,
    identificado por sus códigos técnicos y SKU, conservando todos los IDs.
    """
    if not entradas:
        raise ErrorAPI(422, "CATALOGO_INVALIDO", "El catálogo no puede estar vacío.")
    if len({entrada.codigo for entrada in entradas}) != len(entradas) or len({entrada.sku_externo for entrada in entradas}) != len(entradas):
        raise ErrorAPI(422, "CATALOGO_INVALIDO", "El catálogo contiene códigos o SKU repetidos.")

    productos = list(sesion.scalars(select(Producto).with_for_update()))
    existentes = {producto.codigo: producto.id for producto in productos}
    if existentes:
        skus = list(sesion.scalars(select(SkuProducto).where(SkuProducto.origen == origen)))
        por_sku = {sku.sku_externo: sku.producto_id for sku in skus}
        por_id = {producto.id: producto for producto in productos}
        mapeo_valido = (
            set(por_sku) == {entrada.sku_externo for entrada in entradas}
            and set(por_sku.values()) == set(por_id)
            and len(por_sku) == len(productos) == len(entradas)
            and all(sku.activo for sku in skus)
            and all(producto.activo for producto in productos)
        )
        mismos_codigos = mapeo_valido and all(
            existentes.get(entrada.codigo) == por_sku[entrada.sku_externo]
            for entrada in entradas
        )
        es_piloto = mapeo_valido and origen == ORIGEN_BAKERY and all(
            por_id[producto_id].codigo == "bakery-" + hashlib.sha256(sku.encode("utf-8")).hexdigest()[:20]
            for sku, producto_id in por_sku.items()
        )
        codigos_sin_colision = mapeo_valido and all(
            entrada.codigo not in existentes or existentes[entrada.codigo] == por_sku[entrada.sku_externo]
            for entrada in entradas
        )
        if not mismos_codigos and not (completar_piloto and es_piloto and codigos_sin_colision):
            raise ErrorAPI(
                409,
                "CATALOGO_DIFERENTE",
                "El catálogo cargado no coincide con los códigos y SKU de esta entrega; no se modificó nada.",
            )
        mapa = {entrada.codigo: por_sku[entrada.sku_externo] for entrada in entradas}
        if completar_piloto:
            for entrada in entradas:
                producto = por_id[mapa[entrada.codigo]]
                producto.codigo = entrada.codigo
                producto.nombre = entrada.nombre
                producto.demostrar = entrada.demostrar
            sesion.flush()
        return mapa

    mapa: dict[str, int] = {}
    for entrada in entradas:
        producto = Producto(codigo=entrada.codigo, nombre=entrada.nombre, demostrar=entrada.demostrar)
        sesion.add(producto)
        sesion.flush()
        sesion.add(
            SkuProducto(producto_id=producto.id, origen=origen, sku_externo=entrada.sku_externo)
        )
        mapa[entrada.codigo] = producto.id
    sesion.flush()
    return mapa


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
