"""Contrato mínimo de PostgreSQL/SQLite entre el historial de Edu y Kevin."""

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.core.base import Base
from app.core.errores import ErrorAPI
from app.modules.autenticacion.modelos import Usuario  # noqa: F401, registra FK
from app.modules.productos.modelos import Producto, SkuProducto
from app.modules.productos.servicio import cargar_catalogo_bakery, resolver_sku
from app.modules.ventas.modelos import ImportacionVenta, RevisionVenta, VentaDiaria
from app.modules.ventas.servicio import corregir_venta, importar_bakery, leer_historial


@pytest.fixture
def sesion():
    engine = create_engine("sqlite:///:memory:")
    @event.listens_for(engine, "connect")
    def _char_length(conexion, _registro):
        conexion.create_function("char_length", 1, len)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def _archivos(tmp_path: Path, ventas: str) -> tuple[Path, Path]:
    catalogo = tmp_path / "productos.md"
    catalogo.write_text(
        "| Producto | Precio(s) válido(s) |\n|---|---:|\n"
        "| BAGUETTE | 0.90 |\n| CROISSANT | 1.20 |\n", encoding="utf-8"
    )
    csv = tmp_path / "ventas.csv"
    csv.write_text("date,article,Quantity\n" + ventas, encoding="utf-8")
    return catalogo, csv


def test_carga_lectura_temporal_cero_ausencia_y_revision(sesion, tmp_path):
    catalogo, csv = _archivos(tmp_path,
        "2022-08-21,BAGUETTE,2.0\n2022-08-21,BAGUETTE,3.0\n"
        "2022-08-22,CROISSANT,0.0\n2022-08-22,BAGUETTE,-1.0\n"
        "2022-08-24,BAGUETTE,8.0\n")
    assert cargar_catalogo_bakery(sesion, catalogo) == 2
    baguette = resolver_sku(sesion, "bakery", "BAGUETTE")
    croissant = resolver_sku(sesion, "bakery", "CROISSANT")
    resultado = importar_bakery(sesion, csv, "carga-1")
    assert (resultado.filas_aceptadas, resultado.filas_negativas_excluidas, resultado.ventas_diarias) == (4, 1, 3)
    assert importar_bakery(sesion, csv, "carga-1").importacion_id == resultado.importacion_id

    historial = leer_historial(sesion, [baguette, croissant], date(2022, 8, 21), date(2022, 8, 24))
    assert [(v.sku_externo, v.fecha_local, v.unidades_vendidas) for v in historial] == [
        ("BAGUETTE", date(2022, 8, 21), 5),
        ("CROISSANT", date(2022, 8, 22), 0),
    ]
    assert all(v.revision_venta_id for v in historial)
    venta_id = sesion.scalar(select(VentaDiaria.id).where(VentaDiaria.producto_id == baguette, VentaDiaria.fecha_local == date(2022, 8, 21)))
    revision_nueva = corregir_venta(sesion, venta_id, 7, "Corrección comprobada")
    assert revision_nueva != historial[0].revision_venta_id
    assert sesion.get(RevisionVenta, historial[0].revision_venta_id).unidades_vendidas == 5
    assert leer_historial(sesion, [baguette], date(2022, 8, 21), date(2022, 8, 22))[0].unidades_vendidas == 7


def test_sku_desconocido_y_clave_conflictiva_no_crean_ventas(sesion, tmp_path):
    catalogo, csv = _archivos(tmp_path, "2022-08-21,DESCONOCIDO,1.0\n")
    cargar_catalogo_bakery(sesion, catalogo)
    with pytest.raises(ErrorAPI) as exc:
        importar_bakery(sesion, csv, "carga-1")
    assert exc.value.codigo == "SKU_DESCONOCIDO"
    assert sesion.scalar(select(ImportacionVenta.id)) is None
    assert sesion.scalar(select(VentaDiaria.id)) is None

    csv.write_text("date,article,Quantity\n2022-08-21,BAGUETTE,1.0\n", encoding="utf-8")
    importar_bakery(sesion, csv, "carga-1")
    csv.write_text("date,article,Quantity\n2022-08-21,BAGUETTE,2.0\n", encoding="utf-8")
    with pytest.raises(ErrorAPI) as exc:
        importar_bakery(sesion, csv, "carga-1")
    assert exc.value.codigo == "CLAVE_REUTILIZADA"
