"""Frontera E01/K03: snapshots de venta, reserva transaccional y archivo completo."""
from datetime import date, timedelta
import asyncio

import pytest
from sqlalchemy import select, func
from test_pronosticos_k02_k03 import contexto
from test_api_inicializacion_ventas import cliente
from test_planificacion_m02 import escenario
from app.core.errores import ErrorAPI
from app.modules.ventas.modelos import VentaDiaria, RevisionVenta
from app.modules.ventas.servicio import corregir_venta
from app.modules.pronosticos.modelos import CorridaPronostico, Pronostico, EvaluacionPronostico
from app.modules.pronosticos.evaluacion import evaluar_corrida, detalle_evaluacion, solicitar_evaluacion_corrida
from app.modules.pronosticos.manejadores import evaluacion_programada
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion
from app.workers.tasks.manejadores import ContextoEjecucion
from app.modules.inicializacion import rutas as subidas
from app.modules.ventas import rutas as ventas_http


def sembrar(s, producto, ejecucion, modelo):
    corrida = CorridaPronostico(ejecucion_id=ejecucion, modelo_id=modelo,
        tipo="DEMO_PROGRAMADA", clave_ejecucion="revisiones-fixture", huella_datos_entrada="a"*64,
        fecha_objetivo=date(2022, 8, 24), estado="COMPLETADA")
    s.add(corrida); s.flush()
    s.add(Pronostico(corrida_id=corrida.id, producto_id=producto, estado="DISPONIBLE", cantidad_pronosticada=5))
    venta = VentaDiaria(producto_id=producto, fecha_local=corrida.fecha_objetivo,
                       unidades_vendidas=10, revision_actual=1)
    s.add(venta); s.flush()
    revision = RevisionVenta(venta_id=venta.id, numero_revision=1, unidades_vendidas=10,
                            origen_cambio="IMPORTACION", motivo="Fixture de revisiones")
    s.add(revision); s.flush()
    return corrida, venta, revision.id


def ejecutar(s, tarea):
    return evaluacion_programada(s, ContextoEjecucion(tarea.id, tarea.tipo, tarea.clave_idempotencia, tarea.datos_entrada_json))


def test_tarea_conserva_revision_aunque_se_corrija_antes_del_worker(contexto):
    s, producto, ejecucion, modelo = contexto
    corrida, venta, primera = sembrar(s, producto, ejecucion, modelo)
    antigua = solicitar_evaluacion_corrida(s, corrida.id)
    nueva_revision = corregir_venta(s, venta.id, 12, "Corrección posterior a reserva")
    nueva = solicitar_evaluacion_corrida(s, corrida.id)
    assert nueva.id != antigua.id
    assert ejecutar(s, antigua)["evaluaciones_nuevas"] == 1
    assert ejecutar(s, antigua)["evaluaciones_nuevas"] == 0
    guardada = s.scalar(select(EvaluacionPronostico))
    assert (guardada.revision_venta_id, guardada.unidades_reales) == (primera, 10)
    assert detalle_evaluacion(s, corrida)["pares_pendientes_evaluacion"] == 1
    assert ejecutar(s, nueva)["evaluaciones_nuevas"] == 1
    assert detalle_evaluacion(s, corrida)["total_real_conocido"] == 12
    assert detalle_evaluacion(s, corrida)["pares_pendientes_evaluacion"] == 0
    assert s.scalar(select(func.count()).select_from(EvaluacionPronostico)) == 2
    assert nueva_revision != primera


def test_snapshot_vacio_y_snapshot_ajeno_no_se_sustituyen_por_datos_actuales(contexto):
    s, producto, ejecucion, modelo = contexto
    corrida, venta, revision = sembrar(s, producto, ejecucion, modelo)
    assert evaluar_corrida(s, corrida.id, ejecucion, revisiones=[])["evaluaciones_nuevas"] == 0
    for entrada in [[[producto + 99, revision]], [[producto, revision + 999]], [[True, revision]], [[producto, revision], [producto, revision]]]:
        with pytest.raises(ErrorAPI) as error:
            evaluar_corrida(s, corrida.id, ejecucion, revisiones=entrada)
        assert error.value.codigo == "REVISIONES_INVALIDAS"


def test_patch_reserva_evaluacion_y_repeticion_no_duplica(escenario):
    client, sesiones, admin, _, corrida_id, productos = escenario
    producto = productos["baguette"]
    with sesiones.begin() as s:
        corrida = s.get(CorridaPronostico, corrida_id)
        venta = s.scalar(select(VentaDiaria).where(VentaDiaria.producto_id == producto, VentaDiaria.fecha_local == corrida.fecha_objetivo))
        if venta is None:
            venta = VentaDiaria(producto_id=producto, fecha_local=corrida.fecha_objetivo, unidades_vendidas=10, revision_actual=1)
            s.add(venta); s.flush()
            s.add(RevisionVenta(venta_id=venta.id, numero_revision=1, unidades_vendidas=10, origen_cambio="IMPORTACION", motivo="Fixture"))
        venta_id, cantidad = venta.id, venta.unidades_vendidas + 2
    ruta = f"/api/v1/ventas/{venta_id}"
    entrada = {"unidades_vendidas": cantidad, "motivo": "Conteo corregido"}
    respuesta = client.patch(ruta, headers=admin, json=entrada)
    assert respuesta.status_code == 200, respuesta.text
    ids = respuesta.json()["datos"]["reevaluaciones"]
    assert len(ids) == 1
    assert client.patch(ruta, headers=admin, json=entrada).json()["datos"]["reevaluaciones"] == ids
    with sesiones.begin() as s:
        tarea = s.get(EjecucionAutomatizacion, ids[0])
        assert tarea.estado == "PENDIENTE"
        ejecutar(s, tarea)
        assert detalle_evaluacion(s, s.get(CorridaPronostico, corrida_id))["total_real_conocido"] == cantidad


def test_fallo_reserva_revierte_correccion_http(escenario, monkeypatch):
    client, sesiones, admin, _, _, _ = escenario
    with sesiones() as s:
        venta = s.scalar(select(VentaDiaria))
        id_, cantidad, revision = venta.id, venta.unidades_vendidas, venta.revision_actual
    def fallo(*args):
        raise ErrorAPI(503, "RESERVA_NO_DISPONIBLE", "No se pudo reservar la evaluación")
    monkeypatch.setattr(ventas_http, "solicitar_reevaluaciones_venta", fallo)
    assert client.patch(f"/api/v1/ventas/{id_}", headers=admin,
                        json={"unidades_vendidas": cantidad + 1, "motivo": "Corrección con fallo"}).status_code == 503
    with sesiones() as s:
        venta = s.get(VentaDiaria, id_)
        assert (venta.unidades_vendidas, venta.revision_actual) == (cantidad, revision)


def test_corridas_paginan_mas_alla_de_50_y_filtran_en_servidor(escenario):
    client, sesiones, admin, _, corrida_id, _ = escenario
    with sesiones.begin() as s:
        base = s.get(CorridaPronostico, corrida_id)
        modelo = base.modelo_id
        for i in range(61):
            s.add(CorridaPronostico(ejecucion_id=base.ejecucion_id, modelo_id=modelo, tipo="BACKTEST",
                clave_ejecucion=f"pagina-{i}", huella_datos_entrada="a"*64,
                fecha_objetivo=date(2022, 8, 1) + timedelta(days=i % 20), estado="COMPLETADA"))
    respuesta = client.get(f"/api/v1/pronosticos/corridas?modelo_id={modelo}&tipo=BACKTEST&limite=10&desplazamiento=50", headers=admin)
    assert respuesta.status_code == 200
    assert respuesta.json()["metadatos"]["total"] == 61
    assert len(respuesta.json()["datos"]) == 10
    assert client.get("/api/v1/pronosticos/corridas?desde=2022-08-20&hasta=2022-08-01", headers=admin).status_code == 422
    assert client.get("/api/v1/pronosticos/corridas?limite=101", headers=admin).status_code == 422
    assert client.get("/api/v1/pronosticos/corridas").status_code == 401


def test_subida_acota_lectura_y_detecta_duplicados_y_total(monkeypatch):
    monkeypatch.setattr(subidas, "LIMITE_BYTES", 8)
    monkeypatch.setattr(subidas, "LIMITE_ENTREGA_BYTES", 12)
    class Archivo:
        def __init__(self, nombre, contenido):
            self.filename, self.contenido, self.pedidos = nombre, contenido, []
        async def read(self, size):
            self.pedidos.append(size)
            return self.contenido[:size]
    grande = Archivo("ventas.csv", b"x"*20)
    with pytest.raises(ErrorAPI) as error:
        asyncio.run(subidas._leer_archivos([grande]))
    assert error.value.status_code == 413 and grande.pedidos == [9]
    for archivos, codigo in [([Archivo("Ventas.csv", b"a"), Archivo("VENTAS.CSV", b"a")], "ARCHIVO_REPETIDO"),
            ([Archivo("uno.csv", b"x"*8), Archivo("dos.csv", b"x"*8)], "ENTREGA_DEMASIADO_GRANDE"),
            ([Archivo(f"{i}.csv", b"a") for i in range(6)], "DEMASIADOS_ARCHIVOS")]:
        with pytest.raises(ErrorAPI) as error:
            asyncio.run(subidas._leer_archivos(archivos))
        assert error.value.codigo == codigo
