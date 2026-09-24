import tempfile
import unittest
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from normalizar_ventas import normalizar


class NormalizadorVentasTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ventas.csv"

    def test_estandar_con_cero_y_sucursales_separadas(self):
        pd.DataFrame([
            ["c1", "s1", "2022-07-01", "pan", 0],
            ["c1", "s2", "2022-07-01", "pan", 3],
            ["c1", "s1", "2022-07-02", "pan", 4],
        ], columns=["comercio_id", "sucursal_id", "fecha_local", "producto_id", "unidades_vendidas"]).to_csv(self.path, index=False)
        normalized, report = normalizar(self.path, "estandar", None, None)
        self.assertEqual(len(normalized), 3)
        self.assertEqual(len(report["sucursales"]), 2)
        self.assertEqual(normalized.unidades_vendidas.sum(), 7)
        self.assertEqual(report["politica_ausencias"], "desconocido; no se imputan ceros")

    def test_clave_diaria_duplicada_es_error(self):
        pd.DataFrame([
            ["c1", "s1", "2022-07-01", "pan", 1],
            ["c1", "s1", "2022-07-01", "pan", 2],
        ], columns=["comercio_id", "sucursal_id", "fecha_local", "producto_id", "unidades_vendidas"]).to_csv(self.path, index=False)
        with self.assertRaisesRegex(ValueError, "duplicada"):
            normalizar(self.path, "estandar", None, None)

    def test_fecha_y_cantidad_invalidas_son_error(self):
        frame = pd.DataFrame([{
            "comercio_id": "c1", "sucursal_id": "s1", "fecha_local": "2022-13-01",
            "producto_id": "pan", "unidades_vendidas": 1,
        }])
        frame.to_csv(self.path, index=False)
        with self.assertRaisesRegex(ValueError, "fecha_local"):
            normalizar(self.path, "estandar", None, None)
        frame["fecha_local"] = "2022-07-01"
        frame["unidades_vendidas"] = -1
        frame.to_csv(self.path, index=False)
        with self.assertRaisesRegex(ValueError, "entero no negativo"):
            normalizar(self.path, "estandar", None, None)

    def test_bakery_agrega_y_excluye_devoluciones(self):
        pd.DataFrame([
            ["2022-07-01", "PAN", 2],
            ["2022-07-01", "PAN", 3],
            ["2022-07-01", "PAN", -1],
        ], columns=["date", "article", "Quantity"]).to_csv(self.path, index=False)
        normalized, report = normalizar(self.path, "bakery", "c1", "s1")
        self.assertEqual(len(normalized), 1)
        self.assertEqual(normalized.unidades_vendidas.iloc[0], 5)
        self.assertEqual(report["negativos_excluidos"], 1)

    def test_transacciones_agregan_lineas_y_detectan_duplicados(self):
        columnas = ["comercio_id", "sucursal_id", "fecha_local", "producto_id",
                    "unidades_vendidas", "transaccion_id", "linea_id"]
        frame = pd.DataFrame([
            ["c1", "s1", "2022-07-01", "pan", 2, "t1", "1"],
            ["c1", "s1", "2022-07-01", "pan", 3, "t1", "2"],
        ], columns=columnas)
        frame.to_csv(self.path, index=False)
        normalized, _ = normalizar(self.path, "transacciones", None, None)
        self.assertEqual(len(normalized), 1)
        self.assertEqual(normalized.unidades_vendidas.iloc[0], 5)
        frame.loc[1, "linea_id"] = "1"
        frame.to_csv(self.path, index=False)
        with self.assertRaisesRegex(ValueError, "duplicadas"):
            normalizar(self.path, "transacciones", None, None)


if __name__ == "__main__":
    unittest.main()
