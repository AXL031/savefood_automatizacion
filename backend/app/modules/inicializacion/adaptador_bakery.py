"""Adaptador del CSV piloto `bakery` a la forma diaria del contrato.

El archivo real trae líneas de ticket (`date,time,ticket_number,article,Quantity,
unit_price`). Aquí se valida el artículo contra la lista curada, se excluyen las
líneas negativas informando cuántas, y se agregan las unidades por fecha y
artículo para obtener las tres columnas que espera `validacion.py`.

Una fecha sin líneas no produce fila: sigue siendo desconocida, no un cero.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from app.core.errores import ErrorAPI
from app.modules.inicializacion.lectores import Hoja

COLUMNAS_BAKERY = ("date", "article", "quantity")
ORIGEN = "bakery"


@dataclass(frozen=True)
class ResumenAdaptacion:
    """Lo que el adaptador hizo con el archivo, para mostrarlo en la vista previa."""

    lineas_leidas: int
    lineas_negativas: int
    lineas_invalidas: int
    pares_generados: int
    articulos: int


def es_csv_bakery(contenido: bytes) -> bool:
    """Reconoce el CSV de tickets por sus columnas, sin consumir el archivo entero."""
    try:
        cabecera = contenido[:4096].decode("utf-8-sig", errors="replace").splitlines()[0]
    except IndexError:
        return False
    columnas = {celda.strip().lower() for celda in cabecera.split(",")}
    return all(columna in columnas for columna in COLUMNAS_BAKERY)


def _leer_unidades(valor: str) -> int | None:
    texto = valor.strip()
    if not texto:
        return None
    try:
        numero = Decimal(texto)
    except InvalidOperation:
        return None
    if not numero.is_finite() or numero != numero.to_integral_value():
        return None
    return int(numero)


def adaptar_csv_bakery(
    archivo: str, contenido: bytes, skus_permitidos: set[str] | None = None
) -> tuple[Hoja, ResumenAdaptacion]:
    """Convierte el CSV de tickets en la hoja `ventas` diaria del contrato."""
    try:
        texto = contenido.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ErrorAPI(422, "ARCHIVO_ILEGIBLE", f"{archivo} no está en UTF-8.") from None

    lector = csv.DictReader(io.StringIO(texto))
    presentes = {(campo or "").strip().lower() for campo in (lector.fieldnames or [])}
    faltantes = [columna for columna in COLUMNAS_BAKERY if columna not in presentes]
    if faltantes:
        raise ErrorAPI(
            422,
            "ENCABEZADO_INVALIDO",
            f"En {archivo} faltan columnas del formato bakery: {', '.join(faltantes)}.",
        )

    claves = {(campo or "").strip().lower(): campo for campo in (lector.fieldnames or [])}
    agregado: dict[tuple[date, str], int] = {}
    leidas = negativas = invalidas = 0

    for fila in lector:
        leidas += 1
        articulo = (fila.get(claves["article"]) or "").strip()
        fecha_texto = (fila.get(claves["date"]) or "").strip()
        unidades = _leer_unidades(fila.get(claves["quantity"]) or "")

        try:
            fecha = date.fromisoformat(fecha_texto)
        except ValueError:
            invalidas += 1
            continue
        if not articulo or unidades is None:
            invalidas += 1
            continue
        if skus_permitidos is not None and articulo not in skus_permitidos:
            raise ErrorAPI(
                422,
                "SKU_DESCONOCIDO",
                f"El artículo {articulo!r} de {archivo} no está en la lista curada de productos.",
            )
        if unidades < 0:
            negativas += 1
            continue

        clave = (fecha, articulo)
        agregado[clave] = agregado.get(clave, 0) + unidades

    if not agregado:
        raise ErrorAPI(422, "ARCHIVO_VACIO", f"{archivo} no aportó ninguna venta utilizable.")

    filas = tuple(
        (
            indice,
            {
                "fecha_local": fecha.isoformat(),
                "sku_externo": articulo,
                "unidades_vendidas": str(unidades),
            },
        )
        for indice, ((fecha, articulo), unidades) in enumerate(sorted(agregado.items()), start=2)
    )
    hoja = Hoja(
        nombre="ventas",
        archivo=archivo,
        encabezados=("fecha_local", "sku_externo", "unidades_vendidas"),
        filas=filas,
    )
    resumen = ResumenAdaptacion(
        lineas_leidas=leidas,
        lineas_negativas=negativas,
        lineas_invalidas=invalidas,
        pares_generados=len(agregado),
        articulos=len({articulo for _, articulo in agregado}),
    )
    return hoja, resumen


def adaptar_desde_ruta(
    ruta: Path, skus_permitidos: set[str] | None = None
) -> tuple[Hoja, ResumenAdaptacion]:
    return adaptar_csv_bakery(ruta.name, ruta.read_bytes(), skus_permitidos)
