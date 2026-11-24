"""Fallo definitivo de una tarea en segundo plano: aviso en la bandeja administrativa."""
from datetime import datetime, timezone

from sqlalchemy import func, select

from test_api_inicializacion_ventas import cabecera, cliente, token  # noqa: F401
from app.core.base_datos import obtener_sesion
from app.modules.automatizaciones.avisos import avisar_fallo_definitivo
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion, IntentoAutomatizacion
from app.modules.operaciones.modelos import AvisoOperacion


def _ejecucion(sesion, estado, intentos):
    ahora = datetime.now(timezone.utc)
    e = EjecucionAutomatizacion(tipo="GENERAR_PROPUESTA", clave_idempotencia=f"aviso-{estado}", huella_entrada="a" * 64,
                                datos_entrada_json={}, estado=estado, mensaje_error="Falta receta vigente para Pan.")
    sesion.add(e); sesion.flush()
    for n in range(1, intentos + 1):
        sesion.add(IntentoAutomatizacion(ejecucion_id=e.id, numero_intento=n, inicio_en=ahora, fin_en=ahora,
                                         estado="FALLIDA", mensaje_error="Falta receta"))
    sesion.flush()
    return e


def test_solo_el_fallo_definitivo_crea_un_aviso_y_no_se_duplica(cliente):
    with next(cliente.app.dependency_overrides[obtener_sesion]()) as s:
        reintentando = _ejecucion(s, "REINTENTANDO", 1)
        assert avisar_fallo_definitivo(s, reintentando) is None
        fallida = _ejecucion(s, "FALLIDA", 3)
        primero = avisar_fallo_definitivo(s, fallida)
        assert avisar_fallo_definitivo(s, fallida).id == primero.id
        s.commit()
        assert s.scalar(select(func.count()).select_from(AvisoOperacion)) == 1
        id_ = fallida.id

    avisos = cliente.get("/api/v1/operaciones/avisos",
                         headers=cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))).json()["datos"]
    assert avisos[0]["titulo"] == "Falló la creación del plan y las compras"
    assert avisos[0]["datos"]["ejecucion_id"] == id_ and not avisos[0]["leido"]
    assert "3 intento(s)" in avisos[0]["datos"]["descripcion"] and "Falta receta" in avisos[0]["datos"]["descripcion"]
