"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState, type FormEvent } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { SerieHistorica } from "@/components/charts/SerieHistorica";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { TablaPaginada } from "@/components/tables/TablaPaginada";
import { NavegacionAnalitica, IndicadoresEvaluacion, ParticionModelo, IconoAnalitica, numeroAnalitica as numero } from "@/components/panel/Analitica";
import { listarModelos, obtenerEvaluacion } from "@/services/pronosticos";
import { formatearEscenario } from "@/utils/fechas";
import type { EvaluacionTramo, Modelo } from "@/types/pronostico";

function Contenido({ token }: { token: string }) {
  const parametros = useSearchParams();
  const solicitado = Number(parametros.get("modelo_id"));
  const [modelos, setModelos] = useState<Modelo[]>([]);
  const [modeloId, setModeloId] = useState<number>();
  const [reporte, setReporte] = useState<EvaluacionTramo | null>(null);
  const [fecha, setFecha] = useState("");
  const [borrador, setBorrador] = useState({ desde: "", hasta: "" });
  const [filtros, setFiltros] = useState<{ desde?: string; hasta?: string }>({});
  const [busqueda, setBusqueda] = useState("");
  const [comparacion, setComparacion] = useState("todos");
  const [revision, setRevision] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const control = new AbortController();
    setCargando(true); setError("");
    listarModelos(token, control.signal).then((lista) => {
      if (control.signal.aborted) return;
      setModelos(lista);
      setModeloId(lista.find((m) => m.id === solicitado)?.id ?? lista[0]?.id);
      if (!lista.length) setCargando(false);
    }).catch((e: unknown) => { if (!control.signal.aborted) { setError(e instanceof Error ? e.message : "No se pudieron consultar los modelos."); setCargando(false); } });
    return () => control.abort();
  }, [token, solicitado]);

  useEffect(() => {
    if (!modeloId) return;
    const control = new AbortController();
    setCargando(true); setReporte(null); setError("");
    obtenerEvaluacion(token, modeloId, control.signal, filtros).then((datos) => {
      if (control.signal.aborted) return;
      setReporte(datos);
      setFecha((actual) => datos.serie_diaria.some((d) => d.fecha_local === actual) ? actual : [...datos.serie_diaria].reverse().find((d) => d.productos_evaluables > 0)?.fecha_local ?? datos.serie_diaria.at(-1)?.fecha_local ?? "");
    }).catch((e: unknown) => { if (!control.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo consultar la evaluación."); })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token, modeloId, filtros, revision]);

  function consultar(e: FormEvent) {
    e.preventDefault();
    if (borrador.desde && borrador.hasta && borrador.desde > borrador.hasta) { setError("La fecha inicial no puede ser posterior a la final."); return; }
    setFiltros({ desde: borrador.desde || undefined, hasta: borrador.hasta || undefined });
  }
  const modelo = modelos.find((m) => m.id === modeloId);
  const dia = reporte?.serie_diaria.find((d) => d.fecha_local === fecha);
  const traza = reporte?.trazas.find((t) => t.fecha_local === fecha);
  const productos = dia?.desglose_productos.filter((p) => `${p.producto ?? ""} ${p.producto_id}`.toLocaleLowerCase().includes(busqueda.trim().toLocaleLowerCase()) &&
    (comparacion === "todos" || (comparacion === "fuera" && p.dentro_mas_menos_20 === false) || (comparacion === "pendientes" && p.real === null))) ?? [];
  const diferencia = dia ? dia.total_previsto_evaluable - dia.total_real_conocido : 0;

  return <div className="analytics-page">
    <NavegacionAnalitica />
    <section className="analytics-hero"><div><span className="analytics-eyebrow"><IconoAnalitica /> Inteligencia de tu negocio</span><h2>Del pronóstico<br />a la realidad.</h2><p>Compara lo previsto con las ventas conocidas y encuentra dónde mejorar tu planificación.</p></div><div className="analytics-hero-note"><span className="analytics-status-dot" /><strong>{modelo ? modelo.version_modelo : "Evaluación histórica"}</strong><span>{reporte ? `${reporte.fechas_evaluadas} fechas con comparaciones` : "Cada resultado conserva su versión"}</span><Link href="/pronosticos">Explorar modelos <span aria-hidden="true">↗</span></Link></div></section>

    <section className="card analytics-filter-card"><form className="analytics-filters" onSubmit={consultar}>
      <label>Modelo<select value={modeloId ?? ""} disabled={!modelos.length || cargando} onChange={(e) => { setModeloId(Number(e.target.value)); setFiltros({}); setBorrador({ desde: "", hasta: "" }); }}><option value="" disabled>Elige una versión</option>{modelos.map((m) => <option key={m.id} value={m.id}>{m.version_modelo}</option>)}</select></label>
      <label>Desde<input type="date" value={borrador.desde} min={modelo?.particion.inicio_prueba} max={modelo?.particion.fin_prueba} onChange={(e) => setBorrador({ ...borrador, desde: e.target.value })} /></label>
      <label>Hasta<input type="date" value={borrador.hasta} min={borrador.desde || modelo?.particion.inicio_prueba} max={modelo?.particion.fin_prueba} onChange={(e) => setBorrador({ ...borrador, hasta: e.target.value })} /></label>
      <button className="button-primary" disabled={cargando || !modeloId}>Aplicar filtros</button>
      <button type="button" className="button-secondary" disabled={cargando || !modeloId} onClick={() => { setBorrador({ desde: "", hasta: "" }); setFiltros({}); }}>Todo el período</button>
      <button type="button" className="button-link" disabled={cargando || !modeloId} onClick={() => setRevision((r) => r + 1)}>↻ Actualizar</button>
    </form></section>
    {error && <EstadoPanel tono="alerta" titulo="No se pudo actualizar la evaluación" descripcion={error} />}
    {cargando && <div className="analytics-loading" role="status"><span />Consultando indicadores y comparaciones…</div>}
    {!cargando && !reporte && !error && <EstadoPanel titulo="Tu evaluación comienza con los datos" descripcion="Completa la primera carga y prepara el modelo para ver los resultados aquí." />}
    {reporte && <>
      {!!reporte.pares_pendientes_evaluacion && <div className="analytics-notice" role="status"><strong>{reporte.pares_pendientes_evaluacion} {reporte.pares_pendientes_evaluacion === 1 ? "comparación pendiente" : "comparaciones pendientes"} de evaluación.</strong><span>Las revisiones anteriores se conservan. Consulta la tarea y actualiza al finalizar.</span><Link href="/automatizaciones">Ver tareas →</Link></div>}
      <IndicadoresEvaluacion metricas={reporte.metricas_globales} pendientes={reporte.pares_pendientes_evaluacion} />
      <section className="card analytics-chart-card"><div className="section-heading"><div><span className="analytics-eyebrow">Evolución del período</span><h2>Lo previsto frente a lo vendido</h2><p>{formatearEscenario(reporte.fecha_inicio)} — {formatearEscenario(reporte.fecha_fin)} · unidades de los mismos productos evaluables.</p></div><span className="analytics-count">{reporte.serie_diaria.length} fechas guardadas</span></div>
        {reporte.serie_diaria.length ? <SerieHistorica dias={reporte.serie_diaria} seleccion={fecha} alSeleccionar={setFecha} /> : <EstadoPanel titulo="La evaluación aún no tiene resultados" descripcion="Consulta la preparación del modelo en Automatización para ver sus intentos y posibles errores." />}
      </section>
      {dia && <section className="card analytics-detail"><div className="section-heading"><div><span className="analytics-eyebrow">Una fecha, cada producto</span><h2>Detalle del {formatearEscenario(dia.fecha_local)}</h2><p>{dia.productos_evaluables} pares comparables · {dia.productos_excluidos} sin comparación vigente · {traza?.pronosticos_no_disponibles.length ?? 0} sin pronóstico.</p></div>{traza && <Link href={`/pronosticos?corrida_id=${traza.corrida_id}`} className="button-secondary">Ver pronóstico ↗</Link>}</div>
        <div className="day-summary"><div><span>Previsto comparable</span><strong>{dia.productos_evaluables ? numero(dia.total_previsto_evaluable) : "Sin dato"}<small> u.</small></strong></div><div><span>Venta real comparable</span><strong>{dia.productos_evaluables ? numero(dia.total_real_conocido) : "Sin dato"}<small> u.</small></strong></div><div><span>Diferencia del total</span><strong>{dia.productos_evaluables ? `${diferencia > 0 ? "+" : ""}${numero(diferencia)}` : "Sin dato"}<small> u.</small></strong></div></div>
        <div className="analytics-table-tools"><label>Buscar producto<input type="search" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} placeholder="Nombre o identificador…" /></label><label>Comparaciones<select value={comparacion} onChange={(e) => setComparacion(e.target.value)}><option value="todos">Todos los productos</option><option value="fuera">Fuera de ±20 %</option><option value="pendientes">Sin comparación vigente</option></select></label><span>{productos.length} productos</span></div>
        <TablaPaginada><thead><tr><th>Producto</th><th className="number-cell">Pronóstico</th><th className="number-cell">Venta real</th><th className="number-cell">Error absoluto</th><th>Comparación</th></tr></thead><tbody>{productos.map((p) => <tr key={p.producto_id}><td><strong>{p.producto ?? `Producto #${p.producto_id}`}</strong></td><td className="number-cell">{numero(p.previsto)}</td><td className="number-cell">{numero(p.real)}</td><td className="number-cell">{numero(p.diferencia_absoluta)}</td><td><span className={`badge ${p.dentro_mas_menos_20 === null ? "badge-neutral" : p.dentro_mas_menos_20 ? "badge-ok" : "badge-advertencia"}`}>{p.dentro_mas_menos_20 === null ? p.motivo_exclusion === "EVALUACION_PENDIENTE" ? "Por reevaluar" : "Sin venta conocida" : p.dentro_mas_menos_20 ? "Dentro de ±20 %" : "Fuera de ±20 %"}</span></td></tr>)}</tbody></TablaPaginada>
        {!productos.length && <p className="chart-empty">No hay productos que coincidan con estos filtros.</p>}
      </section>}
      <section className="card model-context"><div className="section-heading"><div><h2>Cómo se separaron los datos</h2><p>La prueba se conserva fuera del entrenamiento y la validación. Cada pronóstico utiliza historia anterior a su fecha.</p></div><IconoAnalitica tipo="modelo" /></div><ParticionModelo particion={reporte.particion} /><p className="helper-text">La evaluación histórica es exploratoria y no acredita rendimiento comercial futuro.</p></section>
    </>}
  </div>;
}

export default function PanelPage() {
  return <ProtectedShell titulo="Evaluación del modelo" descripcion="Indicadores claros para entender tus pronósticos.">{({ token }) => <Suspense fallback={<p role="status">Cargando evaluación…</p>}><Contenido token={token} /></Suspense>}</ProtectedShell>;
}
