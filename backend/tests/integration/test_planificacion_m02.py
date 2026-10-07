"""M02–M04: servicios reales de recetas/stock y propuesta con CatBoost real."""

import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from threading import Barrier

import pytest
from sqlalchemy import func, select

from test_preparacion_e03 import entorno, cargar, reclamar  # fixture aislado compartido
from app.core.errores import ErrorAPI
from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion, programar_propuesta
from app.modules.ingredientes.modelos import Ingrediente
from app.modules.inventario.modelos import LoteIngrediente, LoteProducto, MovimientoInventario
from app.modules.inventario.servicio import SolicitudAjuste, registrar_ajuste
from app.modules.planificacion.modelos import PlanProduccion, NecesidadIngrediente
from app.modules.planificacion.servicio import generar_plan, obtener_plan, _decimal
from app.modules.pronosticos.modelos import ArtefactoModelo, CorridaPronostico, Pronostico
from app.modules.productos.modelos import Producto
from app.modules.recetas.modelos import Receta
from app.modules.recetas.servicio import crear_version, LineaNueva
from app.workers import motor
from app.workers.tasks.manejadores import ContextoEjecucion
from app.modules.planificacion import manejadores


def corrida_fixture(entorno):
    cargar(entorno)
    _, sesiones, _ = entorno
    with sesiones.begin() as s:
        productos = list(s.scalars(select(Producto).order_by(Producto.id)))
        modelo = ArtefactoModelo(version_modelo="fixture-plan", ruta_local="fixture", sha256="a" * 64,
                                huella_datos_entrenamiento="b" * 64, fecha_corte_entrenamiento=date(2022, 8, 31),
                                particion_json={}, estado="LISTO_DEMO")
        s.add(modelo); s.flush()
        ejecucion = crear_o_recuperar_ejecucion(s, "GENERAR_PROPUESTA", "fixture-propuesta", {})
        corrida = CorridaPronostico(ejecucion_id=ejecucion.id, tipo="DEMO_PROGRAMADA", clave_ejecucion="fixture-corrida",
                                   huella_datos_entrada="c" * 64, fecha_objetivo=date(2022, 9, 24), modelo_id=modelo.id, estado="COMPLETADA")
        s.add(corrida); s.flush()
        for p in productos:
            cantidad = {"baguette": 3, "croissant": 10, "banette": 8}[p.codigo]
            s.add(Pronostico(corrida_id=corrida.id, producto_id=p.id, estado="DISPONIBLE", cantidad_pronosticada=cantidad))
        return corrida.id


def test_calculo_agrega_ingredientes_y_no_mueve_stock(entorno):
    id_ = corrida_fixture(entorno)
    cliente, sesiones, cabeceras = entorno
    with sesiones() as s:
        movimientos = s.scalar(select(func.count()).select_from(MovimientoInventario))
        stocks = [(l.id, l.saldo_disponible) for l in s.scalars(select(LoteProducto))]
    respuesta = cliente.post("/api/v1/planes", json={"corrida_id": id_, "clave_ejecucion": "plan-1"}, headers=cabeceras["ADMINISTRADOR"])
    assert respuesta.status_code == 201, respuesta.text
    detalle = respuesta.json()["datos"]
    with sesiones() as s:
        assert movimientos == s.scalar(select(func.count()).select_from(MovimientoInventario))
        assert stocks == [(l.id, l.saldo_disponible) for l in s.scalars(select(LoteProducto))]
        # Oráculo desde las versiones guardadas: suma de TODOS los productos.
        totales = {}
        for e in detalle["elementos"]:
            assert e["cantidad_producir"] == max(0, e["cantidad_pronosticada"] - e["stock_disponible"])
            for l in detalle["trazas"]["recetas"][str(e["producto_id"])]["lineas"]:
                totales[l["ingrediente_id"]] = totales.get(l["ingrediente_id"], Decimal(0)) + e["cantidad_producir"] * Decimal(l["cantidad_por_unidad"])
        assert len(totales) == 2 and len(detalle["elementos"]) == 3
        for n in detalle["necesidades"]:
            assert Decimal(n["cantidad_requerida"]) == totales[n["ingrediente_id"]]
            assert Decimal(n["cantidad_faltante"]) == max(Decimal(0), totales[n["ingrediente_id"]] - Decimal(n["cantidad_disponible"]))
        assert any(e["cantidad_producir"] == 0 for e in detalle["elementos"])  # stock superior a la demanda
        assert {n["ingrediente"]: n["cantidad_requerida"] for n in detalle["necesidades"]} == {"Harina": "3000.000", "Levadura": "66.000"}
    repetida = cliente.post("/api/v1/planes", json={"corrida_id": id_, "clave_ejecucion": "plan-1"}, headers=cabeceras["ADMINISTRADOR"])
    assert repetida.json()["datos"] == detalle
    assert cliente.get(f'/api/v1/planes/{detalle["id"]}', headers=cabeceras["OPERADOR"]).json()["datos"] == detalle
    assert cliente.get(f"/api/v1/planes?corrida_id={id_}", headers=cabeceras["OPERADOR"]).json()["datos"][0]["id"] == detalle["id"]
    assert cliente.post("/api/v1/planes", json={"corrida_id": id_, "clave_ejecucion": "x"}, headers=cabeceras["OPERADOR"]).status_code == 403
    assert cliente.get("/api/v1/planes/99999", headers=cabeceras["ADMINISTRADOR"]).status_code == 404


def test_cambio_receta_stock_conserva_plan_y_conflicto_de_clave(entorno):
    id_ = corrida_fixture(entorno)
    _, sesiones, _ = entorno
    with sesiones.begin() as s:
        plan = generar_plan(s, id_, "antes")
        viejo_id = plan.id
        viejo = obtener_plan(s, plan.id)
    with sesiones.begin() as s:
        e = viejo["elementos"][0]
        lineas = viejo["trazas"]["recetas"][str(e["producto_id"])]["lineas"]
        crear_version(s, e["producto_id"], [LineaNueva(l["ingrediente_id"], Decimal(l["cantidad_por_unidad"]) * 2) for l in lineas], "Cambio para prueba", None)
        lote = s.scalar(select(LoteProducto).where(LoteProducto.producto_id == e["producto_id"]))
        registrar_ajuste(s, SolicitudAjuste("producto", lote.id, Decimal(1), "Prueba", "ajuste-plan", datetime(2022, 9, 24, 8)), None)
    with sesiones.begin() as s:
        with pytest.raises(ErrorAPI) as error:
            generar_plan(s, id_, "antes")
        assert error.value.status_code == 409
        nuevo = generar_plan(s, id_, "despues")
        assert nuevo.id != viejo_id
        assert obtener_plan(s, viejo_id) == viejo
        assert obtener_plan(s, nuevo.id)["elementos"][0]["receta_version"] == 2


@pytest.mark.parametrize("falta", ["pronostico", "receta", "stock_producto", "stock_ingrediente"])
def test_datos_ausentes_no_se_convierten_en_cero(entorno, falta):
    id_ = corrida_fixture(entorno)
    _, sesiones, _ = entorno
    with sesiones.begin() as s:
        p = s.scalar(select(Pronostico).where(Pronostico.corrida_id == id_).order_by(Pronostico.producto_id.desc()))
        if falta == "pronostico":
            p.estado = "HISTORIAL_INSUFICIENTE"; p.cantidad_pronosticada = None
        elif falta == "receta":
            s.scalar(select(Receta).where(Receta.producto_id == p.producto_id)).activo = False
        elif falta == "stock_producto":
            lote = s.scalar(select(LoteProducto).where(LoteProducto.saldo_disponible == 0))
            # El escenario tiene dos productos con saldo cero: sin movimientos que eliminar.
            assert lote.saldo_disponible == 0
            s.delete(lote)
        else:
            lote = s.scalar(select(LoteIngrediente).where(LoteIngrediente.saldo_disponible == 0))
            assert lote is not None
            s.delete(lote)
        s.flush()
        plan = generar_plan(s, id_, "ausentes")
        detalle = obtener_plan(s, plan.id)
        assert detalle["avisos"]
        if falta != "stock_ingrediente":
            assert len(detalle["omisiones"]) == 1
            assert len(detalle["elementos"]) == 2
        else:
            desconocida = next(n for n in detalle["necesidades"] if not n["stock_conocido"])
            assert desconocida["cantidad_disponible"] is None and desconocida["cantidad_faltante"] is None


def test_stock_vencido_excluido_y_vigencia_desconocida_visible(entorno):
    id_ = corrida_fixture(entorno)
    _, sesiones, _ = entorno
    with sesiones.begin() as s:
        lote = s.scalar(select(LoteProducto).where(LoteProducto.saldo_disponible > 0))
        lote.fecha_caducidad = date(2022, 9, 23)
        lote.fecha_limite_venta = date(2022, 9, 23)
        ingrediente = s.scalar(select(LoteIngrediente).where(LoteIngrediente.saldo_disponible > 0))
        ingrediente.fecha_caducidad = None
        s.flush()
        plan = generar_plan(s, id_, "vigencia")
        detalle = obtener_plan(s, plan.id)
        e = next(e for e in detalle["elementos"] if e["producto_id"] == lote.producto_id)
        assert e["stock_disponible"] == 0
        assert any(n["vigencia_stock_desconocida"] for n in detalle["necesidades"])
        assert detalle["avisos"]


def test_rollback_del_llamador_y_rango_decimal(entorno):
    id_ = corrida_fixture(entorno)
    _, sesiones, _ = entorno
    with sesiones() as s:
        # Transacción exterior explícita: savepoint no es confirmación del llamador.
        s.begin(); generar_plan(s, id_, "rollback"); s.rollback()
    with sesiones() as s:
        assert s.scalar(select(func.count()).select_from(PlanProduccion)) == 0
        assert s.scalar(select(func.count()).select_from(NecesidadIngrediente)) == 0
    assert _decimal(Decimal("0.0004") + Decimal("0.0004")) == Decimal("0.001")
    with pytest.raises(ErrorAPI):
        _decimal(Decimal("1000000000000000"))


def test_propuesta_real_atomica_y_reentrega(entorno, monkeypatch):
    cargar(entorno)
    _, sesiones, _ = entorno
    for id_, token in reclamar():
        assert motor.ejecutar(id_, token)["resultado"] == "COMPLETADA"
    # No ejecutar backtest aquí: ya está probado en E03; aislar el evento del plan.
    with sesiones.begin() as s:
        ids = list(s.scalars(select(Producto.id).order_by(Producto.id)))
        ejecucion = crear_o_recuperar_ejecucion(s, "GENERAR_PROPUESTA", "propuesta-real", {"parametros": {"fecha_objetivo_demo": "2022-09-24", "producto_ids": ids}})
        ejecucion_id = ejecucion.id
    real = manejadores.solicitar_evaluacion_corrida
    def fallo(*args):
        raise RuntimeError("Fallo al reservar evaluación")
    with sesiones() as s:
        contexto = ContextoEjecucion(ejecucion_id, "GENERAR_PROPUESTA", "propuesta-real", {"parametros": {"fecha_objetivo_demo": "2022-09-24", "producto_ids": ids}})
        monkeypatch.setattr(manejadores, "solicitar_evaluacion_corrida", fallo)
        with pytest.raises(RuntimeError):
            manejadores.generar_propuesta(s, contexto)
        s.rollback()
    with sesiones() as s:
        assert s.scalar(select(func.count()).select_from(PlanProduccion)) == 0
        assert s.scalar(select(func.count()).select_from(CorridaPronostico)) == 0
    monkeypatch.setattr(manejadores, "solicitar_evaluacion_corrida", real)
    mensajes = reclamar()
    id_, token = next(m for m in mensajes if m[0] == ejecucion_id)
    antes = None
    with sesiones() as s:
        antes = s.scalar(select(func.count()).select_from(MovimientoInventario))
    assert motor.ejecutar(id_, token)["resultado"] == "COMPLETADA"
    assert motor.ejecutar(id_, token)["resultado"] == "IGNORADA"
    with sesiones() as s:
        assert s.scalar(select(func.count()).select_from(PlanProduccion)) == 1
        assert s.scalar(select(func.count()).select_from(MovimientoInventario)) == antes


def test_plan_concurrente_postgres(entorno):
    if os.getenv("E03_POSTGRES_TEST") != "1":
        pytest.skip("Bloqueo concurrente requiere PostgreSQL")
    id_ = corrida_fixture(entorno)
    _, sesiones, _ = entorno
    barrera = Barrier(2)
    def calcular(_):
        barrera.wait(timeout=10)
        with sesiones.begin() as s:
            return generar_plan(s, id_, "concurrente").id
    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(calcular, range(2)))
    assert resultados[0] == resultados[1]
    with sesiones() as s:
        assert s.scalar(select(func.count()).select_from(PlanProduccion)) == 1
