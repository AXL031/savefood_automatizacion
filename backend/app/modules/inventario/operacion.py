"""Interfaz pública de producción por tandas. El llamador controla la transacción."""
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select
from app.core.errores import ErrorAPI
from app.modules.productos.modelos import Producto
from app.modules.ingredientes.modelos import Ingrediente
from .modelos import LoteIngrediente, LoteProducto, MovimientoInventario


def bloquear_catalogo(sesion, producto_ids=(), ingrediente_ids=()):
    for modelo, ids in ((Ingrediente, ingrediente_ids), (Producto, producto_ids)):
        encontrados = list(sesion.scalars(select(modelo).where(modelo.id.in_(sorted(set(ids)))).order_by(modelo.id).with_for_update().execution_options(populate_existing=True)))
        if len(encontrados) != len(set(ids)) or any(not x.activo for x in encontrados):
            raise ErrorAPI(409, 'CATALOGO_NO_DISPONIBLE', 'Hay productos o ingredientes inexistentes o inactivos.')


def movimiento(sesion, lote, delta, tipo, clave, fecha, usuario_id, motivo):
    if lote.saldo_disponible + delta < 0:
        raise ErrorAPI(409, 'STOCK_INSUFICIENTE', 'El saldo no alcanza para completar la operación.')
    lote.saldo_disponible += delta
    lote.actualizado_en = datetime.now(timezone.utc)
    m = MovimientoInventario(lote_producto_id=lote.id if isinstance(lote, LoteProducto) else None,
        lote_ingrediente_id=lote.id if isinstance(lote, LoteIngrediente) else None,
        delta=Decimal(delta), saldo_resultante=Decimal(lote.saldo_disponible), tipo=tipo,
        clave_operacion=clave, motivo=motivo[:300], usuario_id=usuario_id,
        efectivo_en_demo=datetime.combine(fecha, datetime.min.time()))
    sesion.add(m); sesion.flush()
    return m.id


def consumir_ingredientes(sesion, requeridos, fecha, clave, usuario_id):
    movimientos = []
    for ingrediente_id, cantidad in sorted(requeridos.items()):
        lotes = list(sesion.scalars(select(LoteIngrediente).where(
            LoteIngrediente.ingrediente_id == ingrediente_id, LoteIngrediente.saldo_disponible > 0,
            (LoteIngrediente.fecha_caducidad.is_(None)) | (LoteIngrediente.fecha_caducidad >= fecha),
            (LoteIngrediente.fecha_ingreso.is_(None)) | (LoteIngrediente.fecha_ingreso <= fecha))
            .order_by(LoteIngrediente.fecha_caducidad.asc().nulls_last(), LoteIngrediente.id).with_for_update().execution_options(populate_existing=True)))
        if sum((l.saldo_disponible for l in lotes), Decimal(0)) < cantidad:
            raise ErrorAPI(409, 'INGREDIENTES_INSUFICIENTES', f'No alcanza el ingrediente #{ingrediente_id}; registra una tanda menor o recibe la compra.')
        restante = cantidad
        for lote in lotes:
            if restante <= 0: break
            tomar = min(restante, lote.saldo_disponible)
            movimientos.append(movimiento(sesion, lote, -tomar, 'PRODUCCION', f'{clave}:i:{lote.id}', fecha, usuario_id, 'Consumo de producción confirmada'))
            restante -= tomar
    return movimientos


def abrir_produccion(sesion, producto_id, cantidad, fecha, caducidad, clave, usuario_id):
    lote = LoteProducto(producto_id=producto_id, codigo_lote=clave, lote_informado=True,
        fecha_ingreso=fecha, fecha_caducidad=caducidad, fecha_limite_venta=caducidad, saldo_disponible=0)
    sesion.add(lote); sesion.flush()
    mid = movimiento(sesion, lote, cantidad, 'PRODUCCION', f'{clave}:p', fecha, usuario_id, 'Alta de producto fabricado')
    return lote.id, mid

