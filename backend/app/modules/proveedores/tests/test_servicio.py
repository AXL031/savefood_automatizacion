"""Fixtures de ejemplo (datos de prueba, no reales)."""
from decimal import Decimal

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.modules.proveedores.esquemas import OfertaCrear, ProveedorCrear
from app.modules.proveedores.modelos import Base
from app.modules.proveedores.servicio import Conflicto, ServicioProveedores


class TelegramFalso:
    def __init__(self, ok=True):
        self.ok = ok

    def verificar_chat(self, chat_id):
        return self.ok


@pytest.fixture
def db():
    e = create_engine("sqlite://")
    Base.metadata.create_all(e)
    with Session(e) as s:
        yield s


def _prov(s, codigo="P1"):
    return s.crear_proveedor(ProveedorCrear(codigo=codigo, nombre="Prov " + codigo, chat_id_pruebas="123"))


def _oferta(ing=1, pref=False):
    return OfertaCrear(ingrediente_id=ing, descripcion="Saco 25kg", unidad_compra="saco",
                       factor_conversion=Decimal("25000"), minimo=Decimal("1"),
                       multiplo=Decimal("1"), preferida=pref)


def test_factor_obligatorio_y_positivo():
    with pytest.raises(ValidationError):
        OfertaCrear(ingrediente_id=1, descripcion="x", unidad_compra="saco")
    with pytest.raises(ValidationError):
        OfertaCrear(ingrediente_id=1, descripcion="x", unidad_compra="saco", factor_conversion=0)


def test_una_sola_preferida_activa(db):
    s = ServicioProveedores(db)
    p1, p2 = _prov(s, "P1"), _prov(s, "P2")
    o1 = s.crear_oferta(p1.id, _oferta(pref=True))
    o2 = s.crear_oferta(p2.id, _oferta(pref=True))
    db.refresh(o1)
    assert not o1.preferida and o2.preferida


def test_oferta_inactiva_no_puede_ser_preferida(db):
    s = ServicioProveedores(db)
    o = s.crear_oferta(_prov(s).id, _oferta())
    s.desactivar_oferta(o.id)
    with pytest.raises(Conflicto):
        s.marcar_preferida(o.id)


def test_destino_no_verificado_bloquea(db):
    s = ServicioProveedores(db, TelegramFalso(ok=True))
    p = _prov(s)
    assert not s.puede_enviar(p.id)
    s.verificar_destino(p.id)
    assert s.puede_enviar(p.id)
    s.vincular_chat(p.id, "999")  # cambia el destino -> se invalida
    assert not s.puede_enviar(p.id)


def test_proveedor_inactivo_bloquea_compra_automatica(db):
    s = ServicioProveedores(db, TelegramFalso())
    p = _prov(s)
    s.verificar_destino(p.id)
    s.crear_oferta(p.id, _oferta(pref=True))
    assert s.oferta_preferida_para_compras(1).compra_automatica_habilitada
    s.cambiar_estado(p.id, False)
    r = s.oferta_preferida_para_compras(1)
    assert not r.compra_automatica_habilitada and r.motivo_bloqueo == "Proveedor inactivo"
