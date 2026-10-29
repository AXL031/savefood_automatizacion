"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { leerPagoPayme, referenciasPayme, verificarPagoPayme, recuperarPagoPendiente, sincronizarVentaPayme, type PagoPayme } from "../payme";
import { ResumenPagoPayme } from "./PagoPayme";
import { soles } from "../dinero";

export function DetallePagoPayme({ id }: { id: string }) {
  const [pago, setPago] = useState<PagoPayme | null>(null), [error, setError] = useState("");
  const [ocupado, setOcupado] = useState(false);
  useEffect(() => {
    const control = new AbortController();
    leerPagoPayme(id, control.signal).then(setPago).catch(e => { if (!control.signal.aborted) setError(e.message); });
    return () => control.abort();
  }, [id]);
  async function consultar(venta = false) {
    setOcupado(true); setError("");
    try { setPago(await (venta ? sincronizarVentaPayme(id) : verificarPagoPayme(id))); } catch (e) { setError(e instanceof Error ? e.message : "No se pudo verificar el pago."); }
    finally { setOcupado(false); }
  }
  return <div className="t-contenedor t-confirmacion"><div className="t-confirmacion-tarjeta">
    <h1>Tu compra y pago de prueba</h1>
    {pago && <><ResumenPagoPayme pago={pago} /><ul>{pago.cotizacion.lineas.map(l => <li key={l.producto_id}>{l.cantidad} × {l.nombre ?? "Producto"} · {soles(l.subtotal)}</li>)}</ul>
      <p>{pago.comercial?.origen === "FOODSAVE" ? "El pago utiliza preproducción. El ticket y su movimiento de inventario se registran en FoodSave al confirmar la compra." : "Esta operación pertenece al catálogo de ejemplo y no genera venta, entrega ni movimiento en FoodSave."}</p>
      <div className="t-confirmacion-acciones"><button className="t-boton-primario" onClick={() => void consultar()} disabled={ocupado}>{ocupado ? "Consultando…" : "Consultar estado con Payme"}</button>
      {pago.pagado && pago.comercial?.origen === "FOODSAVE" && pago.comercial.estado !== "REGISTRADA" && <button className="t-boton-contorno" disabled={ocupado} onClick={() => void consultar(true)}>Recuperar registro en FoodSave</button>}</div></>}
    {error && <p className="t-error" role="alert">{error}</p>}
    <p><Link href="/tienda/pedidos">Mis pagos y pedidos</Link> · <Link href="/tienda/menu">Volver al menú</Link></p>
  </div></div>;
}

export function PagosPaymeGuardados() {
  const [referencias, setReferencias] = useState<ReturnType<typeof referenciasPayme>>([]);
  const [error, setError] = useState("");
  useEffect(() => {
    let activo = true;
    setReferencias(referenciasPayme());
    recuperarPagoPendiente().then(() => { if (activo) setReferencias(referenciasPayme()); }).catch(e => { if (activo) setError(e.message); });
    return () => { activo = false; };
  }, []);
  return <section className="t-payme-historial"><h2>Operaciones guardadas en este navegador</h2>
    <p>Consulta las operaciones pendientes antes de volver a pagar.</p>
    {!referencias.length && <p>Aún no has iniciado pagos con Payme.</p>}
    {error && <p className="t-error" role="alert">{error}</p>}
    {referencias.map(r => <article className="t-compra-guardada" key={r.id}><Link href={`/tienda/pedido/payme-${r.id}`}>{r.comercial?.ticket?.numero ?? `Operación ${r.operacion}`}</Link><strong>{soles(r.total)}</strong><span>Pago: {r.estado.toLowerCase()}</span><span>{r.comercial?.estado === "REGISTRADA" ? "Compra registrada" : r.comercial?.origen === "FOODSAVE" ? `Compra: ${r.comercial.estado.toLowerCase().replaceAll("_", " ")}` : "Catálogo de ejemplo · sin venta"}</span></article>)}
  </section>;
}
