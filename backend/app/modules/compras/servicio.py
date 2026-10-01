"""L02/L03: snapshots, decisiones y reserva durable de envío en sesión compartida."""
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_CEILING, localcontext

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.negocios.servicio import obtener_modo_envio_pedidos
from app.modules.planificacion.servicio import obtener_contexto_compras
from app.modules.proveedores.servicio import ServicioProveedores
from .modelos import EnvioPedido, LineaPedido, PedidoCompra, PropuestaCompra, RecuperacionEnvio


ESTADOS_CANCELABLES = {"BLOQUEADO", "PENDIENTE_APROBACION", "RECHAZADO"}

ESTADOS_REPORTE = ("BLOQUEADO", "PENDIENTE_APROBACION", "CANCELADO", "RECHAZADO",
                   "PENDIENTE_ENVIO", "ENVIANDO", "ENVIADO", "FALLIDO", "PENDIENTE_VERIFICACION")


def periodo_propuestas(sesion: Session) -> tuple[date | None, date | None]:
    return sesion.execute(select(func.min(PropuestaCompra.fecha_objetivo),
                                 func.max(PropuestaCompra.fecha_objetivo))).one()


def resumen_pedidos(sesion: Session, desde: date, hasta: date) -> dict:
    """Estado actual por fecha objetivo; cuenta pedidos, no intentos de envío."""
    filtro = (PropuestaCompra.fecha_objetivo >= desde, PropuestaCompra.fecha_objetivo <= hasta)
    estados = dict(sesion.execute(select(PedidoCompra.estado, func.count(PedidoCompra.id))
        .join(PropuestaCompra, PropuestaCompra.id == PedidoCompra.propuesta_id)
        .where(*filtro).group_by(PedidoCompra.estado)).all())
    propuestas = dict(sesion.execute(select(PropuestaCompra.estado, func.count(PropuestaCompra.id))
        .where(*filtro).group_by(PropuestaCompra.estado)).all())
    sin_pedidos = sesion.scalar(select(func.count(PropuestaCompra.id)).where(*filtro,
        ~select(PedidoCompra.id).where(PedidoCompra.propuesta_id == PropuestaCompra.id).exists()))
    return {"total": sum(estados.values()),
            "por_estado": [{"estado": estado, "cantidad": estados.get(estado, 0)} for estado in ESTADOS_REPORTE],
            "propuestas": sum(propuestas.values()), "propuestas_sin_pedidos": sin_pedidos,
            "propuestas_por_estado": [{"estado": estado, "cantidad": propuestas.get(estado, 0)}
                                      for estado in ("GENERADA", "BLOQUEADA", "SIN_FALTANTES", "CANCELADA")]}


def _bloquear_fecha(sesion, fecha):
    if sesion.get_bind().dialect.name == "postgresql":
        sesion.execute(text("SELECT pg_advisory_xact_lock(734002, :dia)"), {"dia": fecha.toordinal()})


def estado_compras_del_plan(sesion: Session, plan_id: int) -> str:
    estado = sesion.scalar(select(PropuestaCompra.estado).where(PropuestaCompra.plan_id == plan_id))
    return estado or "PENDIENTE_GENERACION"


def _conflicto_fecha(sesion, fecha):
    anterior = sesion.scalar(select(PropuestaCompra).where(PropuestaCompra.fecha_objetivo == fecha, PropuestaCompra.activa.is_(True)))
    if anterior is not None:
        estados = set(sesion.scalars(select(PedidoCompra.estado).where(PedidoCompra.propuesta_id == anterior.id)))
        referencia = f"La fecha {fecha.isoformat()} ya tiene la propuesta #{anterior.id} del plan #{anterior.plan_id}."
        if "ENVIADO" in estados:
            detalle = "Su mensaje ya fue enviado a Telegram. No se puede cancelar para enviar otro pedido de la misma fecha. Consulta la confirmación en Pedidos y envíos; para una nueva prueba elige otra fecha del escenario histórico."
        elif estados - ESTADOS_CANCELABLES:
            detalle = "Tiene un envío autorizado o un intento registrado y no se puede cancelar. Consulta su estado en Pedidos y envíos antes de cualquier nueva compra; para otra prueba elige otra fecha del escenario histórico."
        else:
            detalle = "Todavía no se ha autorizado ningún envío. Cancélala explícitamente en Pedidos y envíos antes de usar otro plan de esta fecha."
        raise ErrorAPI(409, "RECOMPRA_FECHA", f"{referencia} {detalle}")


def _cantidades(faltante, oferta):
    with localcontext() as contexto:
        contexto.prec = 60
        # Dividir por factor*múltiplo conserva el techo exacto, incluso en cocientes periódicos.
        lotes = max(faltante / (oferta.factor_conversion * oferta.multiplo), oferta.minimo / oferta.multiplo)
        cantidad = (lotes.to_integral_value(rounding=ROUND_CEILING) * oferta.multiplo).quantize(Decimal("0.0001"))
        base = (cantidad * oferta.factor_conversion).quantize(Decimal("0.00000001"))
        if not 0 < cantidad < Decimal("10000000000000000") or not 0 < base < Decimal("10000000000000000000000"):
            raise ErrorAPI(422, "COMPRA_FUERA_DE_RANGO", "La conversión supera el rango de cantidades de compra.")
        return cantidad, base


def generar_pedidos(sesion: Session, plan_id: int, *, modo_envio: str | None = None) -> PropuestaCompra:
    entrada = obtener_contexto_compras(sesion, plan_id)
    fecha = date.fromisoformat(entrada["fecha_objetivo"])
    _bloquear_fecha(sesion, fecha)
    previo = sesion.scalar(select(PropuestaCompra).where(PropuestaCompra.plan_id == plan_id))
    if previo is not None:
        return previo
    modo = modo_envio or obtener_modo_envio_pedidos(sesion)
    if modo not in {"REQUIERE_APROBACION", "AUTOMATICO"}:
        raise ErrorAPI(422, "MODO_ENVIO_INVALIDO", "Modo de envío no admitido.")
    incidencias, grupos = [], {}
    if entrada["necesidades_estado"] != "CALCULADAS":
        incidencias.append({"codigo": "NECESIDADES_INCOMPLETAS", "detalle": "Falta producción calculable o stock conocido. Crear un plan corregido antes de comprar."})
        positivas = []
    else:
        positivas = [n for n in entrada["necesidades"] if Decimal(n["faltante"]) > 0]
    for n in positivas:
        oferta = ServicioProveedores(sesion).oferta_preferida_para_compras(n["ingrediente_id"])
        if oferta is None or not oferta.proveedor_activo:
            incidencias.append({"codigo": "SIN_PROVEEDOR", "ingrediente_id": n["ingrediente_id"], "nombre": n["stock"]["nombre"], "detalle": "Sin oferta preferida de proveedor activo."})
            continue
        cantidad, base = _cantidades(Decimal(n["faltante"]), oferta)
        grupo = grupos.setdefault(oferta.proveedor_id, {"proveedor": {"id": oferta.proveedor_id, "codigo": oferta.proveedor_codigo,
            "nombre": oferta.proveedor_nombre, "chat_id_pruebas": oferta.chat_id_pruebas,
            "destino_verificado": oferta.destino_verificado}, "lineas": [], "bloqueos": []})
        if not oferta.destino_verificado or not oferta.chat_id_pruebas:
            if "DESTINO_NO_VERIFICADO" not in grupo["bloqueos"]:
                grupo["bloqueos"].append("DESTINO_NO_VERIFICADO")
        grupo["lineas"].append({"necesidad_ingrediente_id": n["necesidad_id"], "oferta_ingrediente_id": oferta.oferta_id,
            "ingrediente_id": n["ingrediente_id"], "faltante_base": Decimal(n["faltante"]), "cantidad_compra": cantidad,
            "cantidad_base_pedida": base, "unidad_base": n["unidad_base"], "unidad_compra": oferta.unidad_compra,
            "oferta_json": oferta.model_dump(mode="json"), "ingrediente_json": n})
    sin_faltantes = not positivas and not incidencias
    if not sin_faltantes:
        _conflicto_fecha(sesion, fecha)
    bloqueada = bool(incidencias or any(g["bloqueos"] for g in grupos.values()))
    try:
        with sesion.begin_nested():
            propuesta = PropuestaCompra(plan_id=plan_id, fecha_objetivo=fecha, modo_envio=modo,
                estado="SIN_FALTANTES" if sin_faltantes else "BLOQUEADA" if bloqueada else "GENERADA",
                activa=not sin_faltantes, necesidades_json=entrada, incidencias_json=incidencias)
            sesion.add(propuesta); sesion.flush()
            for proveedor_id, grupo in sorted(grupos.items()):
                bloqueos = grupo["bloqueos"] + (["NECESIDADES_SIN_PROVEEDOR"] if incidencias else [])
                # Un bloqueo de cualquier proveedor bloquea el conjunto completo.
                if bloqueada and not bloqueos:
                    bloqueos = ["PROPUESTA_BLOQUEADA"]
                pedido = PedidoCompra(propuesta_id=propuesta.id, plan_id=plan_id, proveedor_id=proveedor_id,
                    proveedor_json=grupo["proveedor"], estado="BLOQUEADO" if bloqueos else "PENDIENTE_APROBACION",
                    modo_envio=modo, bloqueos_json=bloqueos)
                sesion.add(pedido); sesion.flush()
                sesion.add_all(LineaPedido(pedido_id=pedido.id, **linea) for linea in grupo["lineas"])
            sesion.flush()
            if modo == "AUTOMATICO" and not bloqueada and not sin_faltantes:
                # Preparar TODOS los envíos antes de reservar cualquiera. Sin red,
                # sin commit y sin decisiones administrativas ficticias.
                pedidos = list(sesion.scalars(select(PedidoCompra).where(PedidoCompra.propuesta_id == propuesta.id).order_by(PedidoCompra.id)))
                envios = []
                for pedido in pedidos:
                    try:
                        envios.append(_preparar_envio(sesion, pedido))
                    except ErrorAPI as error:
                        pedido.bloqueos_json = [error.codigo]
                        bloqueada = True
                if bloqueada:
                    propuesta.estado = "BLOQUEADA"
                    for pedido in pedidos:
                        pedido.estado = "BLOQUEADO"
                        if not pedido.bloqueos_json:
                            pedido.bloqueos_json = ["PROPUESTA_BLOQUEADA"]
                else:
                    for pedido in pedidos:
                        pedido.estado = "PENDIENTE_ENVIO"
                    sesion.add_all(envios)
                sesion.flush()
    except IntegrityError:
        previo = sesion.scalar(select(PropuestaCompra).where(PropuestaCompra.plan_id == plan_id))
        if previo is not None:
            return previo
        _conflicto_fecha(sesion, fecha)
        raise
    return propuesta


def detalle_pedido(sesion: Session, pedido_id: int) -> dict:
    pedido = sesion.get(PedidoCompra, pedido_id)
    if pedido is None:
        raise ErrorAPI(404, "PEDIDO_NO_ENCONTRADO", "El pedido no existe.")
    propuesta = sesion.get(PropuestaCompra, pedido.propuesta_id)
    envios = list(sesion.scalars(select(EnvioPedido).where(EnvioPedido.pedido_id == pedido.id).order_by(EnvioPedido.numero_intento)))
    envio = envios[-1] if envios else None
    def resumir(e):
        return {"id": e.id, "numero_intento": e.numero_intento, "estado": e.estado,
                "chat_id": e.chat_id, "message_id": e.message_id, "creado_en": e.creado_en.isoformat(),
                "inicio_en": e.inicio_en.isoformat() if e.inicio_en else None,
                "fin_en": e.fin_en.isoformat() if e.fin_en else None,
                "fecha_telegram": e.fecha_telegram.isoformat() if e.fecha_telegram else None,
                "codigo_error": e.codigo_error, "detalle_error": e.detalle_error}
    destino = ServicioProveedores(sesion).consultar_destino(pedido.proveedor_id)
    return {"id": pedido.id, "propuesta_id": pedido.propuesta_id, "plan_id": pedido.plan_id,
        "fecha_objetivo": propuesta.fecha_objetivo.isoformat(), "proveedor": pedido.proveedor_json,
        "estado": pedido.estado, "modo_envio": pedido.modo_envio, "bloqueos": pedido.bloqueos_json,
        "creado_en": pedido.creado_en.isoformat(), "envio_estado": envio.estado if envio else "SIN_ENVIO",
        "decision": {**pedido.decision_json, "usuario_id": pedido.decidido_por,
                     "fecha": pedido.decidido_en.isoformat()} if pedido.decision_json else None,
        "destino_actual": destino.model_dump(mode="json"),
        "mensaje": envio.texto if envio else construir_mensaje(sesion, pedido),
        "envio": resumir(envio) if envio else None,
        "envios": [resumir(e) for e in envios],
        "recuperaciones": [{"id": r.id, "envio_id": r.envio_id, "accion": r.accion,
            "usuario_id": r.usuario_id, "nombre_usuario": r.nombre_usuario, "fecha": r.creado_en.isoformat(),
            "evidencia": r.evidencia, "nuevo_envio_id": r.nuevo_envio_id,
            "resultado_anterior": r.resultado_anterior_json}
            for r in sesion.scalars(select(RecuperacionEnvio).join(EnvioPedido, RecuperacionEnvio.envio_id == EnvioPedido.id)
                .where(EnvioPedido.pedido_id == pedido.id).order_by(RecuperacionEnvio.id))],
        "lineas": [
            {"id": l.id, "necesidad_ingrediente_id": l.necesidad_ingrediente_id, "ingrediente_id": l.ingrediente_id,
             "nombre": l.ingrediente_json["stock"]["nombre"], "faltante_base": str(l.faltante_base),
             "cantidad_compra": str(l.cantidad_compra), "cantidad_base_pedida": str(l.cantidad_base_pedida),
             "unidad_base": l.unidad_base, "unidad_compra": l.unidad_compra, "oferta": l.oferta_json,
             "necesidad": l.ingrediente_json}
            for l in sesion.scalars(select(LineaPedido).where(LineaPedido.pedido_id == pedido.id).order_by(LineaPedido.ingrediente_id))]}


def detalle_propuesta(sesion: Session, propuesta_id: int) -> dict:
    propuesta = sesion.get(PropuestaCompra, propuesta_id)
    if propuesta is None:
        raise ErrorAPI(404, "PROPUESTA_NO_ENCONTRADA", "La propuesta no existe.")
    return {"id": propuesta.id, "plan_id": propuesta.plan_id, "fecha_objetivo": propuesta.fecha_objetivo.isoformat(),
        "estado": propuesta.estado, "activa": propuesta.activa, "modo_envio": propuesta.modo_envio,
        "necesidades": propuesta.necesidades_json, "incidencias": propuesta.incidencias_json,
        "creado_en": propuesta.creado_en.isoformat(), "motivo_cancelacion": propuesta.motivo_cancelacion,
        "cancelado_por": propuesta.cancelado_por, "cancelado_en": propuesta.cancelado_en.isoformat() if propuesta.cancelado_en else None,
        "pedidos": [detalle_pedido(sesion, id_) for id_ in sesion.scalars(select(PedidoCompra.id).where(PedidoCompra.propuesta_id == propuesta.id).order_by(PedidoCompra.id))]}


def listar_propuestas(sesion: Session, plan_id: int | None = None) -> list[dict]:
    consulta = select(PropuestaCompra.id)
    if plan_id is not None:
        consulta = consulta.where(PropuestaCompra.plan_id == plan_id)
    return [detalle_propuesta(sesion, id_) for id_ in sesion.scalars(consulta.order_by(PropuestaCompra.id.desc()).limit(50))]


def cancelar_propuesta(sesion: Session, propuesta_id: int, usuario_id: int, motivo: str) -> PropuestaCompra:
    motivo = motivo.strip()
    if not 1 <= len(motivo) <= 500:
        raise ErrorAPI(422, "MOTIVO_INVALIDO", "Indica un motivo de cancelación de hasta 500 caracteres.")
    propuesta = sesion.get(PropuestaCompra, propuesta_id)
    if propuesta is None:
        raise ErrorAPI(404, "PROPUESTA_NO_ENCONTRADA", "La propuesta no existe.")
    _bloquear_fecha(sesion, propuesta.fecha_objetivo)
    propuesta = sesion.scalar(select(PropuestaCompra).where(PropuestaCompra.id == propuesta_id).with_for_update().execution_options(populate_existing=True))
    if propuesta.estado == "CANCELADA":
        if propuesta.motivo_cancelacion != motivo:
            raise ErrorAPI(409, "CANCELACION_DIFERENTE", "La propuesta ya se canceló con otro motivo.")
        return propuesta
    pedidos = list(sesion.scalars(select(PedidoCompra).where(PedidoCompra.propuesta_id == propuesta_id).with_for_update()))
    if any(p.estado not in ESTADOS_CANCELABLES for p in pedidos):
        raise ErrorAPI(409, "PROPUESTA_NO_CANCELABLE", "Hay pedidos con aprobación o envío que requieren conciliación.")
    propuesta.estado, propuesta.activa = "CANCELADA", False
    propuesta.cancelado_en, propuesta.cancelado_por, propuesta.motivo_cancelacion = datetime.now(timezone.utc), usuario_id, motivo
    for pedido in pedidos:
        if pedido.estado != "RECHAZADO":
            pedido.estado = "CANCELADO"
    sesion.flush()
    return propuesta


def construir_mensaje(sesion: Session, pedido: PedidoCompra) -> str:
    """Texto plano reproducible desde snapshots, sin fragmentación ni datos futuros."""
    propuesta = sesion.get(PropuestaCompra, pedido.propuesta_id)
    def linea_texto(valor):
        return " ".join(str(valor).split())
    def cantidad_texto(valor, unidad):
        valor = Decimal(valor)
        if abs(valor) >= 1000 and unidad in {"g", "ml"}:
            with localcontext() as contexto:
                contexto.prec = 60
                valor /= 1000
            unidad = "kg" if unidad == "g" else "L"
        if unidad == "l": unidad = "L"
        numero = format(valor, "f")
        if "." in numero: numero = numero.rstrip("0").rstrip(".")
        return f"{numero.replace('.', ',')} {linea_texto(unidad)}"
    partes = ["DEMOSTRACIÓN — NO SURTIR", f"FoodSave · Pedido #{pedido.id}",
        f"Fecha del escenario: {propuesta.fecha_objetivo.isoformat()}",
        f"Proveedor simulado: {linea_texto(pedido.proveedor_json['nombre'])}", f"Plan de origen: #{pedido.plan_id}", "", "Insumos:"]
    for linea in sesion.scalars(select(LineaPedido).where(LineaPedido.pedido_id == pedido.id).order_by(LineaPedido.ingrediente_id)):
        partes.append(f"• {linea_texto(linea.ingrediente_json['stock']['nombre'])}: {cantidad_texto(linea.cantidad_compra, linea.unidad_compra)} "
                      f"(equivale a {cantidad_texto(linea.cantidad_base_pedida, linea.unidad_base)}; faltante {cantidad_texto(linea.faltante_base, linea.unidad_base)})")
    partes.extend(["", "Prueba universitaria con datos de escenario. No abastecer, cobrar ni despachar mercancía."])
    return "\n".join(partes)


def _bloquear_pedido(sesion: Session, pedido_id: int) -> tuple[PedidoCompra, PropuestaCompra]:
    pedido = sesion.get(PedidoCompra, pedido_id)
    if pedido is None:
        raise ErrorAPI(404, "PEDIDO_NO_ENCONTRADO", "El pedido no existe.")
    propuesta = sesion.get(PropuestaCompra, pedido.propuesta_id)
    _bloquear_fecha(sesion, propuesta.fecha_objetivo)
    propuesta = sesion.scalar(select(PropuestaCompra).where(PropuestaCompra.id == propuesta.id).with_for_update().execution_options(populate_existing=True))
    pedido = sesion.scalar(select(PedidoCompra).where(PedidoCompra.id == pedido_id).with_for_update().execution_options(populate_existing=True))
    return pedido, propuesta


def _preparar_envio(sesion: Session, pedido: PedidoCompra, *, chat_id_revisado: str | None = None) -> EnvioPedido:
    proveedores = ServicioProveedores(sesion)
    destino = proveedores.consultar_destino(pedido.proveedor_id, bloquear=True)
    if not destino.activo or not destino.destino_verificado or not destino.chat_id_pruebas:
        raise ErrorAPI(409, "DESTINO_NO_VERIFICADO", "El proveedor debe estar activo y su chat verificado con la credencial vigente.")
    if chat_id_revisado is not None and chat_id_revisado != destino.chat_id_pruebas:
        raise ErrorAPI(409, "DESTINO_CAMBIO", "El chat cambió desde tu revisión. Actualiza el pedido y revisa el nuevo destino.")
    texto = construir_mensaje(sesion, pedido)
    if len(texto.encode("utf-16-le")) // 2 > 4096:
        raise ErrorAPI(422, "MENSAJE_FUERA_DE_RANGO", "El pedido supera el tamaño de un mensaje de Telegram; reduce sus líneas antes de enviarlo.")
    return EnvioPedido(pedido_id=pedido.id, estado="PENDIENTE_ENVIO", chat_id=destino.chat_id_pruebas,
                       credencial_huella=proveedores.telegram.huella, texto=texto)


def decidir_pedido(sesion: Session, pedido_id: int, *, accion: str, clave: str,
                   usuario_id: int, nombre_usuario: str, motivo: str | None = None,
                   chat_id_revisado: str | None = None) -> PedidoCompra:
    clave = clave.strip()
    motivo = motivo.strip() if motivo is not None else None
    if accion not in {"APROBAR", "RECHAZAR"} or not 1 <= len(clave) <= 80 or (accion == "RECHAZAR" and (not motivo or len(motivo) > 500)):
        raise ErrorAPI(422, "DECISION_INVALIDA", "Indica una clave válida y un motivo de rechazo de hasta 500 caracteres.")
    pedido, propuesta = _bloquear_pedido(sesion, pedido_id)
    if pedido.clave_decision is not None:
        if pedido.clave_decision == clave and pedido.decidido_por == usuario_id and pedido.decision_json["accion"] == accion and pedido.decision_json.get("motivo") == motivo:
            if accion == "APROBAR":
                envio = sesion.scalar(select(EnvioPedido).where(EnvioPedido.pedido_id == pedido.id).order_by(EnvioPedido.numero_intento).limit(1))
                if envio.chat_id != chat_id_revisado:
                    raise ErrorAPI(409, "DECISION_DIFERENTE", "La decisión original corresponde a otro chat revisado.")
            return pedido
        raise ErrorAPI(409, "PEDIDO_YA_DECIDIDO", "El pedido ya tiene una decisión administrativa; consulta su evidencia.")
    if sesion.scalar(select(PedidoCompra.id).where(PedidoCompra.clave_decision == clave)) is not None:
        raise ErrorAPI(409, "CLAVE_DECISION_REUTILIZADA", "La clave corresponde a otro pedido.")
    estados_pedido = {"PENDIENTE_APROBACION", "BLOQUEADO"} if accion == "RECHAZAR" else {"PENDIENTE_APROBACION"}
    estados_propuesta = {"GENERADA", "BLOQUEADA"} if accion == "RECHAZAR" else {"GENERADA"}
    if not propuesta.activa or pedido.estado not in estados_pedido or propuesta.estado not in estados_propuesta:
        raise ErrorAPI(409, "PEDIDO_NO_DECIDIBLE", "Revisa los bloqueos y el estado de la propuesta antes de decidir.")
    envio = None
    if accion == "APROBAR":
        if pedido.modo_envio != "REQUIERE_APROBACION":
            raise ErrorAPI(409, "AUTOMATICO_PENDIENTE_PASO7", "El modo automático se verificará en el paso 7.")
        if chat_id_revisado is None:
            raise ErrorAPI(409, "DESTINO_CAMBIO", "Revisa el chat antes de aprobar.")
        envio = _preparar_envio(sesion, pedido, chat_id_revisado=chat_id_revisado)
    try:
        with sesion.begin_nested():
            pedido.clave_decision = clave
            pedido.decidido_por = usuario_id
            pedido.decidido_en = datetime.now(timezone.utc)
            pedido.decision_json = {"accion": accion, "nombre_usuario": nombre_usuario, "motivo": motivo}
            pedido.estado = "PENDIENTE_ENVIO" if envio else "RECHAZADO"
            if envio is not None:
                sesion.add(envio)
            sesion.flush()
    except IntegrityError:
        raise ErrorAPI(409, "CLAVE_DECISION_REUTILIZADA", "La decisión ya fue registrada o su clave corresponde a otro pedido.") from None
    return pedido


def verificar_destinos_propuesta(sesion: Session, propuesta_id: int) -> PropuestaCompra:
    propuesta = sesion.get(PropuestaCompra, propuesta_id)
    if propuesta is None:
        raise ErrorAPI(404, "PROPUESTA_NO_ENCONTRADA", "La propuesta no existe.")
    _bloquear_fecha(sesion, propuesta.fecha_objetivo)
    propuesta = sesion.scalar(select(PropuestaCompra).where(PropuestaCompra.id == propuesta.id).with_for_update().execution_options(populate_existing=True))
    pedidos = list(sesion.scalars(select(PedidoCompra).where(PedidoCompra.propuesta_id == propuesta.id).order_by(PedidoCompra.id).with_for_update().execution_options(populate_existing=True)))
    if not propuesta.activa or any(p.decision_json is not None or p.estado not in {"BLOQUEADO", "PENDIENTE_APROBACION"} for p in pedidos):
        raise ErrorAPI(409, "PROPUESTA_NO_REVALIDABLE", "Solo se pueden revisar destinos antes de tomar decisiones.")
    bloqueada = bool(propuesta.incidencias_json)
    for pedido in pedidos:
        destino = ServicioProveedores(sesion).consultar_destino(pedido.proveedor_id, bloquear=True)
        bloqueos = [b for b in pedido.bloqueos_json if b not in {"DESTINO_NO_VERIFICADO", "PROVEEDOR_INACTIVO", "PROPUESTA_BLOQUEADA"}]
        if not destino.activo: bloqueos.append("PROVEEDOR_INACTIVO")
        if not destino.destino_verificado or not destino.chat_id_pruebas: bloqueos.append("DESTINO_NO_VERIFICADO")
        # Un pedido automático bloqueado requiere una nueva propuesta explícita;
        # revisar destinos nunca debe generar un envío externo por sorpresa.
        if pedido.modo_envio == "AUTOMATICO" and "AUTOMATICO_REQUIERE_NUEVO_PLAN" not in bloqueos:
            bloqueos.append("AUTOMATICO_REQUIERE_NUEVO_PLAN")
        pedido.bloqueos_json = bloqueos
        bloqueada = bloqueada or bool(bloqueos)
    for pedido in pedidos:
        if bloqueada and not pedido.bloqueos_json:
            pedido.bloqueos_json = ["PROPUESTA_BLOQUEADA"]
        pedido.estado = "BLOQUEADO" if bloqueada else "PENDIENTE_APROBACION"
    propuesta.estado = "BLOQUEADA" if bloqueada else "GENERADA"
    sesion.flush()
    return propuesta
