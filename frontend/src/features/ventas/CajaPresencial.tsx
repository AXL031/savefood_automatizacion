"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import type { ContextoSesion } from "@/components/layout/ProtectedShell";
import { PanelDetalle } from "@/components/ui/PanelDetalle";
import { TablaDatos } from "@/components/tables/TablaDatos";
import { HttpError } from "@/services/http";
import { catalogoCaja, guardarPrecioCaja, cotizarCaja, registrarCaja, recuperarCaja, listarCaja, detalleCaja, anularCaja } from "@/services/ventas";
import type { CatalogoCaja, CotizacionCaja, EntradaCaja, MedioCaja, ProductoCaja, TicketCaja } from "@/types/ventas";
import { formatearFechaHora } from "@/utils/fechas";

const soles = (v: string) => new Intl.NumberFormat("es-PE", { style: "currency", currency: "PEN" }).format(Number(v));
const nuevaClave = (tipo: string) => `${tipo}-${crypto.randomUUID()}`;
const medios: { valor: MedioCaja; texto: string }[] = [{ valor: "EFECTIVO", texto: "Efectivo" }, { valor: "TARJETA", texto: "Tarjeta" }, { valor: "YAPE", texto: "Yape" }, { valor: "QR", texto: "QR billeteras" }, { valor: "PAGOEFECTIVO", texto: "PagoEfectivo" }];
export function importeCaja(v: string): string {
  const limpio = v.trim().replace(",", ".");
  if (!/^\d{1,6}(\.\d{1,2})?$/.test(limpio)) throw new Error("Ingresa un importe válido con hasta dos decimales.");
  const [entero, decimales = ""] = limpio.split(".");
  return `${entero}.${decimales.padEnd(2, "0")}`;
}

export function CajaPresencial({ contexto }: { contexto: ContextoSesion }) {
  const { token, perfil, negocio } = contexto;
  const admin = perfil.rol === "ADMINISTRADOR";
  const almacen = `foodsave:caja:pendiente:${perfil.id}`;
  const [catalogo, setCatalogo] = useState<CatalogoCaja | null>(null), [tickets, setTickets] = useState<TicketCaja[]>([]);
  const [cargando, setCargando] = useState(true), [ocupado, setOcupado] = useState(false), [revision, setRevision] = useState(0);
  const [error, setError] = useState(""), [mensaje, setMensaje] = useState("");
  const [pagina, setPagina] = useState(1), [tamano, setTamano] = useState(25), [total, setTotal] = useState(0), [importe, setImporte] = useState("0.00");
  const [canal, setCanal] = useState("");
  const [desde, setDesde] = useState(""), [hasta, setHasta] = useState(""), [estado, setEstado] = useState("");
  const [nueva, setNueva] = useState(false), [detalle, setDetalle] = useState<TicketCaja | null>(null);
  const [producto, setProducto] = useState(""), [lineas, setLineas] = useState<{ producto_id: number; cantidad: number }[]>([]);
  const [cotizacion, setCotizacion] = useState<CotizacionCaja | null>(null), [medio, setMedio] = useState<MedioCaja>("EFECTIVO"), [recibido, setRecibido] = useState("");
  const [pendiente, setPendiente] = useState<EntradaCaja | null>(null);
  const [precio, setPrecio] = useState<ProductoCaja | null>(null), [valorPrecio, setValorPrecio] = useState("");
  const precioSolicitud = useRef<{ clave_idempotencia: string; precio: string; version_actual: number } | null>(null);
  const [busquedaPrecio, setBusquedaPrecio] = useState("");
  const [catalogoAbierto, setCatalogoAbierto] = useState(false);
  const [motivo, setMotivo] = useState(""), [noEntregada, setNoEntregada] = useState(false);
  const claveAnulacion = useRef("");
  const confirmando = useRef(false);

  const recargar = useCallback(() => { setPagina(1); setRevision(r => r + 1); }, []);
  useEffect(() => {
    const c = new AbortController();
    catalogoCaja(token, c.signal).then(v => { if (!c.signal.aborted) setCatalogo(v); })
      .catch(e => { if (!c.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo cargar el catálogo."); });
    return () => c.abort();
  }, [token, revision]);
  useEffect(() => {
    const c = new AbortController(); setCargando(true);
    const q = new URLSearchParams({ limite: String(tamano), desplazamiento: String((pagina - 1) * tamano) });
    if (canal) q.set("canal", canal);
    if (desde) q.set("desde", desde); if (hasta) q.set("hasta", hasta); if (estado) q.set("estado", estado);
    listarCaja(token, q, c.signal).then(v => { if (!c.signal.aborted) { setTickets(v.datos); setTotal(Number(v.metadatos?.total ?? 0)); setImporte(String(v.metadatos?.importe_confirmado ?? "0.00")); } })
      .catch(e => { if (!c.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo leer el historial."); })
      .finally(() => { if (!c.signal.aborted) setCargando(false); });
    return () => c.abort();
  }, [token, revision, pagina, tamano, desde, hasta, estado, canal]);
  useEffect(() => {
    let activa = true;
    try {
      const guardada = sessionStorage.getItem(almacen);
      if (guardada) {
        const p = JSON.parse(guardada) as EntradaCaja; setPendiente(p);
        recuperarCaja(token, p.clave_idempotencia).then(t => {
          if (!activa) return;
          sessionStorage.removeItem(almacen); setPendiente(null); setDetalle(t); setMensaje(`Venta ${t.numero} recuperada. Su inventario ya estaba registrado.`); recargar();
        }).catch(() => { if (activa) setMensaje("Hay una venta pendiente de respuesta. Consulta su resultado o reintenta la misma confirmación."); });
      }
    } catch { setError("No se pudo leer la recuperación de caja en este navegador."); }
    return () => { activa = false; };
  }, [almacen, token, recargar]);

  function abrirNueva() {
    setError(""); setMensaje(""); setNueva(true);
    if (!pendiente) { setProducto(""); setLineas([]); setCotizacion(null); setMedio("EFECTIVO"); setRecibido(""); }
  }
  async function cotizar() {
    setOcupado(true); setError("");
    try { const c = await cotizarCaja(token, lineas, nuevaClave("cotizacion")); setCotizacion(c); setRecibido(c.total); }
    catch (e) { setError(e instanceof Error ? e.message : "No se pudo cotizar."); }
    finally { setOcupado(false); }
  }
  async function confirmar() {
    if (confirmando.current) return;
    confirmando.current = true;
    setOcupado(true); setError("");
    let solicitud = pendiente;
    try {
      if (!solicitud) {
        if (!cotizacion) throw new Error("Cotiza antes de confirmar.");
        solicitud = { clave_idempotencia: nuevaClave("venta"), cotizacion_id: cotizacion.id, total_revisado: cotizacion.total,
          cobro_presencial: { medio, importe_recibido: medio === "EFECTIVO" ? importeCaja(recibido) : cotizacion.total } };
        sessionStorage.setItem(almacen, JSON.stringify(solicitud)); setPendiente(solicitud);
      }
      const ticket = await registrarCaja(token, solicitud);
      sessionStorage.removeItem(almacen); setPendiente(null); setNueva(false); setCotizacion(null);
      setDetalle(ticket); setMensaje(`Venta ${ticket.numero} registrada. Stock actualizado.`); recargar();
    } catch (e) {
      if (e instanceof HttpError && e.status >= 400 && e.status < 500 && e.status !== 401) {
        sessionStorage.removeItem(almacen); setPendiente(null); setCotizacion(null);
      }
      setError(e instanceof Error ? e.message : "No se confirmó la respuesta. Reintenta la misma venta.");
    } finally { confirmando.current = false; setOcupado(false); }
  }
  async function ver(id: number) {
    setError(""); setOcupado(true);
    try { setDetalle(await detalleCaja(token, id)); setMotivo(""); setNoEntregada(false); claveAnulacion.current = nuevaClave("anular"); }
    catch (e) { setError(e instanceof Error ? e.message : "No se pudo leer la venta."); }
    finally { setOcupado(false); }
  }
  async function anular() {
    if (!detalle) return; setOcupado(true); setError("");
    if (!claveAnulacion.current) claveAnulacion.current = nuevaClave("anular");
    try {
      const t = await anularCaja(token, detalle.id, { clave_idempotencia: claveAnulacion.current, motivo, mercancia_no_entregada: true });
      setDetalle(t); setMensaje(`Venta ${t.numero} anulada. Compensación de stock registrada.`); recargar();
    } catch (e) { setError(e instanceof Error ? e.message : "No se pudo anular."); }
    finally { setOcupado(false); }
  }
  async function guardarPrecio() {
    if (!precio) return; setOcupado(true); setError("");
    try {
      precioSolicitud.current ??= { clave_idempotencia: nuevaClave("precio"), precio: importeCaja(valorPrecio), version_actual: precio.version_precio };
      await guardarPrecioCaja(token, precio.id, precioSolicitud.current);
      setPrecio(null); precioSolicitud.current = null; recargar(); setMensaje("Precio guardado. Las ventas anteriores conservan su importe.");
    } catch (e) {
      if (e instanceof HttpError && e.status >= 400 && e.status < 500) { precioSolicitud.current = null; recargar(); }
      setError(e instanceof Error ? e.message : "No se pudo guardar el precio.");
    } finally { setOcupado(false); }
  }
  const productos = catalogo?.productos ?? [];
  const elegibles = productos.filter(p => p.precio !== null && (p.disponible ?? 0) > 0);
  const sinPrecio = productos.filter(p => p.precio === null).length;
  const sinStock = productos.filter(p => (p.disponible ?? 0) <= 0).length;
  const errores = error && <p className="inline-error" role="alert">{error}</p>;
  return <>
    <section className="card section-space">
      <div className="section-heading"><div><h2>Caja e historial de ventas</h2><p>Registra ventas presenciales y consulta las compras confirmadas de la tienda.</p></div><div className="form-actions"><button className="button-secondary" disabled={ocupado} onClick={() => { setError(""); setRevision(r => r + 1); }}>Actualizar</button><button className="button-primary" disabled={ocupado || !catalogo} onClick={abrirNueva}>{pendiente ? "Resolver venta pendiente" : "Registrar venta"}</button></div></div>
      <p className="helper-text">{catalogo ? `Fecha de caja: ${catalogo.fecha_local} · ${catalogo.zona_horaria}.` : "Consultando catálogo y stock…"} El medio de cobro se registra; esta pantalla no procesa pagos.</p>
      {mensaje && <p className="inline-success" role="status">{mensaje}</p>}{!nueva && !detalle && !precio && errores}
      {pendiente && <p className="inline-error" role="status">Una confirmación requiere recuperar su respuesta. Se conserva la misma operación al reintentar.</p>}
      {catalogo && !elegibles.length && <p className="helper-text">Para registrar ventas, configura precios y revisa que existan productos con stock y fecha límite de venta vigentes en Inventario. Los lotes históricos vencidos no se venden en la fecha actual.</p>}
      <div className="form-grid"><label className="field">Desde<input type="date" value={desde} max={hasta || undefined} onChange={e => { setDesde(e.target.value); setPagina(1); }} /></label><label className="field">Hasta<input type="date" value={hasta} min={desde || undefined} onChange={e => { setHasta(e.target.value); setPagina(1); }} /></label><label className="field">Estado<select value={estado} onChange={e => { setEstado(e.target.value); setPagina(1); }}><option value="">Todos</option><option value="CONFIRMADA">Confirmadas</option><option value="ANULADA">Anuladas</option></select></label><label className="field">Canal<select value={canal} onChange={e => { setCanal(e.target.value); setPagina(1); }}><option value="">Todos</option><option value="PRESENCIAL">Presencial</option><option value="TIENDA">Tienda</option></select></label></div>
      <p><strong>{total} venta(s)</strong> · Importe confirmado del filtro: <strong>{soles(importe)}</strong></p>
      <TablaDatos filas={tickets} idFila={t => t.id} cargando={cargando} vacioTitulo="Todavía no hay ventas registradas" vacioDescripcion="Las ventas que registres aparecerán aquí. Puedes conservar y consultar el histórico importado en su pestaña." paginacion={{ pagina, tamano, total, cargando, onCambio: (p,t) => { setPagina(p); setTamano(t); } }} columnas={[
        { clave: "numero", encabezado: "Venta", celda: t => <strong>{t.numero}</strong> },
        { clave: "canal", encabezado: "Canal", celda: t => t.canal === "TIENDA" ? "Tienda · Payme sandbox" : "Presencial" },
        { clave: "fecha", encabezado: "Fecha y hora", celda: t => formatearFechaHora(t.vendida_en, negocio.zona_horaria) },
        { clave: "unidades", encabezado: "Unidades", celda: t => t.unidades },
        { clave: "total", encabezado: "Total", celda: t => soles(t.total) },
        { clave: "estado", encabezado: "Estado", celda: t => <span className={`badge badge-${t.estado === "ANULADA" ? "neutral" : "ok"}`}>{t.estado === "ANULADA" ? "Anulada" : "Confirmada"}</span> },
        { clave: "ver", encabezado: "Detalle", celda: t => <button className="button-link" disabled={ocupado} onClick={() => void ver(t.id)}>Ver venta</button> }
      ]} />
    </section>
    <details className="card section-space" open={catalogoAbierto} onToggle={e => setCatalogoAbierto(e.currentTarget.open)}><summary>Catálogo y precios de caja · {productos.length} productos</summary><p>Los precios se conservan por versión. {admin ? "Configura el precio antes de vender cada producto." : "Un administrador configura los precios."}</p><label className="field">Buscar producto<input type="search" value={busquedaPrecio} onChange={e => setBusquedaPrecio(e.target.value)} /></label>
      <TablaDatos filas={productos.filter(p => `${p.nombre} ${p.codigo}`.toLowerCase().includes(busquedaPrecio.toLowerCase()))} idFila={p => p.id} columnas={[
        { clave: "nombre", encabezado: "Producto", celda: p => <><strong>{p.nombre}</strong><small className="helper-text"> · {p.codigo}</small></> },
        { clave: "precio", encabezado: "Precio", celda: p => p.precio ? soles(p.precio) : "Sin configurar" },
        { clave: "stock", encabezado: "Vendible hoy", celda: p => p.disponible === null ? "Stock desconocido" : `${p.disponible} u.${p.aviso_caducidad ? " · caducidad sin informar" : ""}` },
        { clave: "editar", encabezado: "Precio", celda: p => admin ? <button className="button-link" disabled={ocupado} onClick={() => { setPrecio(p); setValorPrecio(p.precio ?? ""); precioSolicitud.current = null; setError(""); }}>Configurar precio</button> : "Consulta" }
      ]} />
    </details>
    {nueva && <PanelDetalle titulo={pendiente ? "Recuperar confirmación de venta" : "Registrar venta presencial"} ocupado={ocupado} onCerrar={() => setNueva(false)}>{errores}
      {!cotizacion && !pendiente && !elegibles.length && <section className="card section-space" aria-label="Disponibilidad para registrar ventas" role="status">
        <h3>No hay productos disponibles para vender</h3>
        <p>{productos.length ? `Hay ${productos.length} productos en el catálogo. ${sinPrecio ? `${sinPrecio} sin precio de caja. ` : "Todos tienen precio en soles. "}${sinStock ? `${sinStock} sin stock vendible para hoy.` : ""}` : "El catálogo todavía no contiene productos activos."}</p>
        <p>Para agregar un producto necesitas un precio y unidades en lotes con fecha límite de venta vigente. Los lotes vencidos o sin fecha límite no están disponibles.</p>
        <div className="form-actions"><button type="button" className="button-secondary" onClick={() => { setNueva(false); setCatalogoAbierto(true); }}>Revisar catálogo y precios</button><a className="button-secondary" href="/inventario">Revisar inventario</a></div>
      </section>}
      {!cotizacion && !pendiente && <><p>Selecciona productos con precio y stock vendible. La fecha y el importe se validan en el servidor.</p><div className="sale-product-picker"><label className="field">Producto<select value={producto} onChange={e => setProducto(e.target.value)} disabled={ocupado || !elegibles.length}><option value="">{elegibles.length ? "Selecciona un producto" : "Sin productos disponibles"}</option>{elegibles.map(p => <option key={p.id} value={p.id}>{p.nombre} · {soles(p.precio!)} · {p.disponible} u.</option>)}</select></label><button className="button-secondary" disabled={!producto || ocupado} onClick={() => { const id = Number(producto); setLineas(ls => ls.some(l => l.producto_id === id) ? ls.map(l => l.producto_id === id ? { ...l, cantidad: Math.min(1000, l.cantidad + 1) } : l) : [...ls, { producto_id: id, cantidad: 1 }]); }}>Agregar</button></div>
        <ul className="sale-cart">{lineas.map(l => <li key={l.producto_id}><strong>{productos.find(p => p.id === l.producto_id)?.nombre}</strong><label className="field">Cantidad<input type="number" min={1} max={1000} value={l.cantidad} disabled={ocupado} onChange={e => setLineas(ls => ls.map(x => x.producto_id === l.producto_id ? { ...x, cantidad: Number(e.target.value) } : x))} /></label><button className="button-link" disabled={ocupado} onClick={() => setLineas(ls => ls.filter(x => x.producto_id !== l.producto_id))}>Quitar</button></li>)}</ul>
        <button className="button-primary" disabled={ocupado || !lineas.length || lineas.some(l => !Number.isInteger(l.cantidad) || l.cantidad < 1 || l.cantidad > 1000)} onClick={() => void cotizar()}>{ocupado ? "Cotizando…" : "Cotizar y revisar"}</button></>}
      {cotizacion && !pendiente && <><h3>Revisa tu venta</h3><ul>{cotizacion.lineas.map(l => <li key={l.producto_id}>{l.nombre} · {l.cantidad} u. · Precio base {soles(l.precio)} · Total <strong>{soles(l.subtotal)}</strong></li>)}</ul><p className="sale-total">Total: {soles(cotizacion.total)}</p><p className="helper-text">Cotización válida hasta {formatearFechaHora(cotizacion.vence_en, negocio.zona_horaria)}. El stock se verifica al confirmar.</p><label className="field">Medio de cobro<select value={medio} disabled={ocupado} onChange={e => setMedio(e.target.value as MedioCaja)}>{medios.map(m => <option key={m.valor} value={m.valor}>{m.texto}</option>)}</select></label>{medio === "EFECTIVO" && <label className="field">Importe recibido (PEN)<input inputMode="decimal" value={recibido} disabled={ocupado} onChange={e => setRecibido(e.target.value)} /></label>}<p>Confirma cuando hayas recibido el cobro. Se guardará la venta y se descontará el stock una sola vez.</p><div className="form-actions"><button className="button-secondary" disabled={ocupado} onClick={() => setCotizacion(null)}>Cambiar productos</button><button className="button-primary" disabled={ocupado} onClick={() => void confirmar()}>Confirmar venta</button></div></>}
      {pendiente && <><p>Operación pendiente por {soles(pendiente.total_revisado)}. Reintentar utiliza la misma clave y cotización, conservadas en este navegador.</p><button className="button-primary" disabled={ocupado} onClick={() => void confirmar()}>{ocupado ? "Consultando confirmación…" : "Recuperar o confirmar la misma venta"}</button></>}
    </PanelDetalle>}
    {precio && <PanelDetalle titulo={`Precio de ${precio.nombre}`} ocupado={ocupado} onCerrar={() => setPrecio(null)}>{errores}<form onSubmit={e => { e.preventDefault(); void guardarPrecio(); }}><label className="field">Precio por unidad (PEN)<input required inputMode="decimal" value={valorPrecio} disabled={ocupado || Boolean(precioSolicitud.current)} onChange={e => setValorPrecio(e.target.value)} /></label><p className="helper-text">Versión revisada: {precio.version_precio}. Las cotizaciones anteriores deben revisarse si cambia el precio.</p><button className="button-primary" disabled={ocupado}>{ocupado ? "Guardando…" : "Guardar precio"}</button></form></PanelDetalle>}
    {detalle && <PanelDetalle titulo={`Venta ${detalle.numero}`} ocupado={ocupado} onCerrar={() => { setDetalle(null); setError(""); setMotivo(""); setNoEntregada(false); claveAnulacion.current = ""; }}>{errores}<p><strong>{detalle.estado === "ANULADA" ? "Anulada" : "Confirmada"}</strong> · {detalle.canal === "TIENDA" ? "Tienda · Payme preproducción" : "Presencial"} · {formatearFechaHora(detalle.vendida_en, detalle.zona_horaria)} · Registró {detalle.nombre_usuario}</p><ul>{detalle.lineas.map(l => <li key={l.id}>{l.nombre} · {l.cantidad} u. · Precio base {soles(l.precio)} · Total <strong>{soles(l.subtotal)}</strong><details><summary>Trazabilidad de stock</summary><ul>{l.salidas.map(a => <li key={a.movimiento_id}>Lote #{a.lote_id} · {a.cantidad} u. · movimiento #{a.movimiento_id}{a.compensacion_id ? ` · compensado por #${a.compensacion_id}` : ""}</li>)}</ul></details></li>)}</ul><p className="sale-total">Total: {soles(detalle.total)}</p><p>{detalle.canal === "TIENDA" ? "Pago verificado por la tienda:" : "Cobro declarado:"} {medios.find(m => m.valor === detalle.cobro.medio)?.texto} · Recibido {soles(detalle.cobro.importe_recibido)} · Vuelto {soles(detalle.cobro.vuelto)}</p>
      {detalle.anulacion && <p className="inline-error">Anulada por {detalle.anulacion.nombre_usuario}: {detalle.anulacion.motivo}. El ticket y sus movimientos se conservan.</p>}
      {admin && detalle.canal === "PRESENCIAL" && detalle.estado === "CONFIRMADA" && <details><summary>Anular esta venta</summary><p>Solo si la mercancía no se entregó. Se compensará el stock en sus lotes originales; esto no realiza un reembolso ni cambia su caducidad.</p><label className="field">Motivo<input minLength={3} maxLength={300} value={motivo} disabled={ocupado} onChange={e => { setMotivo(e.target.value); claveAnulacion.current = ""; }} /></label><label className="review-checkbox"><input type="checkbox" checked={noEntregada} disabled={ocupado} onChange={e => setNoEntregada(e.target.checked)} />Confirmo que la mercancía no fue entregada</label><button className="button-secondary" disabled={ocupado || !noEntregada || motivo.trim().length < 3} onClick={() => void anular()}>Anular y compensar stock</button></details>}
    </PanelDetalle>}
  </>;
}
