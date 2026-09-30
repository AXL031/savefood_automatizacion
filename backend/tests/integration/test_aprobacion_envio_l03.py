"""Paso 6: HTTP→decisión→outbox→Telegram con transporte aislado, sin mensajes reales."""
import io
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError

import pytest
from pydantic import SecretStr
from sqlalchemy import func, select, text

from test_api_inicializacion_ventas import cliente
from test_planificacion_m02 import escenario, solicitar, saldos
from test_compras_l02 import compra, generar
from test_proveedores_l01 import TelegramFalso
from app.core.errores import ErrorAPI
from app.integrations.proveedores import telegram as canal
from app.modules.compras.envios import despachar_envios, ejecutar_envio
from app.modules.compras.modelos import EnvioPedido, PedidoCompra, PropuestaCompra
from app.modules.compras.servicio import decidir_pedido
from app.modules.proveedores.servicio import ServicioProveedores

TOKEN = "123:token-falso-para-pruebas-locales"


def borrador(compra):
    entorno = compra[0]
    plan = solicitar(entorno).json()["datos"]
    propuesta = generar(entorno, plan["id"]).json()["datos"]
    return propuesta, propuesta["pedidos"][0]


def aprobar(entorno, pedido, clave="decision-l03"):
    return entorno[0].post(f'/api/v1/pedidos/{pedido["id"]}/aprobar', headers=entorno[2],
                          json={"clave_idempotencia": clave, "chat_id_revisado": "123"})


class TelegramEnvio(TelegramFalso):
    def __init__(self, sesiones, resultado=None, al_enviar=None):
        self.sesiones, self.llamadas, self.al_enviar = sesiones, [], al_enviar
        self.resultado = resultado or canal.ResultadoEnvio("ENVIADO", message_id=987,
                                                          fecha_telegram=datetime(2026,9,30,tzinfo=timezone.utc))

    def enviar_mensaje(self, chat, texto):
        # La reclamación debe ser visible ANTES del efecto externo.
        with self.sesiones() as sesion:
            assert sesion.scalar(select(EnvioPedido.estado)) == "ENVIANDO"
        self.llamadas.append((chat, texto))
        if self.al_enviar: self.al_enviar()
        return self.resultado


def publicar(sesiones, ahora=None):
    tareas = []
    datos = despachar_envios(lambda id_, token: tareas.append((id_, token)), sesiones=sesiones, ahora=ahora)
    return tareas, datos


def test_aprobar_auditoria_idempotencia_permisos_y_envio_confirmado(compra):
    entorno = compra[0]
    http, sesiones, admin, operador, _, _ = entorno
    propuesta, pedido = borrador(compra)
    stock = saldos(sesiones)
    ruta = f'/api/v1/pedidos/{pedido["id"]}/aprobar'
    cuerpo = {"clave_idempotencia": "decision-l03", "chat_id_revisado": "123"}
    assert http.post(ruta, json=cuerpo).status_code == 401
    assert http.post(ruta, headers=operador, json=cuerpo).status_code == 403
    for cuerpo_malo in ({"clave_idempotencia":" "}, {**cuerpo,"chat_id_revisado":"@usuario"}):
        assert http.post(ruta, headers=admin, json=cuerpo_malo).status_code == 422
    respuesta = aprobar(entorno, pedido)
    assert respuesta.status_code == 202, respuesta.text
    aprobado = respuesta.json()["datos"]
    assert aprobado["estado"] == "PENDIENTE_ENVIO"
    assert aprobado["decision"]["accion"] == "APROBAR" and aprobado["decision"]["usuario_id"]
    assert aprobado["decision"]["nombre_usuario"] and aprobado["decision"]["fecha"]
    assert aprobado["envio"]["chat_id"] == "123" and aprobado["envio"]["message_id"] is None
    assert aprobado["mensaje"].startswith("DEMOSTRACIÓN — NO SURTIR\n")
    assert "2022-08-24" in aprobado["mensaje"] and "1503" in aprobado["mensaje"]
    assert TOKEN not in respuesta.text and "credencial_huella" not in respuesta.text
    assert aprobar(entorno, pedido).json()["datos"] == aprobado
    assert aprobar(entorno, pedido, "otra-decision").status_code == 409
    assert http.post(f'/api/v1/compras/propuestas/{propuesta["id"]}/cancelar', headers=admin, json={"motivo":"repetir"}).status_code == 409
    tareas, datos = publicar(sesiones)
    assert datos == {"publicados":1,"publicaciones_fallidas":0,"inciertos":0}
    fake = TelegramEnvio(sesiones)
    assert ejecutar_envio(*tareas[0], sesiones=sesiones, cliente=fake)["estado"] == "ENVIADO"
    assert ejecutar_envio(*tareas[0], sesiones=sesiones, cliente=fake)["estado"] == "OMITIDO"
    assert len(fake.llamadas) == 1 and fake.llamadas[0] == ("123", aprobado["mensaje"])
    final = http.get(f'/api/v1/pedidos/{pedido["id"]}', headers=operador).json()["datos"]
    assert final["estado"] == "ENVIADO" and final["envio"]["message_id"] == 987
    assert final["envio"]["fecha_telegram"] and final["envio"]["inicio_en"] and final["envio"]["fin_en"]
    assert final["decision"] == aprobado["decision"] and aprobar(entorno, pedido).json()["datos"] == final
    assert publicar(sesiones)[0] == [] and saldos(sesiones) == stock
    nuevo = solicitar(entorno, "recompra-despues-envio").json()["datos"]
    assert generar(entorno, nuevo["id"]).status_code == 409


@pytest.mark.parametrize("sin_destino", [False,True])
def test_rechazo_motivado_terminal_sin_envio_y_cancelacion_conserva_decision(compra, sin_destino):
    entorno = compra[0]
    http, sesiones, admin, operador, _, _ = entorno
    if sin_destino:
        with sesiones.begin() as sesion: ServicioProveedores(sesion).vincular_chat(compra[1],"456")
    propuesta, pedido = borrador(compra)
    stock = saldos(sesiones)
    ruta = f'/api/v1/pedidos/{pedido["id"]}/rechazar'
    datos = {"clave_idempotencia":"rechazo-l03", "motivo":"Faltante para revisar"}
    assert http.post(ruta, headers=operador, json=datos).status_code == 403
    assert http.post(ruta, headers=admin, json={**datos,"motivo":" "}).status_code == 422
    respuesta = http.post(ruta, headers=admin, json=datos)
    assert respuesta.status_code == 200, respuesta.text
    rechazado = respuesta.json()["datos"]
    assert rechazado["estado"] == "RECHAZADO" and rechazado["envio"] is None
    assert rechazado["decision"]["motivo"] == datos["motivo"]
    assert http.post(ruta, headers=admin, json=datos).json()["datos"] == rechazado
    assert http.post(ruta, headers=admin, json={**datos,"motivo":"otro"}).status_code == 409
    assert aprobar(entorno, pedido).status_code == 409
    assert publicar(sesiones)[0] == []
    cancelada = http.post(f'/api/v1/compras/propuestas/{propuesta["id"]}/cancelar', headers=admin, json={"motivo":"Usar otro plan"}).json()["datos"]
    assert cancelada["pedidos"][0]["estado"] == "RECHAZADO" and cancelada["pedidos"][0]["decision"] == rechazado["decision"]
    assert saldos(sesiones) == stock


@pytest.mark.parametrize("cambio", ["chat", "credencial", "inactivo"])
def test_destino_cambio_antes_del_worker_no_transmite(compra, monkeypatch, cambio):
    entorno, proveedor_id, _, _ = compra
    _, sesiones, _, _, _, _ = entorno
    _, pedido = borrador(compra)
    assert aprobar(entorno, pedido).status_code == 202
    tareas, _ = publicar(sesiones)
    fake = TelegramEnvio(sesiones)
    if cambio == "credencial": fake.huella = "f"*64
    else:
        with sesiones.begin() as sesion:
            s = ServicioProveedores(sesion, fake)
            if cambio == "chat": s.vincular_chat(proveedor_id, "456")
            else: s.cambiar_estado(proveedor_id, False)
    assert ejecutar_envio(*tareas[0], sesiones=sesiones, cliente=fake)["estado"] == "FALLIDO"
    assert fake.llamadas == [] and publicar(sesiones)[0] == []


def test_revalidacion_no_recalcula_y_chat_revisado_obligatorio(compra):
    entorno, proveedor_id, _, _ = compra
    http, sesiones, admin, operador, _, _ = entorno
    with sesiones.begin() as sesion:
        ServicioProveedores(sesion).vincular_chat(proveedor_id, "456")
    propuesta, pedido = borrador(compra)
    assert propuesta["estado"] == "BLOQUEADA" and aprobar(entorno, pedido).status_code == 409
    ruta = f'/api/v1/compras/propuestas/{propuesta["id"]}/verificar-destinos'
    assert http.post(ruta, headers=operador).status_code == 403
    with sesiones.begin() as sesion:
        assert ServicioProveedores(sesion, TelegramFalso()).verificar_destino(proveedor_id).verificado
    revisada = http.post(ruta, headers=admin).json()["datos"]
    assert revisada["estado"] == "GENERADA" and revisada["pedidos"][0]["lineas"] == pedido["lineas"]
    assert revisada["pedidos"][0]["proveedor"] == pedido["proveedor"]
    fallo = aprobar(entorno, pedido)
    assert fallo.status_code == 409 and fallo.json()["error"]["codigo"] == "DESTINO_CAMBIO"
    assert http.post(f'/api/v1/pedidos/{pedido["id"]}/aprobar', headers=admin,
                     json={"clave_idempotencia":"destino-revisado", "chat_id_revisado":"456"}).status_code == 202
    assert http.post(ruta, headers=admin).status_code == 409


@pytest.mark.parametrize("estado", ["FALLIDO", "PENDIENTE_VERIFICACION"])
def test_resultado_no_confirmado_no_se_reintenta(compra, estado):
    entorno = compra[0]
    sesiones = entorno[1]
    _, pedido = borrador(compra)
    assert aprobar(entorno, pedido).status_code == 202
    tareas, _ = publicar(sesiones)
    fake = TelegramEnvio(sesiones, canal.ResultadoEnvio(estado,"TRANSPORTE_PRUEBA","Resultado de fixture"))
    assert ejecutar_envio(*tareas[0], sesiones=sesiones, cliente=fake)["estado"] == estado
    assert ejecutar_envio(*tareas[0], sesiones=sesiones, cliente=fake)["estado"] == "OMITIDO"
    assert publicar(sesiones, datetime.now(timezone.utc)+timedelta(days=1))[0] == []
    assert len(fake.llamadas) == 1


def test_publicacion_recuperable_token_viejo_y_worker_interrumpido(compra):
    entorno = compra[0]
    sesiones = entorno[1]
    _, pedido = borrador(compra)
    assert aprobar(entorno, pedido).status_code == 202
    ahora = datetime.now(timezone.utc)
    def fallar(*_): raise ConnectionError("broker desconectado")
    assert despachar_envios(fallar,sesiones=sesiones,ahora=ahora)["publicaciones_fallidas"] == 1
    with sesiones() as sesion:
        envio = sesion.scalar(select(EnvioPedido))
        viejo = (envio.id,envio.token_despacho)
    assert publicar(sesiones, ahora)[0] == []
    tareas, _ = publicar(sesiones, ahora+timedelta(minutes=3))
    fake = TelegramEnvio(sesiones)
    assert ejecutar_envio(*viejo,sesiones=sesiones,cliente=fake)["estado"] == "OMITIDO"
    with sesiones.begin() as sesion:
        envio = sesion.get(EnvioPedido,tareas[0][0])
        envio.estado = "ENVIANDO"; envio.inicio_en = ahora; envio.lease_hasta = ahora
        sesion.get(PedidoCompra,pedido["id"]).estado = "ENVIANDO"
    assert publicar(sesiones,ahora+timedelta(minutes=4))[1]["inciertos"] == 1
    assert ejecutar_envio(*tareas[0],sesiones=sesiones,cliente=fake)["estado"] == "OMITIDO"
    assert fake.llamadas == [] and publicar(sesiones)[0] == []


def test_confirmacion_tardia_conserva_evidencia_sin_duplicar(compra):
    entorno = compra[0]
    sesiones = entorno[1]
    _, pedido = borrador(compra)
    aprobar(entorno,pedido)
    tareas, _ = publicar(sesiones)
    def vencer():
        assert publicar(sesiones,datetime.now(timezone.utc)+timedelta(minutes=3))[1]["inciertos"] == 1
    fake = TelegramEnvio(sesiones,al_enviar=vencer)
    assert ejecutar_envio(*tareas[0],sesiones=sesiones,cliente=fake)["estado"] == "ENVIADO"
    assert ejecutar_envio(*tareas[0],sesiones=sesiones,cliente=fake)["estado"] == "OMITIDO"
    assert len(fake.llamadas) == 1


@pytest.mark.parametrize("acciones", [["APROBAR","APROBAR"], ["APROBAR","RECHAZAR"]])
def test_rollback_y_decisiones_concurrentes(compra, acciones):
    entorno = compra[0]
    sesiones = entorno[1]
    _, pedido = borrador(compra)
    # La API proporciona la identidad real; servicio conserva la sesión del consumidor.
    from app.modules.autenticacion.modelos import Usuario
    with sesiones() as sesion:
        admin_id = sesion.scalar(select(Usuario.id).where(Usuario.correo=="admin@example.com"))
    def decidir(sesion, accion):
        return decidir_pedido(sesion,pedido["id"],accion=accion,clave="decision-concurrente",
                              usuario_id=admin_id,nombre_usuario="Fixture admin",motivo="Revisar" if accion=="RECHAZAR" else None,
                              chat_id_revisado="123")
    with pytest.raises(RuntimeError), sesiones.begin() as sesion:
        # sqlite3 legacy no abre BEGIN para SELECT/SAVEPOINT: el consumidor
        # realiza también una escritura para probar su transacción real.
        sesion.execute(text("UPDATE configuracion_inicial SET mensaje_error='rollback-fixture' WHERE id=1"))
        decidir(sesion,"APROBAR")
        raise RuntimeError("Consumidor falló")
    with sesiones() as sesion:
        assert sesion.scalar(select(func.count()).select_from(EnvioPedido)) == 0
        assert sesion.get(PedidoCompra,pedido["id"]).decision_json is None
    if os.getenv("E03_POSTGRES_TEST") != "1": return
    def ejecutar(accion):
        try:
            with sesiones.begin() as sesion: return decidir(sesion,accion).estado
        except ErrorAPI as error: return error.codigo
    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(ejecutar,acciones))
    if acciones[0] == acciones[1]: assert resultados == ["PENDIENTE_ENVIO"]*2
    else: assert resultados.count("PEDIDO_YA_DECIDIDO") == 1
    with sesiones() as sesion:
        estado = sesion.get(PedidoCompra,pedido["id"]).estado
        assert sesion.scalar(select(func.count()).select_from(EnvioPedido)) == int(estado=="PENDIENTE_ENVIO")


def test_despachos_y_workers_concurrentes_no_duplican(compra):
    if os.getenv("E03_POSTGRES_TEST") != "1": pytest.skip("Locks PostgreSQL")
    entorno = compra[0]
    sesiones = entorno[1]
    _, pedido = borrador(compra)
    assert aprobar(entorno,pedido).status_code == 202
    with ThreadPoolExecutor(max_workers=2) as pool:
        publicaciones = list(pool.map(lambda _:publicar(sesiones)[0],range(2)))
    tareas = [tarea for grupo in publicaciones for tarea in grupo]
    assert len(tareas)==1
    fake = TelegramEnvio(sesiones)
    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(lambda _:ejecutar_envio(*tareas[0],sesiones=sesiones,cliente=fake)["estado"],range(2)))
    assert sorted(resultados)==["ENVIADO","OMITIDO"] and len(fake.llamadas)==1


@pytest.mark.parametrize("respuesta,estado", [
    ({"ok":True,"result":{"message_id":77,"date":1790726400,"chat":{"id":123}}},"ENVIADO"),
    (HTTPError("https://api.telegram.org/bot"+TOKEN,403,TOKEN,{},None),"FALLIDO"),
    (HTTPError("https://api.telegram.org/bot"+TOKEN,429,TOKEN,{},None),"FALLIDO"),
    (HTTPError("https://api.telegram.org/bot"+TOKEN,500,TOKEN,{},None),"PENDIENTE_VERIFICACION"),
    (URLError(TOKEN),"PENDIENTE_VERIFICACION"),
    (TimeoutError(TOKEN),"PENDIENTE_VERIFICACION"),
    ({"ok":True,"result":{"message_id":77,"date":1790726400,"chat":{"id":456}}},"PENDIENTE_VERIFICACION"),
    ({"ok":True,"result":{"message_id":False,"date":1790726400,"chat":{"id":123}}},"PENDIENTE_VERIFICACION"),
    ({"ok":False,"description":TOKEN},"PENDIENTE_VERIFICACION"),
])
def test_sendmessage_sanitizado_sin_retry(monkeypatch,caplog,respuesta,estado):
    llamadas=[]
    class Opener:
        def open(self,peticion,timeout):
            assert peticion.full_url.endswith("/sendMessage") and timeout==8
            llamadas.append(json.loads(peticion.data))
            if isinstance(respuesta,Exception): raise respuesta
            return io.BytesIO(json.dumps(respuesta).encode())
    monkeypatch.setattr(canal,"build_opener",lambda *_:Opener())
    resultado = canal.ClienteTelegram(SecretStr(TOKEN)).enviar_mensaje("123","DEMOSTRACIÓN — NO SURTIR\nFixture")
    assert resultado.estado == estado and len(llamadas)==1
    assert "parse_mode" not in llamadas[0] and llamadas[0]["chat_id"]=="123"
    assert TOKEN not in str(resultado)+caplog.text
    if estado=="ENVIADO": assert resultado.message_id==77 and resultado.fecha_telegram


def test_mensaje_demasiado_largo_no_llama_transporte(monkeypatch):
    def prohibido(*_): raise AssertionError("No debe iniciar red")
    monkeypatch.setattr(canal,"build_opener",prohibido)
    assert canal.ClienteTelegram(SecretStr(TOKEN)).enviar_mensaje("123","🧪"*2049).estado=="FALLIDO"
