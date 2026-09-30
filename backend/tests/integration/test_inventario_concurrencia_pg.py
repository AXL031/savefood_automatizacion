"""V02 sobre un esquema de prueba aislado; activar V02_POSTGRES_TEST=1."""
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from decimal import Decimal
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.base import Base
from app.core.errores import ErrorAPI
from app.principal import app  # noqa: F401
from app.modules.ingredientes.servicio import crear_ingrediente
from app.modules.inventario.modelos import LoteIngrediente
from app.modules.inventario.servicio import ServicioInventarioV01, SolicitudAjuste, registrar_ajuste
from app.modules.inicializacion.validacion import FilaStock


@pytest.fixture
def motor_pg():
    if os.getenv("V02_POSTGRES_TEST") != "1":
        pytest.skip("V02_POSTGRES_TEST=1 requiere PostgreSQL")
    url = os.environ["DATABASE_URL"]
    assert url.startswith("postgresql")
    esquema = "v02_test_" + uuid4().hex
    admin = create_engine(url)
    with admin.begin() as c:
        c.execute(text(f'CREATE SCHEMA "{esquema}"'))
    motor = create_engine(url, connect_args={"options": f"-csearch_path={esquema}"})
    try:
        Base.metadata.create_all(motor)
        with Session(motor) as s:
            ingrediente = crear_ingrediente(s, "HAR", "Harina", "g")
            ServicioInventarioV01().registrar_apertura(
                s, [FilaStock("ingrediente", "HAR", Decimal("4"), "L1", None, None)],
                {}, {"HAR": ingrediente.id}, date(2022, 8, 23), "apertura",
            )
            s.commit()
        yield motor
    finally:
        motor.dispose()
        with admin.begin() as c:
            c.execute(text(f'DROP SCHEMA "{esquema}" CASCADE'))
        admin.dispose()


@pytest.mark.parametrize("misma_clave", [False, True])
def test_ajustes_concurrentes_serializan_saldo_y_reentrega(motor_pg, misma_clave):
    barrera = Barrier(2)

    def ajustar(indice):
        with Session(motor_pg) as s:
            barrera.wait(timeout=10)
            try:
                resultado = registrar_ajuste(s, SolicitudAjuste(
                    "ingrediente", 1, Decimal("-3"), "Ajuste concurrente",
                    "misma" if misma_clave else f"clave-{indice}", datetime(2022, 8, 24, 10),
                ), None)
                s.commit()
                return ("ok", resultado.repetido)
            except ErrorAPI as error:
                s.rollback()
                return (error.codigo, False)

    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(ajustar, [1, 2]))
    with Session(motor_pg) as s:
        assert s.get(LoteIngrediente, 1).saldo_disponible == Decimal("1")
    if misma_clave:
        assert sorted(resultados) == [("ok", False), ("ok", True)]
    else:
        assert sorted(r[0] for r in resultados) == ["SALDO_INSUFICIENTE", "ok"]
