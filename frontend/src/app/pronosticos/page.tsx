"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState, type FormEvent } from "react";
import { PanelDetalle } from "@/components/ui/PanelDetalle";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { TablaPaginada } from "@/components/tables/TablaPaginada";
import { NavegacionAnalitica, ParticionModelo, IconoAnalitica, numeroAnalitica as numero } from "@/components/panel/Analitica";
import { listarPaginaCorridas, listarModelos, obtenerCorrida, prepararModelo } from "@/services/pronosticos";
import { etiquetaDato } from "@/utils/etiquetas";
import { formatearEscenario } from "@/utils/fechas";
import type { Corrida, Modelo } from "@/types/pronostico";

function Contenido({ token, administrador }: { token: string; administrador: boolean }) {
  const parametros = useSearchParams();
  const corridaSolicitada = Number(parametros.get("corrida_id"));
  const [modelos, setModelos] = useState<Modelo[]>([]);
  const [corridas, setCorridas] = useState<Corrida[]>([]);
  const [modeloId, setModeloId] = useState<number>();
  const [detalle, setDetalle] = useState<Corrida | null>(null);
  const [cargando, setCargando] = useState(true), [cargandoLista, setCargandoLista] = useState(false);
  const [error, setError] = useState("");
  const [version, setVersion] = useState(""), [preparando, setPreparando] = useState(false);
  const [tarea, setTarea] = useState<number>();
  const [entrenando, setEntrenando] = useState(false);
  const [pagina, setPagina] = useState(1), [tamano, setTamano] = useState(10), [total, setTotal] = useState(0);
  const [borrador, setBorrador] = useState({ tipo: "", desde: "", hasta: "" });
  const [filtros, setFiltros] = useState(borrador);
  const [busqueda, setBusqueda] = useState("");
  const [revision, setRevision] = useState(0);
  const [abriendo, setAbriendo] = useState(false);

  useEffect(() => {
    const control = new AbortController(); setError("");
    listarModelos(token, control.signal).then((lista) => { if (!control.signal.aborted) { setModelos(lista); setModeloId((actual) => actual ?? lista[0]?.id); } })
      .catch((e: unknown) => { if (!control.signal.aborted) setError(e instanceof Error ? e.message : "No se pudieron cargar los modelos."); })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token, revision]);

  useEffect(() => {
    if (!modeloId) return;
    const control = new AbortController(); setCargandoLista(true); setError(""); setCorridas([]);
    listarPaginaCorridas(token, { modelo_id: modeloId, ...filtros, limite: tamano, desplazamiento: (pagina - 1) * tamano }, control.signal)
      .then((datos) => { if (!control.signal.aborted) { setCorridas(datos.filas); setTotal(datos.total); } })
      .catch((e: unknown) => { if (!control.signal.aborted) { setError(e instanceof Error ? e.message : "No se pudo consultar el historial."); setTotal(0); } })
      .finally(() => { if (!control.signal.aborted) setCargandoLista(false); });
    return () => control.abort();
  }, [token, modeloId, filtros, pagina, tamano, revision]);

  useEffect(() => {
    if (!Number.isSafeInteger(corridaSolicitada) || corridaSolicitada <= 0) return;
    const control = new AbortController();
    obtenerCorrida(token, corridaSolicitada, control.signal).then((corrida) => { if (!control.signal.aborted) { setDetalle(corrida); setModeloId(corrida.modelo_id); setPagina(1); } })
      .catch((e: unknown) => { if (!control.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo abrir el pronóstico."); });
    return () => control.abort();
  }, [token, corridaSolicitada]);

  async function seleccionar(id: number) {
    setAbriendo(true); setError(""); setBusqueda("");
    try { setDetalle(await obtenerCorrida(token, id)); }
    catch (e) { setError(e instanceof Error ? e.message : "No se pudo abrir el pronóstico."); }
    finally { setAbriendo(false); }
  }
  function consultar(e: FormEvent) {
    e.preventDefault();
    if (borrador.desde && borrador.hasta && borrador.desde > borrador.hasta) { setError("La fecha inicial no puede ser posterior a la final."); return; }
    setPagina(1); setFiltros({ ...borrador });
  }
  async function entrenar(e: FormEvent) {
    e.preventDefault(); setError(""); setPreparando(true);
    try { setTarea((await prepararModelo(token, version, `modelo-${version}`)).ejecucion_id); setEntrenando(false); }
    catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo solicitar el entrenamiento."); }
    finally { setPreparando(false); }
  }
  const modelo = modelos.find((m) => m.id === modeloId);
  const productos = detalle?.pronosticos?.filter((p) => p.producto.toLocaleLowerCase().includes(busqueda.toLocaleLowerCase().trim())) ?? [];
  const disponibles = detalle?.pronosticos?.filter((p) => p.estado === "DISPONIBLE") ?? [];
  return <div className="analytics-page">
    <NavegacionAnalitica />
    {administrador && <div className="section-heading"><h2>Modelos y pronósticos</h2><button type="button" className="button-primary" onClick={() => { setEntrenando(true); setError(""); }}>Entrenar nueva versión</button></div>}
    <section className="analytics-hero analytics-hero-compact"><div><span className="analytics-eyebrow"><IconoAnalitica tipo="modelo" /> Tu biblioteca predictiva</span><h2>Planifica con perspectiva.</h2><p>Explora cada versión y consulta qué unidades se previeron para cada producto.</p></div><Link href={modelo ? `/panel?modelo_id=${modelo.id}` : "/panel"} className="hero-link">Ver evaluación <span aria-hidden="true">↗</span></Link></section>
    {error && <EstadoPanel tono="alerta" titulo="No se pudo completar la consulta" descripcion={error} />}
    {tarea && <div className="analytics-notice" role="status"><strong>Entrenamiento solicitado · tarea #{tarea}</strong><span>Los modelos anteriores permanecen disponibles.</span><Link href={`/automatizaciones/ejecuciones/${tarea}`}>Seguir preparación →</Link></div>}
    {cargando && <div className="analytics-loading" role="status"><span />Consultando versiones del modelo…</div>}
    {!cargando && !modelos.length && !error && <EstadoPanel titulo="Prepara tu primer modelo" descripcion="Carga las ventas para entrenar una versión y consultar sus pronósticos." />}
    {!!modelos.length && <>
      <section className="card model-overview"><div className="section-heading"><div className="model-heading"><span className="model-symbol"><IconoAnalitica tipo="modelo" /></span><div><span className="analytics-eyebrow">Versión seleccionada</span><h2>{modelo?.version_modelo}</h2></div></div><label className="filter-label">Cambiar modelo<select value={modeloId ?? ""} onChange={(e) => { setModeloId(Number(e.target.value)); setPagina(1); setDetalle(null); }}>{modelos.map((m) => <option key={m.id} value={m.id}>{m.version_modelo} · #{m.id}</option>)}</select></label></div>
        {modelo && <><div className="model-facts"><span className={`badge ${modelo.estado === "LISTO_DEMO" ? "badge-ok" : "badge-neutral"}`}>{modelo.estado === "LISTO_DEMO" ? "Disponible para pronosticar" : etiquetaDato(modelo.estado)}</span><span>Historia hasta {formatearEscenario(modelo.fecha_corte_entrenamiento)}</span><span>{modelos.length} versiones disponibles</span></div><ParticionModelo particion={modelo.particion} /><details className="model-technical"><summary>Identificación y trazabilidad</summary><p>Modelo #{modelo.id}. Huella del archivo: <code className="model-hash">{modelo.sha256}</code></p></details></>}
      </section>
      <section className="card"><div className="section-heading"><div><span className="analytics-eyebrow">Historial completo</span><h2>Pronósticos guardados</h2><p>Todos los cálculos de la versión seleccionada, con su fecha y ejecución de origen.</p></div><button type="button" className="button-secondary" disabled={cargandoLista} onClick={() => setRevision((r) => r + 1)}>↻ Actualizar</button></div>
        <form className="analytics-filters history-filters" onSubmit={consultar}><label>Tipo de cálculo<select value={borrador.tipo} onChange={(e) => setBorrador({ ...borrador, tipo: e.target.value })}><option value="">Todos los tipos</option><option value="DEMO_PROGRAMADA">Planificación</option><option value="BACKTEST">Evaluación histórica</option></select></label><label>Desde<input type="date" value={borrador.desde} onChange={(e) => setBorrador({ ...borrador, desde: e.target.value })} /></label><label>Hasta<input type="date" value={borrador.hasta} onChange={(e) => setBorrador({ ...borrador, hasta: e.target.value })} /></label><button className="button-primary" disabled={cargandoLista}>Filtrar historial</button><button type="button" className="button-link" onClick={() => { setBorrador({ tipo: "", desde: "", hasta: "" }); setFiltros({ tipo: "", desde: "", hasta: "" }); setPagina(1); }}>Limpiar</button></form>
        <div aria-busy={cargandoLista}><TablaPaginada remota={{ pagina, tamano, total, cargando: cargandoLista, onCambio: (p, t) => { setPagina(p); setTamano(t); } }}><thead><tr><th>Fecha prevista</th><th>Tipo de cálculo</th><th>Estado</th><th>Ejecución</th><th>Detalle</th></tr></thead><tbody>{corridas.map((c) => <tr key={c.id}><td><strong>{formatearEscenario(c.fecha_objetivo)}</strong><small className="table-subtitle">Pronóstico #{c.id}</small></td><td>{c.tipo === "BACKTEST" ? "Evaluación histórica" : "Planificación"}</td><td><span className={`badge ${c.estado === "COMPLETADA" ? "badge-ok" : "badge-neutral"}`}>{etiquetaDato(c.estado)}</span></td><td><Link href={`/automatizaciones/ejecuciones/${c.ejecucion_id}`}>Tarea #{c.ejecucion_id} ↗</Link></td><td><button type="button" className="button-secondary" disabled={abriendo} onClick={() => void seleccionar(c.id)}>Ver productos →</button></td></tr>)}</tbody></TablaPaginada></div>
        {cargandoLista ? <p role="status" className="helper-text">Consultando historial…</p> : !corridas.length && <p className="chart-empty">No hay pronósticos para estos filtros.</p>}
      </section>
    </>}
    {administrador && entrenando && <PanelDetalle titulo="Entrenar nueva versión" ocupado={preparando} onCerrar={() => setEntrenando(false)}><section className="card training-card"><p>Utiliza las ventas guardadas y conserva los modelos anteriores.</p>{error && <EstadoPanel tono="alerta" titulo="Revisa el entrenamiento" descripcion={error} />}<form className="analytics-filters" onSubmit={entrenar}><label>Nombre de la nueva versión<input value={version} onChange={(e) => setVersion(e.target.value)} placeholder="Por ejemplo: catboost-octubre-01" pattern="[A-Za-z0-9][A-Za-z0-9._-]*" maxLength={80} required /></label><button className="button-primary" disabled={preparando}>{preparando ? "Solicitando preparación…" : "Solicitar entrenamiento"}</button></form></section></PanelDetalle>}
    {detalle && <PanelDetalle titulo={`Pronóstico #${detalle.id} · ${formatearEscenario(detalle.fecha_objetivo)}`} onCerrar={() => setDetalle(null)}><div className="day-summary"><div><span>Unidades previstas</span><strong>{numero(disponibles.reduce((s, p) => s + (p.cantidad_pronosticada ?? 0), 0))}</strong></div><div><span>Productos con pronóstico</span><strong>{disponibles.length} / {detalle.pronosticos?.length ?? 0}</strong></div><div><span>Modelo</span><strong className="model-version-value">{detalle.version_modelo}</strong></div></div><label className="field">Buscar producto<input type="search" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} placeholder="Nombre del producto…" /></label><TablaPaginada><thead><tr><th>Producto</th><th className="number-cell">Unidades previstas</th><th>Disponibilidad</th></tr></thead><tbody>{productos.map((p) => <tr key={p.id}><td>{p.producto}</td><td className="number-cell">{numero(p.cantidad_pronosticada)}</td><td><span className={`badge ${p.estado === "DISPONIBLE" ? "badge-ok" : "badge-advertencia"}`}>{etiquetaDato(p.estado)}</span></td></tr>)}</tbody></TablaPaginada>{!productos.length && <p className="chart-empty">No hay productos que coincidan.</p>}<p className="helper-text">Una cantidad desconocida se conserva sin valor y no se interpreta como cero.</p><Link href={`/automatizaciones/ejecuciones/${detalle.ejecucion_id}`}>Ver tarea e intentos →</Link></PanelDetalle>}
  </div>;
}

export default function PronosticosPage() {
  return <ProtectedShell titulo="Pronósticos y modelos" descripcion="Versiones, trazabilidad y previsión por producto.">{({ token, perfil }) => <Suspense fallback={<p role="status">Cargando pronósticos…</p>}><Contenido token={token} administrador={perfil.rol === "ADMINISTRADOR"} /></Suspense>}</ProtectedShell>;
}
