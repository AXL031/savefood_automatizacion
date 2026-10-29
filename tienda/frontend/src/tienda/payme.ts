/** Checkout Payme de pruebas. Credenciales del comercio y Access Token nunca llegan aquí. */
import type { DatosEntrega, LineaCarrito } from "./tipos";
import type { Cotizacion } from "./servicios";

export type MetodoPayme = "CARD" | "YAPE" | "QR" | "PAGOEFECTIVO";
export const METODOS_PAYME: { id: MetodoPayme; nombre: string; detalle: string }[] = [
  { id: "CARD", nombre: "Tarjetas", detalle: "Crédito o débito" },
  { id: "YAPE", nombre: "Yape", detalle: "Paga con tu celular" },
  { id: "QR", nombre: "QR billeteras", detalle: "Escanea desde tu billetera" },
  { id: "PAGOEFECTIVO", nombre: "PagoEfectivo", detalle: "Genera un código de pago" },
];
export type PagoPayme = {
  id: string; ambiente: "pruebas"; operacion: string; metodo: MetodoPayme; estado: string;
  pagado: boolean; total: string; moneda: "PEN"; cotizacion: Cotizacion;
  creado_en: string; transaction_id: string | null;
  continuacion: { cip?: string | null; cip_url?: string | null; continue_url?: string | null; expira_en?: string | null };
  comercial?: { origen: "EJEMPLO" | "FOODSAVE"; estado: string; ticket: { ticket_id: number; numero: string; total: string; fecha_local: string } | null; reserva_vence_en: string | null; mensaje: string | null };
};
export type CompradorPayme = { nombres: string; apellidos: string; correo: string };
export type FlexDatos = { nonce: string; payload: Record<string, unknown>; metodo: MetodoPayme; script_url: string; css_url: string };
type Checkout = { pago: PagoPayme; flex: FlexDatos | null };
type Referencia = { id: string; clave: string; metodo: MetodoPayme; operacion: string; total: string; estado: string; transaction_id?: string; comercial?: PagoPayme["comercial"] };
const URL_API = (process.env.NEXT_PUBLIC_TIENDA_API_URL ?? "http://localhost:8001").replace(/\/$/, "");
const CLAVE = "foodsave-payme-pruebas-v1";
const BORRADOR = "foodsave-payme-checkout-borrador";

async function api<T>(ruta: string, opciones: { metodo?: string; cuerpo?: unknown; clave?: string; signal?: AbortSignal } = {}): Promise<T> {
  const respuesta = await fetch(`${URL_API}/api/v1/pagos${ruta}`, {
    method: opciones.metodo ?? "GET", cache: "no-store", signal: opciones.signal,
    headers: { ...(opciones.cuerpo ? { "Content-Type": "application/json" } : {}),
      ...(opciones.clave ? { Authorization: `Bearer ${opciones.clave}` } : {}) },
    body: opciones.cuerpo ? JSON.stringify(opciones.cuerpo) : undefined,
  });
  const datos = await respuesta.json().catch(() => null);
  if (!respuesta.ok) throw Object.assign(new Error(datos?.error?.mensaje ?? "No se pudo consultar el pago. Revisa su estado antes de volver a pagar."), { status: respuesta.status });
  return datos.datos as T;
}

export function referenciasPayme(): Referencia[] {
  try { return JSON.parse(localStorage.getItem(CLAVE) ?? "[]") as Referencia[]; } catch { return []; }
}
export function recordarPago(pago: PagoPayme, clave?: string) {
  const referencias = referenciasPayme();
  const anterior = referencias.find(p => p.id === pago.id);
  const capacidad = clave ?? anterior?.clave;
  if (!capacidad) return;
  const actual = { id: pago.id, clave: capacidad, metodo: pago.metodo, operacion: pago.operacion, total: pago.total, estado: pago.estado,
    transaction_id: pago.transaction_id ?? anterior?.transaction_id, comercial: pago.comercial };
  localStorage.setItem(CLAVE, JSON.stringify([actual, ...referencias.filter(p => p.id !== pago.id)].slice(0, 50)));
}

export function configuracionPayme(signal?: AbortSignal) {
  return api<{ ambiente: "pruebas"; configurado: boolean; metodos: MetodoPayme[] }>("/configuracion", { signal });
}

type CuerpoBorrador = { lineas: LineaCarrito[]; comprador: CompradorPayme; entrega: DatosEntrega; origen_catalogo?: string; cotizacion_hash?: string; total_revisado?: string };
type Borrador = { huella: string; metodo: MetodoPayme; clave: string; cuerpo?: CuerpoBorrador };
function leerBorrador(): Borrador | null { try { return JSON.parse(localStorage.getItem(BORRADOR) ?? "null"); } catch { return null; } }

export async function recuperarPagoPendiente(): Promise<PagoPayme | null> {
  const b = leerBorrador();
  if (!b) return null;
  try {
    const pago = await api<PagoPayme>("/recuperar", { clave: b.clave });
    recordarPago(pago, b.clave);
    if (pago.pagado || ["DENEGADO", "INVALIDO", "EXPIRADO", "CANCELADO", "EXTORNADO"].includes(pago.estado)) liberarBorradorPayme();
    return pago;
  } catch (e) {
    if ((e as { status?: number }).status === 404) return null;
    throw e;
  }
}

export async function reabrirPayme(metodo: MetodoPayme): Promise<Checkout> {
  const b = leerBorrador();
  if (!b?.cuerpo) throw new Error("Consulta esta operación desde Mis compras y pagos antes de iniciar otra.");
  const checkout = await api<Checkout>("", { metodo: "POST", cuerpo: { ...b.cuerpo, metodo, clave_checkout: b.clave } });
  recordarPago(checkout.pago, b.clave); return checkout;
}

export async function iniciarPayme(metodo: MetodoPayme, lineas: LineaCarrito[], comprador: CompradorPayme, entrega: DatosEntrega, cotizacion?: Cotizacion | null): Promise<Checkout> {
  const cuerpo = { lineas, comprador, entrega: { ...entrega, celular: entrega.celular.replace(/\s/g, "") },
    ...(cotizacion?.origen ? { origen_catalogo: cotizacion.origen } : {}),
    ...(cotizacion?.huella ? { cotizacion_hash: cotizacion.huella, total_revisado: cotizacion.total } : {}) };
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(JSON.stringify(cuerpo)));
  const huella = Array.from(new Uint8Array(digest), v => v.toString(16).padStart(2, "0")).join("");
  const previo = leerBorrador();
  if (previo && previo.huella !== huella) {
    const recuperado = await recuperarPagoPendiente();
    if (recuperado && !recuperado.pagado && !["DENEGADO", "INVALIDO", "EXPIRADO", "CANCELADO", "EXTORNADO"].includes(recuperado.estado)) {
      throw new Error("Hay una operación pendiente de este navegador. Recupérala desde Mis compras y pagos antes de iniciar otra.");
    }
  }
  const clave = previo?.huella === huella ? previo.clave : crypto.randomUUID();
  // Guardar antes de la petición: un timeout no debe crear otra operación al reabrir.
  localStorage.setItem(BORRADOR, JSON.stringify({ huella, metodo, clave, cuerpo }));
  const checkout = await api<Checkout>("", { metodo: "POST", cuerpo: { ...cuerpo, metodo, clave_checkout: clave } });
  recordarPago(checkout.pago, clave);
  return checkout;
}

export async function leerPagoPayme(id: string, signal?: AbortSignal): Promise<PagoPayme> {
  const ref = referenciasPayme().find(p => p.id === id);
  if (!ref) throw new Error("Este navegador no tiene acceso al pago. Abre la página desde el navegador donde lo iniciaste.");
  const pago = await api<PagoPayme>(`/${encodeURIComponent(id)}`, { clave: ref.clave, signal });
  recordarPago(pago);
  return pago;
}

export async function verificarPagoPayme(id: string, transaction_id?: string): Promise<PagoPayme> {
  const ref = referenciasPayme().find(p => p.id === id);
  if (!ref) throw new Error("No se encontró la referencia privada del pago en este navegador.");
  if (transaction_id) {
    // Solo pista para Consulta backend: jamás determina que el pago esté aprobado.
    ref.transaction_id = transaction_id;
    localStorage.setItem(CLAVE, JSON.stringify(referenciasPayme().map(r => r.id === id ? ref : r)));
  }
  const pago = await api<PagoPayme>(`/${encodeURIComponent(id)}/verificar`, {
    metodo: "POST", cuerpo: { transaction_id: transaction_id ?? ref.transaction_id ?? null }, clave: ref.clave,
  });
  recordarPago(pago);
  return pago;
}

export function liberarBorradorPayme() { localStorage.removeItem(BORRADOR); }

export async function sincronizarVentaPayme(id: string): Promise<PagoPayme> {
  const ref = referenciasPayme().find(r => r.id === id);
  if (!ref) throw new Error("Este navegador no tiene la referencia privada de la compra.");
  const pago = await api<PagoPayme>(`/${encodeURIComponent(id)}/sincronizar`, { metodo: "POST", clave: ref.clave });
  recordarPago(pago); return pago;
}

/** Abrir Flex no es una transacción. Una respuesta recibida aún sin verificar sí se conserva. */
export function puedeCambiarMetodo(pago: PagoPayme | null, resultadoRecibido = false) {
  return !resultadoRecibido && (!pago || (pago.estado === "CREADO" && !pago.transaction_id));
}

export function configuracionFlex(datos: FlexDatos) {
  return { nonce: datos.nonce, payload: datos.payload,
    settings: { display_result_screen: false, show_close_button: true, show_border: false, show_operation_number: true },
    display_settings: { methods: [datos.metodo] },
    i18n: { mode: "multi", default_language: "es", languages: ["es"] } };
}

export type InstanciaFlex = { init: (contenedor: HTMLElement, respuesta: (r: unknown) => void, tracking: (t: unknown) => void, error: (e: unknown) => void) => void; terminate?: () => void };
declare global { interface Window { FlexPaymentForms?: new (config: ReturnType<typeof configuracionFlex>) => InstanciaFlex } }
let libreria: Promise<void> | null = null;

export function cargarFlex(datos: FlexDatos): Promise<void> {
  // No cargar URLs suministradas libremente por cliente/configuración de producción.
  if (datos.script_url !== "https://flex.dev.pay-me.cloud/flex-payment-forms.min.js" ||
      datos.css_url !== "https://flex.dev.pay-me.cloud/main-flex-payment-forms.css") return Promise.reject(new Error("El formulario debe pertenecer al ambiente de pruebas."));
  if (window.FlexPaymentForms) return Promise.resolve();
  if (libreria) return libreria;
  libreria = new Promise<void>((resolve, reject) => {
    const css = document.createElement("link"); css.rel = "stylesheet"; css.href = datos.css_url;
    const script = document.createElement("script"); script.src = datos.script_url; script.async = true;
    const timeout = window.setTimeout(() => fallo(), 20000);
    function fallo() { window.clearTimeout(timeout); css.remove(); script.remove(); libreria = null; reject(new Error("No se pudo cargar Payme. Revisa tu conexión e intenta abrir el mismo pago.")); }
    css.onerror = fallo; script.onerror = fallo;
    script.onload = () => { window.clearTimeout(timeout); if (window.FlexPaymentForms) resolve(); else fallo(); };
    css.onload = () => document.head.appendChild(script);
    document.head.appendChild(css);
  });
  return libreria;
}
