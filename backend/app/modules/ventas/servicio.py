"""Carga diaria del piloto y lectura temporal pública para Kevin."""

import csv
import hashlib
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.productos.modelos import Producto, SkuProducto
from app.modules.productos.servicio import ORIGEN_BAKERY
from app.modules.ventas.modelos import ImportacionVenta, RevisionVenta, VentaDiaria


@dataclass(frozen=True)
class VentaHistorica:
    producto_id: int
    sku_externo: str
    fecha_local: date
    unidades_vendidas: int
    revision_venta_id: int


@dataclass(frozen=True)
class ResultadoImportacion:
    importacion_id: int
    filas_aceptadas: int
    filas_negativas_excluidas: int
    ventas_diarias: int


def _huella_archivo(ruta: Path) -> str:
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def importar_bakery(sesion: Session, csv_path: Path, clave_importacion: str) -> ResultadoImportacion:
    """Agrega tickets por SKU/día en la sesión recibida, sin hacer commit.

    Requiere catálogo bakery ya registrado. Descarta cantidades negativas del
    dataset y comunica cuántas descartó. Las demás filas inválidas fallan antes
    de persistir; el llamador revierte la sesión si ocurre un error.
    """
    if not clave_importacion or len(clave_importacion) > 128:
        raise ErrorAPI(422, "CLAVE_INVALIDA", "La clave de importación debe tener entre 1 y 128 caracteres.")
    huella = _huella_archivo(csv_path)
    anterior = sesion.scalar(select(ImportacionVenta).where(
        ImportacionVenta.origen == ORIGEN_BAKERY,
        ImportacionVenta.clave_importacion == clave_importacion,
    ))
    if anterior is not None:
        if anterior.huella_contenido != huella:
            raise ErrorAPI(409, "CLAVE_REUTILIZADA", "La clave ya corresponde a otro archivo de ventas.")
        return ResultadoImportacion(anterior.id, anterior.filas_aceptadas, 0, 0)

    skus = dict(sesion.execute(
        select(SkuProducto.sku_externo, Producto.id)
        .join(Producto, Producto.id == SkuProducto.producto_id)
        .where(SkuProducto.origen == ORIGEN_BAKERY,
               SkuProducto.activo.is_(True), Producto.activo.is_(True))
    ).all())
    if not skus:
        raise ErrorAPI(422, "CATALOGO_FALTANTE", "Cargue primero la lista de productos bakery.")
    if len(set(skus.values())) != len(skus):
        raise ErrorAPI(409, "MAPEO_AMBIGUO", "Dos SKU bakery apuntan al mismo producto.")

    diarios: dict[tuple[int, date], int] = defaultdict(int)
    aceptadas = negativas = 0
    with csv_path.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if not {"date", "article", "Quantity"}.issubset(lector.fieldnames or []):
            raise ErrorAPI(422, "VENTAS_INVALIDAS", "El CSV requiere date, article y Quantity.")
        if {"comercio_id", "sucursal_id"} & set(lector.fieldnames or []):
            raise ErrorAPI(422, "IDENTIDAD_NO_CONFIGURADA", "La carga bakery no acepta identidades externas; use la inicialización completa.")
        for numero, fila in enumerate(lector, start=2):
            sku = (fila.get("article") or "").strip()
            if sku not in skus:
                raise ErrorAPI(422, "SKU_DESCONOCIDO", f"Fila {numero}: SKU {sku!r} sin mapeo activo.")
            try:
                fecha = date.fromisoformat(fila["date"])
                cantidad = Decimal(fila["Quantity"])
            except (ValueError, TypeError, InvalidOperation):
                raise ErrorAPI(422, "VENTA_INVALIDA", f"Fila {numero}: fecha o cantidad inválida.") from None
            if not cantidad.is_finite() or cantidad != cantidad.to_integral_value():
                raise ErrorAPI(422, "VENTA_INVALIDA", f"Fila {numero}: cantidad no entera.")
            if cantidad < 0:
                negativas += 1
                continue
            diarios[(skus[sku], fecha)] += int(cantidad)
            aceptadas += 1

    resultado = registrar_ventas_diarias(
        sesion,
        diarios,
        clave_importacion=clave_importacion,
        huella_contenido=huella,
        filas_aceptadas=aceptadas,
        motivo="Carga inicial bakery",
    )
    return ResultadoImportacion(
        resultado.importacion_id, aceptadas, negativas, resultado.ventas_diarias
    )


def registrar_ventas_diarias(
    sesion: Session,
    diarios: dict[tuple[int, date], int],
    clave_importacion: str,
    huella_contenido: str,
    filas_aceptadas: int,
    motivo: str,
    origen: str = ORIGEN_BAKERY,
    *, reutilizar_identicas: bool = False,
) -> ResultadoImportacion:
    """Persiste ventas ya agregadas por producto y fecha, sin hacer commit.

    `diarios` llega agregado: esta función no interpreta archivos. La usa tanto la
    carga del piloto como el asistente de primera carga, para que ambos caminos
    compartan una sola escritura y las mismas reglas de idempotencia. La primera
    carga puede reutilizar filas idénticas del piloto e insertar solo las nuevas;
    nunca corrige ni borra ventas/revisiones previas.
    """
    if not clave_importacion or len(clave_importacion) > 128:
        raise ErrorAPI(422, "CLAVE_INVALIDA", "La clave de importación debe tener entre 1 y 128 caracteres.")
    if not diarios:
        raise ErrorAPI(422, "VENTAS_VACIAS", "No hay ventas aceptadas.")
    if any(unidades > 2_147_483_647 for unidades in diarios.values()):
        raise ErrorAPI(422, "VENTA_INVALIDA", "Una suma diaria excede el límite de unidades.")

    anterior = sesion.scalar(select(ImportacionVenta).where(
        ImportacionVenta.origen == origen,
        ImportacionVenta.clave_importacion == clave_importacion,
    ))
    if anterior is not None:
        if anterior.huella_contenido != huella_contenido:
            raise ErrorAPI(409, "CLAVE_REUTILIZADA", "La clave ya corresponde a otro archivo de ventas.")
        return ResultadoImportacion(anterior.id, anterior.filas_aceptadas, 0, 0)

    ids = {producto_id for producto_id, _ in diarios}
    fechas = [fecha for _, fecha in diarios]
    existentes = dict(((producto_id, fecha), unidades) for producto_id, fecha, unidades in sesion.execute(
        select(VentaDiaria.producto_id, VentaDiaria.fecha_local, VentaDiaria.unidades_vendidas).where(
        VentaDiaria.producto_id.in_(ids),
        VentaDiaria.fecha_local.between(min(fechas), max(fechas)),
    ).with_for_update()))
    if existentes and not reutilizar_identicas:
        raise ErrorAPI(409, "VENTA_DUPLICADA", "Ya existen ventas en el periodo de esta importación.")
    if reutilizar_identicas and any(diarios.get(par) != unidades for par, unidades in existentes.items()):
        raise ErrorAPI(409, "HISTORIAL_DIFERENTE", "Las ventas entregadas cambian u omiten días ya cargados en ese periodo; no se modificó nada.")

    registro = ImportacionVenta(
        origen=origen, clave_importacion=clave_importacion,
        huella_contenido=huella_contenido, filas_aceptadas=filas_aceptadas, estado="COMPLETADA",
    )
    sesion.add(registro)
    sesion.flush()
    items = sorted(((par, unidades) for par, unidades in diarios.items() if par not in existentes),
                   key=lambda item: (item[0][1], item[0][0]))
    for offset in range(0, len(items), 1000):
        lote = items[offset:offset + 1000]
        valores = [
            {"producto_id": producto_id, "fecha_local": fecha, "unidades_vendidas": unidades,
             "importacion_id": registro.id, "revision_actual": 1}
            for (producto_id, fecha), unidades in lote
        ]
        ventas = sesion.execute(insert(VentaDiaria).returning(VentaDiaria.id, VentaDiaria.unidades_vendidas), valores)
        revisiones = [
            {"venta_id": venta_id, "numero_revision": 1, "unidades_vendidas": unidades,
             "origen_cambio": "IMPORTACION", "motivo": motivo, "importacion_id": registro.id}
            for venta_id, unidades in ventas
        ]
        sesion.execute(insert(RevisionVenta), revisiones)
    return ResultadoImportacion(registro.id, filas_aceptadas, 0, len(items))


def leer_historial(sesion: Session, producto_ids: list[int], inicio: date, fin_exclusivo: date) -> list[VentaHistorica]:
    """Lee ventas conocidas en [inicio, fin_exclusivo); ausencia no genera fila."""
    if not producto_ids or inicio >= fin_exclusivo:
        return []
    filas = sesion.execute(
        select(VentaDiaria.producto_id, SkuProducto.sku_externo, VentaDiaria.fecha_local,
               VentaDiaria.unidades_vendidas, RevisionVenta.id)
        .join(SkuProducto, SkuProducto.producto_id == VentaDiaria.producto_id)
        .join(RevisionVenta, (RevisionVenta.venta_id == VentaDiaria.id) &
              (RevisionVenta.numero_revision == VentaDiaria.revision_actual))
        .where(VentaDiaria.producto_id.in_(producto_ids),
               VentaDiaria.fecha_local >= inicio, VentaDiaria.fecha_local < fin_exclusivo,
               SkuProducto.origen == ORIGEN_BAKERY)
        .order_by(VentaDiaria.fecha_local, VentaDiaria.producto_id)
    )
    return [VentaHistorica(*fila) for fila in filas]


def limites_historial(sesion: Session, producto_ids: list[int]) -> tuple[date | None, date | None]:
    """Primera y última fecha observada de los productos indicados."""
    if not producto_ids:
        return None, None
    return sesion.execute(select(func.min(VentaDiaria.fecha_local), func.max(VentaDiaria.fecha_local))
                          .where(VentaDiaria.producto_id.in_(producto_ids))).one()


def periodo_ventas(sesion: Session) -> tuple[date | None, date | None]:
    """Límites de todo el historial conocido, incluyendo productos inactivos."""
    return sesion.execute(select(func.min(VentaDiaria.fecha_local), func.max(VentaDiaria.fecha_local))).one()


def resumen_ventas(sesion: Session, desde: date, hasta: date) -> dict:
    """Agrega revisiones actuales del período completo; no rellena ausencias."""
    filtro = (VentaDiaria.fecha_local >= desde, VentaDiaria.fecha_local <= hasta)
    dias = sesion.execute(select(VentaDiaria.fecha_local,
        func.sum(VentaDiaria.unidades_vendidas), func.count(VentaDiaria.id))
        .where(*filtro).group_by(VentaDiaria.fecha_local).order_by(VentaDiaria.fecha_local)).all()
    productos = sesion.execute(select(Producto.id, Producto.nombre,
        func.sum(VentaDiaria.unidades_vendidas), func.count(VentaDiaria.id))
        .join(VentaDiaria, VentaDiaria.producto_id == Producto.id).where(*filtro)
        .group_by(Producto.id, Producto.nombre)
        .order_by(func.sum(VentaDiaria.unidades_vendidas).desc(), Producto.id)).all()
    return {
        "unidades": sum(int(unidades) for _, unidades, _ in dias),
        "registros": sum(int(registros) for _, _, registros in dias),
        "dias_observados": len(dias), "productos_observados": len(productos),
        "serie_diaria": [{"fecha": fecha.isoformat(), "unidades": int(unidades),
                          "productos_observados": int(registros)} for fecha, unidades, registros in dias],
        "por_producto": [{"producto_id": pid, "producto": nombre, "unidades": int(unidades),
                          "dias_observados": int(registros)} for pid, nombre, unidades, registros in productos],
    }


def corregir_venta(sesion: Session, venta_id: int, unidades: int, motivo: str, usuario_id: int | None = None) -> int:
    """Crea revisión sin borrar el valor usado en evaluaciones anteriores."""
    if unidades < 0 or not motivo.strip():
        raise ErrorAPI(422, "CORRECCION_INVALIDA", "Se requieren unidades no negativas y motivo.")
    venta = sesion.scalar(select(VentaDiaria).where(VentaDiaria.id == venta_id).with_for_update())
    if venta is None:
        raise ErrorAPI(404, "VENTA_NO_ENCONTRADA", "La venta no existe.")
    if venta.unidades_vendidas == unidades:
        actual = sesion.scalar(select(RevisionVenta.id).where(
            RevisionVenta.venta_id == venta_id,
            RevisionVenta.numero_revision == venta.revision_actual,
        ))
        return actual
    venta.revision_actual += 1
    venta.unidades_vendidas = unidades
    venta.actualizado_en = datetime.now(timezone.utc)
    revision = RevisionVenta(
        venta_id=venta_id, numero_revision=venta.revision_actual,
        unidades_vendidas=unidades, origen_cambio="CORRECCION", motivo=motivo.strip(), usuario_id=usuario_id,
    )
    sesion.add(revision)
    sesion.flush()
    return revision.id
