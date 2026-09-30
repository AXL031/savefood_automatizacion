"""Asistente de primera carga (E02) y estado durable de inicialización (E03)."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.core.base import Base
from app.core.errores import ErrorAPI
from app.modules.autenticacion.modelos import Usuario  # noqa: F401, registra FK
from app.modules.inicializacion.modelos import (
    ESTADO_DATOS_CARGADOS,
    ESTADO_ENTRENANDO,
    ESTADO_MODELO_LISTO,
    ESTADO_PENDIENTE,
    ConfiguracionInicial,
)
from app.modules.inicializacion.servicio import (
    confirmar_carga,
    hay_datos_cargados,
    leer_estado,
    marcar_entrenando,
    marcar_fallo_entrenamiento,
    marcar_modelo_listo,
    preparar_vista_previa,
)
from app.modules.productos.modelos import Producto, SkuProducto
from app.modules.ventas.modelos import VentaDiaria

OBJETIVO = date(2022, 8, 24)
REFERENCIA = date(2022, 8, 23)

PRODUCTOS = b"""codigo,nombre,sku_externo,demostrar
baguette,Baguette,BAGUETTE,si
croissant,Croissant,CROISSANT,si
pan,Pan de molde,PAN,si
dona,Dona,DONA,no
"""

INGREDIENTES = b"""codigo,nombre,unidad_base
harina,Harina,g
levadura,Levadura,g
"""

RECETAS = b"""codigo_producto,codigo_ingrediente,cantidad_por_unidad
baguette,harina,250.500
baguette,levadura,5
croissant,harina,120
pan,harina,300
"""

STOCK = b"""tipo,codigo,cantidad,codigo_lote,fecha_caducidad,fecha_limite_venta
producto,baguette,4,PT-001,2022-08-25,2022-08-24
producto,croissant,0,,,
producto,pan,2,PT-002,2022-08-26,2022-08-25
ingrediente,harina,12000.500,ING-001,2022-12-31,
ingrediente,levadura,0,,,
"""

VENTAS = b"""fecha_local,sku_externo,unidades_vendidas
2022-08-21,BAGUETTE,12
2022-08-21,CROISSANT,0
2022-08-22,BAGUETTE,15
2022-08-23,PAN,7
"""

# Formato real del piloto: lineas de ticket con columnas propias.
VENTAS_TICKETS = b"""date,time,ticket_number,article,Quantity,unit_price
2022-08-21,08:38,150040.0,BAGUETTE,2.0,0.9
2022-08-21,09:10,150041.0,BAGUETTE,3.0,0.9
2022-08-21,09:15,150042.0,CROISSANT,0.0,1.2
2022-08-22,10:00,150043.0,BAGUETTE,-1.0,0.9
2022-08-22,10:05,150044.0,PAN,7.0,2.0
"""


def entrega(**cambios: bytes) -> dict[str, bytes]:
    archivos = {
        "productos.csv": PRODUCTOS,
        "ingredientes.csv": INGREDIENTES,
        "recetas.csv": RECETAS,
        "stock_inicial.csv": STOCK,
        "ventas.csv": VENTAS,
    }
    archivos.update(cambios)
    return archivos


@pytest.fixture
def sesion():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def _char_length(conexion, _registro):
        conexion.create_function("char_length", 1, len)

    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


class RecetasFalsas:
    """Doble del servicio de Max (M01) para probar la transacción compartida."""

    def __init__(self, fallar: bool = False):
        self.fallar = fallar
        self.ingredientes: dict[str, int] = {}
        self.lineas = 0

    def registrar_ingredientes(self, sesion, filas):
        self.ingredientes = {fila.codigo: indice for indice, fila in enumerate(filas, start=1)}
        return self.ingredientes

    def registrar_recetas(self, sesion, filas, producto_por_codigo, ingrediente_por_codigo):
        if self.fallar:
            raise ErrorAPI(422, "RECETA_INVALIDA", "Receta rechazada por el doble de prueba.")
        self.lineas = len(filas)
        return self.lineas


class InventarioFalso:
    """Doble del servicio de Vera (V01)."""

    def __init__(self):
        self.movimientos = 0
        self.cero_explicito = 0

    def registrar_apertura(
        self, sesion, filas, producto_por_codigo, ingrediente_por_codigo, efectivo_en_demo, clave_operacion_base
    ):
        for fila in filas:
            if fila.cantidad == 0:
                self.cero_explicito += 1
            else:
                self.movimientos += 1
        return self.movimientos


def test_vista_previa_no_escribe_y_resume_la_entrega(sesion):
    vista = preparar_vista_previa(entrega(), OBJETIVO, REFERENCIA)

    assert vista.resultado.aceptable
    assert vista.resultado.filas_por_hoja["ventas"] == 4
    assert vista.resultado.fechas_ventas == (date(2022, 8, 21), date(2022, 8, 23))
    assert len(vista.resultado.entrada.productos_demo) == 3
    assert sesion.scalar(select(Producto.id)) is None


def test_carga_completa_marca_datos_cargados(sesion):
    recetas, inventario = RecetasFalsas(), InventarioFalso()

    informe = confirmar_carga(
        sesion, entrega(), OBJETIVO, REFERENCIA, "primera-carga-1",
        puerto_recetas=recetas, puerto_inventario=inventario,
    )

    assert informe.estado == ESTADO_DATOS_CARGADOS
    assert informe.pendiente_de == []
    assert informe.productos == 4
    assert informe.ventas_diarias == 4
    assert informe.recetas == 4
    assert inventario.cero_explicito == 2
    assert hay_datos_cargados(sesion)

    estado = leer_estado(sesion)
    assert estado.fecha_objetivo_demo == OBJETIVO
    assert estado.fecha_referencia_stock == REFERENCIA
    assert estado.completada_en is not None
    assert estado.mensaje_error is None


def test_sin_servicios_de_max_y_vera_queda_pendiente_con_constancia(sesion):
    informe = confirmar_carga(sesion, entrega(), OBJETIVO, REFERENCIA, "primera-carga-1")

    assert informe.estado == ESTADO_PENDIENTE
    assert len(informe.pendiente_de) == 2
    assert not hay_datos_cargados(sesion)
    # Lo que pertenece a Edu si quedo persistido: Kevin puede leer historial.
    assert informe.ventas_diarias == 4
    estado = leer_estado(sesion)
    assert "M01" in estado.mensaje_error and "V01" in estado.mensaje_error


def test_un_fallo_en_recetas_revierte_catalogo_y_ventas(sesion):
    with pytest.raises(ErrorAPI) as fallo:
        confirmar_carga(
            sesion, entrega(), OBJETIVO, REFERENCIA, "primera-carga-1",
            puerto_recetas=RecetasFalsas(fallar=True), puerto_inventario=InventarioFalso(),
        )
    assert fallo.value.codigo == "RECETA_INVALIDA"

    sesion.rollback()
    assert sesion.scalar(select(Producto.id)) is None
    assert sesion.scalar(select(VentaDiaria.id)) is None
    assert sesion.scalar(select(ConfiguracionInicial.estado)) in (None, ESTADO_PENDIENTE)


def test_repetir_la_misma_solicitud_no_duplica(sesion):
    primera = confirmar_carga(
        sesion, entrega(), OBJETIVO, REFERENCIA, "primera-carga-1",
        puerto_recetas=RecetasFalsas(), puerto_inventario=InventarioFalso(),
    )
    assert primera.ventas_diarias == 4

    segunda = confirmar_carga(
        sesion, entrega(), OBJETIVO, REFERENCIA, "primera-carga-1",
        puerto_recetas=RecetasFalsas(), puerto_inventario=InventarioFalso(),
    )

    assert segunda.ya_estaba_cargada
    assert len(sesion.scalars(select(VentaDiaria.id)).all()) == 4
    assert len(sesion.scalars(select(Producto.id)).all()) == 4


def test_otra_solicitud_sobre_instalacion_cargada_es_conflicto(sesion):
    confirmar_carga(
        sesion, entrega(), OBJETIVO, REFERENCIA, "primera-carga-1",
        puerto_recetas=RecetasFalsas(), puerto_inventario=InventarioFalso(),
    )
    with pytest.raises(ErrorAPI) as fallo:
        confirmar_carga(
            sesion, entrega(), date(2022, 8, 25), REFERENCIA, "primera-carga-2",
            puerto_recetas=RecetasFalsas(), puerto_inventario=InventarioFalso(),
        )
    assert fallo.value.codigo == "YA_INICIALIZADA"


def test_sku_de_ventas_sin_producto_rechaza_el_lote(sesion):
    malas = VENTAS + b"2022-08-23,DESCONOCIDO,3\n"
    with pytest.raises(ErrorAPI) as fallo:
        confirmar_carga(
            sesion, entrega(**{"ventas.csv": malas}), OBJETIVO, REFERENCIA, "primera-carga-1",
            puerto_recetas=RecetasFalsas(), puerto_inventario=InventarioFalso(),
        )
    assert fallo.value.codigo == "CARGA_INVALIDA"
    sesion.rollback()
    assert sesion.scalar(select(Producto.id)) is None


def test_csv_de_tickets_se_adapta_y_agrega_por_dia(sesion):
    vista = preparar_vista_previa(
        entrega(**{"ventas.csv": VENTAS_TICKETS}), OBJETIVO, REFERENCIA
    )

    assert vista.resultado.aceptable
    assert vista.resumen_bakery is not None
    assert vista.resumen_bakery.lineas_negativas == 1
    # Las dos lineas de BAGUETTE del 21 se suman en una sola venta diaria.
    diarias = {
        (venta.fecha_local, venta.sku_externo): venta.unidades_vendidas
        for venta in vista.resultado.entrada.ventas
    }
    assert diarias[(date(2022, 8, 21), "BAGUETTE")] == 5
    # El cero explicito se conserva; la linea negativa no crea fila.
    assert diarias[(date(2022, 8, 21), "CROISSANT")] == 0
    assert (date(2022, 8, 22), "BAGUETTE") not in diarias


def test_huella_de_solicitud_distingue_las_fechas(sesion):
    una = preparar_vista_previa(entrega(), OBJETIVO, REFERENCIA)
    otra = preparar_vista_previa(entrega(), date(2022, 8, 25), REFERENCIA)
    assert una.huella_solicitud != otra.huella_solicitud
    assert una.huella_ventas == otra.huella_ventas


def test_decimales_de_receta_y_stock_sin_perdida(sesion):
    vista = preparar_vista_previa(entrega(), OBJETIVO, REFERENCIA)
    receta = next(
        fila for fila in vista.resultado.entrada.recetas
        if fila.codigo_producto == "baguette" and fila.codigo_ingrediente == "harina"
    )
    stock = next(fila for fila in vista.resultado.entrada.stock if fila.codigo == "harina")
    assert receta.cantidad_por_unidad == Decimal("250.500")
    assert stock.cantidad == Decimal("12000.500")


def test_transiciones_de_entrenamiento(sesion):
    confirmar_carga(
        sesion, entrega(), OBJETIVO, REFERENCIA, "primera-carga-1",
        puerto_recetas=RecetasFalsas(), puerto_inventario=InventarioFalso(),
    )

    assert marcar_entrenando(sesion).estado == ESTADO_ENTRENANDO
    # Un fallo de entrenamiento no obliga a recargar ventas ni stock.
    assert marcar_fallo_entrenamiento(sesion, "sin memoria").estado == ESTADO_DATOS_CARGADOS
    assert leer_estado(sesion).mensaje_error == "sin memoria"

    marcar_entrenando(sesion)
    assert marcar_modelo_listo(sesion).estado == ESTADO_MODELO_LISTO


def test_no_se_entrena_sin_datos_cargados(sesion):
    with pytest.raises(ErrorAPI) as fallo:
        marcar_entrenando(sesion)
    assert fallo.value.codigo == "TRANSICION_INVALIDA"
