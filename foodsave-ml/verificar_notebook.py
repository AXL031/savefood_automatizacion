"""Ejecuta el notebook con datos sintéticos; no mide calidad con datos reales."""
import os
import tempfile
import zipfile
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd

from normalizar_ventas import normalizar


def main():
    notebook = nbformat.read(Path(__file__).parent / 'notebooks/foodsave_colab.ipynb', as_version=4)
    nbformat.validate(notebook)
    for cell in notebook.cells:
        if cell.cell_type == 'code' and not cell.source.startswith('%'):
            compile(cell.source, '<notebook>', 'exec')
    previous = Path.cwd()
    with tempfile.TemporaryDirectory() as directory:
        os.chdir(directory)
        try:
            fechas = pd.date_range('2021-01-01', '2022-09-30')
            rng = np.random.default_rng(42)
            rows = [(d, p, max(0, 20 + 5 * d.dayofweek + rng.integers(-4, 5)))
                    for d in fechas for p in ['BAGUETTE', 'CROISSANT']]
            rows = [row for row in rows if row[0] not in {
                pd.Timestamp('2022-09-01'), pd.Timestamp('2022-09-19')
            }]
            rows.append((pd.Timestamp('2022-03-01'), 'BAGUETTE', -1))
            pd.DataFrame(rows, columns=['date', 'article', 'Quantity']).to_csv('ventas.csv', index=False)
            namespace = {}
            for cell in notebook.cells:
                if cell.cell_type != 'code' or cell.source.startswith('%'):
                    continue
                source = cell.source.replace('CSV_PATH = ""', 'CSV_PATH = "ventas.csv"')
                source = source.replace('DESCARGAR_ZIP = True', 'DESCARGAR_ZIP = False')
                exec(compile(source, '<notebook>', 'exec'), namespace)
                # Avoid rendering tables during automated verification.
                namespace['display'] = lambda *args, **kwargs: None
                if 'plt' in namespace:
                    namespace['plt'].show = lambda: None
            assert namespace['cantidad_negativas'] == 1
            assert len(namespace['metricas_validacion']) == 1
            assert len(namespace['metricas_test']) == 1
            assert namespace['metricas_validacion'].Modelo.iloc[0] == 'CatBoost'
            assert namespace['metricas_test'].Modelo.iloc[0] == 'CatBoost'
            assert namespace['test'].date.max() == pd.Timestamp('2022-09-30')
            assert namespace['test'].date.dt.month.eq(9).any()
            assert 'candidatos' not in namespace
            construir = namespace['crear_features']
            diarias = namespace['diarias']
            features = namespace['FEATURES']
            fecha = pd.Timestamp('2022-08-15')
            alterada = diarias.copy()
            alterada.loc[alterada.date >= fecha, 'ventas_dia'] = 99999
            antes, despues = construir(diarias), construir(alterada)
            pd.testing.assert_frame_equal(antes.loc[antes.date <= fecha, features], despues.loc[despues.date <= fecha, features])
            hueco = diarias.loc[diarias.article == 'BAGUETTE'].index[40]
            alterada = diarias.copy()
            alterada.loc[hueco, 'ventas_dia'] = np.nan
            resultado = construir(alterada)
            siguiente = pd.Timestamp(alterada.loc[hueco, 'date']) + pd.Timedelta(days=1)
            assert resultado.loc[(resultado.article == 'BAGUETTE') & (resultado.date == siguiente), 'ventas_ayer'].isna().all()
            try:
                namespace['predecir_dia']('2022-06-30')
            except ValueError:
                pass
            else:
                raise AssertionError('El simulador aceptó una fecha fuera de test')
            assert namespace['metricas']([0, 0], [0, 1])['WAPE_pct'] != namespace['metricas']([0, 0], [0, 1])['WAPE_pct']
            assert len(namespace['comparar_dia']('2022-08-15')) == 2
            assert len(namespace['comparar_dia']('2022-09-30')) == 2
            sin_ventas = namespace['comparar_dia']('2022-09-01')
            assert len(sin_ventas) == 2
            assert sin_ventas.ventas_dia.isna().all()
            assert sin_ventas.error.isna().all()
            with zipfile.ZipFile(namespace['archivo_zip']) as paquete:
                assert 'catboost_model.cbm' in paquete.namelist()
                assert 'metricas_validacion.csv' in paquete.namelist()
                assert 'metricas_test.csv' in paquete.namelist()
                assert 'comparacion_validacion.csv' not in paquete.namelist()
            normalized, _ = normalizar(Path('ventas.csv'), 'bakery', 'piloto', 'principal')
            normalized.to_csv('ventas_normalizadas.csv', index=False)
            estandar = {}
            for cell in notebook.cells[3:5]:
                source = cell.source.replace('CSV_PATH = ""', 'CSV_PATH = "ventas_normalizadas.csv"')
                exec(compile(source, '<notebook-estandar>', 'exec'), estandar)
                estandar['display'] = lambda *args, **kwargs: None
            assert estandar['FORMATO_ORIGEN'] == 'estandar'
            assert estandar['comercio_elegido'] == 'piloto'
            assert estandar['sucursal_elegida'] == 'principal'
            assert estandar['modo_automatico']
            assert estandar['INICIO_VALIDACION'] < estandar['INICIO_TEST']
            assert estandar['df'].Quantity.sum() == namespace['df'].Quantity.sum()
            for cell_index in [6, 7, 9, 10, 13, 15, 18]:
                source = notebook.cells[cell_index].source
                exec(compile(source, '<notebook-estandar>', 'exec'), estandar)
                estandar['display'] = lambda *args, **kwargs: None
                if 'plt' in estandar:
                    estandar['plt'].show = lambda: None
            assert estandar['test'].date.nunique() == 30
            assert estandar['test'].date.max() == pd.Timestamp('2022-09-30')
            assert len(estandar['predecir_dia']('2022-09-30')) == 2
            multi = pd.concat([normalized, normalized.assign(sucursal_id='otra')], ignore_index=True)
            multi.to_csv('ventas_multisucursal.csv', index=False)
            seleccionado = {}
            for cell in notebook.cells[3:5]:
                source = cell.source.replace('CSV_PATH = ""', 'CSV_PATH = "ventas_multisucursal.csv"')
                source = source.replace('COMERCIO_ID = ""', 'COMERCIO_ID = "piloto"')
                source = source.replace('SUCURSAL_ID = ""', 'SUCURSAL_ID = "principal"')
                exec(compile(source, '<notebook-multisucursal>', 'exec'), seleccionado)
                seleccionado['display'] = lambda *args, **kwargs: None
            assert seleccionado['df'].Quantity.sum() == namespace['df'].Quantity.sum()
            print('OK: CatBoost, validación, test, ausencia de fuga temporal, faltantes, simulador y exportación.')
        finally:
            os.chdir(previous)


if __name__ == '__main__':
    main()
