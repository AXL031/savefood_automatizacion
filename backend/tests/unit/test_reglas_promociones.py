from datetime import date, datetime, time
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.modules.promociones.reglas import (  # noqa: E402
    EstadoProducto,
    ReglaPromocion,
    evaluar_promocion,
)


class ReglasPromocionesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.regla = ReglaPromocion(time(18), time(21), 10, 20, 30)
        self.ahora = datetime(2026, 9, 24, 18, 0)

    def estado(self, stock: int | None = 15, **cambios: object) -> EstadoProducto:
        datos = {
            "fecha_limite_venta": date(2026, 9, 24),
            "stock_actual": stock,
            "stock_actualizado_en": datetime(2026, 9, 24, 17, 45),
            "promocion_activa": False,
        }
        datos.update(cambios)
        return EstadoProducto(**datos)

    def test_propone_descuento_si_hay_excedente_y_vence_hoy(self) -> None:
        propuesta = evaluar_promocion(self.regla, self.estado(), self.ahora)
        self.assertTrue(propuesta.proponer)
        self.assertEqual(propuesta.descuento_pct, 20)

    def test_umbral_es_estricto_y_no_descuenta_pocas_unidades(self) -> None:
        for stock in (0, 9, 10):
            with self.subTest(stock=stock):
                self.assertFalse(
                    evaluar_promocion(self.regla, self.estado(stock), self.ahora).proponer
                )

    def test_no_propone_fuera_de_horario_o_fecha(self) -> None:
        self.assertFalse(
            evaluar_promocion(self.regla, self.estado(), datetime(2026, 9, 24, 17, 59)).proponer
        )
        self.assertFalse(
            evaluar_promocion(self.regla, self.estado(), datetime(2026, 9, 24, 21, 0)).proponer
        )
        self.assertFalse(
            evaluar_promocion(
                self.regla,
                self.estado(fecha_limite_venta=date(2026, 9, 25)),
                self.ahora,
            ).proponer
        )

    def test_no_propone_con_stock_ausente_desactualizado_o_promocion_activa(self) -> None:
        for estado in (
            self.estado(None),
            self.estado(stock_actualizado_en=datetime(2026, 9, 24, 17, 29)),
            self.estado(promocion_activa=True),
        ):
            with self.subTest(estado=estado):
                self.assertFalse(evaluar_promocion(self.regla, estado, self.ahora).proponer)

    def test_rechaza_descuento_superior_al_maximo(self) -> None:
        with self.assertRaises(ValueError):
            ReglaPromocion(time(18), time(21), 10, 40, 30)


if __name__ == "__main__":
    unittest.main()
