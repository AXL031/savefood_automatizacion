"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { MAX_UNIDADES_POR_LINEA, useTienda } from "@/tienda/contexto";
import { soles } from "@/tienda/dinero";
import { DATOS_COMERCIO, confirmarPedido, cotizarCarrito, validarEntrega, type Cotizacion } from "@/tienda/servicios";
import { ErrorTienda, type DatosEntrega, type MetodoPagoSimulado } from "@/tienda/tipos";
import { EstadoStock } from "@/tienda/componentes/EstadoStock";
import { Icono, IconoArchivo } from "@/tienda/componentes/Iconos";
import { QrFicticio } from "@/tienda/componentes/QrFicticio";

const ENTREGA_VACIA: DatosEntrega = { nombre_receptor: "", celular: "", direccion: "", distrito: "", referencia: "" };

function nuevaClave() {
  return typeof crypto !== "undefined" && "randomUUID" in crypto ? `web-${crypto.randomUUID()}` : `web-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function PaginaCarrito() {
  const router = useRouter();
  const { carrito, cambiarCantidad, vaciarCarrito, producto, catalogo, recargarCatalogo, sesion, abrirLogin, guardarSesion } = useTienda();
  const [cotizacion, setCotizacion] = useState<Cotizacion | null>(null);
  const [entrega, setEntrega] = useState<DatosEntrega>(ENTREGA_VACIA);
  const [tocados, setTocados] = useState(false);
  const [tipoPago, setTipoPago] = useState<"BILLETERA" | "TARJETA">("BILLETERA");
  const [billetera, setBilletera] = useState<"YAPE_SIMULADO" | "PLIN_SIMULADO">("YAPE_SIMULADO");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState("");
  const [copiado, setCopiado] = useState(false);
  const clave = useRef(nuevaClave());

  // Se recotiza cuando cambia la canasta o el stock visible (consulta en vivo del contexto).
  useEffect(() => {
    if (!carrito.length) { setCotizacion(null); return; }
    const control = new AbortController();
    cotizarCarrito(carrito, control.signal).then(setCotizacion).catch((e: unknown) => {
      if (!control.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo calcular el total.");
    });
    return () => control.abort();
  }, [carrito, catalogo]);

  // Cambiar la canasta es otro pedido: nueva clave idempotente.
  useEffect(() => { clave.current = nuevaClave(); }, [carrito]);

  const errores = validarEntrega(entrega);
  const hayErrores = Object.values(errores).some(Boolean);
  const sinStock = cotizacion?.lineas.some((l) => !l.disponible) ?? false;
  const metodo: MetodoPagoSimulado = tipoPago === "TARJETA" ? "TARJETA_SIMULADA" : billetera;

  function campo(nombre: keyof DatosEntrega, valor: string) {
    setEntrega((actual) => ({ ...actual, [nombre]: valor }));
  }

  async function confirmar(e: FormEvent) {
    e.preventDefault();
    setError("");
    if (!sesion) { abrirLogin(); return; }
    setTocados(true);
    if (hayErrores || !cotizacion || sinStock) return;
    setEnviando(true);
    try {
      const pedido = await confirmarPedido({
        clave_idempotencia: clave.current,
        lineas: cotizacion.lineas.map((l) => ({ producto_id: l.producto_id, cantidad: l.cantidad, subtotal_esperado: l.subtotal })),
        entrega: { ...entrega, celular: entrega.celular.replace(/\s/g, "") },
        metodo_pago_simulado: metodo,
      }, sesion);
      vaciarCarrito();
      recargarCatalogo();
      router.push(`/tienda/pedido/${pedido.id}`);
    } catch (fallo) {
      if (fallo instanceof ErrorTienda && (fallo.codigo === "PRECIO_CAMBIADO" || fallo.codigo === "STOCK_INSUFICIENTE")) {
        setCotizacion(await cotizarCarrito(carrito).catch(() => null));
        recargarCatalogo();
      }
      if (fallo instanceof ErrorTienda && fallo.codigo === "AUTENTICACION_REQUERIDA") { guardarSesion(null); abrirLogin(); }
      setError(fallo instanceof Error ? fallo.message : "No se pudo confirmar el pedido.");
    } finally {
      setEnviando(false);
    }
  }

  async function copiarNumero() {
    try { await navigator.clipboard.writeText(DATOS_COMERCIO.pago_simulado.numero.replace(/\s/g, "")); setCopiado(true); setTimeout(() => setCopiado(false), 1800); } catch { /* portapapeles no disponible */ }
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
    <form className="t-contenedor t-checkout" onSubmit={confirmar} noValidate>
      <div className="t-checkout-barra">
        <nav className="t-migas" aria-label="Ruta"><Link href="/tienda/menu"><Icono nombre="atras" tamano={14} />Seguir comprando</Link><span>/</span><span aria-current="page">Canasta y pago</span></nav>
        <span className="t-chip-vivo"><span className="t-punto-vivo" aria-hidden="true" />Precios y stock actualizados en vivo</span>
      </div>

      <div className="t-checkout-grid">
        <div className="t-checkout-pasos">
          <section className="t-paso" aria-labelledby="t-paso-1">
            <div className="t-paso-cabecera">
              <span className="t-paso-numero">1</span>
              <div><h2 id="t-paso-1">Paso 1: Tu cuenta</h2><p>Para confirmar tu pedido y consultarlo después, inicia sesión con Google.</p></div>
              {sesion ? <span className="t-chip-ok"><Icono nombre="check" tamano={12} />Identificado</span> : null}
            </div>
            {sesion ? (
              <div className="t-cuenta-tarjeta">
                <span className="t-avatar">{sesion.cliente.nombre.charAt(0).toUpperCase()}<span className="t-avatar-google"><IconoArchivo nombre="google" escala={0.6} /></span></span>
                <div><strong>{sesion.cliente.nombre}</strong><span>{sesion.cliente.correo}</span></div>
                <button type="button" className="t-boton-contorno" onClick={() => { guardarSesion(null); abrirLogin(); }}>Cambiar cuenta</button>
              </div>
            ) : (
              <button type="button" className="t-boton-google t-boton-google-ancho" onClick={abrirLogin}><IconoArchivo nombre="google" />Iniciar sesión con Google</button>
            )}
          </section>

          <section className="t-paso" aria-labelledby="t-paso-2">
            <div className="t-paso-cabecera">
              <span className="t-paso-numero">2</span>
              <div><h2 id="t-paso-2">Paso 2: Datos de entrega</h2><p>Entrega a domicilio en Lima Metropolitana.</p></div>
              <span className="t-chip-entrega"><Icono nombre="camion" tamano={14} />Envío a domicilio</span>
            </div>
            <div className="t-campos">
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
            </div>
          </section>

          <section className="t-paso" aria-labelledby="t-paso-3">
            <div className="t-paso-cabecera">
              <span className="t-paso-numero">3</span>
              <div><h2 id="t-paso-3">Paso 3: Método de pago</h2><p>Pago simulado: no se realiza ningún cobro real.</p></div>
            </div>
            <div className="t-pagos" role="radiogroup" aria-label="Método de pago">
              <label className={`t-pago${tipoPago === "BILLETERA" ? " t-pago-activo" : ""}`}>
                <input type="radio" name="pago" checked={tipoPago === "BILLETERA"} onChange={() => setTipoPago("BILLETERA")} />
                <span><strong>Billeteras digitales</strong><span className="t-chip-salmon">Recomendado</span><small>Yape o Plin</small></span>
              </label>
              <label className={`t-pago${tipoPago === "TARJETA" ? " t-pago-activo" : ""}`}>
                <input type="radio" name="pago" checked={tipoPago === "TARJETA"} onChange={() => setTipoPago("TARJETA")} />
                <span><strong>Tarjeta de débito / crédito</strong><small>Simulada, sin datos de tarjeta</small></span>
              </label>
            </div>
            {tipoPago === "BILLETERA" ? (
              <div className="t-transferencia">
                <div className="t-qr-marco"><QrFicticio /><span>Yape · Plin</span></div>
                <div className="t-transferencia-datos">
                  <div className="t-transferencia-cabecera">
                    <span>Datos de pago</span>
                    <span className="t-chip-ok t-chip-pequeno">Pago simulado</span>
                  </div>
                  <div className="t-billeteras" role="radiogroup" aria-label="Billetera">
                    {(["YAPE_SIMULADO", "PLIN_SIMULADO"] as const).map((b) => (
                      <label key={b} className={billetera === b ? "t-billetera-activa" : ""}>
                        <input type="radio" name="billetera" checked={billetera === b} onChange={() => setBilletera(b)} />{b === "YAPE_SIMULADO" ? "Yape" : "Plin"}
                      </label>
                    ))}
                  </div>
                  <div className="t-numero-receptor">
                    <div><small>Número de celular receptor</small><strong>{DATOS_COMERCIO.pago_simulado.numero}</strong></div>
                    <button type="button" className="t-boton-copiar" onClick={copiarNumero}><Icono nombre="copiar" tamano={14} />{copiado ? "Copiado" : "Copiar"}</button>
                  </div>
                  <p className="t-titular">Titular: <strong>{DATOS_COMERCIO.pago_simulado.titular}</strong></p>
                  <p className="t-aviso-simulado"><Icono nombre="check" tamano={14} /><span><strong>No transfieras dinero.</strong> El QR y el número son de demostración; al confirmar se registra un pago simulado aprobado.</span></p>
                </div>
              </div>
            ) : (
              <div className="t-transferencia t-transferencia-tarjeta">
                <span className="t-tarjeta-icono"><Icono nombre="tarjeta" tamano={28} /></span>
                <p className="t-aviso-simulado"><span><strong>Pago con tarjeta simulado.</strong> No ingreses ni compartas datos de tarjeta: al confirmar se registra un pago aprobado de demostración.</span></p>
              </div>
            )}
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
                    {p ? <img src={p.imagen} alt="" /> : <span className="t-linea-sin-imagen" />}
                    <div className="t-linea-datos">
                      <strong>{p?.nombre ?? "Producto"}</strong>
                      <span>{p ? soles(p.precio) : ""} c/u{cot?.unidades_con_promocion ? ` · ${cot.unidades_con_promocion} con promoción` : ""}</span>
                      <div className="t-cantidad">
                        <button type="button" onClick={() => cambiarCantidad(linea.producto_id, linea.cantidad - 1)} aria-label={`Quitar una unidad de ${p?.nombre ?? "producto"}`}><Icono nombre="menos" tamano={12} /></button>
                        <span aria-live="polite">{linea.cantidad}</span>
                        <button type="button" onClick={() => cambiarCantidad(linea.producto_id, linea.cantidad + 1)} disabled={linea.cantidad >= MAX_UNIDADES_POR_LINEA} aria-label={`Agregar una unidad de ${p?.nombre ?? "producto"}`}><Icono nombre="mas" tamano={12} /></button>
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
              <div className="t-total"><dt>Total a pagar<small>Pago simulado</small></dt><dd>{cotizacion ? soles(cotizacion.total) : "…"}</dd></div>
            </dl>
            {error ? <p className="t-error" role="alert">{error}</p> : null}
            {tocados && hayErrores ? <p className="t-error" role="alert">Completa los datos de entrega obligatorios.</p> : null}
            <button type="submit" className="t-boton-confirmar" disabled={enviando || !cotizacion || sinStock}>
              <IconoArchivo nombre="candado" escala={1.2} />
              {enviando ? "Confirmando…" : sesion ? `Confirmar pedido (${cotizacion ? soles(cotizacion.total) : "…"})` : "Iniciar sesión y confirmar"}
            </button>
            <p className="t-resumen-nota"><span className="t-marca-sello t-marca-sello-pequeno"><IconoArchivo nombre="huella" escala={0.7} /></span>Al confirmar, el stock se descuenta al instante y tu pedido queda registrado.</p>
          </div>
        </aside>
      </div>
    </form>
  );
}
