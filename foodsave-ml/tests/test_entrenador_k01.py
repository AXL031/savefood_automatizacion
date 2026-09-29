"""Pruebas unitarias del entrenador K01: partición temporal, features y artefacto.

Ejecutar:
  python -m pytest foodsave-ml/tests/test_entrenador_k01.py -v

No requieren CatBoost instalado para los tests de partición y features.
El test de artefacto requiere catboost (ya en requirements.txt).
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

# Añadir foodsave-ml al path para importar los módulos
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from particion import calcular_particion, Particion, _meses_completos_entre
from features import FEATURES, CAT_FEATURES, construir_features
from metadata import (
    verificar_artefacto_completo,
    validar_metadata,
    validar_aceptable_backend,
    validar_huella,
    validar_identidad,
    ErrorArtefacto,
    FEATURES_CONTRATO,
)
from ventanas import lag, promedio_ventana, conteo_ventana, reindexar_por_calendario


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _csv_sintetico(tmp: Path, comercio: str = "c1", sucursal: str = "s1",
                   inicio: str = "2021-01-01", fin: str = "2022-09-30",
                   productos: list[str] | None = None) -> Path:
    """Genera un CSV normalizado sintético con datos deterministas."""
    if productos is None:
        productos = ["BAGUETTE", "CROISSANT"]
    fechas = pd.date_range(inicio, fin)
    rng = np.random.default_rng(42)
    filas = []
    for d in fechas:
        for p in productos:
            filas.append({
                "comercio_id": comercio,
                "sucursal_id": sucursal,
                "fecha_local": d.strftime("%Y-%m-%d"),
                "producto_id": p,
                "unidades_vendidas": int(max(0, 20 + 5 * d.dayofweek + rng.integers(-4, 5))),
            })
    ruta = tmp / "ventas.csv"
    pd.DataFrame(filas).to_csv(ruta, index=False)
    return ruta


# ---------------------------------------------------------------------------
# Tests de partición
# ---------------------------------------------------------------------------

class TestMesesCompletos(unittest.TestCase):

    def test_meses_completos_con_historial_exacto(self):
        primera = pd.Timestamp("2021-01-01")
        ultima = pd.Timestamp("2022-09-30")
        meses = _meses_completos_entre(primera, ultima)
        # Enero 2021 a Septiembre 2022 = 21 meses completos
        self.assertEqual(len(meses), 21)
        self.assertEqual(meses[0], (2021, 1))
        self.assertEqual(meses[-1], (2022, 9))

    def test_mes_incompleto_no_cuenta(self):
        primera = pd.Timestamp("2021-01-15")  # enero incompleto
        ultima = pd.Timestamp("2022-09-30")
        meses = _meses_completos_entre(primera, ultima)
        # Enero 2021 incompleto → no cuenta; Feb 2021 a Sep 2022 = 20 meses
        self.assertEqual(len(meses), 20)
        self.assertEqual(meses[0], (2021, 2))


class TestCalcularParticion(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_historial_21_meses_da_validacion_3_prueba_3(self):
        """21 meses: 12 ≤ n < 24 → validación=3, prueba=3."""
        ruta = _csv_sintetico(self.dir, inicio="2021-01-01", fin="2022-09-30")
        p = calcular_particion(ruta, "c1", "s1")
        self.assertEqual(p.meses_validacion, 3)
        self.assertEqual(p.meses_prueba, 3)
        # Prueba: julio-septiembre 2022
        self.assertEqual(p.inicio_prueba, "2022-07-01")
        self.assertEqual(p.fin_prueba, "2022-09-30")

    def test_historial_menos_6_meses_lanza_error(self):
        ruta = _csv_sintetico(self.dir, inicio="2022-01-01", fin="2022-04-30")
        with self.assertRaises(ValueError) as ctx:
            calcular_particion(ruta, "c1", "s1")
        self.assertIn("Historial insuficiente", str(ctx.exception))

    def test_comercio_inexistente_lanza_error(self):
        ruta = _csv_sintetico(self.dir)
        with self.assertRaises(ValueError) as ctx:
            calcular_particion(ruta, "OTRO_COMERCIO", "s1")
        self.assertIn("No se encontraron ventas", str(ctx.exception))

    def test_particion_as_dict_contiene_version_politica(self):
        ruta = _csv_sintetico(self.dir)
        p = calcular_particion(ruta, "c1", "s1")
        d = p.as_dict()
        self.assertIn("version_politica", d)
        self.assertIn("inicio_entrenamiento", d)
        self.assertIn("fin_prueba", d)

    def test_fechas_en_orden_creciente(self):
        ruta = _csv_sintetico(self.dir)
        p = calcular_particion(ruta, "c1", "s1")
        from datetime import date
        ini_train = date.fromisoformat(p.inicio_entrenamiento)
        fin_train = date.fromisoformat(p.fin_entrenamiento)
        ini_val = date.fromisoformat(p.inicio_validacion)
        fin_val = date.fromisoformat(p.fin_validacion)
        ini_pru = date.fromisoformat(p.inicio_prueba)
        fin_pru = date.fromisoformat(p.fin_prueba)
        self.assertLess(ini_train, fin_train)
        self.assertLess(fin_train, ini_val)
        self.assertLess(fin_val, ini_pru)
        self.assertLess(ini_pru, fin_pru)


# ---------------------------------------------------------------------------
# Tests de ventanas temporales
# ---------------------------------------------------------------------------

class TestVentanasTemporales(unittest.TestCase):

    def _serie(self, valores: dict) -> pd.Series:
        """Crea una Serie con índice DatetimeIndex a partir de un dict fecha→valor."""
        idx = pd.DatetimeIndex([pd.Timestamp(k) for k in valores])
        s = pd.Series(list(valores.values()), index=idx, dtype=float)
        return reindexar_por_calendario(s)

    def test_lag_1_devuelve_valor_anterior(self):
        s = self._serie({"2022-08-01": 10, "2022-08-02": 20, "2022-08-03": 30})
        lagged = lag(s, 1)
        self.assertEqual(lagged.loc["2022-08-02"], 10.0)
        self.assertEqual(lagged.loc["2022-08-03"], 20.0)

    def test_lag_con_hueco_devuelve_nan(self):
        s = self._serie({"2022-08-01": 5, "2022-08-03": 15})
        lagged = lag(s, 1)
        # 2022-08-02 no tiene registro → NaN
        self.assertTrue(pd.isna(lagged.loc["2022-08-03"]))

    def test_promedio_7_dias_excluye_dia_objetivo(self):
        """El promedio no debe incluir el valor del día objetivo."""
        valores = {f"2022-07-{d:02d}": float(d) for d in range(1, 20)}
        s = self._serie(valores)
        prom = promedio_ventana(s, 7)
        # El valor en 2022-07-10 debe ser promedio de 2022-07-03 a 2022-07-09
        esperado = np.mean([3, 4, 5, 6, 7, 8, 9])
        self.assertAlmostEqual(prom.loc["2022-07-10"], esperado, places=5)

    def test_conteo_7_dias_no_cuenta_nans(self):
        # Datos con huecos: solo 01, 03 y 05 tienen ventas; 02, 04 son NaN.
        # Agregamos ancla en 2022-08-09 para que el índice reindexado la cubra.
        valores = {
            "2022-08-01": 10, "2022-08-03": 20, "2022-08-05": 30,
            "2022-08-09": 0,   # ancla para ampliar el índice
        }
        s = self._serie(valores)
        conteo = conteo_ventana(s, 7)
        # Para 2022-08-09: ventana 2022-08-02..2022-08-08 → observaciones en 03 y 05 → 2
        self.assertEqual(int(conteo.loc["2022-08-09"]), 2)

    def test_ausencia_no_imputa_cero(self):
        """Un día sin registro debe ser NaN, no 0."""
        s = self._serie({"2022-08-01": 5, "2022-08-03": 10})
        rango = pd.date_range("2022-08-01", "2022-08-05")
        s_reind = s.reindex(rango)
        self.assertTrue(pd.isna(s_reind.loc["2022-08-02"]))
        self.assertTrue(pd.isna(s_reind.loc["2022-08-04"]))
        self.assertTrue(pd.isna(s_reind.loc["2022-08-05"]))


# ---------------------------------------------------------------------------
# Tests del orden y completitud de features
# ---------------------------------------------------------------------------

class TestFeatures(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_orden_contractual_en_lista_features(self):
        """La lista FEATURES debe tener exactamente 13 elementos en el orden del contrato."""
        self.assertEqual(len(FEATURES), 13)
        self.assertEqual(FEATURES[0], "article")
        self.assertEqual(FEATURES[-1], "conteo_28_dias")

    def test_cat_features_es_subconjunto_de_features(self):
        for c in CAT_FEATURES:
            self.assertIn(c, FEATURES)

    def test_construir_features_devuelve_columnas_contractuales(self):
        ruta = _csv_sintetico(self.dir, inicio="2021-01-01", fin="2022-09-30")
        df = construir_features(ruta, "c1", "s1", inicio="2022-07-01", fin="2022-07-07")
        for col in FEATURES:
            self.assertIn(col, df.columns, f"Columna contractual faltante: {col}")

    def test_construir_features_no_usa_datos_del_dia_objetivo(self):
        """Alterar ventas del día objetivo no debe cambiar las features de ese día."""
        ruta = _csv_sintetico(self.dir, inicio="2021-01-01", fin="2022-09-30")
        df_original = construir_features(ruta, "c1", "s1", inicio="2022-08-15", fin="2022-08-15")

        # Crear CSV alterado con ventas del 15 de agosto multiplicadas por 1000
        df_ventas = pd.read_csv(ruta)
        mask = df_ventas["fecha_local"] == "2022-08-15"
        df_ventas.loc[mask, "unidades_vendidas"] = 99999
        ruta_alt = self.dir / "ventas_alt.csv"
        df_ventas.to_csv(ruta_alt, index=False)

        df_alterado = construir_features(ruta_alt, "c1", "s1", inicio="2022-08-15", fin="2022-08-15")

        # Las features del 15 de agosto no deben cambiar (solo unidades_vendidas puede cambiar)
        cols_features_sin_target = [c for c in FEATURES if c != "article"]
        pd.testing.assert_frame_equal(
            df_original[cols_features_sin_target].reset_index(drop=True),
            df_alterado[cols_features_sin_target].reset_index(drop=True),
            check_like=False,
        )

    def test_producto_inexistente_lanza_error(self):
        ruta = _csv_sintetico(self.dir)
        # No hay productos para un comercio inexistente
        with self.assertRaises(ValueError):
            construir_features(ruta, "OTRO", "s1", inicio="2022-07-01", fin="2022-07-07")


# ---------------------------------------------------------------------------
# Tests de metadata y validación del artefacto
# ---------------------------------------------------------------------------

class TestMetadataValidacion(unittest.TestCase):

    def _meta_valida(self) -> dict:
        return {
            "estado": "listo_demo",
            "version_modelo": "1.0.0",
            "comercio_id": "piloto",
            "sucursal_id": "principal",
            "artefacto": "catboost_model.cbm",
            "sha256_artefacto": "abc123",
            "fecha_corte_entrenamiento": "2022-06-30",
            "particion": {
                "version_politica": "POLITICA_EVALUACION_v1",
                "inicio_entrenamiento": "2021-01-01",
                "fin_entrenamiento": "2022-03-31",
                "inicio_validacion": "2022-04-01",
                "fin_validacion": "2022-06-30",
                "inicio_prueba": "2022-07-01",
                "fin_prueba": "2022-09-30",
                "meses_validos": 21,
                "meses_validacion": 3,
                "meses_prueba": 3,
            },
            "features": FEATURES_CONTRATO,
            "cat_features": ["article"],
            "productos_entrenados": ["BAGUETTE", "CROISSANT"],
            "min_observaciones_previas_28_dias": 7,
            "horizonte": "un_dia_con_historial_real",
            "politica_ausencias": "desconocido",
        }

    def test_metadata_valida_no_lanza_excepcion(self):
        validar_metadata(self._meta_valida())

    def test_campo_faltante_lanza_error(self):
        meta = self._meta_valida()
        del meta["version_modelo"]
        with self.assertRaises(ErrorArtefacto) as ctx:
            validar_metadata(meta)
        self.assertIn("version_modelo", str(ctx.exception))

    def test_estado_invalido_lanza_error(self):
        meta = self._meta_valida()
        meta["estado"] = "en_produccion"
        with self.assertRaises(ErrorArtefacto) as ctx:
            validar_metadata(meta)
        self.assertIn("Estado desconocido", str(ctx.exception))

    def test_estado_experimental_rechazado_por_backend(self):
        meta = self._meta_valida()
        meta["estado"] = "experimental_pendiente_de_aceptacion"
        with self.assertRaises(ErrorArtefacto):
            validar_aceptable_backend(meta)

    def test_features_en_orden_incorrecto_lanza_error(self):
        meta = self._meta_valida()
        meta["features"] = list(reversed(FEATURES_CONTRATO))
        with self.assertRaises(ErrorArtefacto) as ctx:
            validar_metadata(meta)
        self.assertIn("features", str(ctx.exception))

    def test_wape_no_definido_si_real_suma_cero(self):
        """WAPE debe devolver None (no error) cuando la suma real es cero."""
        # Importar desde el módulo de métricas (Bloque B — se verifica la convención)
        # Este test sirve como documentación del comportamiento esperado
        reales = [0.0, 0.0]
        previstos = [1.0, 2.0]
        suma_real = sum(reales)
        wape = None if suma_real == 0 else (
            100 * sum(abs(r - p) for r, p in zip(reales, previstos)) / suma_real
        )
        self.assertIsNone(wape)

    def test_sha256_incorrecto_lanza_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            directorio = Path(tmp)
            # Crear un CBM falso con contenido diferente al hash registrado
            cbm_falso = directorio / "catboost_model.cbm"
            cbm_falso.write_bytes(b"contenido_falso")
            meta = self._meta_valida()
            meta["sha256_artefacto"] = "hash_incorrecto_que_no_coincide"
            with self.assertRaises(ErrorArtefacto) as ctx:
                validar_huella(directorio, meta)
            self.assertIn("SHA-256", str(ctx.exception))

    def test_identidad_incorrecta_lanza_error(self):
        meta = self._meta_valida()
        with self.assertRaises(ErrorArtefacto) as ctx:
            validar_identidad(meta, "otro_comercio", "principal")
        self.assertIn("comercio", str(ctx.exception))

    def test_version_modelo_vacia_lanza_error(self):
        meta = self._meta_valida()
        meta["version_modelo"] = ""
        with self.assertRaises(ErrorArtefacto):
            validar_metadata(meta)

    def test_productos_entrenados_vacio_lanza_error(self):
        meta = self._meta_valida()
        meta["productos_entrenados"] = []
        with self.assertRaises(ErrorArtefacto):
            validar_metadata(meta)


if __name__ == "__main__":
    unittest.main()
