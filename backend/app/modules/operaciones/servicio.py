"""Producción por tandas y registro operativo; sin commit ni red."""
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_CEILING
from sqlalchemy import select
from app.core.errores import ErrorAPI
from app.modules.planificacion.modelos import PlanProduccion, ElementoPlan
from app.modules.inventario.operacion import bloquear_catalogo, consumir_ingredientes, abrir_produccion, retirar_productos
from .modelos import RegistroOperacion, AvisoOperacion, ConfiguracionOperacion


def utc(valor):
    return valor.replace(tzinfo=timezone.utc) if valor.tzinfo is None else valor.astimezone(timezone.utc)


def configuracion(s):
    c = s.get(ConfiguracionOperacion, 1)
    if c is None:
        c = ConfiguracionOperacion(id=1, datos={'reloj': 'ACTUAL', 'fecha_escenario': None, 'hora_escenario': '17:15', 'producto_ids': [], 'habilitada': False}, proxima_revision=None)
        s.add(c); s.flush()
    return c


def fecha_operativa(s):
    from zoneinfo import ZoneInfo
    from app.modules.negocios.servicio import zona_horaria_negocio
    c = configuracion(s).datos
    return date.fromisoformat(c['fecha_escenario']) if c['reloj'] == 'ESCENARIO' and c.get('fecha_escenario') else datetime.now(ZoneInfo(zona_horaria_negocio(s))).date()


def aviso(s, clave, titulo, datos):
    previo = s.scalar(select(AvisoOperacion).where(AvisoOperacion.clave == clave))
    if previo: return previo
    a = AvisoOperacion(clave=clave, titulo=titulo, datos=datos, leido=False)
    s.add(a); s.flush(); return a


def previo(s, clave, tipo, entrada, usuario_id=None, cliente_id=None):
    p = s.scalar(select(RegistroOperacion).where(RegistroOperacion.clave == clave))
    if p and (p.tipo, p.solicitud, p.usuario_id, p.cliente_id) != (tipo, entrada, usuario_id, cliente_id):
        raise ErrorAPI(409, 'CLAVE_REUTILIZADA', 'La clave ya corresponde a otra operación, contenido o persona.')
    return p


def nuevo(s, clave, tipo, entrada, fecha, usuario_id=None, cliente_id=None, plan_id=None):
    p = RegistroOperacion(clave=clave, tipo=tipo, solicitud=entrada, resultado={}, fecha=fecha,
        usuario_id=usuario_id, cliente_id=cliente_id, plan_id=plan_id)
    s.add(p); s.flush(); return p


def producidos(s, plan_id):
    total = {}
    for r in s.scalars(select(RegistroOperacion).where(RegistroOperacion.plan_id == plan_id, RegistroOperacion.tipo == 'PRODUCCION')):
        for l in r.resultado.get('lineas', []): total[l['producto_id']] = total.get(l['producto_id'], 0) + l['cantidad']
    return total


def producir(s, entrada, usuario_id):
    plan = s.scalar(select(PlanProduccion).where(PlanProduccion.id == entrada['plan_id']).with_for_update())
    if not plan: raise ErrorAPI(404, 'PLAN_NO_ENCONTRADO', 'El plan no existe.')
    if p := previo(s, entrada['clave_idempotencia'], 'PRODUCCION', entrada, usuario_id): return p
    fecha = date.fromisoformat(entrada['fecha'])
    if fecha != fecha_operativa(s): raise ErrorAPI(422, 'FECHA_OPERATIVA', 'Registra la producción en la fecha operativa configurada.')
    if plan.fecha_objetivo != fecha: raise ErrorAPI(409, 'FECHA_PLAN_DISTINTA', 'Selecciona un plan de la fecha operativa; no fabriques con un plan histórico de otra fecha.')
    elementos = {e.producto_id: e for e in s.scalars(select(ElementoPlan).where(ElementoPlan.plan_id == plan.id))}
    hechos, requeridos = producidos(s, plan.id), {}
    for linea in entrada['lineas']:
        e = elementos.get(linea['producto_id'])
        if not e or e.cantidad_producir is None or not e.receta_json:
            raise ErrorAPI(409, 'PRODUCTO_NO_PRODUCIBLE', 'El producto no tiene cálculo y receta conservados en el plan.')
        if linea['cantidad'] > e.cantidad_producir - hechos.get(e.producto_id, 0):
            raise ErrorAPI(409, 'EXCEDE_PLAN', 'La tanda supera la cantidad pendiente del plan.')
        if date.fromisoformat(linea['fecha_caducidad']) < fecha:
            raise ErrorAPI(422, 'CADUCIDAD_INVALIDA', 'El producto no puede fabricarse vencido.')
        for i in e.receta_json['lineas']:
            requeridos[i['ingrediente_id']] = requeridos.get(i['ingrediente_id'], Decimal(0)) + Decimal(i['cantidad_por_unidad']) * linea['cantidad']
    requeridos = {i: n.quantize(Decimal('.001'), rounding=ROUND_CEILING) for i, n in requeridos.items()}
    bloquear_catalogo(s, [l['producto_id'] for l in entrada['lineas']], requeridos)
    r = nuevo(s, entrada['clave_idempotencia'], 'PRODUCCION', entrada, fecha, usuario_id, plan_id=plan.id)
    movimientos = consumir_ingredientes(s, requeridos, fecha, f'op:{r.id}', usuario_id)
    lineas = []
    for l in entrada['lineas']:
        lote, mid = abrir_produccion(s, l['producto_id'], l['cantidad'], fecha, date.fromisoformat(l['fecha_caducidad']), f'PROD-{r.id}-{l["producto_id"]}', usuario_id)
        lineas.append({**l, 'lote_id': lote, 'movimiento_id': mid})
    r.resultado = {'lineas': lineas, 'consumos': {str(i): str(n) for i,n in requeridos.items()}, 'movimientos_ingredientes': movimientos}
    s.flush(); return r


def vender(s, entrada, usuario_id):
    bloquear_catalogo(s, [l['producto_id'] for l in entrada['lineas']])
    if p := previo(s, entrada['clave_idempotencia'], 'VENTA_INTERNA', entrada, usuario_id): return p
    fecha = date.fromisoformat(entrada['fecha'])
    if fecha != fecha_operativa(s): raise ErrorAPI(422, 'FECHA_OPERATIVA', 'La venta debe corresponder a la fecha operativa.')
    r = nuevo(s, entrada['clave_idempotencia'], 'VENTA_INTERNA', entrada, fecha, usuario_id)
    lineas = []
    for l in entrada['lineas']:
        asignaciones = retirar_productos(s, l['producto_id'], l['cantidad'], fecha, f'op:{r.id}:{l["producto_id"]}', usuario_id, 'VENTA')
        from app.modules.ventas.operacion import agregar_venta_operativa
        agregar_venta_operativa(s, l['producto_id'], fecha, l['cantidad'], usuario_id)
        lineas.append({**l, 'asignaciones': asignaciones})
    r.resultado = {'lineas': lineas}; s.flush(); return r
