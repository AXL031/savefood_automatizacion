"""Recuperación con evidencia y transporte falso. Nunca envía mensajes reales."""
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select, text

from test_api_inicializacion_ventas import cliente
from test_planificacion_m02 import escenario, saldos
from test_compras_l02 import compra
from test_aprobacion_envio_l03 import borrador, aprobar, publicar, TelegramEnvio
from test_proveedores_l01 import TelegramFalso
from app.core.errores import ErrorAPI
from app.modules.autenticacion.modelos import Usuario
from app.modules.compras.modelos import EnvioPedido, PedidoCompra, RecuperacionEnvio
from app.modules.compras.envios import ejecutar_envio
from app.modules.compras.recuperacion import recuperar_envio
from app.modules.proveedores.servicio import ServicioProveedores
from app.integrations.proveedores.telegram import ResultadoEnvio


def fallar(compra, estado="PENDIENTE_VERIFICACION"):
    entorno = compra[0]
    _, pedido = borrador(compra)
    assert aprobar(entorno, pedido).status_code == 202
    tarea = publicar(entorno[1])[0][0]
    fake = TelegramEnvio(entorno[1], ResultadoEnvio(estado, "TIMEOUT_FIXTURE", "Resultado de prueba aislada."))
    assert ejecutar_envio(*tarea, sesiones=entorno[1], cliente=fake)["estado"] == estado
    return entorno[0].get(f'/api/v1/pedidos/{pedido["id"]}', headers=entorno[2]).json()["datos"], tarea


def cuerpo(pedido, resultado="NO_ENVIADO", clave="conciliar-fixture"):
    datos = {"clave_idempotencia": clave, "envio_id": pedido["envio"]["id"],
             "chat_id_revisado": pedido["envio"]["chat_id"],
             "evidencia": "Revisión documentada del pedido y chat propio de pruebas."}
    if resultado:
        datos["resultado"] = resultado
    if resultado == "ENVIADO":
        datos.update(message_id=765, fecha_telegram=datetime.now(timezone.utc).isoformat())
    return datos


def post(compra, pedido, accion, datos, headers=None):
    entorno = compra[0]
    return entorno[0].post(f'/api/v1/pedidos/{pedido["id"]}/{accion}', headers=headers or entorno[2], json=datos)


def test_confirmar_entrega_idempotencia_permisos_y_recompra(compra):
    entorno = compra[0]
    pedido, tarea = fallar(compra)
    stock = saldos(entorno[1])
    datos = cuerpo(pedido, "ENVIADO")
    ruta = f'/api/v1/pedidos/{pedido["id"]}/conciliar'
    assert entorno[0].post(ruta, json=datos).status_code == 401
    assert post(compra, pedido, "conciliar", datos, entorno[3]).status_code == 403
    respuesta = post(compra, pedido, "conciliar", datos)
    assert respuesta.status_code == 200, respuesta.text
    confirmado = respuesta.json()["datos"]
    assert confirmado["estado"] == "ENVIADO" and confirmado["envio"]["message_id"] == 765
    assert confirmado["envio"]["codigo_error"] == "TIMEOUT_FIXTURE"
    r = confirmado["recuperaciones"][0]
    assert r["accion"] == "CONFIRMAR_ENVIO" and r["usuario_id"] and r["nombre_usuario"] and r["fecha"]
    assert r["resultado_anterior"]["estado"] == "PENDIENTE_VERIFICACION"
    assert post(compra, pedido, "conciliar", datos).json()["datos"] == confirmado
    assert post(compra, pedido, "conciliar", {**datos, "message_id": 766}).status_code == 409
    assert post(compra, pedido, "conciliar", {**datos, "clave_idempotencia": "otra"}).status_code == 409
    assert post(compra, pedido, "reintentar", cuerpo(pedido, None)).status_code == 409
    assert entorno[0].post(f'/api/v1/compras/propuestas/{pedido["propuesta_id"]}/cancelar', headers=entorno[2], json={"motivo":"repetir"}).status_code == 409
    fake = TelegramEnvio(entorno[1])
    assert ejecutar_envio(*tarea, sesiones=entorno[1], cliente=fake)["estado"] == "OMITIDO"
    assert publicar(entorno[1])[0] == [] and fake.llamadas == [] and saldos(entorno[1]) == stock
    assert "credencial_huella" not in respuesta.text and "token-falso" not in respuesta.text


@pytest.mark.parametrize("mal", [
    {"evidencia": "          "}, {"chat_id_revisado": "456"}, {"envio_id": 999999},
    {"resultado": "ENVIADO"}, {"resultado": "ENVIADO", "message_id": True},
    {"resultado": "ENVIADO", "message_id": 12, "fecha_telegram": "2026-10-01T08:00:00"},
    {"resultado": "ENVIADO", "message_id": 12, "fecha_telegram": "2099-10-01T08:00:00Z"},
    {"resultado": "ENVIADO", "message_id": 12, "fecha_telegram": "2020-10-01T08:00:00Z"},
    {"message_id": 12}, {"resultado": "OTRO"},
])
def test_evidencia_invalida_no_cambia_estado(compra, mal):
    pedido, _ = fallar(compra)
    respuesta = post(compra, pedido, "conciliar", {**cuerpo(pedido), **mal})
    assert respuesta.status_code in {409, 422}, respuesta.text
    with compra[0][1]() as sesion:
        assert sesion.get(PedidoCompra, pedido["id"]).estado == "PENDIENTE_VERIFICACION"
        assert sesion.scalar(select(func.count()).select_from(RecuperacionEnvio)) == 0


def test_no_enviado_reintento_explicito_historial_y_destino_nuevo(compra):
    entorno, proveedor_id, _, _ = compra
    pedido, viejo = fallar(compra)
    stock = saldos(entorno[1])
    # Incierto: ningún botón de retry directo ni permiso para transmitir.
    assert post(compra, pedido, "reintentar", cuerpo(pedido, None)).status_code == 409
    datos = cuerpo(pedido)
    conciliado = post(compra, pedido, "conciliar", datos).json()["datos"]
    assert conciliado["estado"] == "FALLIDO"
    assert conciliado["envio"]["codigo_error"] == "CONCILIADO_NO_ENVIADO"
    assert conciliado["recuperaciones"][0]["resultado_anterior"]["codigo_error"] == "TIMEOUT_FIXTURE"
    assert publicar(entorno[1])[0] == []
    with entorno[1].begin() as sesion:
        s = ServicioProveedores(sesion, TelegramFalso())
        s.vincular_chat(proveedor_id, "456")
    nuevo = cuerpo(pedido, None, "retry-fixture")
    assert post(compra, pedido, "reintentar", nuevo).status_code == 409
    with entorno[1].begin() as sesion:
        ServicioProveedores(sesion, TelegramFalso()).verificar_destino(proveedor_id)
    assert post(compra, pedido, "reintentar", nuevo).status_code == 409  # chat revisado obsoleto
    nuevo["chat_id_revisado"] = "456"
    assert post(compra, pedido, "reintentar", nuevo, entorno[3]).status_code == 403
    respuesta = post(compra, pedido, "reintentar", nuevo)
    assert respuesta.status_code == 202, respuesta.text
    reintentado = respuesta.json()["datos"]
    assert reintentado["estado"] == "PENDIENTE_ENVIO" and reintentado["envio"]["numero_intento"] == 2
    assert [e["estado"] for e in reintentado["envios"]] == ["FALLIDO", "PENDIENTE_ENVIO"]
    assert reintentado["envio"]["chat_id"] == "456" and reintentado["mensaje"] == pedido["mensaje"]
    assert reintentado["lineas"] == pedido["lineas"] and reintentado["decision"] == pedido["decision"]
    assert post(compra, pedido, "reintentar", nuevo).json()["datos"] == reintentado
    assert post(compra, pedido, "reintentar", {**nuevo, "clave_idempotencia": "retry-distinto"}).status_code == 409
    # La repetición de la aprobación original conserva el chat original, no el nuevo.
    assert aprobar(entorno, pedido).status_code == 202
    class Transporte(TelegramFalso):
        llamadas = []
        def enviar_mensaje(self, chat, texto):
            with entorno[1]() as sesion:
                assert sesion.scalar(select(EnvioPedido.estado).where(EnvioPedido.numero_intento == 2)) == "ENVIANDO"
            self.llamadas.append((chat, texto))
            return ResultadoEnvio("ENVIADO", message_id=987, fecha_telegram=datetime.now(timezone.utc))
    fake = Transporte()
    assert ejecutar_envio(*viejo, sesiones=entorno[1], cliente=fake)["estado"] == "OMITIDO"
    tarea = publicar(entorno[1])[0][0]
    assert ejecutar_envio(*tarea, sesiones=entorno[1], cliente=fake)["estado"] == "ENVIADO"
    assert ejecutar_envio(*tarea, sesiones=entorno[1], cliente=fake)["estado"] == "OMITIDO"
    assert len(fake.llamadas) == 1 and saldos(entorno[1]) == stock


def test_fallo_definitivo_puede_reintentar_sin_conciliacion_y_revalida_worker(compra):
    entorno, proveedor_id, _, _ = compra
    pedido, _ = fallar(compra, "FALLIDO")
    respuesta = post(compra, pedido, "reintentar", cuerpo(pedido, None, "retry-directo"))
    assert respuesta.status_code == 202
    tarea = publicar(entorno[1])[0][0]
    with entorno[1].begin() as sesion:
        ServicioProveedores(sesion).cambiar_estado(proveedor_id, False)
    fake = TelegramEnvio(entorno[1])
    assert ejecutar_envio(*tarea, sesiones=entorno[1], cliente=fake)["estado"] == "FALLIDO"
    assert fake.llamadas == []


def test_respuesta_tardia_no_sobrescribe_conciliacion(compra):
    entorno = compra[0]
    _, pedido = borrador(compra)
    aprobar(entorno, pedido)
    tarea = publicar(entorno[1])[0][0]
    def intervenir():
        assert post(compra, pedido, "conciliar", cuerpo(pedido, "ENVIADO")).status_code == 409  # ENVIANDO
        assert publicar(entorno[1], datetime.now(timezone.utc) + timedelta(minutes=3))[1]["inciertos"] == 1
        assert post(compra, pedido, "conciliar", cuerpo(pedido, "ENVIADO")).status_code == 200
    # Se usa el envio_id del pedido aprobado para conciliar.
    pedido = entorno[0].get(f'/api/v1/pedidos/{pedido["id"]}', headers=entorno[2]).json()["datos"]
    fake = TelegramEnvio(entorno[1], al_enviar=intervenir)
    assert ejecutar_envio(*tarea, sesiones=entorno[1], cliente=fake)["estado"] == "OMITIDO"
    final = entorno[0].get(f'/api/v1/pedidos/{pedido["id"]}', headers=entorno[2]).json()["datos"]
    assert final["envio"]["message_id"] == 765 and len(fake.llamadas) == 1


def test_rollback_y_dos_conciliaciones_concurrentes(compra):
    entorno = compra[0]
    pedido, _ = fallar(compra)
    with entorno[1]() as sesion:
        usuario = sesion.scalar(select(Usuario.id).where(Usuario.correo == "admin@example.com"))
    def registrar(sesion, clave, accion="CONFIRMAR_NO_ENVIO"):
        return recuperar_envio(sesion, pedido["id"], accion=accion, clave=clave,
            envio_id=pedido["envio"]["id"], chat_id_revisado="123", evidencia="Revisión documentada y explícita del chat de prueba.",
            usuario_id=usuario, nombre_usuario="Fixture admin")
    with pytest.raises(RuntimeError), entorno[1].begin() as sesion:
        sesion.execute(text("UPDATE configuracion_inicial SET mensaje_error='rollback-fixture' WHERE id=1"))
        registrar(sesion, "rollback-fixture")
        raise RuntimeError("Consumidor falló")
    with entorno[1]() as sesion:
        assert sesion.get(PedidoCompra, pedido["id"]).estado == "PENDIENTE_VERIFICACION"
        assert sesion.scalar(select(func.count()).select_from(RecuperacionEnvio)) == 0
    if os.getenv("E03_POSTGRES_TEST") != "1": return
    def resolver(clave):
        try:
            with entorno[1].begin() as sesion: return registrar(sesion, clave).accion
        except ErrorAPI as error: return error.codigo
    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(resolver, ["concurrente-uno", "concurrente-dos"]))
    assert sorted(resultados) == ["CONFIRMAR_NO_ENVIO", "RECUPERACION_NO_PERMITIDA"]
    def retry(clave):
        try:
            with entorno[1].begin() as sesion: return registrar(sesion, clave, "REINTENTAR").accion
        except ErrorAPI as error: return error.codigo
    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(retry, ["retry-uno", "retry-dos"]))
    assert sorted(resultados) == ["INTENTO_CAMBIO", "REINTENTAR"]
    assert len(publicar(entorno[1])[0]) == 1


def test_clave_global_y_evidencia_telegram_no_reutilizable(compra):
    from test_planificacion_m02 import solicitar
    from test_compras_l02 import generar
    entorno = compra[0]
    pedido, _ = fallar(compra)
    datos = cuerpo(pedido, "ENVIADO")
    assert post(compra, pedido, "conciliar", datos).status_code == 200
    # Otra fecha permite una compra distinta, pero no apropiarse de la misma evidencia.
    from datetime import date
    from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion
    from app.modules.pronosticos.modelos import CorridaPronostico, Pronostico
    with entorno[1].begin() as sesion:
        anterior = sesion.get(CorridaPronostico, entorno[4])
        tarea_nueva = crear_o_recuperar_ejecucion(sesion, "GENERAR_PROPUESTA", "fixture-otra-fecha", {})
        corrida = CorridaPronostico(ejecucion_id=tarea_nueva.id, modelo_id=anterior.modelo_id,
            tipo="DEMO_PROGRAMADA", clave_ejecucion="fixture-otra-fecha", huella_datos_entrada="d"*64,
            fecha_objetivo=date(2022, 8, 25), estado="COMPLETADA")
        sesion.add(corrida); sesion.flush()
        for p in sesion.scalars(select(Pronostico).where(Pronostico.corrida_id == anterior.id)):
            sesion.add(Pronostico(corrida_id=corrida.id, producto_id=p.producto_id,
                estado=p.estado, cantidad_pronosticada=p.cantidad_pronosticada))
        corrida_id = corrida.id
    nuevo_entorno = (*entorno[:4], corrida_id, entorno[5])
    plan = solicitar(nuevo_entorno, clave="plan-otra-fecha").json()["datos"]
    otro = generar(entorno, plan["id"]).json()["datos"]["pedidos"][0]
    assert aprobar(entorno, otro, "decision-otra").status_code == 202
    tarea = publicar(entorno[1])[0][0]
    class Timeout(TelegramFalso):
        def enviar_mensaje(self, *_): return ResultadoEnvio("PENDIENTE_VERIFICACION", "TIMEOUT_FIXTURE", "Resultado incierto.")
    ejecutar_envio(*tarea, sesiones=entorno[1], cliente=Timeout())
    otro = entorno[0].get(f'/api/v1/pedidos/{otro["id"]}', headers=entorno[2]).json()["datos"]
    nueva = cuerpo(otro, "ENVIADO")
    assert post(compra, otro, "conciliar", nueva).status_code == 409  # clave del otro pedido
    nueva["clave_idempotencia"] = "evidencia-repetida"
    assert post(compra, otro, "conciliar", nueva).status_code == 409
    assert entorno[0].get(f'/api/v1/pedidos/{otro["id"]}', headers=entorno[2]).json()["datos"]["estado"] == "PENDIENTE_VERIFICACION"
    # Una respuesta tardía del worker que reutiliza ese mensaje tampoco acredita entrega.
    # El envío incierto mantiene el token anterior hasta una decisión humana.
    class EvidenciaRepetida(TelegramFalso):
        def enviar_mensaje(self, *_): return ResultadoEnvio("ENVIADO", message_id=765, fecha_telegram=datetime.now(timezone.utc))
    with entorno[1].begin() as sesion:
        envio = sesion.get(EnvioPedido, otro["envio"]["id"])
        envio.estado = sesion.get(PedidoCompra, otro["id"]).estado = "PENDIENTE_ENVIO"
    assert ejecutar_envio(*tarea, sesiones=entorno[1], cliente=EvidenciaRepetida())["estado"] == "PENDIENTE_VERIFICACION"


def test_reintento_automatico_conserva_modo_sin_aprobacion_ficticia(compra):
    entorno = compra[0]
    assert entorno[0].patch('/api/v1/negocios/actual', headers=entorno[2], json={"modo_envio_pedidos": "AUTOMATICO"}).status_code == 200
    _, pedido = borrador(compra)
    tarea = publicar(entorno[1])[0][0]
    fake = TelegramEnvio(entorno[1], ResultadoEnvio("FALLIDO", "PRUEBA_FALLO", "No enviado en fixture."))
    assert ejecutar_envio(*tarea, sesiones=entorno[1], cliente=fake)["estado"] == "FALLIDO"
    actual = entorno[0].get(f'/api/v1/pedidos/{pedido["id"]}', headers=entorno[2]).json()["datos"]
    respuesta = post(compra, actual, "reintentar", cuerpo(actual, None, "retry-auto"))
    assert respuesta.status_code == 202, respuesta.text
    assert respuesta.json()["datos"]["decision"] is None
    assert respuesta.json()["datos"]["modo_envio"] == "AUTOMATICO"
    assert respuesta.json()["datos"]["recuperaciones"][0]["accion"] == "REINTENTAR"
