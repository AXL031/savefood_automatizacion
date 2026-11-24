"""Control por desviación: la evaluación pronóstico-real abre y cierra el aviso de reentrenamiento."""
from datetime import date

import pytest
from sqlalchemy import func, select

from test_pronosticos_k02_k03 import contexto  # noqa: F401
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion
from app.modules.operaciones.modelos import AvisoOperacion
from app.modules.pronosticos.control_desviacion import controlar_desviacion
from app.modules.pronosticos.evaluacion import solicitar_evaluacion_corrida
from app.modules.pronosticos.manejadores import evaluacion_programada
from app.modules.pronosticos.modelos import CorridaPronostico, Pronostico
from app.modules.ventas.modelos import RevisionVenta, VentaDiaria
from app.workers.tasks.manejadores import ContextoEjecucion


@pytest.fixture(autouse=True)
def consigna(monkeypatch):
    monkeypatch.setenv("DESVIACION_WAPE_UMBRAL", "35")
    monkeypatch.setenv("DESVIACION_MIN_PARES", "1")


def corrida_evaluada(s, producto, ejecucion, modelo, fecha, previsto, real, tipo="DEMO_PROGRAMADA"):
    corrida = CorridaPronostico(ejecucion_id=ejecucion, modelo_id=modelo, tipo=tipo,
                                clave_ejecucion=f"desviacion-{fecha}-{tipo}", huella_datos_entrada="a" * 64,
                                fecha_objetivo=fecha, estado="COMPLETADA")
    s.add(corrida); s.flush()
    s.add(Pronostico(corrida_id=corrida.id, producto_id=producto, estado="DISPONIBLE", cantidad_pronosticada=previsto))
    venta = s.scalar(select(VentaDiaria).where(VentaDiaria.producto_id == producto, VentaDiaria.fecha_local == fecha))
    if venta is None:
        venta = VentaDiaria(producto_id=producto, fecha_local=fecha, unidades_vendidas=real, revision_actual=1)
        s.add(venta); s.flush()
        s.add(RevisionVenta(venta_id=venta.id, numero_revision=1, unidades_vendidas=real,
                            origen_cambio="CIERRE", motivo="Cierre del día"))
        s.flush()
    tarea = solicitar_evaluacion_corrida(s, corrida.id)
    salida = evaluacion_programada(s, ContextoEjecucion(tarea.id, tarea.tipo, tarea.clave_idempotencia,
                                                         tarea.datos_entrada_json))
    return corrida, salida["control_desviacion"]


def avisos(s):
    return list(s.scalars(select(AvisoOperacion).order_by(AvisoOperacion.id)))


def test_desviacion_abre_un_solo_aviso_y_una_medicion_correcta_lo_cierra(contexto):
    s, producto, ejecucion, modelo = contexto

    # 5 previstas frente a 10 vendidas: WAPE 50 % > 35 % → aviso con la acción correctiva.
    primera, control = corrida_evaluada(s, producto, ejecucion, modelo, date(2022, 9, 1), 5, 10)
    assert control["control"] == "DESVIACION" and control["wape"] == 50.0 and control["nuevo_aviso"]
    aviso = avisos(s)[0]
    assert aviso.datos["accion"] == "REENTRENAR" and aviso.datos["modelo_id"] == modelo
    assert "50.00 %" in aviso.datos["descripcion"] and aviso.resolucion is None

    # Otra desviación no repite la alerta: actualiza la misma con la última medición.
    _, control = corrida_evaluada(s, producto, ejecucion, modelo, date(2022, 9, 2), 20, 10)
    assert control["control"] == "DESVIACION" and not control["nuevo_aviso"]
    assert len(avisos(s)) == 1 and avisos(s)[0].datos["desviaciones_consecutivas"] == 2

    # Una fecha anterior a la desviación no demuestra la corrección.
    _, control = corrida_evaluada(s, producto, ejecucion, modelo, date(2022, 8, 31), 10, 10)
    assert control["control"] == "DENTRO_UMBRAL" and control["avisos_resueltos"] == []

    # Vuelve a la consigna (9 frente a 10: WAPE 10 %) → el aviso se resuelve solo con la evidencia.
    _, control = corrida_evaluada(s, producto, ejecucion, modelo, date(2022, 9, 3), 9, 10)
    assert control["control"] == "DENTRO_UMBRAL" and control["avisos_resueltos"] == [aviso.id]
    s.refresh(aviso)
    assert "10.00 %" in aviso.resolucion and aviso.datos["wape_resolucion"] == 10.0


def test_backtest_y_datos_insuficientes_no_alertan(contexto, monkeypatch):
    s, producto, ejecucion, modelo = contexto
    corrida, _ = corrida_evaluada(s, producto, ejecucion, modelo, date(2022, 9, 5), 1, 10, tipo="BACKTEST")
    assert controlar_desviacion(s, corrida.id)["control"] == "NO_APLICA"
    monkeypatch.setenv("DESVIACION_MIN_PARES", "5")
    _, control = corrida_evaluada(s, producto, ejecucion, modelo, date(2022, 9, 6), 1, 10)
    assert control["control"] == "DATOS_INSUFICIENTES"
    assert s.scalar(select(func.count()).select_from(AvisoOperacion)) == 0
    assert s.scalar(select(func.count()).select_from(EjecucionAutomatizacion)) >= 1
