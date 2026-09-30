"""Paso 5: canal real con transporte simulado, secretos y consumidor Compras."""
import hashlib
import io
import json
from urllib.error import HTTPError, URLError

import pytest
from pydantic import SecretStr

from test_api_inicializacion_ventas import cliente
from app.integrations.proveedores import telegram as canal

TOKEN = "123:token-falso-para-pruebas-locales"
OTRO = "456:otro-token-falso-para-pruebas-locales"


@pytest.fixture
def aislado(monkeypatch, tmp_path):
    monkeypatch.setenv("JWT_SECRET", "clave-de-instalacion-de-prueba-mayor-que-32-caracteres")
    monkeypatch.setenv("TELEGRAM_CONFIG_DIR", str(tmp_path / "secretos"))
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    return tmp_path


def transporte(monkeypatch, resultados):
    llamadas = []
    pendientes = list(resultados)
    class Opener:
        def open(self, peticion, timeout):
            metodo = peticion.full_url.rsplit("/", 1)[-1]
            llamadas.append((metodo, json.loads(peticion.data)))
            assert timeout == 8 and metodo in ("getMe", "getChat", "getChatMember", "getWebhookInfo", "getUpdates")
            resultado = pendientes.pop(0)
            if isinstance(resultado, Exception):
                raise resultado
            return io.BytesIO(json.dumps(resultado).encode())
    monkeypatch.setattr(canal, "build_opener", lambda *_: Opener())
    return llamadas


def bot(numero=123):
    return {"ok": True, "result": {"id": numero, "is_bot": True, "first_name": "Bot de prueba", "username": "foodsave_test_bot"}}


def login(cliente, operador=False):
    rol = "operador" if operador else "admin"
    respuesta = cliente.post("/api/v1/autenticacion/iniciar-sesion", json={"correo": f"{rol}@example.com", "contrasena": f"clave-segura-{rol}"})
    assert respuesta.status_code == 200, respuesta.text
    return {"Authorization": "Bearer " + respuesta.json()["datos"]["token_acceso"]}


def test_archivo_cifrado_durable_deshabilitar_y_clave_distinta(aislado, monkeypatch):
    configuracion = canal.ConfiguracionTelegram()
    configuracion.guardar(SecretStr(TOKEN))
    assert TOKEN.encode() not in configuracion.ruta.read_bytes()
    assert canal.ConfiguracionTelegram().leer().get_secret_value() == TOKEN
    assert TOKEN not in repr(canal.ClienteTelegram.desde_configuracion())
    monkeypatch.setenv("JWT_SECRET", "otra-clave-de-instalacion-de-32-caracteres")
    with pytest.raises(canal.ErrorTelegram, match="configuración protegida"):
        canal.ConfiguracionTelegram().leer()
    configuracion.guardar(SecretStr(""))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TOKEN)
    assert not canal.ClienteTelegram.desde_configuracion().huella


@pytest.mark.parametrize("error,codigo", [
    (URLError(TOKEN), "TELEGRAM_SIN_CONEXION"), (TimeoutError(TOKEN), "TELEGRAM_SIN_CONEXION"),
    (HTTPError("https://api.telegram.org/bot" + TOKEN, 401, TOKEN, {}, None), "TOKEN_RECHAZADO"),
    (HTTPError("https://api.telegram.org/bot" + TOKEN, 403, TOKEN, {}, None), "TELEGRAM_RECHAZADO"),
    (HTTPError("https://api.telegram.org/bot" + TOKEN, 429, TOKEN, {}, None), "TELEGRAM_LIMITE"),
    ({"ok": False, "description": TOKEN}, "TELEGRAM_RESPUESTA_INVALIDA"),
    ({"ok": True, "result": {"id": 123, "is_bot": False}}, "TELEGRAM_RESPUESTA_INVALIDA"),
])
def test_errores_sin_secretos_ni_retry(aislado, monkeypatch, caplog, error, codigo):
    llamadas = transporte(monkeypatch, [error])
    with pytest.raises(canal.ErrorTelegram) as fallo:
        canal.ClienteTelegram(SecretStr(TOKEN)).comprobar_bot()
    assert fallo.value.codigo == codigo
    assert TOKEN not in str(fallo.value) + caplog.text
    assert len(llamadas) == 1


@pytest.mark.parametrize("tipo,miembro,permisos,ok", [
    ("private", None, None, True),
    ("group", {"status": "administrator"}, {}, True),
    ("supergroup", {"status": "member"}, {"can_send_messages": True}, True),
    ("group", {"status": "member"}, {"can_send_messages": False}, False),
    ("supergroup", {"status": "restricted", "is_member": True, "can_send_messages": False}, {}, False),
    ("group", {"status": "left"}, {}, False),
    ("channel", None, {}, False),
])
def test_verificacion_acceso_y_permisos_sin_envios(aislado, monkeypatch, tipo, miembro, permisos, ok):
    respuestas = [bot(), {"ok": True, "result": {"id": 789, "type": tipo, "permissions": permisos}}]
    if miembro: respuestas.append({"ok": True, "result": miembro})
    llamadas = transporte(monkeypatch, respuestas)
    cliente = canal.ClienteTelegram(SecretStr(TOKEN))
    if ok: assert cliente.verificar_chat("789")
    else:
        with pytest.raises(canal.ErrorTelegram): cliente.verificar_chat("789")
    assert all(metodo != "sendMessage" for metodo, _ in llamadas)


def test_api_configuracion_permisos_vinculo_rotacion_y_consumidor(cliente, aislado, monkeypatch, caplog):
    admin, operador = login(cliente), login(cliente, True)
    ruta = "/api/v1/proveedores/telegram/configuracion"
    assert cliente.get(ruta).status_code == 401
    for metodo, url in [("get", ruta), ("post", ruta), ("delete", ruta), ("post", "/api/v1/proveedores/telegram/comprobar"), ("post", "/api/v1/proveedores/telegram/chats-pruebas")]:
        assert getattr(cliente, metodo)(url, headers=operador).status_code == 403
    assert not cliente.get(ruta, headers=admin).json()["datos"]["configurado"]
    llamadas = transporte(monkeypatch, [bot(), bot(), {"ok": True, "result": {"id": 789, "type": "private"}}, bot(456)])
    guardado = cliente.post(ruta, headers=admin, json={"token": TOKEN})
    assert guardado.status_code == 200 and guardado.json()["datos"]["bot"]["id"] == 123
    assert TOKEN not in guardado.text
    proveedor = cliente.post("/api/v1/proveedores", headers=admin, json={"codigo": "TG", "nombre": "Pruebas"}).json()["datos"]
    prefijo = f'/api/v1/proveedores/{proveedor["id"]}'
    assert cliente.put(prefijo + "/chat?chat_id=789", headers=operador).status_code == 403
    assert cliente.post(prefijo + "/verificar-destino", headers=operador).status_code == 403
    for chat in ("@usuario", "0", "  ", "001", "-0"):
        assert cliente.put(prefijo + "/chat", params={"chat_id": chat}, headers=admin).status_code in (409, 422)
    assert cliente.put(prefijo + "/chat?chat_id=789", headers=admin).status_code == 200
    verificado = cliente.post(prefijo + "/verificar-destino", headers=admin)
    assert verificado.json()["datos"]["verificado"]
    lista = cliente.get("/api/v1/proveedores", headers=operador).json()["datos"]
    assert lista[0]["destino_verificado"] and lista[0]["destino_verificado_en"]
    assert "destino_credencial_huella" not in lista[0]
    from app.core.base_datos import obtener_sesion
    from app.modules.proveedores.servicio import ServicioProveedores
    with next(cliente.app.dependency_overrides[obtener_sesion]()) as sesion:
        assert ServicioProveedores(sesion).puede_enviar(proveedor["id"])
    assert cliente.post(ruta, headers=admin, json={"token": OTRO}).json()["datos"]["bot"]["id"] == 456
    assert not cliente.get("/api/v1/proveedores", headers=admin).json()["datos"][0]["destino_verificado"]
    with next(cliente.app.dependency_overrides[obtener_sesion]()) as sesion:
        assert not ServicioProveedores(sesion).puede_enviar(proveedor["id"])
    assert cliente.delete(ruta, headers=admin).status_code == 200
    assert not canal.ClienteTelegram.desde_configuracion().huella
    assert TOKEN not in caplog.text and OTRO not in caplog.text
    assert [m for m, _ in llamadas] == ["getMe", "getMe", "getChat", "getMe"]


def test_buscar_chat_filtra_start_sin_consumir_actualizaciones(aislado, monkeypatch):
    llamadas = transporte(monkeypatch, [bot(), {"ok": True, "result": {"url": ""}}, {"ok": True, "result": [
        {"message": {"text": "/start", "chat": {"id": 789, "type": "private"}, "from": {"first_name": "Privado"}}},
        {"message": {"text": "otro mensaje", "chat": {"id": 111, "type": "private"}}},
        {"message": {"text": "/start@foodsave_test_bot", "chat": {"id": -987, "type": "group"}}},
        {"message": {"text": "/start@otro_bot", "chat": {"id": 222, "type": "private"}}},
        {"message": {"text": "/start", "chat": {"id": 789, "type": "private"}}},
    ]}])
    resultado = canal.ClienteTelegram(SecretStr(TOKEN)).buscar_chats_pruebas()
    assert resultado == [{"chat_id": "789", "tipo": "private"}, {"chat_id": "-987", "tipo": "group"}]
    assert llamadas[-1] == ("getUpdates", {"limit": 100, "timeout": 0})
    assert "Privado" not in str(resultado)


def test_buscar_chat_respeta_webhook(aislado, monkeypatch):
    llamadas = transporte(monkeypatch, [bot(), {"ok": True, "result": {"url": "https://otro-sistema.example"}}])
    with pytest.raises(canal.ErrorTelegram) as fallo:
        canal.ClienteTelegram(SecretStr(TOKEN)).buscar_chats_pruebas()
    assert fallo.value.codigo == "BOT_CON_WEBHOOK"
    assert [m for m, _ in llamadas] == ["getMe", "getWebhookInfo"]


def test_rechazo_no_reemplaza_token_y_fallo_revoca_verificacion(cliente, aislado, monkeypatch):
    admin = login(cliente)
    configuracion = canal.ConfiguracionTelegram()
    configuracion.guardar(SecretStr(TOKEN))
    ruta = "/api/v1/proveedores/telegram/configuracion"
    assert cliente.post(ruta, headers=admin, json={"token": "secreto-malformado"}).status_code == 422
    assert configuracion.leer().get_secret_value() == TOKEN
    transporte(monkeypatch, [HTTPError("https://api.telegram.org/bot" + OTRO, 401, OTRO, {}, None)])
    respuesta = cliente.post(ruta, headers=admin, json={"token": OTRO})
    assert respuesta.json()["datos"]["codigo"] == "TOKEN_RECHAZADO"
    assert configuracion.leer().get_secret_value() == TOKEN and OTRO not in respuesta.text
    proveedor = cliente.post("/api/v1/proveedores", headers=admin, json={"codigo": "TG", "nombre": "Pruebas", "chat_id_pruebas": "789"}).json()["datos"]
    ruta_verificar = f'/api/v1/proveedores/{proveedor["id"]}/verificar-destino'
    transporte(monkeypatch, [bot(), {"ok": True, "result": {"id": 789, "type": "private"}}])
    assert cliente.post(ruta_verificar, headers=admin).json()["datos"]["verificado"]
    transporte(monkeypatch, [URLError(TOKEN)])
    respuesta = cliente.post(ruta_verificar, headers=admin)
    assert not respuesta.json()["datos"]["verificado"] and TOKEN not in respuesta.text
    assert not cliente.get("/api/v1/proveedores", headers=admin).json()["datos"][0]["destino_verificado"]
