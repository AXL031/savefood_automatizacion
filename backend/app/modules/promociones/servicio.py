"""Frontera V03: reserva y evaluación en la sesión del consumidor."""
from datetime import date, datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.errores import ErrorAPI
from app.modules.promociones.esquemas import ConfigurarRegla
from app.modules.promociones.modelos import EvaluacionPromocion, ReglaPromocionDemo
from app.modules.promociones.reglas import EstadoProducto, ReglaPromocion, evaluar_promocion


def ultima_regla(sesion: Session):
    return sesion.scalar(select(ReglaPromocionDemo).order_by(ReglaPromocionDemo.version.desc()).limit(1))


def guardar_regla(sesion: Session, datos: ConfigurarRegla, usuario_id: int):
    anterior = ultima_regla(sesion)
    parametros = datos.model_dump(mode="json")
    if anterior and anterior.parametros == parametros:
        return anterior
    regla = ReglaPromocionDemo(version=(anterior.version + 1 if anterior else 1), parametros=parametros, creado_por=usuario_id)
    sesion.add(regla)
    sesion.flush()  # UNIQUE(version) protege cambios concurrentes; la ruta traduce el conflicto.
    return regla


def reservar_tras_ajuste(sesion: Session, movimiento_id: int, usuario_id: int | None):
    from app.modules.inventario.servicio import lectura_para_promocion
    from app.modules.automatizaciones.servicio import programar_ejecucion
    regla = ultima_regla(sesion)
    if not regla or not regla.parametros["habilitada"]:
        return None
    lectura = lectura_para_promocion(sesion, movimiento_id)
    if not lectura:
        return None
    return programar_ejecucion(
        sesion, tipo="EVALUAR_PROMOCION",
        ejecutar_desde_utc=datetime.now(timezone.utc) + timedelta(seconds=regla.parametros["demora_segundos"]),
        fecha_hora_simulada_local=datetime.fromisoformat(lectura["efectivo_en_demo"]),
        parametros={"regla_id": regla.id, "movimiento_id": movimiento_id, "lectura": lectura},
        clave_idempotencia=f"promocion-movimiento-{movimiento_id}", creado_por=usuario_id,
    )


def evaluar_programada(sesion: Session, contexto):
    from app.modules.inventario.servicio import lectura_para_promocion
    parametros = contexto.datos_entrada["parametros"]
    movimiento_id = parametros["movimiento_id"]
    existente = sesion.scalar(select(EvaluacionPromocion).where(EvaluacionPromocion.movimiento_id == movimiento_id))
    if existente:
        return {"evaluacion_promocion_id": existente.id, "proponer": existente.proponer, "motivo": existente.motivo}
    regla = sesion.get(ReglaPromocionDemo, parametros["regla_id"])
    if regla is None:
        raise ErrorAPI(404, "REGLA_NO_ENCONTRADA", "La regla conservada no existe.")
    lectura = parametros["lectura"]
    actual = lectura_para_promocion(sesion, movimiento_id)
    efectivo = datetime.fromisoformat(contexto.datos_entrada["fecha_hora_simulada_local"])
    antiguedad_real = max(timedelta(0), datetime.now(timezone.utc) - datetime.fromisoformat(lectura["registrado_en"]))
    ahora = efectivo + antiguedad_real
    proponer, descuento = False, None
    if not actual or actual["ultimo_movimiento_id"] != movimiento_id:
        motivo = "Otro movimiento reemplazó esta lectura de stock."
    elif not lectura["fecha_limite_venta"]:
        motivo = "Falta la fecha límite de venta del lote."
    elif (lectura.get("fecha_caducidad") and date.fromisoformat(lectura["fecha_caducidad"]) < ahora.date()) or date.fromisoformat(lectura["fecha_limite_venta"]) < ahora.date():
        motivo = "El lote está vencido para la fecha del escenario."
    else:
        datos = ConfigurarRegla(**regla.parametros)
        resultado = evaluar_promocion(
            ReglaPromocion(datos.hora_revision, datos.hora_cierre, datos.stock_umbral,
                          datos.descuento_pct, datos.descuento_maximo_pct, datos.antiguedad_maxima_stock_min),
            EstadoProducto(date.fromisoformat(lectura["fecha_limite_venta"]), lectura["saldo"],
                           datetime.fromisoformat(lectura["efectivo_en_demo"])), ahora,
        )
        proponer, descuento, motivo = resultado.proponer, resultado.descuento_pct, resultado.motivo
    evaluacion = EvaluacionPromocion(regla_id=regla.id, movimiento_id=movimiento_id,
        ejecucion_id=contexto.id, proponer=proponer, descuento_pct=descuento, motivo=motivo,
        lectura=lectura, fecha_hora_simulada=ahora)
    sesion.add(evaluacion)
    sesion.flush()
    return {"evaluacion_promocion_id": evaluacion.id, "proponer": proponer, "motivo": motivo}


def serializar_regla(regla):
    return {"id": regla.id, "version": regla.version, **regla.parametros} if regla else None


def serializar_evaluacion(sesion, evaluacion):
    return {"id": evaluacion.id, "regla": serializar_regla(sesion.get(ReglaPromocionDemo, evaluacion.regla_id)),
        "movimiento_id": evaluacion.movimiento_id, "ejecucion_id": evaluacion.ejecucion_id,
        "proponer": evaluacion.proponer, "descuento_pct": evaluacion.descuento_pct, "motivo": evaluacion.motivo,
        "lectura": evaluacion.lectura, "fecha_hora_simulada": evaluacion.fecha_hora_simulada.isoformat(),
        "creado_en": evaluacion.creado_en.isoformat()}
