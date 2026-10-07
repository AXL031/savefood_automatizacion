"""Plan y necesidades con snapshots de interfaces públicas, sin commit."""

import hashlib
import json
from dataclasses import asdict
from datetime import timezone
from decimal import Decimal, ROUND_CEILING

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.inventario.servicio import consultar_disponibilidad
from app.modules.planificacion.modelos import ElementoPlan, NecesidadIngrediente, PlanProduccion
from app.modules.productos.servicio import nombres_productos
from app.modules.pronosticos.servicio import obtener_corrida, obtener_pronosticos
from app.modules.recetas.servicio import recetas_activas


def _decimal(valor):
    if valor is None:
        return None
    numero = Decimal(valor).quantize(Decimal("0.001"), rounding=ROUND_CEILING)
    if numero < 0 or numero >= Decimal("1000000000000000"):
        raise ErrorAPI(422, "CANTIDAD_PLAN_FUERA_RANGO", "Una cantidad del plan supera el rango admitido.")
    return numero


def _json(valor):
    return json.loads(json.dumps(valor, default=str, sort_keys=True, ensure_ascii=False))


def generar_plan(sesion: Session, corrida_id: int, clave_ejecucion: str) -> PlanProduccion:
    """Misma clave y snapshots recuperan; otra clave conserva una revisión nueva."""
    if not clave_ejecucion or len(clave_ejecucion) > 128 or clave_ejecucion != clave_ejecucion.strip():
        raise ErrorAPI(422, "CLAVE_INVALIDA", "La clave del plan admite 1–128 caracteres sin espacios al inicio o final.")
    corrida = obtener_corrida(sesion, corrida_id, bloquear=True)
    pronosticos = obtener_pronosticos(sesion, corrida_id)
    if not pronosticos:
        raise ErrorAPI(409, "CORRIDA_SIN_PRONOSTICOS", "La corrida todavía no tiene pronósticos.")
    ids = [p.producto_id for p in pronosticos]
    nombres = nombres_productos(sesion, ids)
    recetas = recetas_activas(sesion, ids)
    ingredientes = {l.ingrediente_id for r in recetas.values() for l in r.lineas}
    stock = consultar_disponibilidad(sesion, corrida.fecha_objetivo, producto_ids=ids, ingrediente_ids=ingredientes)
    entrada = _json({
        "corrida_id": corrida.id, "modelo_id": corrida.modelo_id,
        "pronosticos": [{"id": p.id, "producto_id": p.producto_id, "estado": p.estado,
                         "cantidad": p.cantidad_pronosticada} for p in pronosticos],
        "recetas": {str(id_): asdict(r) for id_, r in sorted(recetas.items())},
        "stock": {"fecha": stock.fecha, "huella": stock.huella,
                  "items": [asdict(item) for item in stock.items]},
    })
    # Identidad de las recetas: el indicador activo/instante no cambia una versión.
    huella = hashlib.sha256(json.dumps(entrada, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    existente = sesion.scalar(select(PlanProduccion).where(PlanProduccion.clave_ejecucion == clave_ejecucion))
    if existente is not None:
        return _recuperar(existente, corrida.id, huella)

    elementos, omisiones, avisos, requeridos, datos_ingredientes = [], [], [], {}, {}
    for p in pronosticos:
        nombre = nombres.get(p.producto_id, f"Producto {p.producto_id}")
        receta = recetas.get(p.producto_id)
        disponible = stock.de("producto", p.producto_id)
        motivo = (p.estado if p.estado != "DISPONIBLE" else
                  "SIN_RECETA" if receta is None else
                  "STOCK_PRODUCTO_DESCONOCIDO" if disponible is None or not disponible.stock_conocido else None)
        if motivo:
            omisiones.append({"producto_id": p.producto_id, "producto": nombre, "motivo": motivo})
            continue
        cantidad_stock = int(disponible.cantidad_disponible)
        if cantidad_stock > 2_147_483_647:
            raise ErrorAPI(422, "CANTIDAD_PLAN_FUERA_RANGO", "El stock de producto supera el rango del plan.")
        producir = max(0, p.cantidad_pronosticada - cantidad_stock)
        elementos.append(dict(producto_id=p.producto_id, pronostico_id=p.id, receta_id=receta.receta_id,
                              cantidad_pronosticada=p.cantidad_pronosticada, stock_disponible=cantidad_stock,
                              cantidad_producir=producir, vigencia_stock_desconocida=disponible.vigencia_desconocida))
        if disponible.vigencia_desconocida:
            avisos.append(f"{nombre}: stock incluido con vigencia desconocida.")
        for linea in receta.lineas:
            requeridos[linea.ingrediente_id] = requeridos.get(linea.ingrediente_id, Decimal(0)) + producir * linea.cantidad_por_unidad
            datos_ingredientes[str(linea.ingrediente_id)] = {"nombre": linea.nombre, "codigo": linea.codigo, "unidad": linea.unidad_base}
    necesidades = []
    for id_, total in sorted(requeridos.items()):
        item = stock.de("ingrediente", id_)
        requerido = _decimal(total)
        conocido = item is not None and item.stock_conocido
        disponible = _decimal(item.cantidad_disponible) if conocido else None
        faltante = _decimal(max(Decimal(0), requerido - disponible)) if conocido else None
        desconocida = item.vigencia_desconocida if item else False
        nombre = datos_ingredientes[str(id_)]["nombre"]
        if not conocido:
            avisos.append(f"{nombre}: stock desconocido; faltante sin calcular.")
        elif desconocida:
            avisos.append(f"{nombre}: stock incluido con vigencia desconocida.")
        necesidades.append(dict(ingrediente_id=id_, cantidad_requerida=requerido, cantidad_disponible=disponible,
                                cantidad_faltante=faltante, unidad=datos_ingredientes[str(id_)]["unidad"],
                                stock_conocido=conocido, vigencia_stock_desconocida=desconocida))
    if omisiones:
        avisos.insert(0, "Las necesidades son parciales: hay productos sin cálculo de producción.")
    trazas = {**entrada, "nombres_productos": {str(k): v for k, v in nombres.items()},
              "ingredientes": datos_ingredientes, "omisiones": omisiones, "avisos": avisos}
    try:
        with sesion.begin_nested():
            plan = PlanProduccion(corrida_id=corrida.id, ejecucion_id=corrida.ejecucion_id,
                                  clave_ejecucion=clave_ejecucion, huella_stock_recetas=huella,
                                  fecha_objetivo=corrida.fecha_objetivo, stock_leido_en=stock.leido_en,
                                  estado="PROPUESTO", trazas_json=trazas)
            sesion.add(plan)
            sesion.flush()
            sesion.add_all(ElementoPlan(plan_id=plan.id, **e) for e in elementos)
            sesion.add_all(NecesidadIngrediente(plan_id=plan.id, **n) for n in necesidades)
            sesion.flush()
    except IntegrityError:
        existente = sesion.scalar(select(PlanProduccion).where(PlanProduccion.clave_ejecucion == clave_ejecucion))
        if existente is None:
            raise
        return _recuperar(existente, corrida.id, huella)
    return plan


def _recuperar(plan, corrida_id, huella):
    if plan.corrida_id != corrida_id or plan.huella_stock_recetas != huella:
        raise ErrorAPI(409, "CLAVE_REUTILIZADA", "La clave del plan pertenece a otra corrida, receta o lectura de stock. Usa otra clave para recalcular.")
    return plan


def obtener_necesidades(sesion: Session, plan_id: int) -> list[NecesidadIngrediente]:
    """Entrega M03 para compras; null nunca es faltante cero."""
    _buscar(sesion, plan_id)
    return list(sesion.scalars(select(NecesidadIngrediente).where(NecesidadIngrediente.plan_id == plan_id)
                               .order_by(NecesidadIngrediente.ingrediente_id)))


def _buscar(sesion, plan_id):
    plan = sesion.get(PlanProduccion, plan_id)
    if plan is None:
        raise ErrorAPI(404, "PLAN_NO_ENCONTRADO", "El plan no existe.")
    return plan


def _utc(valor):
    return (valor if valor.tzinfo is not None else valor.replace(tzinfo=timezone.utc)).isoformat()


def resumen_plan(plan):
    return {"id": plan.id, "corrida_id": plan.corrida_id, "ejecucion_id": plan.ejecucion_id,
            "fecha_objetivo": plan.fecha_objetivo.isoformat(), "clave_ejecucion": plan.clave_ejecucion,
            "huella_stock_recetas": plan.huella_stock_recetas, "stock_leido_en": _utc(plan.stock_leido_en),
            "creado_en": _utc(plan.creado_en), "estado": plan.estado, "margen_seguridad": 0}


def obtener_plan(sesion: Session, plan_id: int) -> dict:
    plan = _buscar(sesion, plan_id)
    trazas = plan.trazas_json
    elementos = list(sesion.scalars(select(ElementoPlan).where(ElementoPlan.plan_id == plan_id).order_by(ElementoPlan.producto_id)))
    return {**resumen_plan(plan), "elementos": [
        {"id": e.id, "producto_id": e.producto_id, "producto": trazas["nombres_productos"][str(e.producto_id)],
         "pronostico_id": e.pronostico_id, "receta_id": e.receta_id,
         "receta_version": trazas["recetas"][str(e.producto_id)]["version"],
         "cantidad_pronosticada": e.cantidad_pronosticada, "stock_disponible": e.stock_disponible,
         "cantidad_producir": e.cantidad_producir, "vigencia_stock_desconocida": e.vigencia_stock_desconocida}
        for e in elementos], "necesidades": [
        {"id": n.id, "ingrediente_id": n.ingrediente_id, "ingrediente": trazas["ingredientes"][str(n.ingrediente_id)]["nombre"],
         "cantidad_requerida": str(_decimal(n.cantidad_requerida)), "cantidad_disponible": None if n.cantidad_disponible is None else str(_decimal(n.cantidad_disponible)),
         "cantidad_faltante": None if n.cantidad_faltante is None else str(_decimal(n.cantidad_faltante)),
         "unidad": n.unidad, "stock_conocido": n.stock_conocido, "vigencia_stock_desconocida": n.vigencia_stock_desconocida}
        for n in obtener_necesidades(sesion, plan_id)], "omisiones": trazas["omisiones"], "avisos": trazas["avisos"], "trazas": trazas}


def listar_planes(sesion: Session, corrida_id: int | None = None) -> list[dict]:
    consulta = select(PlanProduccion)
    if corrida_id is not None:
        consulta = consulta.where(PlanProduccion.corrida_id == corrida_id)
    return [resumen_plan(p) for p in sesion.scalars(consulta.order_by(PlanProduccion.id.desc()).limit(50))]
