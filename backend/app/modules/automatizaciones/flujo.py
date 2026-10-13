"""Configuración reutilizable y diagnóstico del recorrido histórico."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.core.errores import ErrorAPI
from app.modules.automatizaciones.esquemas import ConfigurarFlujo, ProgramarFlujo
from app.modules.automatizaciones.modelos import ConfiguracionFlujo, EjecucionAutomatizacion, IntentoAutomatizacion, ProgramacionDemo
from app.modules.automatizaciones.servicio import programar_ejecucion
from app.modules.negocios.servicio import zona_horaria_negocio
from app.modules.productos.servicio import productos_activos, listar_skus_bakery
from app.modules.pronosticos.servicio import modelo_listo
from app.modules.recetas.servicio import recetas_activas
from app.modules.inventario.servicio import consultar_disponibilidad
from app.modules.ingredientes.servicio import obtener_ingredientes
from app.modules.proveedores.servicio import ServicioProveedores
from app.modules.compras.servicio import fechas_con_compra_activa


def guardar_configuracion(sesion, datos, usuario_id):
    config = sesion.scalar(select(ConfiguracionFlujo).where(ConfiguracionFlujo.id == 1).with_for_update())
    if not config:
        config = ConfiguracionFlujo(id=1)
        sesion.add(config)
    config.parametros = datos.model_dump(mode="json")
    config.actualizado_por, config.actualizado_en = usuario_id, datetime.now(timezone.utc)
    sesion.flush()
    return config.parametros


def comprobar(sesion: Session, datos: ConfigurarFlujo) -> dict:
    requisitos = []
    def requisito(titulo, listo, motivo, enlace):
        requisitos.append({"titulo": titulo, "listo": bool(listo), "motivo": motivo, "enlace": enlace})
    nombres = productos_activos(sesion, datos.producto_ids)
    reservadas = fechas_con_compra_activa(sesion, datos.fecha_objetivo_demo, datos.fecha_objetivo_demo + timedelta(days=datos.dias - 1))
    requisito("Fechas disponibles para compras", not reservadas,
              "Ya hay compras activas para: " + ", ".join(reservadas) if reservadas else "El calendario no repite una fecha con compra activa.", "/compras")
    sku = listar_skus_bakery(sesion)
    requisito("Productos", len(nombres) == len(datos.producto_ids) and all(i in sku for i in datos.producto_ids),
              "Todos deben estar activos y tener un código de ventas compatible.", "/productos")
    modelo = None
    try:
        modelo = modelo_listo(sesion, datos.modelo_id)
        inicio, fin = modelo.particion_json["inicio_prueba"], modelo.particion_json["fin_prueba"]
        ultimo = datos.fecha_objetivo_demo + timedelta(days=datos.dias - 1)
        requisito("Modelo y fechas", inicio <= datos.fecha_objetivo_demo.isoformat() <= ultimo.isoformat() <= fin
                  and datos.fecha_objetivo_demo > modelo.fecha_corte_entrenamiento,
                  f"Modelo {modelo.version_modelo}. Fechas disponibles: {inicio} a {fin}.", "/pronosticos")
    except (ErrorAPI, KeyError):
        requisito("Modelo y fechas", False, "Prepara un modelo con su período de prueba reservado.", "/inicializacion")
    recetas = recetas_activas(sesion, datos.producto_ids)
    for producto_id in datos.producto_ids:
        requisito(f"Receta de {nombres.get(producto_id, 'producto seleccionado')}", producto_id in recetas,
                  "Se necesita una receta vigente para calcular ingredientes.", "/recetas")
    ids_ingredientes = sorted({linea.ingrediente_id for receta in recetas.values() for linea in receta.lineas})
    ingredientes = obtener_ingredientes(sesion, ids_ingredientes)
    proveedores = ServicioProveedores(sesion)
    for ingrediente_id in ids_ingredientes:
        ingrediente = ingredientes.get(ingrediente_id)
        oferta = proveedores.oferta_preferida_para_compras(ingrediente_id)
        nombre = ingrediente.nombre if ingrediente else f"Ingrediente #{ingrediente_id}"
        requisito(f"Oferta de {nombre}", ingrediente and ingrediente.activo and oferta and oferta.proveedor_activo,
                  "Configura una oferta preferida activa con su presentación y contenido.", "/proveedores")
        if oferta:
            requisito(f"Telegram de {oferta.proveedor_nombre}", oferta.destino_verificado,
                      "Vincula y verifica tu chat propio para poder enviar los pedidos.", "/proveedores")
    stock = consultar_disponibilidad(sesion, datos.fecha_objetivo_demo,
                                     producto_ids=datos.producto_ids, ingrediente_ids=ids_ingredientes)
    for item in stock.items:
        requisito(f"Stock de {item.nombre}", item.stock_conocido,
                  "Registra un lote; cero explícito es válido, ausencia no equivale a cero.", "/inventario")
    return {"listo": all(r["listo"] for r in requisitos), "requisitos": requisitos,
            "modelo_id": modelo.id if modelo else None,
            "productos": [nombres.get(i, f"#{i}") for i in datos.producto_ids]}


def _hora_utc(local, zona):
    candidatos = {local.replace(tzinfo=zona, fold=fold).astimezone(timezone.utc) for fold in (0, 1)
                  if local.replace(tzinfo=zona, fold=fold).astimezone(timezone.utc).astimezone(zona).replace(tzinfo=None) == local}
    if len(candidatos) != 1:
        raise ErrorAPI(422, "HORARIO_AMBIGUO", "Ese horario no existe o se repite en la zona del negocio. Elige otro.")
    return candidatos.pop()


def programar_flujo(sesion, datos: ProgramarFlujo, usuario_id):
    solicitud = datos.model_dump(mode="json")
    claves = [f"{datos.clave_idempotencia}-{dia}" for dia in range(datos.dias)]
    anteriores = list(sesion.scalars(select(ProgramacionDemo).where(ProgramacionDemo.clave_idempotencia.in_(claves)).order_by(ProgramacionDemo.id)))
    if anteriores:
        if len(anteriores) != datos.dias or any(p.parametros_json.get("solicitud_flujo") != solicitud for p in anteriores):
            raise ErrorAPI(409, "CLAVE_REUTILIZADA", "Esta solicitud pertenece a otro calendario.")
        return anteriores
    if datos.modo_envio_pedidos == "AUTOMATICO" and not datos.autorizar_envio:
        raise ErrorAPI(422, "ENVIO_NO_AUTORIZADO", "Confirma el envío a tu chat propio de pruebas.")
    diagnostico = comprobar(sesion, datos)
    if not diagnostico["listo"]:
        raise ErrorAPI(409, "FLUJO_INCOMPLETO", "Corrige los requisitos pendientes antes de programar.")
    zona = ZoneInfo(zona_horaria_negocio(sesion))
    resultado = []
    for dia in range(datos.dias):
        objetivo = datos.fecha_objetivo_demo + timedelta(days=dia)
        horario = _hora_utc(datos.primera_ejecucion_local + timedelta(days=dia), zona)
        resultado.append(programar_ejecucion(sesion, tipo="GENERAR_PROPUESTA", ejecutar_desde_utc=horario,
            fecha_hora_simulada_local=datetime.combine(objetivo, datos.hora_simulada),
            parametros={"fecha_objetivo_demo": objetivo.isoformat(), "producto_ids": datos.producto_ids,
                        "modelo_id": diagnostico["modelo_id"], "modo_envio_pedidos": datos.modo_envio_pedidos,
                        "solicitud_flujo": solicitud}, clave_idempotencia=claves[dia], creado_por=usuario_id))
    return resultado


def gestionar(sesion, programacion_id, usuario_id, motivo, *, accion=None, horario=None):
    # El motor reclama primero la ejecución. Mantener ese orden también en API.
    ejecucion = sesion.scalar(select(EjecucionAutomatizacion).where(
        EjecucionAutomatizacion.programacion_id == programacion_id).with_for_update().execution_options(populate_existing=True))
    programacion = sesion.scalar(select(ProgramacionDemo).where(ProgramacionDemo.id == programacion_id)
                               .with_for_update().execution_options(populate_existing=True))
    if not programacion or not ejecucion:
        raise ErrorAPI(404, "PROGRAMACION_NO_ENCONTRADA", "Programación no encontrada.")
    destino = {"PAUSAR": "PAUSADA", "REANUDAR": "PROGRAMADA", "CANCELAR": "CANCELADA"}.get(accion)
    if destino and programacion.estado == destino:
        return programacion
    if (programacion.tipo != "GENERAR_PROPUESTA" or programacion.estado not in ("PROGRAMADA", "PAUSADA")
            or ejecucion.estado != "PENDIENTE" or ejecucion.token_despacho or ejecucion.lease_hasta
            or sesion.scalar(select(func.count()).select_from(IntentoAutomatizacion).where(IntentoAutomatizacion.ejecucion_id == ejecucion.id))):
        raise ErrorAPI(409, "TAREA_YA_INICIADA", "Esta tarea ya fue despachada o finalizada y conserva su resultado.")
    ahora = datetime.now(timezone.utc)
    vigente = programacion.ejecutar_desde_utc
    vigente = vigente.replace(tzinfo=timezone.utc) if vigente.tzinfo is None else vigente
    if (horario is not None and horario <= ahora) or (accion == "REANUDAR" and vigente <= ahora):
        raise ErrorAPI(422, "HORA_NO_FUTURA", "Elige un horario futuro antes de continuar.")
    cambio = {"accion": accion or "REPROGRAMAR", "usuario_id": usuario_id, "motivo": motivo,
              "fecha": ahora.isoformat(), "estado_anterior": programacion.estado, "hora_anterior": vigente.isoformat()}
    if horario is not None:
        programacion.ejecutar_desde_utc = horario
    else:
        programacion.estado = destino
    if accion == "CANCELAR":
        ejecucion.estado, ejecucion.fin_en = "CANCELADA", ahora
    cambio.update(estado=programacion.estado, hora=programacion.ejecutar_desde_utc.isoformat())
    programacion.cambios_json = [*(programacion.cambios_json or []), cambio]
    sesion.flush()
    return programacion
