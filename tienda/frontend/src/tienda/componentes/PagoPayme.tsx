"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import type { DatosEntrega, LineaCarrito } from "../tipos";
import { soles } from "../dinero";
import { cargarFlex, configuracionFlex, configuracionPayme, iniciarPayme, liberarBorradorPayme, puedeCambiarMetodo,
  METODOS_PAYME, verificarPagoPayme, type CompradorPayme, type InstanciaFlex, type MetodoPayme, type PagoPayme as Pago } from "../payme";
import { recuperarPagoPendiente, reabrirPayme } from "../payme";
import type { Cotizacion } from "../servicios";

const TERMINALES = ["DENEGADO", "INVALIDO", "EXPIRADO", "CANCELADO", "EXTORNADO"];
export function ResumenPagoPayme({ pago }: { pago: Pago }) {
  const etiqueta = METODOS_PAYME.find(m => m.id === pago.metodo)?.nombre;
  const estadosComerciales: Record<string,string> = { PREPARANDO: "Preparando la reserva", RESERVADA: "Stock reservado para esta compra", RESERVA_VENCIDA: "Reserva vencida · revisa el pago", PENDIENTE_VENTA: "Pago verificado · registro de venta pendiente", LIBERACION_PENDIENTE: "Liberación de la reserva pendiente", LIBERADA: "Reserva liberada", REVISION_REQUERIDA: "Compra en revisión" };
  return <div className="t-payme-resultado" role="status">
    <strong>{pago.pagado ? "Pago de prueba confirmado por Payme" : pago.estado === "CREADO" ? "Pago preparado" : `Pago ${pago.estado.toLowerCase()}`}</strong>
    <p>{etiqueta} · Operación {pago.operacion} · {soles(pago.total)}</p>
    {!pago.pagado && ["CREADO", "PENDIENTE", "REGISTRADO"].includes(pago.estado) && <p>El pago todavía no está confirmado. Puedes revisar su estado sin volver a pagar.</p>}
    {pago.continuacion.cip && <p>Código CIP: <strong>{pago.continuacion.cip}</strong>. Generarlo no confirma el pago.</p>}
    {pago.continuacion.cip_url && <p><a href={pago.continuacion.cip_url} target="_blank" rel="noopener noreferrer">Ver instrucciones de PagoEfectivo</a></p>}
    {pago.continuacion.continue_url && <p><a href={pago.continuacion.continue_url} target="_blank" rel="noopener noreferrer">Continuar la validación del pago</a></p>}
    {pago.continuacion.expira_en && <p>Vencimiento: {pago.continuacion.expira_en}</p>}
    {pago.comercial && <div className="t-estado-comercial">
      <strong>{pago.comercial.estado === "REGISTRADA" ? `Compra registrada · ${pago.comercial.ticket?.numero}` : pago.comercial.origen === "EJEMPLO" ? "Catálogo de ejemplo · sin venta en FoodSave" : estadosComerciales[pago.comercial.estado] ?? "Consulta el estado de la compra"}</strong>
      {pago.comercial.reserva_vence_en && !pago.pagado && <p>Reserva hasta {new Date(pago.comercial.reserva_vence_en).toLocaleString("es-PE")}. Si pagas después, la compra necesitará revisión.</p>}
      {pago.comercial.mensaje && <p>{pago.comercial.mensaje}</p>}
      {pago.pagado && pago.comercial.estado === "PENDIENTE_VENTA" && <p>Conservamos el pago y reintentaremos su registro. No vuelvas a pagar.</p>}
    </div>}
  </div>;
}

export function PagoPayme({ lineas, entrega, nombre, correo, cotizacion, alIntentar, alAprobar, alBloquear }: {
  lineas: LineaCarrito[]; entrega: DatosEntrega; nombre: string; correo: string;
  cotizacion?: Cotizacion | null;
  alIntentar: () => boolean; alAprobar: (id: string) => void; alBloquear: (valor: boolean) => void;
}) {
  const partes = nombre.trim().split(/\s+/);
  const [comprador, setComprador] = useState<CompradorPayme>({ nombres: partes.slice(0, -1).join(" ") || nombre, apellidos: partes.length > 1 ? partes.at(-1)! : "", correo });
  const [listo, setListo] = useState<boolean | null>(null);
  const [ocupado, setOcupado] = useState(false), [error, setError] = useState("");
  const [pago, setPago] = useState<Pago | null>(null);
  const [visible, setVisible] = useState(false);
  const [resultadoRecibido, setResultadoRecibido] = useState(false);
  const respuestaEnCurso = useRef(false), pagoActual = useRef<Pago | null>(null);
  const marco = useRef<HTMLDivElement>(null), contenedor = useRef<HTMLDivElement>(null);
  const metodoVisible = useRef<MetodoPayme | null>(null);
  const instancia = useRef<InstanciaFlex | null>(null), consulta = useRef<Promise<void> | null>(null), montado = useRef(true), iniciado = useRef(false);
  const aprobarRef = useRef(alAprobar); aprobarRef.current = alAprobar;
  useEffect(() => {
    let activa = true;
    recuperarPagoPendiente().then(p => {
      if (!activa || !p) return;
      pagoActual.current = p; setPago(p); alBloquear(true);
      if (p.pagado) { liberarBorradorPayme(); aprobarRef.current(p.id); }
    }).catch(e => { if (activa) setError(e.message); });
    return () => { activa = false; };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { setComprador(c => ({ ...c, nombres: partes.slice(0, -1).join(" ") || nombre, apellidos: partes.length > 1 ? partes.at(-1)! : c.apellidos, correo })); }, [nombre, correo]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    const control = new AbortController();
    configuracionPayme(control.signal).then(c => setListo(c.configurado)).catch(() => { if (!control.signal.aborted) { setListo(false); setError("No se pudo consultar la disponibilidad de los pagos de prueba."); } });
    return () => control.abort();
  }, []);
  useEffect(() => { montado.current = true; return () => { montado.current = false; instancia.current?.terminate?.(); }; }, []);
  useEffect(() => {
    if (!visible || !marco.current || !contenedor.current) return;
    const padre = marco.current, interior = contenedor.current;
    const ajustar = () => {
      const escala = Math.min(1, padre.clientWidth / 415);
      interior.style.transform = `scale(${escala})`;
      const altura = `${Math.ceil(interior.scrollHeight * escala)}px`;
      if (padre.style.height !== altura) padre.style.height = altura;
    };
    const observer = new ResizeObserver(ajustar); observer.observe(padre); observer.observe(interior); ajustar();
    return () => observer.disconnect();
  }, [visible]);

  function actualizar(actual: Pago) {
    if (!montado.current) return;
    pagoActual.current = actual; setPago(actual);
    if (actual.transaction_id && metodoVisible.current !== actual.metodo) {
      const sdk = instancia.current; instancia.current = null;
      sdk?.terminate?.(); setVisible(false);
    }
    if (actual.pagado) { instancia.current?.terminate?.(); liberarBorradorPayme(); aprobarRef.current(actual.id); }
  }
  async function comprobar(id: string, tid?: string) {
    if (iniciado.current && !tid) return;
    if (consulta.current) {
      if (!tid) return;
      await consulta.current;
    }
    const tarea = (async () => {
      try { actualizar(await verificarPagoPayme(id, tid)); }
      catch (e) { if (montado.current) setError(e instanceof Error ? e.message : "El pago aún necesita verificación."); }
    })();
    consulta.current = tarea;
    await tarea;
    if (consulta.current === tarea) consulta.current = null;
  }

  useEffect(() => {
    if (!pago || pago.pagado || TERMINALES.includes(pago.estado)) return;
    const id = window.setInterval(() => void comprobar(pago.id), 5000);
    return () => window.clearInterval(id);
  }, [pago?.id, pago?.estado]); // eslint-disable-line react-hooks/exhaustive-deps

  async function abrir(metodo: MetodoPayme) {
    if (iniciado.current) return;
    if (!puedeCambiarMetodo(pagoActual.current, respuestaEnCurso.current)) {
      if (pagoActual.current?.metodo === metodo) await comprobar(pagoActual.current.id);
      else setError("Hay una transacción pendiente de verificación. Consulta su estado antes de cambiar de método.");
      return;
    }
    if (!pagoActual.current && !alIntentar()) return;
    if (!pagoActual.current && (comprador.nombres.trim().length < 2 || comprador.apellidos.trim().length < 2 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(comprador.correo))) {
      setError("Completa nombres, apellidos y correo de quien realiza el pago."); return;
    }
    iniciado.current = true; setOcupado(true); setError("");
    try {
      // Desmontar primero: nunca mantener dos formularios de pago activos.
      const anterior = instancia.current; instancia.current = null;
      anterior?.terminate?.(); contenedor.current?.replaceChildren(); setVisible(false);
      if (consulta.current) await consulta.current;
      if (!puedeCambiarMetodo(pagoActual.current, respuestaEnCurso.current)) return;
      const checkout = pagoActual.current ? await reabrirPayme(metodo) : await iniciarPayme(metodo, lineas, comprador, entrega, cotizacion);
      if (!montado.current) return;
      pagoActual.current = checkout.pago; setPago(checkout.pago); alBloquear(true);
      if (checkout.pago.pagado) { actualizar(checkout.pago); return; }
      if (!checkout.flex) return;
      await cargarFlex(checkout.flex);
      if (!montado.current || !contenedor.current || !window.FlexPaymentForms) return;
      if (respuestaEnCurso.current) return;
      contenedor.current.replaceChildren();
      setVisible(true);
      const sdk = new window.FlexPaymentForms(configuracionFlex(checkout.flex)); instancia.current = sdk; metodoVisible.current = checkout.flex.metodo;
      sdk.init(contenedor.current, (respuesta: unknown) => {
        // Incluso una respuesta tardía del formulario anterior se concilia con la misma operación.
        respuestaEnCurso.current = true; setResultadoRecibido(true);
        const r = respuesta as { transaction?: { transaction_id?: unknown } } | null;
        const tid = r?.transaction?.transaction_id;
        if (typeof tid === "string" && /^[A-Za-z0-9_-]{1,128}$/.test(tid)) void comprobar(checkout.pago.id, tid);
        else { setError("Payme no entregó una transacción verificable. Revisa el estado antes de volver a pagar."); void comprobar(checkout.pago.id); }
      }, () => {}, (fallo: unknown) => {
        if (instancia.current !== sdk) return;
        const mensaje = typeof fallo === "string" ? fallo : (fallo as { message?: string })?.message;
        if (mensaje === "cerro el carrito") { instancia.current = null; sdk.terminate?.(); setVisible(false); void comprobar(checkout.pago.id); }
        else setError("Payme no pudo completar el formulario. Revisa el estado de la operación antes de intentar otro pago.");
      });
    } catch (e) { if (montado.current) setError(e instanceof Error ? e.message : "No se pudo abrir Payme de pruebas."); }
    finally { iniciado.current = false; if (montado.current) setOcupado(false); }
  }
  const enCurso = Boolean(pago && !pago.pagado && !TERMINALES.includes(pago.estado));
  const cambiable = puedeCambiarMetodo(pago, resultadoRecibido);
  return <>
    <p className="t-aviso-simulado">Ambiente de pruebas Payme. Usa únicamente los datos de prueba del proveedor.</p>
    <div className="t-campos">
      <label className="t-campo"><span>Nombres del comprador</span><span className="t-campo-caja"><input value={comprador.nombres} disabled={ocupado || enCurso} maxLength={80} onChange={e => setComprador(c => ({ ...c, nombres: e.target.value }))} /></span></label>
      <label className="t-campo"><span>Apellidos del comprador</span><span className="t-campo-caja"><input value={comprador.apellidos} disabled={ocupado || enCurso} maxLength={80} onChange={e => setComprador(c => ({ ...c, apellidos: e.target.value }))} /></span></label>
      <label className="t-campo t-campo-ancho"><span>Correo del comprador (sin iniciar sesión)</span><span className="t-campo-caja"><input type="email" placeholder="nombre@ejemplo.com" autoComplete="email" value={comprador.correo} disabled={ocupado || enCurso} maxLength={254} onChange={e => setComprador(c => ({ ...c, correo: e.target.value }))} /></span></label>
    </div>
    {listo === false && <p role="status">Los pagos de prueba están pendientes de configuración.</p>}
    <div className="t-payme-metodos" aria-label="Pagar con Payme">
      {METODOS_PAYME.map(m => <button type="button" className="t-payme-metodo" key={m.id}
        aria-pressed={pago?.metodo === m.id}
        disabled={!listo || ocupado || Boolean(!cambiable && pago?.metodo !== m.id)} onClick={() => void abrir(m.id)}>
        <strong>{m.nombre}</strong><small>{ocupado && pago?.metodo === m.id ? "Preparando…" : !cambiable && pago?.metodo === m.id ? "Consultar estado" : m.detalle}</small>
      </button>)}
    </div>
    {pago && cambiable && <p role="status">Puedes elegir otro método. Conservaremos esta misma operación de prueba.</p>}
    {enCurso && !cambiable && <p role="status">Hay una transacción en verificación. Consulta su estado antes de iniciar otro pago.</p>}
    {error && <p className="t-error" role="alert">{error}</p>}
    <div className="t-payme-marco" ref={marco} hidden={!visible}><div className="t-payme-flex" ref={contenedor} /></div>
    {pago && <><ResumenPagoPayme pago={pago} /><Link href={`/tienda/pedido/payme-${pago.id}`}>Consultar este pago</Link>
      {TERMINALES.includes(pago.estado) && <button type="button" className="t-boton-contorno" onClick={() => { instancia.current?.terminate?.(); instancia.current = null; liberarBorradorPayme(); pagoActual.current = null; respuestaEnCurso.current = false; setResultadoRecibido(false); setPago(null); setVisible(false); alBloquear(false); }}>Elegir un método para un nuevo intento</button>}</>}
  </>;
}
