"""Reportes reales en sesión aislada; sin Telegram ni cambios de stock."""
import csv
from datetime import date, timedelta
from io import StringIO

import pytest
from sqlalchemy import func, select

from test_api_inicializacion_ventas import cliente, token, cabecera
from test_planificacion_m02 import escenario, solicitar, saldos
from test_compras_l02 import compra, generar
from app.core.base_datos import obtener_sesion
from app.modules.productos.modelos import Producto, SkuProducto
from app.modules.ventas.servicio import registrar_ventas_diarias, corregir_venta
from app.modules.pronosticos.evaluacion import evaluar_corrida
from app.modules.pronosticos.modelos import ArtefactoModelo, CorridaPronostico, Pronostico
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion
from app.modules.compras.modelos import EnvioPedido, PedidoCompra, PropuestaCompra
from app.principal import app


@pytest.fixture
def operador(cliente):
    return cabecera(token(cliente, "operador@example.com", "clave-segura-operador"))


def sesion_prueba():
    return next(app.dependency_overrides[obtener_sesion]())


def sembrar_ventas(diarios, nombre="Pan"):
    with sesion_prueba() as sesion:
        producto = Producto(codigo="pan", nombre=nombre)
        sesion.add(producto); sesion.flush()
        sesion.add(SkuProducto(producto_id=producto.id, origen="bakery", sku_externo="PAN"))
        registrar_ventas_diarias(sesion, {(producto.id, fecha): cantidad for fecha, cantidad in diarios.items()},
                                "reportes", "a" * 64, len(diarios), "Prueba aislada")
        sesion.commit()
        return producto.id


def datos(cliente, operador, consulta=""):
    respuesta = cliente.get("/api/v1/informes/resumen" + consulta, headers=operador)
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["datos"]


def test_permisos_y_base_vacia(cliente, operador):
    for ruta in ("/resumen", "/exportar?tipo=ventas"):
        assert cliente.get("/api/v1/informes" + ruta).status_code == 401
    reporte = datos(cliente, operador)
    assert reporte["ventas"]["registros"] == 0 and reporte["ventas"]["serie_diaria"] == []
    assert reporte["evaluacion"] is None and reporte["aviso_evaluacion"]
    assert reporte["periodo"]["ventas_hasta"] is None
    assert reporte["pedidos"]["total"] == 0
    assert len(reporte["pedidos"]["por_estado"]) == 9
    assert cliente.get("/api/v1/informes/exportar?tipo=ventas", headers=operador).status_code == 200


def test_fechas_default_ceros_huecos_y_revision_actual(cliente, operador):
    pid = sembrar_ventas({date(2022, 8, 21): 12, date(2022, 8, 23): 0})
    reporte = datos(cliente, operador)
    assert reporte["periodo"]["hasta"] == "2022-08-23" and reporte["periodo"]["dias_calendario"] == 30
    assert reporte["ventas"]["unidades"] == 12 and reporte["ventas"]["dias_observados"] == 2
    assert reporte["ventas"]["serie_diaria"] == [
        {"fecha": "2022-08-21", "unidades": 12, "productos_observados": 1},
        {"fecha": "2022-08-23", "unidades": 0, "productos_observados": 1}]
    from app.modules.ventas.modelos import VentaDiaria, RevisionVenta
    with sesion_prueba() as sesion:
        venta_id = sesion.scalar(select(VentaDiaria.id).where(VentaDiaria.producto_id == pid, VentaDiaria.unidades_vendidas == 12))
        corregir_venta(sesion, venta_id, 7, "Corregida en prueba"); sesion.commit()
    assert datos(cliente, operador)["ventas"]["unidades"] == 7
    with sesion_prueba() as sesion:
        assert sesion.scalar(select(func.count()).select_from(RevisionVenta)) == 3


@pytest.mark.parametrize("consulta", [
    "?desde=2022-08-24&hasta=2022-08-23", "?desde=2022-01-01&hasta=2023-01-02",
    "?desde=fecha-invalida", "?modelo_id=0", "?modelo_id=-1"])
def test_validacion_rangos_y_modelo(cliente, operador, consulta):
    assert cliente.get("/api/v1/informes/resumen" + consulta, headers=operador).status_code == 422
    assert cliente.get("/api/v1/informes/exportar" + consulta + "&tipo=ventas", headers=operador).status_code == 422


def test_periodo_maximo_366_e_inexistente(cliente, operador):
    assert datos(cliente, operador, "?desde=2022-01-01&hasta=2023-01-01")["periodo"]["dias_calendario"] == 366
    assert cliente.get("/api/v1/informes/resumen?modelo_id=999", headers=operador).status_code == 404
    assert cliente.get("/api/v1/informes/exportar?tipo=desconocido", headers=operador).status_code == 422


def test_error_de_evaluacion_no_se_convierte_en_cero(cliente, operador, monkeypatch):
    from app.core.errores import ErrorAPI
    from app.modules.informes import servicio

    def fallar(*args, **kwargs):
        raise ErrorAPI(503, "EVALUACION_NO_DISPONIBLE", "La evaluación requiere revisión.")

    monkeypatch.setattr(servicio, "resumen_evaluacion", fallar)
    respuesta = cliente.get("/api/v1/informes/resumen", headers=operador)
    assert respuesta.status_code == 503
    assert respuesta.json()["error"]["codigo"] == "EVALUACION_NO_DISPONIBLE" and "datos" not in respuesta.json()
    assert cliente.get("/api/v1/informes/resumen?incluir_evaluacion=false", headers=operador).status_code == 200
    assert cliente.get("/api/v1/informes/exportar?tipo=ventas", headers=operador).status_code == 200


def test_periodo_completo_csv_sin_limite_y_texto_seguro(cliente, operador):
    inicio = date(2022, 1, 1)
    sembrar_ventas({inicio + timedelta(days=n): n for n in range(75)}, nombre=' =HYPERLINK("mal");Pan\nprueba')
    consulta = "?desde=2022-01-01&hasta=2022-03-16"
    reporte = datos(cliente, operador, consulta)
    assert len(reporte["ventas"]["serie_diaria"]) == 75 and reporte["ventas"]["unidades"] == sum(range(75))
    respuesta = cliente.get("/api/v1/informes/exportar" + consulta + "&tipo=ventas", headers=operador)
    assert respuesta.status_code == 200 and respuesta.content.startswith(b"\xef\xbb\xbf")
    assert respuesta.headers["cache-control"] == "no-store" and "2022-03-16.csv" in respuesta.headers["content-disposition"]
    filas = list(csv.reader(StringIO(respuesta.content.decode("utf-8-sig")), delimiter=";"))
    fechas = [fila for fila in filas if fila and fila[0].startswith("2022-")]
    assert len(fechas) == 75 and fechas[-1][0] == "2022-03-16"
    assert any(len(fila) == 4 and fila[1].startswith("' =HYPERLINK") for fila in filas)
    vacio = datos(cliente, operador, "?desde=2023-01-01&hasta=2023-01-31")
    assert vacio["ventas"]["serie_diaria"] == []


def test_pedidos_no_cuentan_intentos_y_conservan_stock(compra):
    entorno, _, _, _ = compra
    cliente, sesiones, admin, operador, _, _ = entorno
    plan = solicitar(entorno).json()["datos"]
    propuesta = generar(entorno, plan["id"]).json()["datos"]
    pedido = propuesta["pedidos"][0]
    otro_plan = solicitar(entorno, "informe-sin-pedidos").json()["datos"]
    with sesiones.begin() as sesion:
        sesion.get(PedidoCompra, pedido["id"]).estado = "FALLIDO"
        for intento in (1, 2):
            sesion.add(EnvioPedido(pedido_id=pedido["id"], numero_intento=intento, estado="FALLIDO",
                                  chat_id="123", credencial_huella="d" * 64, texto="Solo fixture"))
        sesion.add(PropuestaCompra(plan_id=otro_plan["id"], fecha_objetivo=date(2022, 8, 24),
            estado="SIN_FALTANTES", activa=False, modo_envio="REQUIERE_APROBACION", necesidades_json={}, incidencias_json=[]))
    antes = saldos(sesiones)
    reporte = datos(cliente, operador, "?desde=2022-08-24&hasta=2022-08-24&incluir_evaluacion=false")
    assert reporte["pedidos"]["total"] == 1
    assert next(e for e in reporte["pedidos"]["por_estado"] if e["estado"] == "FALLIDO")["cantidad"] == 1
    assert reporte["pedidos"]["propuestas"] == 2 and reporte["pedidos"]["propuestas_sin_pedidos"] == 1
    exportado = cliente.get("/api/v1/informes/exportar?tipo=pedidos&desde=2022-08-24&hasta=2022-08-24", headers=operador)
    assert exportado.status_code == 200 and "Fallido;1" in exportado.content.decode("utf-8-sig")
    assert "credencial_huella" not in exportado.text and "Solo fixture" not in exportado.text
    assert saldos(sesiones) == antes
    with sesiones() as sesion:
        assert sesion.scalar(select(func.count()).select_from(EnvioPedido)) == 2


def test_evaluacion_filtrada_reutiliza_pares_y_exporta_ausencia(cliente, operador):
    pid = sembrar_ventas({date(2022, 8, 21): 10, date(2022, 8, 23): 0})
    with sesion_prueba() as sesion:
        desconocido = Producto(codigo="sin-ventas", nombre="Sin ventas"); sesion.add(desconocido); sesion.flush()
        modelo = ArtefactoModelo(version_modelo="informes-test", ruta_local="test", sha256="b" * 64,
            huella_datos_entrenamiento="c" * 64, fecha_corte_entrenamiento=date(2022, 6, 30),
            particion_json={"inicio_prueba": "2022-08-01", "fin_prueba": "2022-08-31"}, estado="LISTO_DEMO")
        sesion.add(modelo); sesion.flush()
        for dia, cantidad in ((21, 12), (23, 4)):
            tarea = EjecucionAutomatizacion(tipo="GENERAR_PROPUESTA", clave_idempotencia=f"informe-{dia}",
                huella_entrada="a" * 64, datos_entrada_json={}, estado="PENDIENTE")
            sesion.add(tarea); sesion.flush()
            corrida = CorridaPronostico(ejecucion_id=tarea.id, modelo_id=modelo.id, tipo="BACKTEST",
                clave_ejecucion=f"backtest-{modelo.id}-{dia}", huella_datos_entrada="a" * 64,
                fecha_objetivo=date(2022, 8, dia), estado="COMPLETADA")
            sesion.add(corrida); sesion.flush()
            for producto, previsto in ((pid, cantidad), (desconocido.id, 8)):
                sesion.add(Pronostico(corrida_id=corrida.id, producto_id=producto, cantidad_pronosticada=previsto, estado="DISPONIBLE"))
            sesion.flush(); evaluar_corrida(sesion, corrida.id, tarea.id)
        sesion.commit(); modelo_id = modelo.id
    consulta = f"?desde=2022-08-21&hasta=2022-08-21&modelo_id={modelo_id}"
    reporte = datos(cliente, operador, consulta)
    evaluacion = reporte["evaluacion"]
    assert evaluacion["fecha_inicio"] == evaluacion["fecha_fin"] == "2022-08-21"
    assert len(evaluacion["serie_diaria"]) == 1 and evaluacion["metricas_globales"]["mae"] == 2
    assert evaluacion["metricas_globales"]["cobertura_pct"] == 50
    csv_respuesta = cliente.get("/api/v1/informes/exportar" + consulta + "&tipo=pronosticos", headers=operador)
    filas = list(csv.reader(StringIO(csv_respuesta.content.decode("utf-8-sig")), delimiter=";"))
    assert any(len(f) == 7 and f[2] == "Sin ventas" and f[4] == "" for f in filas)
    otro = datos(cliente, operador, f"?desde=2022-08-23&hasta=2022-08-23&modelo_id={modelo_id}")["evaluacion"]
    assert otro["metricas_globales"]["mae"] == 4 and otro["metricas_globales"]["wape_pct"] is None
