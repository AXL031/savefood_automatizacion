"""Pruebas unitarias exhaustivas de la evaluación histórica y métricas K03.

Verifica todas las reglas contractuales de POLITICA_EVALUACION.md:
  1. MAE en unidades físicas.
  2. WAPE indefinido (None) si la suma real es cero; WAPE puede superar el 100%.
  3. Convención ±20% con max(real, 1).
  4. Cobertura: ausencia de venta = desconocida (no cero).
  5. Agregación global del tramo completo: NO promediar porcentajes diarios.
  6. Evaluación por día: totales sumados exclusivamente sobre productos evaluables.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

# Añadir foodsave-ml al path para importar módulos
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from metricas import (
    ParEvaluacion,
    MetricasResultado,
    calcular_mae,
    calcular_wape,
    calcular_dentro_rango,
    calcular_cobertura,
    evaluar_pares,
)
from evaluador import evaluar_dia, consolidar_evaluacion_tramo, EvaluacionDia, EvaluacionTramoCompleto
from ejecutar_backtest import _filtrar_cobertura


class TestCoberturaBacktest(unittest.TestCase):
    def test_excluye_producto_sin_modelo_o_historial_suficiente(self):
        filas = pd.DataFrame([
            {"article": "A", "conteo_28_dias": 7, "fecha_objetivo": "2022-07-01"},
            {"article": "A", "conteo_28_dias": 6, "fecha_objetivo": "2022-07-02"},
            {"article": "B", "conteo_28_dias": 28, "fecha_objetivo": "2022-07-01"},
        ])
        elegibles = _filtrar_cobertura(filas, {
            "productos_entrenados": ["A"], "min_observaciones_previas_28_dias": 7,
        })
        self.assertEqual(elegibles[["article", "fecha_objetivo"]].values.tolist(), [["A", "2022-07-01"]])


class TestMae(unittest.TestCase):

    def test_mae_lista_vacia_devuelve_none(self):
        self.assertIsNone(calcular_mae([]))

    def test_mae_prediccion_perfecta_es_cero(self):
        pares = [(10.0, 10.0), (25.0, 25.0)]
        self.assertEqual(calcular_mae(pares), 0.0)

    def test_mae_calculo_exacto_en_unidades(self):
        # Errores: |10 - 15| = 5, |20 - 18| = 2, |30 - 35| = 5 -> total 12 / 3 = 4.0
        pares = [(10.0, 15.0), (20.0, 18.0), (30.0, 35.0)]
        self.assertEqual(calcular_mae(pares), 4.0)


class TestWape(unittest.TestCase):

    def test_wape_lista_vacia_devuelve_none(self):
        self.assertIsNone(calcular_wape([]))

    def test_wape_suma_real_cero_es_indefinido_none(self):
        """POLITICA_EVALUACION.md: Si la suma real es cero, mostrar 'no definido'."""
        pares = [(0.0, 5.0), (0.0, 2.0)]
        self.assertIsNone(calcular_wape(pares))

    def test_wape_prediccion_perfecta_es_cero(self):
        pares = [(15.0, 15.0), (30.0, 30.0)]
        self.assertEqual(calcular_wape(pares), 0.0)

    def test_wape_calculo_porcentual_estandar(self):
        # Reales = 100, suma errores = 20 -> WAPE = 20.0%
        pares = [(60.0, 50.0), (40.0, 50.0)]  # errores: 10 + 10 = 20
        self.assertAlmostEqual(calcular_wape(pares), 20.0, places=4)

    def test_wape_puede_superar_el_100_por_ciento(self):
        """WAPE es un error relativo a la suma real y puede ser > 100%."""
        # Real = 10, pred = 50 -> error = 40 -> WAPE = 400%
        pares = [(10.0, 50.0)]
        wape = calcular_wape(pares)
        self.assertIsNotNone(wape)
        self.assertEqual(wape, 400.0)


class TestDentroRango(unittest.TestCase):

    def test_dentro_rango_lista_vacia_devuelve_none(self):
        self.assertIsNone(calcular_dentro_rango([]))

    def test_dentro_rango_20_por_ciento_estandar(self):
        # (100, 110) -> error 10 / 100 = 10% <= 20% -> acierto
        # (100, 130) -> error 30 / 100 = 30% > 20% -> no
        pares = [(100.0, 110.0), (100.0, 130.0)]
        self.assertEqual(calcular_dentro_rango(pares, 0.20), 50.0)

    def test_dentro_rango_con_real_cero_usa_max_real_uno(self):
        """Fórmula contractual: |real - p| / max(real, 1.0) <= umbral.

        Si real=0 y pred=0 -> |0-0| / 1 = 0 <= 0.20 -> acierto.
        Si real=0 y pred=1 -> |0-1| / 1 = 1 > 0.20 -> fallo.
        """
        pares = [(0.0, 0.0), (0.0, 1.0)]
        self.assertEqual(calcular_dentro_rango(pares, 0.20), 50.0)

    def test_tolerancia_10_por_ciento(self):
        pares = [(100.0, 108.0), (100.0, 115.0)]
        self.assertEqual(calcular_dentro_rango(pares, 0.10), 50.0)


class TestCobertura(unittest.TestCase):

    def test_cobertura_cero_pronosticados(self):
        self.assertEqual(calcular_cobertura(0, 0), 0.0)

    def test_cobertura_total_conocido(self):
        self.assertEqual(calcular_cobertura(10, 10), 100.0)

    def test_cobertura_parcial_por_ausencias(self):
        # 10 productos pronosticados, solo 7 con venta real registrada
        self.assertAlmostEqual(calcular_cobertura(10, 7), 70.0, places=2)


class TestEvaluarPares(unittest.TestCase):

    def test_evaluar_pares_separa_evaluables_de_excluidos(self):
        pares = [
            ParEvaluacion("P1", "2022-08-01", previsto=10.0, real=12.0),
            ParEvaluacion("P2", "2022-08-01", previsto=20.0, real=None),  # ausencia
            ParEvaluacion("P3", "2022-08-01", previsto=30.0, real=28.0),
        ]
        res = evaluar_pares(pares)
        self.assertEqual(res.total_pronosticados, 3)
        self.assertEqual(res.pares_evaluables, 2)
        self.assertEqual(res.productos_excluidos, 1)
        self.assertAlmostEqual(res.cobertura_pct, 66.67, places=1)
        self.assertEqual(res.mae, 2.0)  # (|12-10| + |28-30|) / 2 = 2.0
        self.assertIsNotNone(res.wape_pct)

    def test_as_dict_formato_completo(self):
        pares = [ParEvaluacion("P1", "2022-08-01", previsto=5.0, real=5.0)]
        d = evaluar_pares(pares).as_dict()
        for k in ["cobertura_pct", "mae", "wape_pct", "dentro_mas_menos_20_pct", "dentro_mas_menos_10_pct"]:
            self.assertIn(k, d)


class TestEvaluadorDia(unittest.TestCase):

    def test_evaluar_dia_suma_exclusivamente_productos_evaluables(self):
        """POLITICA_EVALUACION.md: total previsto y total real sumados ambos sobre los

        mismos productos evaluables de ese día.
        """
        pares = [
            ParEvaluacion("P1", "2022-08-10", previsto=15.0, real=20.0),
            ParEvaluacion("P2", "2022-08-10", previsto=50.0, real=None),  # Debe quedar fuera de la suma
            ParEvaluacion("P3", "2022-08-10", previsto=25.0, real=30.0),
        ]
        dia = evaluar_dia("2022-08-10", pares)
        # Previsto evaluable: 15 + 25 = 40 (NO 90)
        self.assertEqual(dia.total_previsto_evaluable, 40.0)
        # Real evaluable: 20 + 30 = 50
        self.assertEqual(dia.total_real_conocido, 50.0)
        self.assertEqual(dia.productos_evaluables, 2)
        self.assertEqual(dia.productos_excluidos, 1)

        # Verificar desglose
        self.assertEqual(len(dia.desglose_productos), 3)
        excluido = [d for d in dia.desglose_productos if d["producto_id"] == "P2"][0]
        self.assertEqual(excluido["motivo_exclusion"], "VENTA_REAL_DESCONOCIDA")
        self.assertIsNone(excluido["real"])


class TestConsolidarTramoCompleto(unittest.TestCase):

    def test_tramo_completo_no_promedia_porcentajes_diarios(self):
        """Regla clave: el WAPE global se calcula sobre sumas globales de error y real,

        NUNCA promediando los WAPEs de cada día.
        """
        # Día 1: Real = 10, Error = 5 -> WAPE_dia1 = 50.0%
        # Día 2: Real = 100, Error = 10 -> WAPE_dia2 = 10.0%
        # Promedio simple de WAPEs = (50 + 10) / 2 = 30.0%
        # WAPE global contractual = 100 * (5 + 10) / (10 + 100) = 15 / 110 = 13.636%
        pares = [
            ParEvaluacion("P1", "2022-08-01", previsto=15.0, real=10.0),
            ParEvaluacion("P1", "2022-08-02", previsto=110.0, real=100.0),
        ]
        tramo = consolidar_evaluacion_tramo(
            version_modelo="1.0.0",
            fecha_inicio="2022-08-01",
            fecha_fin="2022-08-02",
            pares_todos=pares,
        )

        wape_global = tramo.metricas_globales.wape_pct
        self.assertIsNotNone(wape_global)
        # Debe coincidir con 13.636%, NO con el promedio de 30.0%
        self.assertAlmostEqual(wape_global, 13.636, places=2)
        self.assertNotEqual(round(wape_global, 2), 30.0)

    def test_tramo_completo_estructura_y_metadatos(self):
        pares = [ParEvaluacion("P1", "2022-08-01", previsto=10.0, real=10.0)]
        tramo = consolidar_evaluacion_tramo("1.0.0", "2022-08-01", "2022-08-01", pares)
        d = tramo.as_dict()
        self.assertEqual(d["estado"], "demostracion_historica")
        self.assertEqual(d["version_modelo"], "1.0.0")
        self.assertEqual(d["fechas_evaluadas"], 1)
        self.assertEqual(d["total_pares_evaluables"], 1)
        self.assertEqual(len(d["serie_diaria"]), 1)


if __name__ == "__main__":
    unittest.main()
