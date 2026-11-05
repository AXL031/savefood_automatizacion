"""Publicación puntual explícita; misma sesión, motor durable y catálogo canónico."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import select
from app.core.errores import ErrorAPI
from app.modules.automatizaciones.modelos import ProgramacionDemo
from app.modules.automatizaciones.servicio import programar_ejecucion
from app.modules.inventario.modelos import LoteProducto
from app.modules.inventario.operacion import bloquear_catalogo
from app.modules.negocios.servicio import zona_horaria_negocio
from app.modules.productos.modelos import Producto
from app.modules.promociones.modelos import ReglaPromocionDemo
from app.modules.promociones.esquemas import ConfigurarRegla
from app.modules.promociones.reglas import evaluar_promocion, EstadoProducto, ReglaPromocion
from .modelos import ConfiguracionOperacion, PromocionOperacion
from .servicio import configuracion, aviso


def ahora():
    return datetime.now(timezone.utc)


def bloquear(s, id_):
    configuracion(s)
    s.scalar(select(ConfiguracionOperacion).where(ConfiguracionOperacion.id==1).with_for_update())
    referencia=s.get(PromocionOperacion,id_)
    if referencia is None:raise ErrorAPI(404,'PROMOCION_NO_ENCONTRADA','No existe la promoción.')
    lote=s.get(LoteProducto,referencia.lote_id)
    bloquear_catalogo(s,[lote.producto_id])
    lote=s.scalar(select(LoteProducto).where(LoteProducto.id==lote.id).with_for_update().execution_options(populate_existing=True))
    p=s.scalar(select(PromocionOperacion).where(PromocionOperacion.id==id_).with_for_update().execution_options(populate_existing=True))
    return p,lote


def resultado_regla(s,p,lote,local):
    producto=s.get(Producto,lote.producto_id)
    if not producto or not producto.activo:return False,None,'El producto dejó de estar activo.'
    if lote.fecha_ingreso and lote.fecha_ingreso>local.date():return False,None,'El lote aún no ha ingresado.'
    if not lote.fecha_caducidad or lote.fecha_caducidad<local.date():return False,None,'El lote está vencido o sin caducidad.'
    if not lote.fecha_limite_venta:return False,None,'El lote no tiene fecha límite de venta.'
    regla=s.get(ReglaPromocionDemo,p.regla_id)
    d=ConfigurarRegla(**regla.parametros)
    if not d.habilitada:return False,None,'La regla conservada está deshabilitada.'
    r=evaluar_promocion(ReglaPromocion(d.hora_revision,d.hora_cierre,d.stock_umbral,d.descuento_pct,d.descuento_maximo_pct,d.antiguedad_maxima_stock_min),
        EstadoProducto(lote.fecha_limite_venta,lote.saldo_disponible,local),local)
    return r.proponer,r.descuento_pct,r.motivo


def programar(s,id_,entrada,usuario_id):
    solicitud={'promocion_id':id_,'usuario_id':usuario_id,**entrada.model_dump(mode='json')}
    clave='promocion-puntual:'+entrada.clave_idempotencia
    existente=s.scalar(select(ProgramacionDemo).where(ProgramacionDemo.clave_idempotencia==clave))
    if existente:
        if existente.parametros_json.get('solicitud')!=solicitud:raise ErrorAPI(409,'CLAVE_REUTILIZADA','La clave corresponde a otra programación.')
        return {'programacion_id':existente.id,'estado':existente.estado,'ejecutar_desde_utc':existente.ejecutar_desde_utc.isoformat()}
    zona=ZoneInfo(zona_horaria_negocio(s));local=entrada.fecha_hora_local
    candidatos={local.replace(tzinfo=zona,fold=f).astimezone(timezone.utc) for f in (0,1)
        if local.replace(tzinfo=zona,fold=f).astimezone(timezone.utc).astimezone(zona).replace(tzinfo=None)==local}
    if len(candidatos)!=1:raise ErrorAPI(422,'HORARIO_AMBIGUO','Ese horario no existe o se repite en la zona del negocio.')
    real=candidatos.pop()
    if real<=ahora():raise ErrorAPI(422,'HORA_NO_FUTURA','Elige una hora futura.')
    p,lote=bloquear(s,id_)
    existente=s.scalar(select(ProgramacionDemo).where(ProgramacionDemo.clave_idempotencia==clave))
    if existente:
        if existente.parametros_json.get('solicitud')!=solicitud:raise ErrorAPI(409,'CLAVE_REUTILIZADA','La clave corresponde a otra programación.')
        return {'programacion_id':existente.id,'estado':existente.estado,'ejecutar_desde_utc':existente.ejecutar_desde_utc.isoformat()}
    if p.estado not in {'PENDIENTE','APROBADA'}:raise ErrorAPI(409,'PROMOCION_NO_PROGRAMABLE','Selecciona una promoción pendiente o aprobada.')
    valido,_,motivo=resultado_regla(s,p,lote,local)
    if not valido:raise ErrorAPI(409,'PROMOCION_NO_PROGRAMABLE',motivo)
    # Es una autorización explícita sobre esta promoción; no un cambio retroactivo global.
    prog=programar_ejecucion(s,tipo='EVALUAR_PROMOCION',ejecutar_desde_utc=real,fecha_hora_simulada_local=local,
        parametros={'accion':'PUBLICAR_PROMOCION_OPERATIVA','promocion_id':p.id,'solicitud':solicitud},
        clave_idempotencia=clave,creado_por=usuario_id)
    historial=list((p.programacion or {}).get('historial',[]))
    historial.append({'accion':'PROGRAMAR','usuario_id':usuario_id,'fecha':ahora().isoformat(),'estado_anterior':p.estado,'modo_anterior':p.modo_publicacion,
        'decidido_por_anterior':p.decidido_por,'fecha_promocion_anterior':p.fecha.isoformat(),'motivo_anterior':p.motivo,'descuento_anterior':p.descuento,'programacion_id':prog.id})
    p.programacion={'programacion_id':prog.id,'fecha_hora_local':local.isoformat(),'ejecutar_desde_utc':real.isoformat(),
        'zona_horaria':str(zona),'modo_publicacion':entrada.modo_publicacion,'estado':'PROGRAMADA','historial':historial}
    p.estado='PROGRAMADA'
    s.flush()
    return {'programacion_id':prog.id,'estado':'PROGRAMADA','ejecutar_desde_utc':real.isoformat()}


def ejecutar_programada(s,contexto):
    params=contexto.datos_entrada['parametros']
    p,lote=bloquear(s,params['promocion_id'])
    datos=p.programacion or {}
    from app.modules.automatizaciones.modelos import EjecucionAutomatizacion
    ejecucion=s.get(EjecucionAutomatizacion,contexto.id)
    if not ejecucion or ejecucion.programacion_id!=datos.get('programacion_id'):
        return {'promocion_id':p.id,'estado':'OMITIDA','motivo':'La programación fue sustituida.'}
    prog=s.get(ProgramacionDemo,ejecucion.programacion_id)
    if prog.parametros_json!=params:raise ErrorAPI(409,'PROGRAMACION_NO_COINCIDE','Revisa la programación de la promoción.')
    if datos.get('estado')=='EJECUTADA':return datos['resultado']
    if p.estado!='PROGRAMADA':return {'promocion_id':p.id,'estado':'OMITIDA','motivo':'La programación fue cancelada.'}
    if ahora()<datetime.fromisoformat(datos['ejecutar_desde_utc']):raise ErrorAPI(409,'HORA_NO_CUMPLIDA','Aún no corresponde ejecutar la promoción.')
    local=ahora().astimezone(ZoneInfo(datos['zona_horaria'])).replace(tzinfo=None)
    valido,descuento,motivo=resultado_regla(s,p,lote,local)
    p.estado=('APROBADA' if datos['modo_publicacion']=='AUTOMATICO' else 'PENDIENTE') if valido else 'NO_APLICA'
    p.modo_publicacion=datos['modo_publicacion'];p.decidido_por=None
    p.fecha=local.date();p.descuento=descuento;p.motivo=motivo
    salida={'promocion_id':p.id,'estado':p.estado,'descuento':descuento,'motivo':motivo}
    p.programacion={**datos,'estado':'EJECUTADA','ejecutada_en':ahora().isoformat(),'ejecucion_id':contexto.id,'resultado':salida}
    aviso(s,f'promocion-programada:{datos["programacion_id"]}',f'Promoción programada: {p.estado.lower()}',salida)
    s.flush();return salida


def cancelar(s,id_,programacion_id,usuario_id):
    # El motor bloquea ejecución antes de dominio; conservar ese orden.
    referencia=s.get(PromocionOperacion,id_)
    if referencia is None:raise ErrorAPI(404,'PROMOCION_NO_ENCONTRADA','No existe la promoción.')
    datos=referencia.programacion or {}
    if datos.get('programacion_id')!=programacion_id:raise ErrorAPI(409,'PROGRAMACION_DISTINTA','La promoción tiene otra programación; actualiza la vista.')
    if datos.get('estado')=='CANCELADA':return {'estado':referencia.estado}
    if referencia.estado!='PROGRAMADA':raise ErrorAPI(409,'PROMOCION_NO_PROGRAMADA','La promoción no tiene una programación pendiente.')
    from app.modules.automatizaciones.modelos import EjecucionAutomatizacion
    ejecucion=s.scalar(select(EjecucionAutomatizacion).where(EjecucionAutomatizacion.programacion_id==programacion_id).with_for_update().execution_options(populate_existing=True))
    prog=s.scalar(select(ProgramacionDemo).where(ProgramacionDemo.id==programacion_id).with_for_update().execution_options(populate_existing=True))
    if not ejecucion or not prog or ejecucion.estado!='PENDIENTE' or ejecucion.token_despacho or ejecucion.lease_hasta:
        raise ErrorAPI(409,'TAREA_YA_INICIADA','El motor ya inició la tarea; consulta su resultado.')
    p,_=bloquear(s,id_);datos=p.programacion
    if datos['programacion_id']!=programacion_id:raise ErrorAPI(409,'PROGRAMACION_DISTINTA','La promoción tiene otra programación; actualiza la vista.')
    ejecucion.estado='CANCELADA';ejecucion.fin_en=ahora();prog.estado='CANCELADA'
    prog.cambios_json=[*(prog.cambios_json or []),{'accion':'CANCELAR','usuario_id':usuario_id,'fecha':ahora().isoformat(),'motivo':'Cancelación explícita de promoción.'}]
    p.estado='PENDIENTE';p.decidido_por=None
    p.programacion={**datos,'estado':'CANCELADA','historial':[*datos['historial'],{'accion':'CANCELAR','usuario_id':usuario_id,'fecha':ahora().isoformat()}]}
    s.flush();return {'estado':'PENDIENTE'}
