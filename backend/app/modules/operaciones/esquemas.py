from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Estricto(BaseModel):
    model_config=ConfigDict(extra='forbid')


class Linea(Estricto):
    producto_id:int=Field(gt=0)
    cantidad:int=Field(gt=0,le=100000,strict=True)


class LineaProduccion(Linea):
    fecha_caducidad:date


class Operacion(Estricto):
    clave_idempotencia:str=Field(min_length=8,max_length=64,pattern=r'^[A-Za-z0-9_-]+$')
    fecha:date
    lineas:list[Linea]=Field(min_length=1,max_length=100)

    @model_validator(mode='after')
    def unicas(self):
        if len({l.producto_id for l in self.lineas})!=len(self.lineas):raise ValueError('No repitas productos')
        return self


class Produccion(Operacion):
    plan_id:int=Field(gt=0)
    lineas:list[LineaProduccion]=Field(min_length=1,max_length=100)


class Configuracion(Estricto):
    reloj:Literal['ACTUAL','ESCENARIO']='ACTUAL'
    fecha_escenario:date|None=None
    hora_escenario:time=time(17,15)
    producto_ids:list[int]=Field(default_factory=list,max_length=500)
    habilitada:bool=False

    @model_validator(mode='after')
    def fechas(self):
        if self.reloj=='ESCENARIO' and not self.fecha_escenario:raise ValueError('Indica la fecha del escenario')
        if any(i<=0 for i in self.producto_ids) or len(set(self.producto_ids))!=len(self.producto_ids):raise ValueError('Productos inválidos')
        if self.hora_escenario.tzinfo:raise ValueError('Hora local sin zona')
        return self


class Respuesta(Estricto):
    accion:Literal['ACEPTAR','RECHAZAR']
    nombre:str=Field(min_length=3,max_length=150)
    descripcion:str=Field(default='',max_length=500)
    entrega_comprometida:datetime|None=None

    @model_validator(mode='after')
    def entrega(self):
        if self.accion=='ACEPTAR' and (not self.entrega_comprometida or self.entrega_comprometida.tzinfo is None):raise ValueError('Indica entrega con zona horaria')
        return self


class LineaRecepcion(Estricto):
    linea_pedido_id:int=Field(gt=0)
    cantidad_compra:Decimal=Field(ge=0,max_digits=20,decimal_places=4)
    codigo_lote:str|None=Field(default=None,max_length=80)
    fecha_caducidad:date|None=None


class Recepcion(Estricto):
    clave_idempotencia:str=Field(min_length=8,max_length=64,pattern=r'^[A-Za-z0-9_-]+$')
    fecha_recepcion:date
    motivo:str=Field(min_length=3,max_length=300)
    lineas:list[LineaRecepcion]=Field(min_length=1,max_length=100)


class Ficha(Estricto):
    precio:Decimal=Field(gt=0,max_digits=12,decimal_places=2)
    categoria:str=Field(default='panes',min_length=1,max_length=60)
    descripcion:str=Field(default='',max_length=500)
    presentacion:str=Field(default='Unidad',max_length=100)
    imagen:str=Field(default='/tienda/productos/baguette.jpg',max_length=300,pattern=r'^(/[^/]|https://)')
    publicado:bool=True


class Entrega(Estricto):
    nombre_receptor:str=Field(min_length=3,max_length=150)
    celular:str=Field(pattern=r'^9\d{8}$')
    direccion:str=Field(min_length=5,max_length=300)
    distrito:str=Field(min_length=2,max_length=100)
    referencia:str=Field(default='',max_length=200)


class LineaCompra(Linea):
    cantidad:int=Field(gt=0,le=100,strict=True)
    subtotal_esperado:Decimal=Field(ge=0,max_digits=12,decimal_places=2)


class Compra(Estricto):
    clave_idempotencia:str=Field(min_length=8,max_length=64,pattern=r'^[A-Za-z0-9_-]+$')
    lineas:list[LineaCompra]=Field(min_length=1,max_length=30)
    entrega:Entrega
    metodo_pago_simulado:Literal['TARJETA_SIMULADA','YAPE_SIMULADO','PLIN_SIMULADO']

    @model_validator(mode='after')
    def unicas(self):
        if len(set(l.producto_id for l in self.lineas))!=len(self.lineas):raise ValueError('No repitas productos')
        return self


class Cotizacion(Estricto):
    lineas:list[Linea]=Field(min_length=1,max_length=30)

    @model_validator(mode='after')
    def unicas(self):
        if len(set(l.producto_id for l in self.lineas))!=len(self.lineas):raise ValueError('No repitas productos')
        return self
