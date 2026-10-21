"""Consumidores reales del motor, permisos, snapshots y calendarios históricos."""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker
from test_programaciones_a02 import entorno, _token, _cabecera, _programacion
from test_motor_a03 import entorno_pg
from app.modules.productos.modelos import Producto, SkuProducto
from app.modules.ingredientes.modelos import Ingrediente
from app.modules.recetas.servicio import crear_version, LineaNueva
from app.modules.inventario.modelos import LoteProducto, LoteIngrediente, MovimientoInventario
from app.modules.inventario.servicio import SolicitudAjuste, registrar_ajuste
from app.modules.pronosticos.modelos import ArtefactoModelo
from app.modules.promociones.esquemas import ConfigurarRegla
from app.modules.promociones.modelos import EvaluacionPromocion, ReglaPromocionDemo
from app.modules.promociones.servicio import guardar_regla, evaluar_programada
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion, ProgramacionDemo
from app.modules.automatizaciones.flujo import _hora_utc
from app.modules.proveedores.servicio import ServicioProveedores
from app.workers import motor
from app.workers.tasks.manejadores import ContextoEjecucion
from app.core.errores import ErrorAPI
from zoneinfo import ZoneInfo


def sembrar(engine):
    with Session(engine) as s:
        p = Producto(codigo="pan", nombre="Pan", demostrar=True, activo=True)
        i = Ingrediente(codigo="harina", nombre="Harina", unidad_base="g", activo=True)
        s.add_all([p, i]); s.flush()
        s.add(SkuProducto(producto_id=p.id, origen="bakery", sku_externo="PAN", activo=True))
        crear_version(s, producto_id=p.id, lineas=[LineaNueva(i.id, Decimal("20"))], motivo="Prueba", usuario_id=1)
        lote = LoteProducto(producto_id=p.id, codigo_lote="PT", lote_informado=True,
                            fecha_caducidad=date(2022, 8, 24), fecha_limite_venta=date(2022, 8, 24), saldo_disponible=10)
        s.add(lote)
        s.add(LoteIngrediente(ingrediente_id=i.id, codigo_lote="IN", lote_informado=True, saldo_disponible=0))
        m = ArtefactoModelo(version_modelo="fixture", ruta_local="fixture", sha256="a"*64,
                            huella_datos_entrenamiento="b"*64, fecha_corte_entrenamiento=date(2022, 7, 31),
                            particion_json={"inicio_prueba": "2022-08-01", "fin_prueba": "2022-08-31"}, estado="LISTO_DEMO")
        s.add(m); s.commit()
        return p.id, i.id, lote.id, m.id


def ajustar(s, lote_id, clave, hora=datetime(2022, 8, 24, 17, 15), delta="2"):
    return registrar_ajuste(s, SolicitudAjuste("producto", lote_id, Decimal(delta), "Ajuste de prueba", clave, hora), 1)


def test_ajuste_motor_evaluacion_idempotente_sin_cambiar_stock(entorno, monkeypatch):
    cliente, engine = entorno
    _, _, lote_id, _ = sembrar(engine)
    with Session(engine) as s:
        guardar_regla(s, ConfigurarRegla(habilitada=True), 1)
        ajuste = ajustar(s, lote_id, "ajuste-promo")
        assert ajustar(s, lote_id, "ajuste-promo").repetido
        s.commit()
        assert s.scalar(select(func.count()).select_from(ProgramacionDemo)) == 1
        p = s.scalar(select(ProgramacionDemo)); p.ejecutar_desde_utc = datetime.now(timezone.utc) - timedelta(seconds=1); s.commit()
    monkeypatch.setattr(motor, "SessionLocal", sessionmaker(bind=engine, expire_on_commit=False))
    publicados = []
    assert motor.despachar_pendientes(lambda id, token: publicados.append((id, token)))["publicadas"] == 1
    assert motor.ejecutar(*publicados[0])["resultado"] == "COMPLETADA"
    assert motor.ejecutar(*publicados[0])["resultado"] == "IGNORADA"
    with Session(engine) as s:
        e = s.scalar(select(EvaluacionPromocion))
        assert e.proponer and e.descuento_pct == 20 and e.movimiento_id == ajuste.movimiento_id
        assert s.get(LoteProducto, lote_id).saldo_disponible == 12
        assert s.scalar(select(func.count()).select_from(MovimientoInventario)) == 1
    admin = _cabecera(_token(cliente, "admin@example.com", "clave-segura-admin"))
    listado = cliente.get("/api/v1/promociones/evaluaciones?limite=1", headers=admin).json()
    assert listado["metadatos"]["total"] == 1 and listado["datos"][0]["lectura"]["saldo"] == 12


def test_rollback_del_ajuste_revierte_tarea_y_lectura_reemplazada_se_descarta(entorno):
    _, engine = entorno
    _, _, lote_id, _ = sembrar(engine)
    with Session(engine) as s:
        guardar_regla(s, ConfigurarRegla(habilitada=True), 1); s.commit()
        ajustar(s, lote_id, "rollback"); s.rollback()
        assert s.get(LoteProducto, lote_id).saldo_disponible == 10
        assert s.scalar(select(func.count()).select_from(ProgramacionDemo)) == 0
        ajustar(s, lote_id, "primero"); s.commit()
        ejecucion = s.scalar(select(EjecucionAutomatizacion)); entrada = ejecucion.datos_entrada_json
        ajustar(s, lote_id, "segundo", delta="1"); s.commit()
        guardar_regla(s, ConfigurarRegla(habilitada=False, descuento_pct=10), 1); s.commit()
        salida = evaluar_programada(s, ContextoEjecucion(ejecucion.id, ejecucion.tipo, ejecucion.clave_idempotencia, entrada)); s.commit()
        assert not salida["proponer"] and "reemplazó" in salida["motivo"]
        assert s.scalar(select(EvaluacionPromocion)).regla_id == 1
        assert s.scalar(select(func.count()).select_from(ReglaPromocionDemo)) == 2


@pytest.mark.parametrize("limite,hora,delta,motivo", [
    (None, datetime(2022,8,24,17), "1", "Falta"),
    (date(2022,8,23), datetime(2022,8,24,17), "1", "vencido"),
    (date(2022,8,24), datetime(2022,8,24,10), "1", "ventana"),
    (date(2022,8,24), datetime(2022,8,24,17), "-10", "umbral"),
])
def test_rechazos_explicados(entorno, limite, hora, delta, motivo):
    _, engine = entorno
    _, _, lote_id, _ = sembrar(engine)
    with Session(engine) as s:
        s.get(LoteProducto, lote_id).fecha_limite_venta = limite
        guardar_regla(s, ConfigurarRegla(habilitada=True), 1)
        ajustar(s, lote_id, "rechazo", hora, delta); s.commit()
        e = s.scalar(select(EjecucionAutomatizacion))
        salida = evaluar_programada(s, ContextoEjecucion(e.id, e.tipo, e.clave_idempotencia, e.datos_entrada_json)); s.commit()
        assert not salida["proponer"] and motivo in salida["motivo"]


def test_permisos_configuracion_y_regla(entorno):
    c, _ = entorno
    operador = _cabecera(_token(c, "operador@example.com", "clave-segura-operador"))
    admin = _cabecera(_token(c, "admin@example.com", "clave-segura-admin"))
    assert c.get("/api/v1/promociones/regla").status_code == 401
    assert c.put("/api/v1/promociones/regla", headers=operador, json={}).status_code == 403
    assert c.put("/api/v1/promociones/regla", headers=admin, json={"descuento_pct": 90, "descuento_maximo_pct": 20}).status_code == 422
    r = c.put("/api/v1/promociones/regla", headers=admin, json={"habilitada": True})
    assert r.status_code == 200 and r.json()["datos"]["version"] == 1
    assert c.put("/api/v1/promociones/regla", headers=admin, json={"habilitada": True}).json()["datos"]["version"] == 1


def test_version_reservada_y_lectura_antigua(entorno, monkeypatch):
    import app.modules.promociones.servicio as promociones
    _, engine = entorno
    _, _, lote_id, _ = sembrar(engine)
    with Session(engine) as s:
        guardar_regla(s, ConfigurarRegla(habilitada=True, descuento_pct=20), 1)
        ajustar(s, lote_id, "version-reservada"); s.commit()
        guardar_regla(s, ConfigurarRegla(habilitada=False, descuento_pct=10), 1); s.commit()
        e = s.scalar(select(EjecucionAutomatizacion))
        contexto = ContextoEjecucion(e.id, e.tipo, e.clave_idempotencia, e.datos_entrada_json)
        salida = evaluar_programada(s, contexto)
        assert salida["proponer"] and s.scalar(select(EvaluacionPromocion)).descuento_pct == 20
        s.rollback()
        class RelojAtrasado(datetime):
            @classmethod
            def now(cls, tz=None): return datetime.now(tz) + timedelta(hours=1)
        monkeypatch.setattr(promociones, "datetime", RelojAtrasado)
        salida = evaluar_programada(s, contexto)
        assert not salida["proponer"] and "vigente" in salida["motivo"]


def datos_flujo(producto_id, modelo_id):
    return {"producto_ids": [producto_id], "modelo_id": modelo_id, "fecha_objetivo_demo": "2022-08-24",
            "hora_simulada": "10:00", "primera_ejecucion_local": (datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=1)).isoformat(),
            "dias": 2, "modo_envio_pedidos": "REQUIERE_APROBACION"}


def oferta_falsa(self, ingrediente_id):
    return SimpleNamespace(proveedor_activo=True, destino_verificado=True, proveedor_nombre="Prueba")


def test_flujo_diagnostico_guardado_calendario_y_consentimiento(entorno, monkeypatch):
    c, engine = entorno
    producto_id, _, _, modelo_id = sembrar(engine)
    admin = _cabecera(_token(c, "admin@example.com", "clave-segura-admin"))
    datos = datos_flujo(producto_id, modelo_id)
    monkeypatch.setattr(ServicioProveedores, "oferta_preferida_para_compras", lambda self, id: None)
    diag = c.post("/api/v1/flujo-automatizacion/comprobar", headers=admin, json=datos).json()["datos"]
    assert diag["listo"] and not diag["compras_listas"]
    assert any("Harina" in r["titulo"] and r["codigo"] == "SIN_PROVEEDOR" and r["recomendacion"] for r in diag["avisos"])
    sin_proveedor = c.post("/api/v1/flujo-automatizacion/programar", headers=admin,
        json={**datos, "clave_idempotencia": "sin-proveedor", "autorizar_envio": False})
    assert sin_proveedor.status_code == 200, sin_proveedor.text
    assert c.put("/api/v1/flujo-automatizacion/configuracion", headers=admin, json=datos).status_code == 200
    assert c.get("/api/v1/flujo-automatizacion/configuracion", headers=admin).json()["datos"]["producto_ids"] == [producto_id]
    monkeypatch.setattr(ServicioProveedores, "oferta_preferida_para_compras", oferta_falsa)
    assert c.post("/api/v1/flujo-automatizacion/comprobar", headers=admin, json=datos).json()["datos"]["listo"]
    solicitud = {**datos, "clave_idempotencia": "calendario", "autorizar_envio": False}
    creada = c.post("/api/v1/flujo-automatizacion/programar", headers=admin, json=solicitud)
    assert creada.status_code == 200
    tareas = creada.json()["datos"]
    assert len(tareas) == 2 and tareas[1]["parametros"]["fecha_objetivo_demo"] == "2022-08-25"
    assert all(t["parametros"]["modelo_id"] == modelo_id for t in tareas)
    pagina = c.get("/api/v1/programaciones-demo?limite=1&desplazamiento=1", headers=admin).json()
    assert pagina["metadatos"]["total"] == 4 and len(pagina["datos"]) == 1
    assert c.post("/api/v1/flujo-automatizacion/programar", headers=admin, json=solicitud).json() == creada.json()
    assert c.post("/api/v1/flujo-automatizacion/programar", headers=admin, json={**solicitud, "dias": 3}).status_code == 409
    automatico = {**solicitud, "clave_idempotencia": "auto", "modo_envio_pedidos": "AUTOMATICO"}
    assert c.post("/api/v1/flujo-automatizacion/programar", headers=admin, json=automatico).status_code == 422
    assert c.post("/api/v1/flujo-automatizacion/programar", headers=admin, json={**automatico, "autorizar_envio": True}).status_code == 200
    with Session(engine) as s:
        assert s.scalar(select(func.count()).select_from(MovimientoInventario)) == 0


def test_destino_pendiente_es_aviso_pero_ingrediente_inactivo_impide_plan(entorno, monkeypatch):
    c, engine = entorno
    producto_id, ingrediente_id, _, modelo_id = sembrar(engine)
    admin = _cabecera(_token(c, "admin@example.com", "clave-segura-admin"))
    datos = datos_flujo(producto_id, modelo_id)
    monkeypatch.setattr(ServicioProveedores, "oferta_preferida_para_compras", lambda self, id:
        SimpleNamespace(proveedor_activo=True, proveedor_id=7, destino_verificado=False, proveedor_nombre="Harinas"))
    diag = c.post("/api/v1/flujo-automatizacion/comprobar", headers=admin, json=datos).json()["datos"]
    assert diag["listo"] and not diag["compras_listas"]
    assert [a["codigo"] for a in diag["avisos"]] == ["DESTINO_NO_VERIFICADO"]
    with Session(engine) as s:
        s.get(Ingrediente, ingrediente_id).activo = False
        s.commit()
    diag = c.post("/api/v1/flujo-automatizacion/comprobar", headers=admin, json=datos).json()["datos"]
    assert not diag["listo"]
    assert c.post("/api/v1/flujo-automatizacion/programar", headers=admin,
        json={**datos, "clave_idempotencia": "ingrediente-inactivo"}).status_code == 409


def test_gestion_pendientes_y_despacho_no_recoge_pausadas(entorno, monkeypatch):
    c, engine = entorno
    admin = _cabecera(_token(c, "admin@example.com", "clave-segura-admin"))
    operador = _cabecera(_token(c, "operador@example.com", "clave-segura-operador"))
    p = c.post("/api/v1/programaciones-demo", headers=admin, json=_programacion()).json()["datos"]
    ruta = f"/api/v1/programaciones-demo/{p['id']}"
    assert c.post(ruta + "/gestionar", headers=operador, json={"accion":"PAUSAR", "motivo":"Prueba"}).status_code == 403
    assert c.post(ruta + "/gestionar", headers=admin, json={"accion":"PAUSAR", "motivo":"Prueba"}).json()["datos"]["estado"] == "PAUSADA"
    with Session(engine) as s:
        s.get(ProgramacionDemo, p["id"]).ejecutar_desde_utc = datetime.now(timezone.utc) - timedelta(seconds=1); s.commit()
    monkeypatch.setattr(motor, "SessionLocal", sessionmaker(bind=engine, expire_on_commit=False))
    assert motor.despachar_pendientes(lambda *_: pytest.fail("No debe publicar una tarea pausada"))["reclamadas"] == 0
    assert c.post(ruta + "/gestionar", headers=admin, json={"accion":"REANUDAR", "motivo":"Prueba"}).status_code == 422
    assert c.patch(ruta, headers=admin, json={"ejecutar_desde_utc": (datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(), "motivo":"Nueva hora"}).status_code == 200
    assert c.post(ruta + "/gestionar", headers=admin, json={"accion":"REANUDAR", "motivo":"Continuar"}).status_code == 200
    assert c.post(ruta + "/gestionar", headers=admin, json={"accion":"CANCELAR", "motivo":"Ya no se necesita"}).status_code == 200
    assert c.get(f"/api/v1/ejecuciones-automatizacion/{p['ejecucion_id']}", headers=admin).json()["datos"]["estado"] == "CANCELADA"
    assert c.patch(ruta, headers=admin, json={"ejecutar_desde_utc": (datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(), "motivo":"No permitido"}).status_code == 409


@pytest.mark.parametrize("pausada", [False, True])
def test_ejecutar_ahora_conserva_entrada_y_despacha_una_vez(entorno, monkeypatch, pausada):
    c, engine = entorno
    admin = _cabecera(_token(c, "admin@example.com", "clave-segura-admin"))
    operador = _cabecera(_token(c, "operador@example.com", "clave-segura-operador"))
    original = c.post("/api/v1/programaciones-demo", headers=admin, json=_programacion()).json()["datos"]
    ruta = f"/api/v1/programaciones-demo/{original['id']}/gestionar"
    solicitud = {"accion": "EJECUTAR_AHORA", "motivo": "Probar automatización"}
    assert c.post(ruta, headers=operador, json=solicitud).status_code == 403
    if pausada:
        assert c.post(ruta, headers=admin, json={"accion": "PAUSAR", "motivo": "Esperar"}).status_code == 200
    antes = datetime.now(timezone.utc)
    respuesta = c.post(ruta, headers=admin, json=solicitud)
    assert respuesta.status_code == 200, respuesta.text
    actual = respuesta.json()["datos"]
    assert actual["estado"] == "PROGRAMADA"
    assert antes <= datetime.fromisoformat(actual["ejecutar_desde_utc"]) <= datetime.now(timezone.utc)
    for campo in ("parametros", "fecha_hora_simulada_local", "ejecucion_id", "clave_idempotencia"):
        assert actual[campo] == original[campo]
    assert actual["cambios"][-1]["accion"] == "EJECUTAR_AHORA"
    assert actual["cambios"][-1]["motivo"] == solicitud["motivo"]
    assert c.post(ruta, headers=admin, json=solicitud).json()["datos"] == actual
    monkeypatch.setattr(motor, "SessionLocal", sessionmaker(bind=engine, expire_on_commit=False))
    publicaciones = []
    assert motor.despachar_pendientes(lambda *args: publicaciones.append(args))["reclamadas"] == 1
    assert len(publicaciones) == 1
    assert motor.despachar_pendientes(lambda *_: pytest.fail("No debe duplicar la tarea"))["reclamadas"] == 0
    assert c.post(ruta, headers=admin, json=solicitud).status_code == 409


def test_horarios_de_cambio_de_zona_no_se_adivinan():
    for hora in (datetime(2026,3,8,2,30), datetime(2026,11,1,1,30)):
        with pytest.raises(ErrorAPI):
            _hora_utc(hora, ZoneInfo("America/New_York"))


def test_promocion_concurrente_postgresql(entorno_pg):
    """A03_POSTGRES_TEST=1: dos ajustes/reentregas conservan un solo efecto."""
    from concurrent.futures import ThreadPoolExecutor
    from app.modules.autenticacion.modelos import Usuario
    from app.modules.negocios.modelos import Negocio
    sesiones = entorno_pg
    with sesiones.begin() as s:
        s.add(Negocio(id=1, nombre="Prueba", zona_horaria="America/Lima", moneda="PEN"))
        s.add(Usuario(id=1, nombre="Prueba", correo="prueba@example.com", hash_contrasena="fixture", rol="ADMINISTRADOR", activo=True))
    _, _, lote_id, _ = sembrar(sesiones.kw["bind"])
    with sesiones.begin() as s:
        guardar_regla(s, ConfigurarRegla(habilitada=True), 1)
    def ajustar_dos_veces(_):
        with sesiones.begin() as s:
            return ajustar(s, lote_id, "concurrente").repetido
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(ajustar_dos_veces, range(2))) == [False, True]
    with sesiones.begin() as s:
        p = s.scalar(select(ProgramacionDemo)); p.ejecutar_desde_utc = datetime.now(timezone.utc) - timedelta(seconds=1)
    mensajes = []
    motor.despachar_pendientes(lambda id, token: mensajes.append((id, token)))
    assert len(mensajes) == 1
    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(lambda _: motor.ejecutar(*mensajes[0])["resultado"], range(2)))
    assert sorted(resultados) == ["COMPLETADA", "IGNORADA"]
    with sesiones() as s:
        assert s.scalar(select(func.count()).select_from(EvaluacionPromocion)) == 1
        assert s.scalar(select(func.count()).select_from(MovimientoInventario)) == 1
        assert s.get(LoteProducto, lote_id).saldo_disponible == 12


def test_migracion_aditiva_y_metadatos():
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from sqlalchemy import create_engine, text, event
    from test_migraciones_entregas import cargar_revision
    from app.core.base import Base
    engine = create_engine("sqlite://")
    @event.listens_for(engine, "connect")
    def funciones(conexion, _):
        conexion.create_function("char_length", 1, len)
    nuevas = {"programacion_demo", "ejecucion_automatizacion", "intento_automatizacion",
              "regla_promocion_demo", "evaluacion_promocion", "configuracion_flujo"}
    Base.metadata.create_all(engine, tables=[t for t in Base.metadata.sorted_tables if t.name not in nuevas])
    with engine.begin() as con:
        contexto = MigrationContext.configure(con)
        with Operations.context(contexto):
            cargar_revision("0001b_automatizaciones").upgrade()
            cargar_revision("0001c_motor").upgrade()
            con.execute(text("INSERT INTO producto(codigo,nombre,demostrar,activo) VALUES ('conservar','Conservar',0,1)"))
            nueva = cargar_revision("0015_flujo_promociones")
            nueva.upgrade()
            assert con.execute(text("SELECT nombre FROM producto WHERE codigo='conservar'")).scalar() == "Conservar"
            assert compare_metadata(contexto, Base.metadata) == []
            nueva.downgrade()
            nueva.upgrade()
            assert compare_metadata(contexto, Base.metadata) == []
    engine.dispose()
