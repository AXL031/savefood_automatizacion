"use client";

import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import Link from "next/link";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { HttpError, solicitar } from "@/services/http";

type Producto = { id: number; nombre: string; codigo: string };
type Plan = { id: number; fecha: string; lineas: { producto_id: number; nombre: string; previsto: number | null; producido: number; pendiente: number | null }[] };
type LineaRecepcion = { id: number; nombre: string; cantidad_pendiente: string; unidad_compra: string };
type Pedido = { id: number; proveedor: { nombre: string }; estado: string; respuesta_proveedor: string; recepcion_estado: string; lineas: LineaRecepcion[] };
type Config = { reloj: "ACTUAL" | "ESCENARIO"; fecha_escenario: string | null; hora_escenario: string; producto_ids: number[]; habilitada: boolean };
type Resumen = { fecha_operativa: string; productos: Producto[]; planes: Plan[]; pedidos: Pedido[]; configuracion: Config;
  promociones: { id: number; lote_id: number; estado: string; descuento: number | null; motivo: string; fecha: string }[];
  registros: { id: number; tipo: string; fecha: string; plan_id: number | null }[] };
type Ejecutar = (ruta: string, body: unknown, method?: "POST" | "PUT") => Promise<boolean>;
type EnvioPendiente = { ruta: string; body: unknown; method: "POST" | "PUT" };

function Contenido({ contexto }: { contexto: ContextoSesion }) {
  const [datos, setDatos] = useState<Resumen | null>(null);
  const [tab, setTab] = useState("Producción");
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const pendiente = useRef(false);
  const [recuperar, setRecuperar] = useState<EnvioPendiente | null>(null);
  const [versionFormulario, setVersionFormulario] = useState(0);
  const almacen = `foodsave-operacion-pendiente:${contexto.perfil.id}`;
  useEffect(() => {
    setRecuperar(null);
    try {
      const valor = sessionStorage.getItem(almacen);
      if (valor) setRecuperar(JSON.parse(valor));
    } catch { setError("No se pudo leer el registro pendiente de este navegador."); }
  }, [almacen]);
  const cargar = useCallback(async (signal?: AbortSignal) => {
    const r = await solicitar<Resumen>("/operaciones/resumen", { token: contexto.token, signal });
    setDatos(r);
  }, [contexto.token]);
  useEffect(() => {
    const c = new AbortController();
    let consultando = false;
    const actualizar = async () => {
      if (consultando || pendiente.current) return;
      consultando = true;
      try { await cargar(c.signal); } catch (e) { if (!c.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo actualizar la operación."); }
      finally { consultando = false; }
    };
    actualizar();
    const intervalo = setInterval(actualizar, 30000);
    return () => { c.abort(); clearInterval(intervalo); };
  }, [cargar]);
  const ejecutar: Ejecutar = async (ruta, body, method = "POST") => {
    if (pendiente.current) return false;
    pendiente.current = true; setOcupado(true); setError(""); setMensaje("");
    const durable = ruta === "/operaciones/producciones" || ruta.startsWith("/operaciones/recepciones/");
    const envio = { ruta, body, method };
    try {
      if (durable) {
        if (recuperar && JSON.stringify(recuperar) !== JSON.stringify(envio)) {
          throw new Error("Recupera primero la operación pendiente antes de registrar otra.");
        }
        sessionStorage.setItem(almacen, JSON.stringify(envio));
        setRecuperar(envio);
      }
      await solicitar(ruta, { token: contexto.token, method, body });
      if (durable) { sessionStorage.removeItem(almacen); setRecuperar(null); setVersionFormulario(v => v + 1); }
      setMensaje("Operación registrada.");
      try { await cargar(); } catch { setError("El registro se confirmó; no se pudo actualizar la vista. Recarga para consultarlo."); }
      return true;
    } catch (e) {
      if (durable && e instanceof HttpError && e.status >= 400 && e.status < 500 && ![408, 429].includes(e.status)) {
        sessionStorage.removeItem(almacen); setRecuperar(null);
      }
      setError(e instanceof Error ? e.message : "No se pudo completar la operación."); return false;
    }
    finally { pendiente.current = false; setOcupado(false); }
  };
  if (!datos) return <><p role="status">Consultando operación…</p>{error && <p role="alert">{error}</p>}</>;
  const admin = contexto.perfil.rol === "ADMINISTRADOR";
  return <>
    <div className="operation-banner"><div><span className="eyebrow">Fecha operativa</span><strong>{datos.fecha_operativa}</strong></div><p>Confirma tandas y recepciones con trazabilidad. Las ventas se registran desde Caja e historial.</p><Link href="/notificaciones" className="button-secondary">Incidencias y avisos</Link></div>
    <p className="action-row"><Link href="/ventas">Ir a Caja e historial →</Link><Link href="/inventario">Registrar entradas de productos →</Link></p>
    <div className="operation-tabs" aria-label="Áreas de operación">{["Producción", "Recepciones", ...(admin ? ["Promociones", "Configuración"] : [])].map(t => <button key={t} type="button" aria-pressed={tab === t} className={tab === t ? "" : "button-secondary"} onClick={() => { setTab(t); setError(""); setMensaje(""); }} disabled={ocupado}>{t}</button>)}</div>
    {error && <p className="error-text" role="alert">{error}</p>}{mensaje && <p className="success-text" role="status">{mensaje}</p>}
    {recuperar && <div className="card" role="status"><p>Hay una operación pendiente de confirmar. Recupera su resultado con la misma clave antes de registrar otra.</p><button disabled={ocupado} onClick={() => ejecutar(recuperar.ruta, recuperar.body, recuperar.method)}>{ocupado ? "Comprobando…" : "Recuperar operación pendiente"}</button></div>}
    <fieldset disabled={ocupado || !!recuperar} className="operation-fieldset">
      {tab === "Producción" && <Produccion key={versionFormulario} datos={datos} ejecutar={ejecutar} />}
      
      {tab === "Recepciones" && <Recepciones key={versionFormulario} datos={datos} ejecutar={ejecutar} token={contexto.token} admin={admin} />}
      {tab === "Promociones" && <section className="card"><h2>Sugerencias y aprobación</h2><p>La revisión automática consulta los productos vigilados cada diez minutos. La aprobación conserva la decisión administrativa. Las promociones aprobadas y vigentes se envían a la tienda para los productos publicados.</p><div className="action-row"><Link href="/promociones">Configurar regla de descuento →</Link><Link href="/tienda-admin">Revisar publicación en tienda →</Link><button onClick={() => ejecutar("/operaciones/revisar", {})}>Revisar ahora</button></div><div className="table-scroll"><table><thead><tr><th>Lote</th><th>Resultado</th><th>Motivo</th><th>Decisión</th></tr></thead><tbody>{datos.promociones.map(p => <tr key={p.id}><td>#{p.lote_id}<small>{p.fecha}</small></td><td>{p.estado}{p.descuento ? ` · ${p.descuento}%` : ""}</td><td>{p.motivo}</td><td>{p.estado === "PENDIENTE" && <div className="action-row"><button onClick={() => ejecutar(`/operaciones/promociones/${p.id}/decision`, { aprobar: true })}>Aprobar</button><button className="button-secondary" onClick={() => ejecutar(`/operaciones/promociones/${p.id}/decision`, { aprobar: false })}>Rechazar</button></div>}</td></tr>)}</tbody></table></div>{!datos.promociones.length && <p>Aún no hay evaluaciones. Selecciona productos en Configuración y habilita su regla.</p>}</section>}
      
      {tab === "Configuración" && <Configuracion datos={datos} ejecutar={ejecutar} />}
    </fieldset>
    <details className="card"><summary>Últimas operaciones</summary><div className="table-scroll"><table><thead><tr><th>Registro</th><th>Tipo</th><th>Fecha</th><th>Plan</th></tr></thead><tbody>{datos.registros.map(r => <tr key={r.id}><td>#{r.id}</td><td>{r.tipo.replaceAll("_", " ")}</td><td>{r.fecha}</td><td>{r.plan_id ? `#${r.plan_id}` : "—"}</td></tr>)}</tbody></table></div></details>
  </>;
}

function Produccion({ datos, ejecutar }: { datos: Resumen; ejecutar: Ejecutar }) {
  const [planId, setPlanId] = useState(""); const [productoId, setProductoId] = useState("");
  const [cantidad, setCantidad] = useState(1); const [caducidad, setCaducidad] = useState(datos.fecha_operativa);
  const clave = useRef("");
  const plan = datos.planes.find(p => p.id === Number(planId));
  const linea = plan?.lineas.find(l => l.producto_id === Number(productoId));
  async function enviar(e: FormEvent) {
    e.preventDefault(); clave.current ||= crypto.randomUUID();
    if (await ejecutar("/operaciones/producciones", { clave_idempotencia: clave.current, plan_id: Number(planId), fecha: datos.fecha_operativa, lineas: [{ producto_id: Number(productoId), cantidad, fecha_caducidad: caducidad }] })) clave.current = "";
  }
  return <section className="card"><h2>Registrar producción</h2><p>Confirma cada tanda realmente fabricada. Se consumen ingredientes con la receta conservada del plan y se crea un lote de producto terminado.</p><form onSubmit={enviar} onChange={() => { clave.current = ""; }} className="operation-form">
    <label>Plan<select required value={planId} onChange={e => { setPlanId(e.target.value); setProductoId(""); }}><option value="">Seleccionar plan</option>{datos.planes.filter(p => p.fecha === datos.fecha_operativa).map(p => <option key={p.id} value={p.id}>Plan #{p.id} · {p.fecha}</option>)}</select></label>
    <label>Producto<select required disabled={!plan} value={productoId} onChange={e => setProductoId(e.target.value)}><option value="">Seleccionar producto</option>{plan?.lineas.filter(l => (l.pendiente ?? 0) > 0).map(l => <option key={l.producto_id} value={l.producto_id}>{l.nombre} · pendientes {l.pendiente}</option>)}</select></label>
    <label>Unidades fabricadas<input required disabled={!linea} type="number" min={1} max={linea?.pendiente ?? 0} step={1} value={cantidad} onChange={e => setCantidad(Number(e.target.value))} /></label>
    <label>Vencimiento del lote<input required disabled={!linea} type="date" min={datos.fecha_operativa} max={new Date(Date.parse(`${datos.fecha_operativa}T00:00:00Z`) + 4 * 86400000).toISOString().slice(0, 10)} value={caducidad} onChange={e => setCaducidad(e.target.value)} /></label>
    {linea && <p>Propuesto: {linea.previsto} · Ya fabricado: {linea.producido} · Pendiente: {linea.pendiente}</p>}
    <button type="submit" disabled={!linea}>Confirmar producción</button>
  </form>{!datos.planes.some(p => p.fecha === datos.fecha_operativa) && <p>No hay un plan para esta fecha. Revisa la fecha en Configuración o genera un plan desde <Link href="/automatizaciones">Automatización</Link>.</p>}</section>;
}


function Recepciones({ datos, ejecutar, token, admin }: { datos: Resumen; ejecutar: Ejecutar; token: string; admin: boolean }) {
  const [pedido, setPedido] = useState<Pedido | null>(null); const [cantidades, setCantidades] = useState<Record<number, number>>({});
  const [fechas, setFechas] = useState<Record<number, string>>({}); const [fecha, setFecha] = useState(new Date().toLocaleDateString("en-CA"));
  const [motivo, setMotivo] = useState(""); const [url, setUrl] = useState(""); const [error, setError] = useState(""); const [creando, setCreando] = useState(false); const clave = useRef("");
  function abrir(p: Pedido) { setPedido(p); setCantidades(Object.fromEntries(p.lineas.map(l => [l.id, Number(l.cantidad_pendiente)]))); setMotivo(""); clave.current = ""; }
  async function enlace(id: number) {
    if (creando) return; setCreando(true); setError("");
    try { const r = await solicitar<{ url: string }>(`/operaciones/pedidos/${id}/enlace`, { token, method: "POST" }); setUrl(r.url); }
    catch (e) { setError(e instanceof Error ? e.message : "No se pudo crear el enlace."); } finally { setCreando(false); }
  }
  async function recibir(e: FormEvent) {
    e.preventDefault(); if (!pedido) return; clave.current ||= crypto.randomUUID();
    const ok = await ejecutar(`/operaciones/recepciones/${pedido.id}`, { clave_idempotencia: clave.current, fecha_recepcion: fecha, motivo, lineas: pedido.lineas.map(l => ({ linea_pedido_id: l.id, cantidad_compra: String(cantidades[l.id] ?? 0), fecha_caducidad: fechas[l.id] || null })) });
    if (ok) { setPedido(null); clave.current = ""; }
  }
  return <section className="card"><h2>Recepción de compras</h2><p>Selecciona un pedido aceptado, revisa sus cantidades y confirma únicamente lo recibido en buen estado. Las diferencias avisan al administrador.</p>{error && <p role="alert">{error}</p>}{url && <p className="operation-link">Enlace privado, válido una hora: <a href={url} target="_blank" rel="noreferrer">Revisar pedido como proveedor</a><button className="button-secondary" onClick={() => { navigator.clipboard.writeText(url).catch(() => setError("No se pudo copiar. Abre el enlace y copia su dirección.")); }}>Copiar enlace</button></p>}
    <div className="table-scroll"><table><thead><tr><th>Pedido</th><th>Proveedor</th><th>Respuesta</th><th>Recepción</th><th>Acciones</th></tr></thead><tbody>{datos.pedidos.map(p => <tr key={p.id}><td>#{p.id}</td><td>{p.proveedor.nombre}</td><td>{p.respuesta_proveedor}</td><td>{p.recepcion_estado}</td><td><div className="action-row">{p.respuesta_proveedor === "ACEPTADO" && p.estado === "ENVIADO" && p.recepcion_estado !== "RECIBIDO" && <button onClick={() => abrir(p)}>Registrar llegada</button>}{admin && p.respuesta_proveedor !== "ACEPTADO" && !["CANCELADO", "RECHAZADO", "BLOQUEADO"].includes(p.estado) && <button disabled={creando} className="button-secondary" onClick={() => enlace(p.id)}>Crear enlace</button>}</div></td></tr>)}</tbody></table></div>
    {pedido && <form className="operation-receipt" onSubmit={recibir} onChange={() => { clave.current = ""; }}><h3>Pedido #{pedido.id} · Cantidades aceptadas</h3>{pedido.lineas.map(l => <div className="operation-receipt-line" key={l.id}><div><strong>{l.nombre}</strong><small>Pendiente: {l.cantidad_pendiente} {l.unidad_compra}</small></div><div className="quantity-control"><button type="button" aria-label={`Disminuir ${l.nombre}`} onClick={() => { clave.current = ""; setCantidades(c => ({ ...c, [l.id]: Math.max(0, (c[l.id] ?? 0) - 1) })); }}>−</button><input aria-label={`Cantidad aceptada de ${l.nombre}`} required type="number" step="0.0001" min={0} max={Number(l.cantidad_pendiente)} value={cantidades[l.id] ?? 0} onChange={e => setCantidades(c => ({ ...c, [l.id]: Number(e.target.value) }))} /><button type="button" aria-label={`Aumentar ${l.nombre}`} onClick={() => { clave.current = ""; setCantidades(c => ({ ...c, [l.id]: Math.min(Number(l.cantidad_pendiente), (c[l.id] ?? 0) + 1) })); }}>+</button></div><label>Caducidad<input type="date" min={fecha} value={fechas[l.id] ?? ""} onChange={e => setFechas(f => ({ ...f, [l.id]: e.target.value }))} /></label></div>)}<label>Fecha de recepción<input type="date" required value={fecha} onChange={e => setFecha(e.target.value)} /></label><label>Descripción y observaciones<textarea required minLength={3} maxLength={300} value={motivo} onChange={e => setMotivo(e.target.value)} placeholder="Indica faltantes, daños o conformidad de la entrega" /></label><div className="action-row"><button>Confirmar recepción</button><button type="button" className="button-secondary" onClick={() => setPedido(null)}>Cancelar</button></div></form>}
  </section>;
}

function Configuracion({ datos, ejecutar }: { datos: Resumen; ejecutar: Ejecutar }) {
  const [c, setC] = useState<Config>(datos.configuracion);
  return <section className="card"><h2>Vigilancia cada diez minutos</h2><p>Este reloj define la fecha de producción y vigilancia; Caja e historial conserva la fecha actual del negocio. El vencimiento de los enlaces del proveedor siempre usa una hora real.</p><form className="operation-form" onSubmit={e => { e.preventDefault(); ejecutar("/operaciones/configuracion", c, "PUT"); }}><label>Reloj<select value={c.reloj} onChange={e => setC({ ...c, reloj: e.target.value as Config["reloj"] })}><option value="ACTUAL">Fecha actual del negocio</option><option value="ESCENARIO">Fecha de prueba</option></select></label>{c.reloj === "ESCENARIO" && <><label>Fecha<input required type="date" value={c.fecha_escenario ?? ""} onChange={e => setC({ ...c, fecha_escenario: e.target.value })} /></label><label>Hora<input required type="time" value={c.hora_escenario.slice(0, 5)} onChange={e => setC({ ...c, hora_escenario: e.target.value })} /></label></>}<label className="checkbox-row"><input type="checkbox" checked={c.habilitada} onChange={e => setC({ ...c, habilitada: e.target.checked })} /> Habilitar revisión periódica</label><fieldset><legend>Productos vigilados</legend><div className="operation-products">{datos.productos.map(p => <label className="checkbox-row" key={p.id}><input type="checkbox" checked={c.producto_ids.includes(p.id)} onChange={e => setC({ ...c, producto_ids: e.target.checked ? [...c.producto_ids, p.id] : c.producto_ids.filter(i => i !== p.id) })} />{p.nombre}</label>)}</div></fieldset><button>Guardar vigilancia</button><Link href="/promociones">Configurar horario, umbral y descuento de la regla →</Link></form></section>;
}


export default function PaginaOperaciones() {
  return <ProtectedShell titulo="Operación diaria" descripcion="Tandas, recepciones y vigilancia del inventario.">{contexto => <Contenido contexto={contexto} />}</ProtectedShell>;
}
