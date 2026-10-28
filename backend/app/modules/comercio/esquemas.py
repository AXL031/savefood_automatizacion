from decimal import Decimal
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Entrada(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class Ficha(Entrada):
    version_actual: int = Field(ge=0, strict=True)
    publicado: bool
    categoria: Literal['panes','tortas','kekes','postres-personales','postres-enteros','bocados','otros'] = 'otros'
    descripcion: str = Field(default='', max_length=500)
    presentacion: str = Field(default='Unidad', max_length=100)
    imagen: str = Field(default='', max_length=300, pattern=r'^(|/tienda/[^\s]+|https://[^\s]+)$')


class Linea(Entrada):
    producto_id: int = Field(gt=0, strict=True)
    cantidad: int = Field(ge=1, le=20, strict=True)


class Consulta(Entrada):
    origen: UUID
    lineas: list[Linea] = Field(min_length=1, max_length=30)

    @model_validator(mode='after')
    def unicas(self):
        if len({l.producto_id for l in self.lineas}) != len(self.lineas):
            raise ValueError('No repitas productos')
        return self


class CrearReserva(Consulta):
    clave_idempotencia: str = Field(min_length=8, max_length=80, pattern=r'^[A-Za-z0-9_-]+$')
    cotizacion_hash: str = Field(pattern=r'^[a-f0-9]{64}$')


class PagoVerificado(Entrada):
    proveedor: Literal['PAYME']
    ambiente: Literal['PRUEBAS']
    verificado: Literal[True]
    operacion: str = Field(pattern=r'^\d{12}$')
    transaccion: str = Field(min_length=1, max_length=128, pattern=r'^[A-Za-z0-9_-]+$')
    metodo: Literal['CARD','YAPE','QR','PAGOEFECTIVO']
    monto: Decimal = Field(gt=0, le=Decimal('999999.99'), decimal_places=2)
    moneda: Literal['PEN']


class ConfirmarVenta(Entrada):
    origen: UUID
    reserva_id: UUID
    evento_id: UUID
    pedido_externo: UUID
    pago: PagoVerificado


class LiberarReserva(Entrada):
    motivo: Literal['DENEGADO','INVALIDO','EXPIRADO','CANCELADO','EXTORNADO']
