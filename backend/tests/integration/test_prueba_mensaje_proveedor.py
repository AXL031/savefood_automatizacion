"""Prueba real del contrato HTTP con transporte externo falso, sin mensajes reales."""
from datetime import datetime, timezone
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from app.integrations.proveedores.telegram import ClienteTelegram, ResultadoEnvio
from test_api_inicializacion_ventas import cliente
from test_telegram_config_l03 import login, TOKEN


@pytest.fixture
def preparado(cliente, monkeypatch):
    admin = login(cliente)
    monkeypatch.setattr(ClienteTelegram, "verificar_chat", lambda *_: True)
    p = cliente.post("/api/v1/proveedores", headers=admin,
                     json={"nombre": "Distribuidora", "chat_id_pruebas": "123"}).json()["datos"]
    url = f'/api/v1/proveedores/{p["id"]}'
    cliente.post(url + "/verificar-destino", headers=admin).raise_for_status()
    return cliente, admin, url


def entrada(clave="prueba-0001", revision=False):
    return {"clave_idempotencia": clave, "chat_id_revisado": "123", "confirmar_revision_chat": revision}


def test_envio_confirmado_idempotente_historial_y_permisos(preparado, monkeypatch):
    cliente, admin, url = preparado
    llamadas = []
    def enviar(_, chat, texto):
        # La reserva es visible desde otra petición ANTES de transmitir.
        historial = cliente.get(url + "/mensajes-prueba", headers=admin).json()["datos"]
        assert historial[0]["estado"] == "PENDIENTE_VERIFICACION"
        assert chat == "123" and "Prueba · Mensaje de prueba" in texto and "No corresponde a un pedido" in texto
        llamadas.append(chat)
        return ResultadoEnvio("ENVIADO", message_id=42, fecha_telegram=datetime.now(timezone.utc))
    monkeypatch.setattr(ClienteTelegram, "enviar_mensaje", enviar)
    operador = login(cliente, operador=True)
    assert cliente.post(url + "/mensaje-prueba", headers=operador, json=entrada()).status_code == 403
    assert cliente.get(url + "/mensajes-prueba", headers=operador).status_code == 403
    assert cliente.post(url + "/mensaje-prueba", json=entrada()).status_code == 401
    primera = cliente.post(url + "/mensaje-prueba", headers=admin, json=entrada())
    assert primera.status_code == 200, primera.text
    assert primera.json()["datos"]["estado"] == "ENVIADO"
    assert primera.json()["datos"]["message_id"] == 42
    segunda = cliente.post(url + "/mensaje-prueba", headers=admin, json=entrada())
    assert segunda.json() == primera.json()
    assert len(llamadas) == 1
    assert "credencial_huella" not in primera.text and TOKEN not in primera.text
    assert cliente.post(url + "/mensaje-prueba", headers=admin, json={**entrada(), "chat_id_revisado": "456"}).status_code == 409


@pytest.mark.parametrize("resultado", [ResultadoEnvio("PENDIENTE_VERIFICACION"), RuntimeError(TOKEN),
                                      ResultadoEnvio("ENVIADO", message_id=-1)])
def test_incertidumbre_requiere_revision_y_no_reintenta(preparado, monkeypatch, resultado):
    cliente, admin, url = preparado
    llamadas = []
    def enviar(*_):
        llamadas.append(True)
        if isinstance(resultado, Exception): raise resultado
        return resultado
    monkeypatch.setattr(ClienteTelegram, "enviar_mensaje", enviar)
    respuesta = cliente.post(url + "/mensaje-prueba", headers=admin, json=entrada())
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["datos"]["estado"] == "PENDIENTE_VERIFICACION"
    assert TOKEN not in respuesta.text
    cliente.post(url + "/mensaje-prueba", headers=admin, json=entrada()).raise_for_status()
    assert cliente.post(url + "/mensaje-prueba", headers=admin, json=entrada("prueba-0002")).status_code == 409
    assert len(llamadas) == 1
    cliente.post(url + "/mensaje-prueba", headers=admin, json=entrada("prueba-0002", revision=True)).raise_for_status()
    assert len(llamadas) == 2


def test_fallo_definitivo_destino_inactivo_y_rotacion(preparado, monkeypatch):
    cliente, admin, url = preparado
    llamadas = []
    def enviar(*_):
        llamadas.append(True)
        return ResultadoEnvio("FALLIDO", detalle=TOKEN)
    monkeypatch.setattr(ClienteTelegram, "enviar_mensaje", enviar)
    respuesta = cliente.post(url + "/mensaje-prueba", headers=admin, json=entrada())
    assert respuesta.json()["datos"]["estado"] == "FALLIDO" and TOKEN not in respuesta.text
    cliente.patch(url + "/estado?activo=false", headers=admin).raise_for_status()
    assert cliente.post(url + "/mensaje-prueba", headers=admin, json=entrada("prueba-0002")).status_code == 409
    cliente.patch(url + "/estado?activo=true", headers=admin).raise_for_status()
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "456:token-rotado-para-pruebas-locales")
    assert cliente.post(url + "/mensaje-prueba", headers=admin, json=entrada("prueba-0002")).status_code == 409
    assert len(llamadas) == 1


def test_caida_tras_reserva_no_reenvia(preparado, monkeypatch):
    from app.modules.proveedores import rutas
    cliente, admin, url = preparado
    def caer(*_): raise RuntimeError("Caída simulada antes de enviar")
    monkeypatch.setattr(rutas, "transmitir_prueba", caer)
    with pytest.raises(RuntimeError):
        cliente.post(url + "/mensaje-prueba", headers=admin, json=entrada())
    historial = cliente.get(url + "/mensajes-prueba", headers=admin).json()["datos"]
    assert len(historial) == 1 and historial[0]["estado"] == "PENDIENTE_VERIFICACION"
    # Recupera la reserva; no invoca de nuevo la función que falla.
    cliente.post(url + "/mensaje-prueba", headers=admin, json=entrada()).raise_for_status()


@pytest.mark.skipif(os.getenv("E03_POSTGRES_TEST") != "1", reason="Bloqueos de fila requieren PostgreSQL")
def test_doble_click_concurrente_transmite_una_vez(preparado, monkeypatch):
    cliente, admin, url = preparado
    barrera = Barrier(2)
    llamadas = []
    def enviar(*_):
        llamadas.append(True)
        return ResultadoEnvio("ENVIADO", message_id=50, fecha_telegram=datetime.now(timezone.utc))
    monkeypatch.setattr(ClienteTelegram, "enviar_mensaje", enviar)
    def solicitar():
        barrera.wait(timeout=10)
        return cliente.post(url + "/mensaje-prueba", headers=admin, json=entrada())
    with ThreadPoolExecutor(max_workers=2) as pool:
        respuestas = list(pool.map(lambda _: solicitar(), range(2)))
    assert all(r.status_code == 200 for r in respuestas)
    assert len(llamadas) == 1


def test_tabla_resume_varios_ingredientes_activos_sin_duplicarlos(preparado):
    cliente, admin, url = preparado
    for nombre in ("Harina", "Sal"):
        ing = cliente.post("/api/v1/ingredientes", headers=admin,
            json={"codigo": nombre, "nombre": nombre, "unidad_base": "g"}).json()["datos"]
        for indice in range(2):
            cliente.post(url + "/ofertas", headers=admin, json={"ingrediente_id": ing["id"],
                "descripcion": f"Bolsa {indice}", "unidad_compra": "bolsa", "factor_conversion": "1000"}).raise_for_status()
    datos = cliente.get("/api/v1/proveedores", headers=admin).json()["datos"][0]
    assert [i["nombre"] for i in datos["ingredientes"]] == ["Harina", "Sal"]
