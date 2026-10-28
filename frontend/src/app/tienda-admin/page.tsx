"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { solicitar } from "@/services/http";
import { PanelDetalle } from "@/components/ui/PanelDetalle";

type Ficha = { version: number; publicado: boolean; categoria: string; descripcion: string; presentacion: string; imagen: string };
type Producto = { id: number; nombre: string; codigo: string; precio: string | null; disponible: number | null; reservado: number; ficha: Ficha };
type Entrega = { version: number; estado: string; intentos: number; ultimo_error: string | null };
type Estado = { habilitada: boolean; credenciales_configuradas: boolean; origen: string | null; version: number; entregas: Entrega[] };
type Reserva = { id: string; estado: string; vence_en: string; cotizacion: { total: string } };
const categorias = [{ id: "panes", nombre: "Panes y hojaldres" }, { id: "tortas", nombre: "Tortas" }, { id: "kekes", nombre: "Kekes" }, { id: "postres-personales", nombre: "Postres personales" }, { id: "postres-enteros", nombre: "Postres para compartir" }, { id: "bocados", nombre: "Bocados salados" }, { id: "otros", nombre: "Otros" }];
const soles = (n: string) => new Intl.NumberFormat("es-PE", { style: "currency", currency: "PEN" }).format(Number(n));

function Contenido({ contexto }: { contexto: ContextoSesion }) {
  const [productos, setProductos] = useState<Producto[]>([]), [estado, setEstado] = useState<Estado | null>(null), [reservas, setReservas] = useState<Reserva[]>([]);
  const [busqueda, setBusqueda] = useState(""), [editando, setEditando] = useState<Producto | null>(null), [ficha, setFicha] = useState<Ficha | null>(null);
  const [error, setError] = useState(""), [mensaje, setMensaje] = useState(""), [ocupado, setOcupado] = useState(false);
  const cargar = useCallback(async (signal?: AbortSignal) => {
    const [p, e, r] = await Promise.all([solicitar<{ productos: Producto[] }>("/tienda-admin/productos", { token: contexto.token, signal }), solicitar<Estado>("/tienda-admin/estado", { token: contexto.token, signal }), solicitar<Reserva[]>("/tienda-admin/reservas", { token: contexto.token, signal })]);
    setProductos(p.productos); setEstado(e); setReservas(r);
  }, [contexto.token]);
  useEffect(() => {
    const c = new AbortController(); let consultando = false;
    const actualizar = async () => { if (consultando) return; consultando = true; try { await cargar(c.signal); } catch (e) { if (!c.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo cargar el catálogo."); } finally { consultando = false; } };
    actualizar(); const id = setInterval(actualizar, 10000); return () => { c.abort(); clearInterval(id); };
  }, [cargar]);
  async function guardar() {
    if (!editando || !ficha || ocupado) return;
    setOcupado(true); setError(""); setMensaje("");
    try {
      const { version, ...campos } = ficha;
      await solicitar(`/tienda-admin/productos/${editando.id}`, { token: contexto.token, method: "PUT", body: { ...campos, version_actual: version } });
      setEditando(null); setFicha(null); setMensaje("Ficha guardada y catálogo preparado para su envío a la tienda."); await cargar();
    } catch (e) { setError(e instanceof Error ? e.message : "No se pudo guardar la ficha."); } finally { setOcupado(false); }
  }
  async function sincronizar() {
    setOcupado(true); setError("");
    try { await solicitar("/tienda-admin/sincronizar", { token: contexto.token, method: "POST" }); setMensaje("Catálogo preparado. El servicio de publicación enviará la misma versión hasta recibir su confirmación."); await cargar(); }
    catch (e) { setError(e instanceof Error ? e.message : "No se pudo preparar la publicación."); } finally { setOcupado(false); }
  }
  const admin = contexto.perfil.rol === "ADMINISTRADOR";
  return <>
    <div className="card"><div className="section-heading"><div><h2>Catálogo de la tienda independiente</h2><p>Publica los productos que ofrecerás online. Los precios se mantienen en <Link href="/ventas">Ventas</Link>; las promociones necesitan aprobación en <Link href="/operaciones">Operación diaria</Link>.</p></div><div className="form-actions"><button className="button-secondary" disabled={ocupado} onClick={() => cargar().catch(e => setError(e.message))}>Actualizar</button>{admin && <button disabled={ocupado} onClick={sincronizar}>Preparar sincronización</button>}</div></div>
      {estado && <p role="status">Conexión {estado.habilitada && estado.credenciales_configuradas ? "configurada" : "pendiente de configuración"} · Versión {estado.version} · {productos.filter(p => p.ficha.publicado).length} productos publicados</p>}
      {estado?.entregas[0] && <p>Última entrega: {estado.entregas[0].estado === "CONFIRMADO" ? "Confirmada por la tienda" : "Pendiente de confirmación"} · {estado.entregas[0].intentos} intento(s). {estado.entregas[0].ultimo_error}</p>}
      {mensaje && <p role="status">{mensaje}</p>}{error && <p role="alert" className="error-text">{error}</p>}
      <label className="field">Buscar producto<input type="search" value={busqueda} onChange={e => setBusqueda(e.target.value)} /></label>
      <div className="table-scroll"><table><thead><tr><th>Producto</th><th>Precio</th><th>Vendible</th><th>Reservado</th><th>Publicación</th><th>Acciones</th></tr></thead><tbody>{productos.filter(p => `${p.nombre} ${p.codigo}`.toLowerCase().includes(busqueda.toLowerCase())).map(p => <tr key={p.id}><td>{p.nombre}<small>{p.codigo}</small></td><td>{p.precio ? soles(p.precio) : "Sin precio"}</td><td>{p.disponible ?? "Desconocido"}</td><td>{p.reservado ?? 0}</td><td>{p.ficha.publicado ? "Publicado" : "Sin publicar"} · v{p.ficha.version}</td><td>{admin && <button className="button-secondary" disabled={ocupado} onClick={() => { setEditando(p); setFicha({ ...p.ficha }); setError(""); }}>Editar ficha</button>}</td></tr>)}</tbody></table></div>
    </div>
    <details className="card"><summary>Últimas reservas de tienda</summary><p>Apartan disponibilidad; el saldo físico se descuenta al registrar la venta. Las reservas vencidas dejan de apartar unidades.</p><div className="table-scroll"><table><thead><tr><th>Reserva</th><th>Estado</th><th>Total</th><th>Vence</th></tr></thead><tbody>{reservas.map(r => <tr key={r.id}><td>{r.id}</td><td>{r.estado}</td><td>{soles(r.cotizacion.total)}</td><td>{new Date(r.vence_en).toLocaleString("es-PE")}</td></tr>)}</tbody></table></div>{!reservas.length && <p>No hay reservas registradas.</p>}</details>
    {editando && ficha && <PanelDetalle titulo={`Ficha · ${editando.nombre}`} onCerrar={() => { if (!ocupado) { setEditando(null); setFicha(null); } }}><form className="operation-form" onSubmit={e => { e.preventDefault(); void guardar(); }}><fieldset disabled={ocupado}><label className="checkbox-row"><input type="checkbox" checked={ficha.publicado} onChange={e => setFicha({ ...ficha, publicado: e.target.checked })} /> Publicar en la tienda</label><label>Categoría<select value={ficha.categoria} onChange={e => setFicha({ ...ficha, categoria: e.target.value })}>{categorias.map(c => <option value={c.id} key={c.id}>{c.nombre}</option>)}</select></label><label>Descripción<textarea maxLength={500} value={ficha.descripcion} onChange={e => setFicha({ ...ficha, descripcion: e.target.value })} /></label><label>Presentación<input maxLength={100} value={ficha.presentacion} onChange={e => setFicha({ ...ficha, presentacion: e.target.value })} /></label><label>Imagen de la tienda o URL HTTPS<input maxLength={300} value={ficha.imagen} onChange={e => setFicha({ ...ficha, imagen: e.target.value })} placeholder="/tienda/productos/croissant.jpg" /></label><p>Sin imagen se muestra un marcador neutral. Usa la foto correspondiente a este producto.</p><p>Precio vigente: {editando.precio ? soles(editando.precio) : "Configurar en Ventas antes de publicar"}.</p><button type="submit">Guardar ficha</button></fieldset></form>{error && <p role="alert">{error}</p>}</PanelDetalle>}
  </>;
}

export default function TiendaAdmin() {
  return <ProtectedShell titulo="Publicar en tienda" descripcion="Productos, promociones y reservas conectados mediante API.">{c => <Contenido contexto={c} />}</ProtectedShell>;
}
