"""Escenario público sintético: ampliación segura y ventas históricas reproducibles."""
from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy import select, func, delete
from sqlalchemy.orm import sessionmaker
from test_api_inicializacion_ventas import cliente  # noqa: F401
from app.core.base_datos import obtener_sesion
from app.modules.autenticacion.modelos import Usuario
from app.modules.productos.modelos import Producto
from app.modules.ingredientes.modelos import Ingrediente
from app.modules.inventario.modelos import LoteProducto, MovimientoInventario
from app.modules.recetas.modelos import Receta
from app.modules.ventas.modelos import VentaDiaria
from app.modules.operaciones import semilla, semilla_catalogo
from app.modules.operaciones.modelos import RegistroOperacion, FichaTienda, ConfiguracionOperacion
from app.modules.operaciones.tienda import catalogo


@pytest.fixture
def demo_db(cliente, monkeypatch):
    contexto=cliente.app.dependency_overrides[obtener_sesion]()
    sesion=next(contexto)
    sesiones=sessionmaker(bind=sesion.get_bind())
    try:
        with sesiones.begin() as s:s.execute(delete(Usuario))
        monkeypatch.setattr(semilla,'SessionLocal',sesiones)
        monkeypatch.setenv('HABILITAR_DATOS_PRUEBA','1')
        for clave in ['DEMO_ADMIN_PASSWORD','DEMO_OPERADOR_PASSWORD','DEMO_CLIENTE_PASSWORD']:
            monkeypatch.setenv(clave,'clave-ficticia-solo-semilla-2026')
        yield sesiones
    finally:contexto.close()


def conteos(s):
    return tuple(s.scalar(select(func.count()).select_from(m)) for m in [Producto,Ingrediente,VentaDiaria,MovimientoInventario,Receta,RegistroOperacion])


def test_demo_variada_y_repetible_sin_reponer_stock(demo_db):
    from app.modules.proveedores.modelos import Proveedor
    semilla.cargar()
    with demo_db.begin() as s:
        c=catalogo(s)
        assert len(c['productos'])==12 and len(c['categorias'])==6
        assert {p['estado_stock'] for p in c['productos']}=={'DISPONIBLE','ULTIMAS_UNIDADES','AGOTADO'}
        assert len({c['imagen'] for c in c['categorias']})==6
        assert s.scalar(select(func.count()).select_from(Ingrediente))==16
        proveedores=list(s.scalars(select(Proveedor)))
        assert len(proveedores)==3 and all(p.chat_id_pruebas is None and not p.destino_verificado for p in proveedores)
        tarta=s.scalar(select(Producto).where(Producto.codigo=='DEMO-TARTA-FRESA'))
        quiche=s.scalar(select(Producto).where(Producto.codigo=='DEMO-QUICHE'))
        assert s.scalar(select(VentaDiaria).where(VentaDiaria.producto_id==tarta.id,VentaDiaria.fecha_local==date(2026,2,24))) is None
        assert s.scalar(select(VentaDiaria.unidades_vendidas).where(VentaDiaria.producto_id==quiche.id,VentaDiaria.fecha_local==date(2026,9,27)))==0
        assert next(p for p in c['productos'] if p['id']==quiche.id)['estado_stock']=='AGOTADO'
        assert s.scalar(select(LoteProducto.saldo_disponible).where(LoteProducto.producto_id==quiche.id))==8
        antes=conteos(s)
    semilla.cargar()
    with demo_db() as s:assert conteos(s)==antes


def test_ampliar_v1_preserva_cuentas_ventas_y_operaciones(demo_db,monkeypatch):
    from app.modules.operaciones.servicio import vender
    original=semilla_catalogo.enriquecer
    monkeypatch.setattr(semilla_catalogo,'enriquecer',lambda *a,**k:False)
    semilla.cargar()
    monkeypatch.setattr(semilla_catalogo,'enriquecer',original)
    with demo_db.begin() as s:
        admin=s.scalar(select(Usuario).where(Usuario.correo=='admin.foodsave@example.com'))
        pid=s.scalar(select(Producto.id).where(Producto.codigo=='DEMO-PAN'))
        venta=vender(s,{'clave_idempotencia':'venta-anterior-demo','fecha':'2026-09-29','lineas':[{'producto_id':pid,'cantidad':1}]},admin.id)
        venta_id=venta.id
        ficha=s.get(FichaTienda,pid);ficha.precio=Decimal('0.70');ficha.version=2;ficha.datos={**ficha.datos,'descripcion':'Ficha editada por el usuario'}
        config=s.get(ConfiguracionOperacion,1);config.datos={**config.datos,'habilitada':False}
        usuarios=[(u.id,u.hash_contrasena) for u in s.scalars(select(Usuario).order_by(Usuario.id))]
        ventas=[(v.id,v.unidades_vendidas,v.revision_actual) for v in s.scalars(select(VentaDiaria).order_by(VentaDiaria.id))]
        saldo=s.scalar(select(LoteProducto.saldo_disponible).where(LoteProducto.producto_id==pid))
        rid=s.scalar(select(Receta.id).where(Receta.producto_id==pid))
    semilla.cargar()
    with demo_db() as s:
        assert [(u.id,u.hash_contrasena) for u in s.scalars(select(Usuario).order_by(Usuario.id))]==usuarios
        assert [(v.id,v.unidades_vendidas,v.revision_actual) for v in s.scalars(select(VentaDiaria).where(VentaDiaria.id.in_([v[0] for v in ventas])).order_by(VentaDiaria.id))]==ventas
        assert s.get(RegistroOperacion,venta_id).clave=='venta-anterior-demo'
        assert s.scalar(select(LoteProducto.saldo_disponible).where(LoteProducto.producto_id==pid))==saldo
        assert s.get(Receta,rid).version==1 and not s.get(Receta,rid).activo
        assert s.get(FichaTienda,pid).precio==Decimal('0.70')
        assert s.get(ConfiguracionOperacion,1).datos['habilitada'] is False


def test_base_ajena_y_flag_desactivado_no_se_modifican(demo_db,monkeypatch):
    monkeypatch.setenv('HABILITAR_DATOS_PRUEBA','0')
    with pytest.raises(RuntimeError,match='HABILITAR_DATOS_PRUEBA'):semilla.cargar()
    monkeypatch.setenv('HABILITAR_DATOS_PRUEBA','1')
    with demo_db.begin() as s:s.add(Producto(codigo='REAL-001',nombre='Catálogo ajeno',demostrar=True,activo=True))
    with pytest.raises(RuntimeError,match='base ya contiene'):semilla.cargar()
    with demo_db() as s:assert s.scalar(select(func.count()).select_from(Ingrediente))==0


def test_ampliacion_espera_entrenamiento_y_reserva_nuevo_modelo_una_vez(demo_db,monkeypatch):
    from app.modules.inicializacion.modelos import ConfiguracionInicial
    from app.modules.pronosticos.modelos import ArtefactoModelo
    from app.modules.automatizaciones.modelos import EjecucionAutomatizacion
    ampliar=semilla_catalogo.enriquecer
    monkeypatch.setattr(semilla_catalogo,'enriquecer',lambda *a,**k:False)
    semilla.cargar()
    monkeypatch.setattr(semilla_catalogo,'enriquecer',ampliar)
    with demo_db.begin() as s:s.get(ConfiguracionInicial,1).estado='ENTRENANDO'
    with pytest.raises(RuntimeError,match='termine el entrenamiento'):semilla.cargar()
    with demo_db.begin() as s:
        assert s.scalar(select(func.count()).select_from(Producto))==3
        # Artefacto ficticio solo dentro de esta fixture: no ejecuta ni simula entrenamiento real.
        m=ArtefactoModelo(version_modelo='fixture-anterior',ruta_local='fixture',sha256='a'*64,
            huella_datos_entrenamiento='b'*64,fecha_corte_entrenamiento=date(2026,7,31),particion_json={},estado='LISTO_DEMO')
        s.add(m);s.flush();modelo_id=m.id
        estado=s.get(ConfiguracionInicial,1);estado.estado='MODELO_LISTO';estado.modelo_id=m.id
    semilla.cargar()
    with demo_db() as s:
        estado=s.get(ConfiguracionInicial,1)
        tarea=s.get(EjecucionAutomatizacion,estado.preparacion_ejecucion_id)
        assert tarea.datos_entrada_json['version_modelo']==semilla_catalogo.VERSION
        assert tarea.datos_entrada_json['huella_inicializacion']==estado.huella_solicitud
        assert s.get(ArtefactoModelo,modelo_id) is not None
        numero=s.scalar(select(func.count()).select_from(EjecucionAutomatizacion))
    semilla.cargar()
    with demo_db() as s:assert s.scalar(select(func.count()).select_from(EjecucionAutomatizacion))==numero
