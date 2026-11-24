"""Cierre del día: tickets de caja y tienda alimentan el historial que usa el modelo ML."""
from datetime import date, timedelta

import pytest
from sqlalchemy import func, select

from test_comercio_tienda import comercio, reservar, venta  # noqa: F401  (fixture reutilizada)
from test_entradas_productos import HOY, inv, cliente  # noqa: F401
from app.modules.productos.modelos import SkuProducto
from app.modules.productos.servicio import ORIGEN_BAKERY
from app.modules.ventas import cierre
from app.modules.ventas.modelos import ImportacionVenta, RevisionVenta, VentaDiaria
from app.modules.ventas.servicio import leer_historial

RUTA = "/api/v1/ventas/cierres"
DIA = HOY.date()


@pytest.fixture
def escenario(comercio, monkeypatch):
    monkeypatch.setattr(cierre, "ahora", lambda: HOY)
    (c, sesiones, admin, op, ids), cab, origen, lotes = comercio
    with sesiones.begin() as s:
        s.add(SkuProducto(producto_id=ids[0], origen=ORIGEN_BAKERY, sku_externo="PAN-QA"))
    return comercio


def venta_presencial(c, op, producto_id, cantidad, clave):
    cot = c.post("/api/v1/ventas/cotizaciones", headers=op, json={
        "clave_idempotencia": f"cot-{clave}", "lineas": [{"producto_id": producto_id, "cantidad": cantidad}]})
    assert cot.status_code == 201, cot.text
    q = cot.json()["datos"]
    r = c.post("/api/v1/ventas/tickets", headers=op, json={
        "clave_idempotencia": clave, "cotizacion_id": q["id"], "total_revisado": q["total"],
        "cobro_presencial": {"medio": "EFECTIVO", "importe_recibido": q["total"]}})
    assert r.status_code == 201, r.text
    return r.json()["datos"]


def fila(sesiones, producto_id):
    with sesiones() as s:
        return s.scalar(select(VentaDiaria).where(VentaDiaria.producto_id == producto_id,
                                                  VentaDiaria.fecha_local == DIA))


def test_tienda_y_caja_se_consolidan_y_el_modelo_las_lee(escenario):
    (c, sesiones, admin, op, ids), cab, _, _ = escenario
    r, body = reservar(escenario, 5)
    assert r.status_code == 201, r.text
    reserva = r.json()["datos"]

    # Una compra de la tienda en curso impide cerrar: quedaría fuera del día.
    pendiente = c.post(RUTA, headers=admin, json={"fecha": DIA.isoformat(), "jornada_terminada": True})
    assert pendiente.status_code == 409 and pendiente.json()["error"]["codigo"] == "RESERVAS_PENDIENTES"

    assert c.post("/api/v1/integracion-tienda/ventas", headers=cab, json=venta(escenario, reserva, body)).status_code == 201
    ticket = venta_presencial(c, op, ids[0], 2, "venta-cierre-001")
    assert fila(sesiones, ids[0]) is None  # Vender no escribe el historial: la jornada sigue abierta.

    abierta = c.post(RUTA, headers=admin, json={"fecha": DIA.isoformat()})
    assert abierta.status_code == 409 and abierta.json()["error"]["codigo"] == "JORNADA_ABIERTA"
    assert c.post(RUTA, headers=op, json={"fecha": DIA.isoformat(), "jornada_terminada": True}).status_code == 403

    r = c.post(RUTA, headers=admin, json={"fecha": DIA.isoformat(), "jornada_terminada": True})
    assert r.status_code == 200, r.text
    datos = r.json()["datos"]
    assert datos["unidades"] == 7 and datos["creadas"] == 1 and not datos["repetido"] and not datos["conflictos"]
    venta_dia = fila(sesiones, ids[0])
    assert venta_dia.unidades_vendidas == 7 and venta_dia.revision_actual == 1

    with sesiones() as s:
        historial = leer_historial(s, [ids[0]], DIA, DIA + timedelta(days=1))
    assert [(h.fecha_local, h.unidades_vendidas) for h in historial] == [(DIA, 7)]

    repetido = c.post(RUTA, headers=admin, json={"fecha": DIA.isoformat(), "jornada_terminada": True}).json()["datos"]
    assert repetido["repetido"] and repetido["cierre_id"] == datos["cierre_id"]
    with sesiones() as s:
        assert s.scalar(select(func.count()).select_from(RevisionVenta)) == 1

    # Anular después del cierre: un nuevo cierre crea otra revisión y conserva la anterior.
    anulada = c.post(f"/api/v1/ventas/tickets/{ticket['id']}/anular", headers=admin, json={
        "clave_idempotencia": "anular-cierre-001", "motivo": "Venta duplicada en caja", "mercancia_no_entregada": True})
    assert anulada.status_code == 200, anulada.text
    segundo = c.post(RUTA, headers=admin, json={"fecha": DIA.isoformat(), "jornada_terminada": True}).json()["datos"]
    assert segundo["actualizadas"] == 1 and segundo["unidades"] == 5
    venta_dia = fila(sesiones, ids[0])
    assert venta_dia.unidades_vendidas == 5 and venta_dia.revision_actual == 2
    with sesiones() as s:
        revisiones = s.scalars(select(RevisionVenta.unidades_vendidas).order_by(RevisionVenta.numero_revision)).all()
    assert revisiones == [7, 5]

    lista = c.get(RUTA, headers=op).json()
    assert lista["metadatos"]["hoy"] == DIA.isoformat() and [x["unidades"] for x in lista["datos"]] == [5, 7]


def test_no_sobrescribe_historial_importado_ni_cierra_el_futuro(escenario):
    (c, sesiones, admin, op, ids), _, _, _ = escenario
    with sesiones.begin() as s:
        imp = ImportacionVenta(origen="QA", clave_importacion="historial-qa", huella_contenido="x" * 64,
                               filas_aceptadas=1, estado="COMPLETADA")
        s.add(imp); s.flush()
        v = VentaDiaria(producto_id=ids[0], fecha_local=DIA, unidades_vendidas=40, importacion_id=imp.id, revision_actual=1)
        s.add(v); s.flush()
        s.add(RevisionVenta(venta_id=v.id, numero_revision=1, unidades_vendidas=40, origen_cambio="IMPORTACION",
                            motivo="Historial", importacion_id=imp.id))
    venta_presencial(c, op, ids[0], 2, "venta-conflicto-001")
    r = c.post(RUTA, headers=admin, json={"fecha": DIA.isoformat(), "jornada_terminada": True}).json()["datos"]
    assert r["creadas"] == 0 and r["conflictos"][0]["unidades_historial"] == 40
    assert fila(sesiones, ids[0]).unidades_vendidas == 40

    futuro = c.post(RUTA, headers=admin, json={"fecha": (DIA + timedelta(days=1)).isoformat(), "jornada_terminada": True})
    assert futuro.status_code == 422


def test_cierre_automatico_del_dia_anterior(escenario, monkeypatch):
    (c, sesiones, admin, op, ids), _, _, _ = escenario
    venta_presencial(c, op, ids[0], 3, "venta-automatica-001")
    with sesiones.begin() as s:
        assert cierre.cerrar_dia_anterior(s, instante=HOY).creadas == 0  # Ayer no hubo ventas.
    with sesiones.begin() as s:
        resultado = cierre.cerrar_dia_anterior(s, instante=HOY + timedelta(days=1))
    assert resultado.fecha == DIA and resultado.creadas == 1
    assert fila(sesiones, ids[0]).unidades_vendidas == 3
