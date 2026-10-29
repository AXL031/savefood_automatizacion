"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { obtenerCatalogo, obtenerStock, type Catalogo } from "./servicios";
import type { ClienteTienda, LineaCarrito, ProductoTienda } from "./tipos";

/** Intervalo de consulta del stock visible (contrato T03: 5 s, sin SSE). */
export const INTERVALO_STOCK_MS = 5000;
export const MAX_UNIDADES_POR_LINEA = 20;

const CLAVE_CARRITO = "foodsave-tienda-carrito";
const CLAVE_SESION = "foodsave-tienda-sesion";

export type SesionCliente = { token: string; cliente: ClienteTienda };

type ContextoTienda = {
  catalogo: Catalogo | null;
  errorCatalogo: string;
  recargarCatalogo: () => void;
  producto: (id: number) => ProductoTienda | undefined;
  carrito: LineaCarrito[];
  unidadesCarrito: number;
  agregar: (productoId: number, cantidad?: number) => void;
  cambiarCantidad: (productoId: number, cantidad: number) => void;
  vaciarCarrito: () => void;
  sesion: SesionCliente | null;
  guardarSesion: (sesion: SesionCliente | null) => void;
  loginAbierto: boolean;
  abrirLogin: () => void;
  cerrarLogin: () => void;
  aviso: string;
};

const Contexto = createContext<ContextoTienda | null>(null);

function leer<T>(clave: string, defecto: T): T {
  try {
    const valor = window.localStorage.getItem(clave);
    return valor ? (JSON.parse(valor) as T) : defecto;
  } catch {
    return defecto;
  }
}

function escribir(clave: string, valor: unknown) {
  try {
    if (valor === null) window.localStorage.removeItem(clave);
    else window.localStorage.setItem(clave, JSON.stringify(valor));
  } catch { /* preferencia local opcional */ }
}

export function ProveedorTienda({ children }: { children: ReactNode }) {
  const [catalogo, setCatalogo] = useState<Catalogo | null>(null);
  const [errorCatalogo, setErrorCatalogo] = useState("");
  const [revision, setRevision] = useState(0);
  const [carrito, setCarrito] = useState<LineaCarrito[]>([]);
  const [sesion, setSesion] = useState<SesionCliente | null>(null);
  const [loginAbierto, setLoginAbierto] = useState(false);
  const [aviso, setAviso] = useState("");
  const origenCarrito = useRef("");
  const temporizadorAviso = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {

    setSesion(leer<SesionCliente | null>(CLAVE_SESION, null));
  }, []);

  useEffect(() => {
    const control = new AbortController();
    setErrorCatalogo("");
    obtenerCatalogo(control.signal)
      .then(c => {
        const almacen = CLAVE_CARRITO + ":" + c.origen;
        if (origenCarrito.current !== c.origen) {
          const anteriores = leer<LineaCarrito[]>(almacen, []);
          setCarrito(anteriores.filter(l => c.productos.some(p => p.id === l.producto_id)));
          origenCarrito.current = c.origen;
        }
        setCatalogo(c);
      })
      .catch((e: unknown) => { if (!control.signal.aborted) setErrorCatalogo(e instanceof Error ? e.message : "No se pudo cargar el catálogo."); });
    return () => control.abort();
  }, [revision]);

  // Stock visible en vivo: consulta liviana cada 5 s; si cambia una promoción se recarga el catálogo.
  useEffect(() => {
    if (!catalogo) return;
    let activo = true;
    let consultando = false;
    const control = new AbortController();
    const id = setInterval(() => {
      if (consultando) return;
      consultando = true;
      obtenerStock(control.signal).then((stock) => {
        const items = stock.items;
        if (!activo) return;
        if (stock.origen !== catalogo.origen || stock.version !== catalogo.version) { setRevision(r => r + 1); return; }
        const cambioPromo = items.some((i) => (catalogo.productos.find((p) => p.id === i.producto_id)?.promocion?.id ?? null) !== i.promocion_id);
        if (cambioPromo) { setRevision((r) => r + 1); return; }
        setCatalogo((actual) => actual && {
          ...actual, disponibilidad_actualizada: stock.actualizada,
          productos: actual.productos.map((p) => {
            const item = items.find((i) => i.producto_id === p.id);
            return item && item.estado_stock !== p.estado_stock ? { ...p, estado_stock: item.estado_stock } : p;
          }),
        });
      }).catch(() => { if (activo) setCatalogo(c => c && ({ ...c, disponibilidad_actualizada: false })); }).finally(() => { consultando = false; });
    }, INTERVALO_STOCK_MS);
    return () => { activo = false; control.abort(); clearInterval(id); };
  }, [catalogo]);

  const actualizarCarrito = useCallback((cambio: (actual: LineaCarrito[]) => LineaCarrito[]) => {
    setCarrito((actual) => {
      const nuevo = cambio(actual).filter((l) => l.cantidad > 0);
      if (origenCarrito.current) escribir(CLAVE_CARRITO + ":" + origenCarrito.current, nuevo);
      return nuevo;
    });
  }, []);

  const mostrarAviso = useCallback((texto: string) => {
    setAviso(texto);
    clearTimeout(temporizadorAviso.current);
    temporizadorAviso.current = setTimeout(() => setAviso(""), 2600);
  }, []);

  const valor = useMemo<ContextoTienda>(() => ({
    catalogo,
    errorCatalogo,
    recargarCatalogo: () => setRevision((r) => r + 1),
    producto: (id) => catalogo?.productos.find((p) => p.id === id),
    carrito,
    unidadesCarrito: carrito.reduce((s, l) => s + l.cantidad, 0),
    agregar: (productoId, cantidad = 1) => {
      if (!catalogo?.productos.some(p => p.id === productoId && p.estado_stock !== "AGOTADO")) return;
      actualizarCarrito((actual) => {
        const existe = actual.find((l) => l.producto_id === productoId);
        if (!existe) return [...actual, { producto_id: productoId, cantidad: Math.min(cantidad, MAX_UNIDADES_POR_LINEA) }];
        return actual.map((l) => l.producto_id === productoId ? { ...l, cantidad: Math.min(l.cantidad + cantidad, MAX_UNIDADES_POR_LINEA) } : l);
      });
      const nombre = catalogo?.productos.find((p) => p.id === productoId)?.nombre;
      mostrarAviso(nombre ? `${nombre} se agregó a tu canasta` : "Producto agregado a tu canasta");
    },
    cambiarCantidad: (productoId, cantidad) => actualizarCarrito((actual) =>
      actual.map((l) => l.producto_id === productoId ? { ...l, cantidad: Math.max(0, Math.min(cantidad, MAX_UNIDADES_POR_LINEA)) } : l)),
    vaciarCarrito: () => actualizarCarrito(() => []),
    sesion,
    guardarSesion: (nueva) => { setSesion(nueva); escribir(CLAVE_SESION, nueva); },
    loginAbierto,
    abrirLogin: () => setLoginAbierto(true),
    cerrarLogin: () => setLoginAbierto(false),
    aviso,
  }), [catalogo, errorCatalogo, carrito, sesion, loginAbierto, aviso, actualizarCarrito, mostrarAviso]);

  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>;
}

export function useTienda(): ContextoTienda {
  const valor = useContext(Contexto);
  if (!valor) throw new Error("useTienda debe usarse dentro de ProveedorTienda");
  return valor;
}
