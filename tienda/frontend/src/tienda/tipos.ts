/** Tipos de la tienda del cliente según docs/api/contrato-tienda.md. */

export type EstadoStock = "DISPONIBLE" | "ULTIMAS_UNIDADES" | "AGOTADO";

export type MetodoPagoSimulado = "TARJETA_SIMULADA" | "YAPE_SIMULADO" | "PLIN_SIMULADO";

export type Categoria = {
  codigo: string;
  nombre: string;
  descripcion: string;
  imagen: string;
};

export type PromocionVisible = {
  id: number;
  producto_id: number;
  descuento_pct: number;
  /** Cadenas decimales con 2 decimales, como en el contrato. */
  precio_normal: string;
  precio_promocional: string;
  vigente_hasta: string;
};

export type ProductoTienda = {
  id: number;
  codigo: string;
  nombre: string;
  categoria: string;
  descripcion: string;
  /** Peso o presentación visible, por ejemplo "500 g · 4 porciones". */
  presentacion: string;
  imagen: string;
  precio: string;
  moneda: "PEN";
  estado_stock: EstadoStock;
  promocion: PromocionVisible | null;
};

export type EstadoStockItem = { producto_id: number; estado_stock: EstadoStock; promocion_id: number | null };

export type ClienteTienda = { id: number; correo: string; nombre: string };

export type LineaCarrito = { producto_id: number; cantidad: number };

export type DatosEntrega = {
  nombre_receptor: string;
  celular: string;
  direccion: string;
  distrito: string;
  referencia: string;
};

/** subtotal_esperado viene de la cotización: una línea puede mezclar unidades con y sin promoción. */
export type LineaPedidoEntrada = { producto_id: number; cantidad: number; subtotal_esperado: string };

export type ConfirmarPedidoEntrada = {
  clave_idempotencia: string;
  lineas: LineaPedidoEntrada[];
  entrega: DatosEntrega;
  metodo_pago_simulado: MetodoPagoSimulado;
};

export type LineaPedido = {
  producto_id: number;
  nombre: string;
  cantidad: number;
  precio_unitario: string;
  subtotal: string;
};

export type PedidoCliente = {
  id: number;
  estado: "CONFIRMADO";
  creado_en: string;
  total: string;
  moneda: "PEN";
  lineas: LineaPedido[];
  entrega: DatosEntrega;
  pago: { metodo: MetodoPagoSimulado; estado: "APROBADO"; referencia: string; monto: string };
};

export type ErrorTiendaCodigo =
  | "TIENDA_CERRADA"
  | "STOCK_INSUFICIENTE"
  | "PRECIO_CAMBIADO"
  | "CARRITO_INVALIDO"
  | "DATOS_ENTREGA_INVALIDOS"
  | "PRODUCTO_NO_PUBLICADO"
  | "PEDIDO_NO_ENCONTRADO"
  | "CLAVE_REUTILIZADA"
  | "AUTENTICACION_REQUERIDA"
  | "CORREO_NO_VERIFICADO"
  | "SERVICIO_NO_DISPONIBLE";

export class ErrorTienda extends Error {
  constructor(public codigo: ErrorTiendaCodigo, mensaje: string, public detalles?: unknown) {
    super(mensaje);
  }
}
