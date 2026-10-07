"""Frontera M02; el llamador conserva el control de la transacción."""
import hashlib
import json
import re
from dataclasses import asdict
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_CEILING, localcontext

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.inventario.servicio import consultar_disponibilidad
from app.modules.planificacion.modelos import ElementoPlan, PlanProduccion, NecesidadIngrediente
from app.modules.pronosticos.servicio import consultar_corrida, obtener_pronosticos
from app.modules.recetas.servicio import recetas_activas

VERSION_CALCULO = "m02-v1"


def _json(datos):
    def convertir(valor):
        if isinstance(valor, (date, datetime)):
            return valor.isoformat()
        if isinstance(valor, Decimal):
            return str(valor)
        raise TypeError(f"Tipo no admitido: {type(valor)}")
    return json.loads(json.dumps(datos, default=convertir, sort_keys=True, allow_nan=False))


def _receta(receta):
    if receta is None:
        return None
    return _json({"receta_id": receta.receta_id, "version": receta.version,
                  "lineas": [asdict(l) for l in sorted(receta.lineas, key=lambda l: l.ingrediente_id)]})


def _existente(sesion, clave, corrida_id, huella):
    plan = sesion.scalar(select(PlanProduccion).where(PlanProduccion.clave_ejecucion == clave))
    if plan is not None and (plan.corrida_id != corrida_id or plan.huella_stock_recetas != huella):
        raise ErrorAPI(409, "CLAVE_REUTILIZADA", "La clave del plan corresponde a otra corrida, receta o lectura de stock. Usa una nueva clave para recalcular.")
    return plan


def generar_plan(sesion: Session, *, corrida_id: int, clave_ejecucion: str) -> PlanProduccion:
    """Guarda la propuesta, incluyendo productos impedidos. Sin commit ni movimiento."""
    if not isinstance(clave_ejecucion, str) or re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", clave_ejecucion) is None:
        raise ErrorAPI(422, "CLAVE_INVALIDA", "La clave admite 1–128 letras, números, puntos, guiones y dos puntos.")
    corrida = consultar_corrida(sesion, corrida_id, bloquear=True)
    pronosticos = obtener_pronosticos(sesion, corrida_id)
    if not pronosticos:
        raise ErrorAPI(422, "CORRIDA_SIN_PRODUCTOS", "La corrida no contiene productos para planificar.")
    ids = [p.producto_id for p in pronosticos]
    recetas = recetas_activas(sesion, ids)
    disponibilidad = consultar_disponibilidad(sesion, corrida.fecha_objetivo, tipo="producto", producto_ids=ids)
    origen = _json(asdict(corrida))
    elementos = []
    for p in pronosticos:
        if p.estado == "DISPONIBLE" and (p.cantidad_pronosticada is None or p.cantidad_pronosticada < 0):
            raise ErrorAPI(422, "PRONOSTICO_INVALIDO", "El pronóstico disponible necesita una cantidad no negativa.")
        receta = _receta(recetas.get(p.producto_id))
        item = disponibilidad.de("producto", p.producto_id)
        if item is None:
            raise ErrorAPI(422, "STOCK_INVALIDO", "El inventario no devolvió el producto de la corrida.")
        stock = _json(asdict(item))
        stock["lotes"].sort(key=lambda l: l["lote_id"])
        cantidad_stock = int(item.cantidad_disponible) if item.cantidad_disponible is not None else None
        if cantidad_stock is not None and not 0 <= cantidad_stock <= 2_147_483_647:
            raise ErrorAPI(422, "STOCK_FUERA_DE_RANGO", "El stock agregado supera el rango de unidades del plan.")
        avisos = []
        if p.estado != "DISPONIBLE":
            avisos.append(p.estado)
        if receta is None:
            avisos.append("SIN_RECETA")
        if cantidad_stock is None:
            avisos.append("STOCK_DESCONOCIDO")
        if item.vigencia_desconocida:
            avisos.append("VIGENCIA_STOCK_DESCONOCIDA")
        if any(not l.cuenta for l in item.lotes):
            avisos.append("LOTES_EXCLUIDOS")
        estado = (p.estado if p.estado != "DISPONIBLE" else "SIN_RECETA" if receta is None
                  else "STOCK_DESCONOCIDO" if cantidad_stock is None else "CALCULADO")
        cantidad = max(0, p.cantidad_pronosticada - cantidad_stock) if estado == "CALCULADO" else None
        elementos.append({"producto_id": p.producto_id, "pronostico_id": p.id,
                          "receta_id": receta["receta_id"] if receta else None,
                          "cantidad_pronosticada": p.cantidad_pronosticada,
                          "stock_disponible": cantidad_stock, "cantidad_producir": cantidad,
                          "estado": estado, "receta_json": receta, "stock_json": stock,
                          "avisos_json": avisos})
    huella = hashlib.sha256(json.dumps({"version": VERSION_CALCULO, "origen": origen,
                                       "elementos": elementos}, sort_keys=True, separators=(",", ":"))
                            .encode("utf-8")).hexdigest()
    if previo := _existente(sesion, clave_ejecucion, corrida_id, huella):
        calcular_necesidades(sesion, previo.id, verificar_entrada=True)
        return previo
    try:
        with sesion.begin_nested():
            plan = PlanProduccion(corrida_id=corrida_id, ejecucion_id=corrida.ejecucion_id,
                                  clave_ejecucion=clave_ejecucion, huella_stock_recetas=huella,
                                  fecha_objetivo=corrida.fecha_objetivo, stock_leido_en=disponibilidad.leido_en,
                                  estado="PROPUESTO", version_calculo=VERSION_CALCULO,
                                  origen_pronostico_json=origen)
            sesion.add(plan)
            sesion.flush()
            sesion.add_all(ElementoPlan(plan_id=plan.id, **e) for e in elementos)
            sesion.flush()
            calcular_necesidades(sesion, plan.id)
    except IntegrityError:
        previo = _existente(sesion, clave_ejecucion, corrida_id, huella)
        if previo is None:
            raise
        return previo
    return plan


def _resumen(plan: PlanProduccion, sesion: Session) -> dict:
    from app.modules.compras.servicio import estado_compras_del_plan
    def hora(fecha):
        utc = fecha.replace(tzinfo=timezone.utc) if fecha.tzinfo is None else fecha.astimezone(timezone.utc)
        return utc.isoformat()
    return {"id": plan.id, "corrida_id": plan.corrida_id, "ejecucion_id": plan.ejecucion_id,
            "clave_ejecucion": plan.clave_ejecucion, "fecha_objetivo": plan.fecha_objetivo.isoformat(),
            "estado": plan.estado, "version_calculo": plan.version_calculo,
            "huella_stock_recetas": plan.huella_stock_recetas,
            "stock_leido_en": hora(plan.stock_leido_en), "creado_en": hora(plan.creado_en),
            "origen_pronostico": plan.origen_pronostico_json,
            "necesidades_estado": plan.necesidades_estado, "pedidos_estado": estado_compras_del_plan(sesion, plan.id)}


def listar_planes(sesion: Session, corrida_id: int | None = None) -> list[dict]:
    consulta = select(PlanProduccion)
    if corrida_id is not None:
        consulta = consulta.where(PlanProduccion.corrida_id == corrida_id)
    return [_resumen(p, sesion) for p in sesion.scalars(consulta.order_by(PlanProduccion.id.desc()).limit(50))]


def detalle_plan(sesion: Session, plan_id: int) -> dict:
    """Solo los snapshots guardados; cambios posteriores no alteran el detalle."""
    plan = sesion.get(PlanProduccion, plan_id)
    if plan is None:
        raise ErrorAPI(404, "PLAN_NO_ENCONTRADO", "El plan no existe.")
    resultado = _resumen(plan, sesion)
    resultado["elementos"] = [{"producto_id": e.producto_id, "pronostico_id": e.pronostico_id,
                              "cantidad_pronosticada": e.cantidad_pronosticada,
                              "stock_disponible": e.stock_disponible, "cantidad_producir": e.cantidad_producir,
                              "estado": e.estado, "avisos": e.avisos_json,
                              "receta": e.receta_json, "stock": e.stock_json}
                             for e in sesion.scalars(select(ElementoPlan).where(ElementoPlan.plan_id == plan_id)
                                                    .order_by(ElementoPlan.producto_id))]
    resultado.update(obtener_necesidades(sesion, plan_id))
    return resultado


def calcular_necesidades(sesion: Session, plan_id: int, *, verificar_entrada: bool = False) -> PlanProduccion:
    """Completa una vez el plan. Comparar entradas solo al reutilizar su clave."""
    plan = sesion.scalar(select(PlanProduccion).where(PlanProduccion.id == plan_id).with_for_update())
    if plan is None:
        raise ErrorAPI(404, "PLAN_NO_ENCONTRADO", "El plan no existe.")
    if plan.necesidades_estado != "PENDIENTE_M03" and not verificar_entrada:
        return plan
    grupos, excluidos = {}, []
    with localcontext() as contexto:
        contexto.prec = 50
        for e in sesion.scalars(select(ElementoPlan).where(ElementoPlan.plan_id == plan_id).order_by(ElementoPlan.producto_id)):
            if e.estado != "CALCULADO":
                excluidos.append({"producto_id": e.producto_id, "nombre": e.stock_json["nombre"], "estado": e.estado})
                continue
            for linea in e.receta_json["lineas"]:
                ingrediente_id, unidad = linea["ingrediente_id"], linea["unidad_base"]
                grupo = grupos.setdefault(ingrediente_id, {"unidad": unidad, "total": Decimal(0), "aportes": []})
                if grupo["unidad"] != unidad:
                    raise ErrorAPI(422, "UNIDAD_INCOMPATIBLE", "Las recetas conservadas usan unidades incompatibles.")
                aporte = Decimal(linea["cantidad_por_unidad"]) * e.cantidad_producir
                grupo["total"] += aporte
                grupo["aportes"].append({"producto_id": e.producto_id, "receta_id": e.receta_id,
                    "version_receta": e.receta_json["version"], "cantidad_producir": e.cantidad_producir,
                    "cantidad_por_unidad": linea["cantidad_por_unidad"], "aporte": str(aporte)})
        stock = consultar_disponibilidad(sesion, plan.fecha_objetivo, tipo="ingrediente", ingrediente_ids=sorted(grupos))
        filas = []
        for ingrediente_id, grupo in sorted(grupos.items()):
            item = stock.de("ingrediente", ingrediente_id)
            if item is None or item.unidad != grupo["unidad"]:
                raise ErrorAPI(422, "UNIDAD_INCOMPATIBLE", "La unidad del inventario debe coincidir con la receta conservada.")
            necesaria = grupo["total"].quantize(Decimal("0.001"), rounding=ROUND_CEILING)
            disponible = item.cantidad_disponible
            if necesaria < 0 or necesaria >= Decimal("100000000000") or (disponible is not None and not 0 <= disponible < Decimal("100000000000")):
                raise ErrorAPI(422, "NECESIDAD_FUERA_DE_RANGO", "Las cantidades de ingredientes superan el rango admitido.")
            snapshot = _json(asdict(item))
            snapshot["lotes"].sort(key=lambda lote: lote["lote_id"])
            filas.append({"ingrediente_id": ingrediente_id, "unidad_base": grupo["unidad"],
                "cantidad_necesaria": necesaria, "stock_disponible": disponible,
                "faltante": max(Decimal(0), necesaria - disponible) if disponible is not None else None,
                "estado": "DISPONIBLE" if disponible is not None else "STOCK_DESCONOCIDO",
                "aportes_json": grupo["aportes"], "stock_json": snapshot})
    huella = hashlib.sha256(json.dumps(_json({"version": "m03-v1", "filas": filas, "excluidos": excluidos}), sort_keys=True).encode()).hexdigest()
    if plan.necesidades_estado != "PENDIENTE_M03":
        if plan.necesidades_meta_json["huella"] != huella:
            raise ErrorAPI(409, "CLAVE_REUTILIZADA", "Cambió el stock de ingredientes. Usa una nueva clave para conservar otro cálculo.")
        return plan
    sesion.add_all(NecesidadIngrediente(plan_id=plan.id, **fila) for fila in filas)
    plan.necesidades_estado = "INCOMPLETAS" if excluidos or any(f["estado"] != "DISPONIBLE" for f in filas) else "CALCULADAS"
    plan.necesidades_meta_json = {"version": "m03-v1", "huella": huella, "stock_leido_en": stock.leido_en.isoformat(),
        "productos_excluidos": excluidos, "vigencia_desconocida": any(f["stock_json"]["vigencia_desconocida"] for f in filas)}
    sesion.flush()
    return plan


def obtener_necesidades(sesion: Session, plan_id: int) -> dict:
    """Frontera pública M03: solo snapshots; Compras debe exigir CALCULADAS."""
    plan = sesion.get(PlanProduccion, plan_id)
    if plan is None:
        raise ErrorAPI(404, "PLAN_NO_ENCONTRADO", "El plan no existe.")
    return {"necesidades_estado": plan.necesidades_estado, "necesidades_meta": plan.necesidades_meta_json,
        "necesidades": [_json({"ingrediente_id": n.ingrediente_id, "unidad_base": n.unidad_base,
            "cantidad_necesaria": n.cantidad_necesaria, "stock_disponible": n.stock_disponible,
            "faltante": n.faltante, "estado": n.estado, "aportes": n.aportes_json, "stock": n.stock_json})
            for n in sesion.scalars(select(NecesidadIngrediente).where(NecesidadIngrediente.plan_id == plan_id).order_by(NecesidadIngrediente.ingrediente_id))]}


def obtener_contexto_compras(sesion: Session, plan_id: int) -> dict:
    """Entrega pública M03→L02 con IDs de necesidades y fecha; bloquea el plan."""
    plan = sesion.scalar(select(PlanProduccion).where(PlanProduccion.id == plan_id).with_for_update())
    if plan is None:
        raise ErrorAPI(404, "PLAN_NO_ENCONTRADO", "El plan no existe.")
    datos = obtener_necesidades(sesion, plan_id)
    ids = {n.ingrediente_id: n.id for n in sesion.scalars(select(NecesidadIngrediente).where(NecesidadIngrediente.plan_id == plan_id))}
    return {"plan_id": plan_id, "fecha_objetivo": plan.fecha_objetivo.isoformat(), **datos,
            "necesidades": [{**n, "necesidad_id": ids[n["ingrediente_id"]]} for n in datos["necesidades"]]}
