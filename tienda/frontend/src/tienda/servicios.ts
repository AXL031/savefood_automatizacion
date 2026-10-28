/**
 * Frontera de datos de la tienda. Las pantallas solo usan estas funciones.
 *
 * Modo "ejemplo" (por defecto): datos locales que respetan el contrato y persisten en
 * localStorage del navegador, para revisar la interfaz sin backend.
 * Modo "api" (NEXT_PUBLIC_TIENDA_MODO=api): llama a /api/v1/tienda/* cuando T01–T04 existan.
 */
import { CATEGORIAS, COMERCIO, PRODUCTOS, PROMOCIONES, UMBRAL_ULTIMAS_UNIDADES } from "./datos-ejemplo";
import { aCentimos, aplicarDescuento, deCentimos } from "./dinero";
import {
  ErrorTienda,
  type Categoria,
  type ClienteTienda,
  type ConfirmarPedidoEntrada,
  type DatosEntrega,
  type EstadoStock,
  type EstadoStockItem,
  type LineaCarrito,
  type PedidoCliente,
  type ProductoTienda,
  type PromocionVisible,
} from "./tipos";

export const MODO_TIENDA: "ejemplo" | "api" = process.env.NEXT_PUBLIC_TIENDA_MODO === "api" ? "api" : "ejemplo";
const baseUrl = (process.env.NEXT_PUBLIC_FOODSAVE_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export const DATOS_COMERCIO = COMERCIO;

// --- Cliente HTTP propio (no comparte sesión ni eventos con el administrador) ---

async function solicitar<T>(ruta: string, opciones: { method?: string; body?: unknown; token?: string; signal?: AbortSignal } = {}): Promise<T> {
  let respuesta: Response;
  try {
    respuesta = await fetch(`${baseUrl}/api/v1/tienda${ruta}`, {
      method: opciones.method ?? "GET",
      headers: {
        ...(opciones.body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...(opciones.token ? { Authorization: `Bearer ${opciones.token}` } : {}),
      },
      body: opciones.body !== undefined ? JSON.stringify(opciones.body) : undefined,
      signal: opciones.signal,
    });
  } catch {
    throw new ErrorTienda("SERVICIO_NO_DISPONIBLE", "No pudimos conectar con la tienda. Revisa tu conexión e inténtalo otra vez.");
  }
  const cuerpo = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    const error = cuerpo?.error;
    throw new ErrorTienda(error?.codigo ?? "SERVICIO_NO_DISPONIBLE", error?.mensaje ?? "No se pudo completar la solicitud.", error?.detalles);
  }
  return cuerpo.datos as T;
}

// --- Estado del modo ejemplo ---

type EstadoEjemplo = {
  stock: Record<number, number>;
  promo: Record<number, number>;
  pedidos: (PedidoCliente & { cliente_id: number; clave: string; huella: string })[];
};

const CLAVE_ESTADO = "foodsave-tienda-ejemplo-v1";
let memoria: EstadoEjemplo | null = null;

function estadoInicial(): EstadoEjemplo {
  return {
    stock: Object.fromEntries(PRODUCTOS.map((p) => [p.id, p.stock])),
    promo: Object.fromEntries(PROMOCIONES.map((p) => [p.id, p.unidades_lote])),
    pedidos: [],
  };
}

function leerEstado(): EstadoEjemplo {
  try {
    const guardado = window.localStorage.getItem(CLAVE_ESTADO);
    if (guardado) return JSON.parse(guardado) as EstadoEjemplo;
  } catch { /* almacenamiento bloqueado: se usa memoria */ }
  memoria ??= estadoInicial();
  return memoria;
}

function guardarEstado(estado: EstadoEjemplo) {
  memoria = estado;
  try { window.localStorage.setItem(CLAVE_ESTADO, JSON.stringify(estado)); } catch { /* sin persistencia */ }
}

/** Solo para la demostración local: devuelve stock y pedidos de ejemplo a su estado inicial. */
export function reiniciarDatosEjemplo() {
  guardarEstado(estadoInicial());
}

function estadoDe(cantidad: number): EstadoStock {
  if (cantidad <= 0) return "AGOTADO";
  return cantidad <= UMBRAL_ULTIMAS_UNIDADES ? "ULTIMAS_UNIDADES" : "DISPONIBLE";
}

function promocionVigente(estado: EstadoEjemplo, productoId: number): PromocionVisible | null {
  const promo = PROMOCIONES.find((p) => p.producto_id === productoId && (estado.promo[p.id] ?? 0) > 0);
  const producto = PRODUCTOS.find((p) => p.id === productoId);
  if (!promo || !producto || (estado.stock[productoId] ?? 0) <= 0) return null;
  return {
    id: promo.id,
    producto_id: productoId,
    descuento_pct: promo.descuento_pct,
    precio_normal: producto.precio,
    precio_promocional: aplicarDescuento(producto.precio, promo.descuento_pct),
    vigente_hasta: promo.vigente_hasta,
  };
}

const esperar = (ms: number) => new Promise((r) => setTimeout(r, ms));

// --- Catálogo y stock (T03) ---

export type Catalogo = { origen: string; version: string | number; modo: "ejemplo" | "api"; disponibilidad_actualizada: boolean; categorias: Categoria[]; productos: ProductoTienda[] };

const apiPropia = (process.env.NEXT_PUBLIC_TIENDA_API_URL ?? "http://localhost:8001").replace(/\/$/, "");

export async function obtenerCatalogo(signal?: AbortSignal): Promise<Catalogo> {
  const r = await fetch(apiPropia + "/api/v1/catalogo", { signal, cache: "no-store" });
  const body = await r.json();
  if (!r.ok) throw new Error(body?.error?.mensaje ?? "No se pudo cargar el catálogo de la tienda.");
  return body.datos;
}

export type StockVisible = { origen: string; version: string | number; actualizada: boolean; items: EstadoStockItem[] };
export async function obtenerStock(signal?: AbortSignal): Promise<StockVisible> {
  const r = await fetch(apiPropia + "/api/v1/stock", { signal, cache: "no-store" });
  const body = await r.json();
  if (!r.ok) throw new Error(body?.error?.mensaje ?? "No se pudo actualizar la disponibilidad.");
  return body.datos;
}

// --- Cotización del carrito ---

export type LineaCotizada = {
  nombre?: string;
  producto_id: number;
  cantidad: number;
  precio_unitario_base: string;
  unidades_con_promocion: number;
  precio_promocional: string | null;
  subtotal: string;
  disponible: boolean;
  estado_stock: EstadoStock;
};
export type Cotizacion = { origen?: string; huella?: string; lineas: LineaCotizada[]; total: string; moneda: "PEN" };

function cotizarEnEstado(estado: EstadoEjemplo, lineas: LineaCarrito[]): Cotizacion {
  const cotizadas = lineas.map((linea) => {
    const producto = PRODUCTOS.find((p) => p.id === linea.producto_id);
    if (!producto) throw new ErrorTienda("PRODUCTO_NO_PUBLICADO", "Uno de los productos ya no está a la venta.");
    const stock = estado.stock[producto.id] ?? 0;
    const promo = promocionVigente(estado, producto.id);
    const conPromo = promo ? Math.min(linea.cantidad, estado.promo[promo.id] ?? 0) : 0;
    const subtotal = conPromo * aCentimos(promo?.precio_promocional ?? "0") + (linea.cantidad - conPromo) * aCentimos(producto.precio);
    return {
      producto_id: producto.id,
      cantidad: linea.cantidad,
      precio_unitario_base: producto.precio,
      unidades_con_promocion: conPromo,
      precio_promocional: promo?.precio_promocional ?? null,
      subtotal: deCentimos(subtotal),
      disponible: linea.cantidad <= stock,
      estado_stock: estadoDe(stock),
    };
  });
  return { lineas: cotizadas, total: deCentimos(cotizadas.reduce((s, l) => s + aCentimos(l.subtotal), 0)), moneda: "PEN" };
}

/** Precios vigentes del carrito sin reservar stock. */
export async function cotizarCarrito(lineas: LineaCarrito[], origen: string, signal?: AbortSignal): Promise<Cotizacion> {
  const url = (process.env.NEXT_PUBLIC_TIENDA_API_URL ?? "http://localhost:8001").replace(/\/$/, "");
  const r = await fetch(`${url}/api/v1/pagos/cotizar`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ lineas, origen_catalogo: origen }), signal, cache: "no-store" });
  const cuerpo = await r.json();
  if (!r.ok) throw new Error(cuerpo?.error?.mensaje ?? "No se pudo cotizar la canasta.");
  return cuerpo.datos as Cotizacion;
}

// --- Sesión del cliente (T02) ---

/** Modo ejemplo: simula la cuenta de Google pidiendo un correo Gmail. No verifica identidad. */
export async function iniciarSesionEjemplo(correo: string, nombre: string): Promise<{ token: string; cliente: ClienteTienda }> {
  await esperar(250);
  const limpio = correo.trim().toLowerCase();
  if (!/^[a-z0-9._%+-]+@gmail\.com$/.test(limpio)) throw new ErrorTienda("CORREO_NO_VERIFICADO", "Usa una dirección de Gmail, por ejemplo nombre@gmail.com.");
  if (nombre.trim().length < 2) throw new ErrorTienda("CORREO_NO_VERIFICADO", "Escribe tu nombre.");
  let id = 0;
  for (const c of limpio) id = (id * 31 + c.charCodeAt(0)) % 100000;
  return { token: `ejemplo-${id}`, cliente: { id: id + 1, correo: limpio, nombre: nombre.trim() } };
}

/** Siempre usa la API real (T02), también cuando el catálogo está en modo ejemplo. */
export async function iniciarSesionGoogle(idToken: string): Promise<{ token: string; cliente: ClienteTienda }> {
  return solicitar("/sesion/google", { method: "POST", body: { id_token: idToken } });
}

// --- Pedidos (T04) ---

export function validarEntrega(entrega: DatosEntrega): Record<keyof DatosEntrega, string> {
  return {
    nombre_receptor: entrega.nombre_receptor.trim().length < 3 ? "Escribe el nombre de quien recibirá el pedido." : "",
    celular: /^9\d{8}$/.test(entrega.celular.replace(/\s/g, "")) ? "" : "El celular debe tener 9 dígitos y empezar con 9.",
    direccion: entrega.direccion.trim().length < 5 ? "Escribe la dirección de entrega." : "",
    distrito: entrega.distrito.trim().length < 2 ? "Indica el distrito." : "",
    referencia: entrega.referencia.length > 200 ? "La referencia admite hasta 200 caracteres." : "",
  };
}

export async function confirmarPedido(entrada: ConfirmarPedidoEntrada, sesion: { token: string; cliente: ClienteTienda }): Promise<PedidoCliente> {
  if (MODO_TIENDA === "api") return solicitar<PedidoCliente>("/pedidos", { method: "POST", body: entrada, token: sesion.token });
  await esperar(500);
  const estado = leerEstado();
  const huella = JSON.stringify([entrada.lineas, entrada.entrega, entrada.metodo_pago_simulado]);
  const previo = estado.pedidos.find((p) => p.cliente_id === sesion.cliente.id && p.clave === entrada.clave_idempotencia);
  if (previo) {
    if (previo.huella !== huella) throw new ErrorTienda("CLAVE_REUTILIZADA", "Este pedido ya se envió con otros datos. Actualiza la página.");
    return previo;
  }
  if (!entrada.lineas.length || entrada.lineas.length > 30) throw new ErrorTienda("CARRITO_INVALIDO", "Tu canasta está vacía.");
  if (Object.values(validarEntrega(entrada.entrega)).some(Boolean)) throw new ErrorTienda("DATOS_ENTREGA_INVALIDOS", "Revisa los datos de entrega.");
  const cotizacion = cotizarEnEstado(estado, entrada.lineas);
  const sinStock = cotizacion.lineas.filter((l) => !l.disponible);
  if (sinStock.length) throw new ErrorTienda("STOCK_INSUFICIENTE", "Algunos productos ya no tienen unidades suficientes.", sinStock.map((l) => ({ producto_id: l.producto_id, estado_stock: l.estado_stock })));
  const cambiados = cotizacion.lineas.filter((l, i) => l.subtotal !== entrada.lineas[i].subtotal_esperado);
  if (cambiados.length) throw new ErrorTienda("PRECIO_CAMBIADO", "Algunos precios cambiaron. Revisa tu canasta antes de pagar.", cambiados);

  // Efecto atómico del ejemplo: descuenta stock y unidades de promoción en un solo guardado.
  for (const linea of cotizacion.lineas) {
    estado.stock[linea.producto_id] -= linea.cantidad;
    const promo = PROMOCIONES.find((p) => p.producto_id === linea.producto_id);
    if (promo && linea.unidades_con_promocion) estado.promo[promo.id] -= linea.unidades_con_promocion;
  }
  const id = estado.pedidos.reduce((max, p) => Math.max(max, p.id), 1000) + 1;
  const pedido: PedidoCliente = {
    id,
    estado: "CONFIRMADO",
    creado_en: new Date().toISOString(),
    total: cotizacion.total,
    moneda: "PEN",
    lineas: cotizacion.lineas.map((l) => ({
      producto_id: l.producto_id,
      nombre: PRODUCTOS.find((p) => p.id === l.producto_id)?.nombre ?? `Producto #${l.producto_id}`,
      cantidad: l.cantidad,
      precio_unitario: deCentimos(Math.round(aCentimos(l.subtotal) / l.cantidad)),
      subtotal: l.subtotal,
    })),
    entrega: entrada.entrega,
    pago: { metodo: entrada.metodo_pago_simulado, estado: "APROBADO", referencia: `SIM-${id}`, monto: cotizacion.total },
  };
  estado.pedidos.push({ ...pedido, cliente_id: sesion.cliente.id, clave: entrada.clave_idempotencia, huella });
  guardarEstado(estado);
  return pedido;
}

function sinInternos({ cliente_id: _c, clave: _k, huella: _h, ...pedido }: EstadoEjemplo["pedidos"][number]): PedidoCliente {
  return pedido;
}

export async function listarPedidos(sesion: { token: string; cliente: ClienteTienda }, signal?: AbortSignal): Promise<PedidoCliente[]> {
  if (MODO_TIENDA === "api") return solicitar<PedidoCliente[]>("/pedidos", { token: sesion.token, signal });
  return leerEstado().pedidos.filter((p) => p.cliente_id === sesion.cliente.id).map(sinInternos).reverse();
}

export async function obtenerPedido(id: number, sesion: { token: string; cliente: ClienteTienda }, signal?: AbortSignal): Promise<PedidoCliente> {
  if (MODO_TIENDA === "api") return solicitar<PedidoCliente>(`/pedidos/${id}`, { token: sesion.token, signal });
  const pedido = leerEstado().pedidos.find((p) => p.id === id && p.cliente_id === sesion.cliente.id);
  if (!pedido) throw new ErrorTienda("PEDIDO_NO_ENCONTRADO", "No encontramos ese pedido en tu cuenta.");
  return sinInternos(pedido);
}
