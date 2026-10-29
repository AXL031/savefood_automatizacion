"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { MAX_UNIDADES_POR_LINEA, useTienda } from "@/tienda/contexto";
import { soles } from "@/tienda/dinero";
import { cotizarCarrito, validarEntrega, type Cotizacion } from "@/tienda/servicios";
import { type DatosEntrega } from "@/tienda/tipos";
import { EstadoStock } from "@/tienda/componentes/EstadoStock";
import { Icono, IconoArchivo } from "@/tienda/componentes/Iconos";
import { PagoPayme } from "@/tienda/componentes/PagoPayme";
import { LogoTienda } from "@/tienda/componentes/LogoTienda";

const ENTREGA_VACIA: DatosEntrega = { nombre_receptor: "", celular: "", direccion: "", distrito: "", referencia: "" };

export default function PaginaCarrito() {
  const router = useRouter();
  const { carrito, cambiarCantidad, vaciarCarrito, producto, catalogo, recargarCatalogo, sesion } = useTienda();
  const [cotizacion, setCotizacion] = useState<Cotizacion | null>(null);
  const [entrega, setEntrega] = useState<DatosEntrega>(ENTREGA_VACIA);
  const [tocados, setTocados] = useState(false);
  const [bloqueado, setBloqueado] = useState(false);
  const [error, setError] = useState("");

  // Se recotiza cuando cambia la canasta o el stock visible (consulta en vivo del contexto).
  useEffect(() => {
    if (bloqueado) return; // El pago iniciado conserva su cotización/reserva congeladas.
    if (!carrito.length || !catalogo) { setCotizacion(null); return; }
    setCotizacion(null); setError("");
    const control = new AbortController();
    cotizarCarrito(carrito, catalogo.origen, control.signal).then(setCotizacion).catch((e: unknown) => {
      if (!control.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo calcular el total.");
    });
    return () => control.abort();
  }, [carrito, catalogo, bloqueado]);

  const errores = validarEntrega(entrega);
  const hayErrores = Object.values(errores).some(Boolean);
  const sinStock = cotizacion?.lineas.some(l => !l.disponible) ?? false;

  function campo(nombre: keyof DatosEntrega, valor: string) {
    setEntrega((actual) => ({ ...actual, [nombre]: valor }));
  }

  function prepararPago() {
    setTocados(true);
    return !hayErrores && Boolean(cotizacion) && !sinStock;
  }
  function aprobado(id: string) {
    vaciarCarrito(); recargarCatalogo();
    router.push(`/tienda/pedido/payme-${id}`);
  }

  if (!carrito.length) {
    return (
      <div className="t-contenedor t-estado">
        <span className="t-estado-icono"><IconoArchivo nombre="canasta" escala={2} /></span>
        <h1>Tu canasta está vacía</h1>
        <p>Agrega panes, tortas o postres del día para armar tu pedido.</p>
        <Link href="/tienda/menu" className="t-boton-primario">Ver el menú</Link>
      </div>
    );
  }

  const mostrar = (c: keyof DatosEntrega) => tocados && errores[c];

  return (
    <div className="t-contenedor t-checkout">
      <div className="t-checkout-barra">
        <nav className="t-migas" aria-label="Ruta"><Link href="/tienda/menu"><Icono nombre="atras" tamano={14} />Seguir comprando</Link><span>/</span><span aria-current="page">Canasta y pago</span></nav>
        <span className="t-chip-vivo"><span className="t-punto-vivo" aria-hidden="true" />{catalogo?.modo === "api" ? "Catálogo de FoodSave" : "Catálogo de ejemplo"}</span>
      </div>

      <div className="t-checkout-grid">
        <div className="t-checkout-pasos">
          <section className="t-paso" aria-labelledby="t-paso-1">
            <div className="t-paso-cabecera">
              <span className="t-paso-numero">1</span>
              <div><h2 id="t-paso-1">Paso 1: Datos de entrega</h2><p>Entrega a domicilio en Lima Metropolitana.</p></div>
              <span className="t-chip-entrega"><Icono nombre="camion" tamano={14} />Envío a domicilio</span>
            </div>
            <fieldset className="t-campos t-entrega-campos" disabled={bloqueado}>
              <label className="t-campo t-campo-ancho">
                <span className="t-campo-etiqueta">1. Dirección exacta de entrega <em>*Obligatorio</em></span>
                <span className="t-campo-caja"><IconoArchivo nombre="ubicacion" /><input value={entrega.direccion} onChange={(e) => campo("direccion", e.target.value)} placeholder="Av. Primavera 640, Dpto 402" autoComplete="street-address" maxLength={200} aria-invalid={Boolean(mostrar("direccion"))} /></span>
                {mostrar("direccion") ? <span className="t-campo-error">{errores.direccion}</span> : null}
              </label>
              <label className="t-campo">
                <span className="t-campo-etiqueta">Distrito <em>*Obligatorio</em></span>
                <span className="t-campo-caja"><input value={entrega.distrito} onChange={(e) => campo("distrito", e.target.value)} placeholder="San Borja" autoComplete="address-level2" maxLength={80} aria-invalid={Boolean(mostrar("distrito"))} /></span>
                {mostrar("distrito") ? <span className="t-campo-error">{errores.distrito}</span> : null}
              </label>
              <label className="t-campo">
                <span className="t-campo-etiqueta">Referencia <small>(opcional)</small></span>
                <span className="t-campo-caja"><input value={entrega.referencia} onChange={(e) => campo("referencia", e.target.value)} placeholder="Frente al parque" maxLength={200} /></span>
              </label>
              <label className="t-campo">
                <span className="t-campo-etiqueta">2. Número de celular <em>*Obligatorio</em></span>
                <span className="t-campo-caja"><span className="t-prefijo">+51</span><input value={entrega.celular} onChange={(e) => campo("celular", e.target.value.replace(/[^\d ]/g, ""))} placeholder="987 654 321" inputMode="tel" autoComplete="tel-national" maxLength={11} aria-invalid={Boolean(mostrar("celular"))} /></span>
                {mostrar("celular") ? <span className="t-campo-error">{errores.celular}</span> : <span className="t-campo-ayuda">Para coordinar la llegada de tu pedido.</span>}
              </label>
              <label className="t-campo">
                <span className="t-campo-etiqueta">3. Persona que recibirá el pedido <em>*Obligatorio</em></span>
                <span className="t-campo-caja t-campo-caja-icono"><Icono nombre="persona" tamano={16} /><input value={entrega.nombre_receptor} onChange={(e) => campo("nombre_receptor", e.target.value)} placeholder="María Elena Rojas" autoComplete="name" maxLength={120} aria-invalid={Boolean(mostrar("nombre_receptor"))} /></span>
                {mostrar("nombre_receptor") ? <span className="t-campo-error">{errores.nombre_receptor}</span> : <span className="t-campo-ayuda">Indicará su nombre al repartidor.</span>}
              </label>
            </fieldset>
          </section>

          <section className="t-paso" aria-labelledby="t-paso-2">
            <div className="t-paso-cabecera">
              <span className="t-paso-numero">2</span>
              <div><h2 id="t-paso-2">Paso 2: Método de pago</h2><p>Elige cómo quieres pagar tu pedido.</p></div>
            </div>
            <PagoPayme lineas={carrito} entrega={entrega} cotizacion={cotizacion} nombre={sesion?.cliente.nombre ?? ""}
              correo={sesion?.cliente.correo ?? ""} alIntentar={prepararPago} alAprobar={aprobado} alBloquear={setBloqueado} />
          </section>
        </div>

        <aside className="t-resumen" aria-label="Tu canasta">
          <div className="t-resumen-tarjeta">
            <div className="t-resumen-cabecera">
              <h2><IconoArchivo nombre="canasta" /> Tu canasta</h2>
              <span className="t-chip-crema">{carrito.reduce((s, l) => s + l.cantidad, 0)} productos</span>
            </div>
            <ul className="t-resumen-lineas">
              {carrito.map((linea) => {
                const p = producto(linea.producto_id);
                const cot = cotizacion?.lineas.find((l) => l.producto_id === linea.producto_id);
                return (
                  <li key={linea.producto_id} className={cot && !cot.disponible ? "t-linea-sin-stock" : ""}>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    {p?.imagen ? <img src={p.imagen} alt="" /> : <span className="t-linea-sin-imagen" aria-label="Sin imagen del producto" />}
                    <div className="t-linea-datos">
                      <strong>{p?.nombre ?? cot?.nombre ?? "Producto retirado del menú"}</strong>
                      {!p && !bloqueado && <span className="t-linea-aviso">Este producto ya no está publicado. Quítalo para continuar.</span>}
                      <span>{p ? soles(p.precio) : ""} c/u{cot?.unidades_con_promocion ? ` · ${cot.unidades_con_promocion} con promoción` : ""}</span>
                      <div className="t-cantidad">
                        <button type="button" disabled={bloqueado} onClick={() => cambiarCantidad(linea.producto_id, linea.cantidad - 1)} aria-label={`Quitar una unidad de ${p?.nombre ?? "producto"}`}><Icono nombre="menos" tamano={12} /></button>
                        <span aria-live="polite">{linea.cantidad}</span>
                        <button type="button" onClick={() => cambiarCantidad(linea.producto_id, linea.cantidad + 1)} disabled={bloqueado || linea.cantidad >= MAX_UNIDADES_POR_LINEA} aria-label={`Agregar una unidad de ${p?.nombre ?? "producto"}`}><Icono nombre="mas" tamano={12} /></button>
                      </div>
                      {cot && !cot.disponible ? <span className="t-linea-aviso"><EstadoStock estado={cot.estado_stock} /> Reduce la cantidad o quítalo.</span> : null}
                    </div>
                    <strong className="t-linea-subtotal">{cot ? soles(cot.subtotal) : "…"}</strong>
                  </li>
                );
              })}
            </ul>
            <dl className="t-totales">
              <div><dt>Subtotal</dt><dd>{cotizacion ? soles(cotizacion.total) : "…"}</dd></div>
              <div><dt>Envío a domicilio</dt><dd><span className="t-chip-ok t-chip-pequeno">Sin costo</span></dd></div>
              <div className="t-total"><dt>Total a pagar</dt><dd>{cotizacion ? soles(cotizacion.total) : "…"}</dd></div>
            </dl>
            {error ? <p className="t-error" role="alert">{error}</p> : null}
            {tocados && hayErrores ? <p className="t-error" role="alert">Completa los datos obligatorios de entrega.</p> : null}
            <p className="t-resumen-nota"><LogoTienda tamano={34} />{catalogo?.modo === "api" ? "Pago Payme de preproducción. La venta se confirma en FoodSave al verificar el pago y consumir su reserva." : "Pago Payme de preproducción sobre catálogo de ejemplo, sin movimiento de inventario FoodSave."}</p>
          </div>
        </aside>
      </div>
    </div>
  );
}
