"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { SerieHistorica } from "@/components/charts/SerieHistorica";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { listarModelos, obtenerEvaluacion } from "@/services/pronosticos";
import type { EvaluacionTramo, Modelo } from "@/types/pronostico";

function valor(numero: number | null, sufijo = "") { return numero === null ? "No definido" : `${numero}${sufijo}`; }

function Contenido({ token }: { token: string }) {
  const parametros = useSearchParams();
  const [modelos, setModelos] = useState<Modelo[]>([]);
  const [modeloId, setModeloId] = useState<number | undefined>();
  const [reporte, setReporte] = useState<EvaluacionTramo | null>(null);
  const [fecha, setFecha] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const control = new AbortController();
    listarModelos(token, control.signal).then((datos) => {
      if (control.signal.aborted) return;
      setModelos(datos);
      const solicitado = Number(parametros.get("modelo_id"));
      setModeloId(datos.find((item) => item.id === solicitado)?.id ?? datos[0]?.id);
      setCargando(false);
    }).catch((fallo: unknown) => { if (!control.signal.aborted) { setError(fallo instanceof Error ? fallo.message : "No se pudieron cargar los modelos."); setCargando(false); } });
    return () => control.abort();
  }, [token, parametros]);

  useEffect(() => {
    if (!modeloId) return;
    const control = new AbortController();
    setCargando(true);
    obtenerEvaluacion(token, modeloId, control.signal).then((datos) => {
      if (control.signal.aborted) return;
      setReporte(datos);
      setFecha([...datos.serie_diaria].reverse().find((dia) => dia.productos_evaluables > 0)?.fecha_local
        ?? datos.serie_diaria.at(-1)?.fecha_local ?? "");
      setError(""); setCargando(false);
    }).catch((fallo: unknown) => { if (!control.signal.aborted) { setError(fallo instanceof Error ? fallo.message : "No se pudo cargar la evaluación."); setCargando(false); } });
    return () => control.abort();
  }, [token, modeloId]);

  const dia = reporte?.serie_diaria.find((item) => item.fecha_local === fecha);
  const traza = reporte?.trazas.find((item) => item.fecha_local === fecha);
  return <>
    {error && <div className="inline-error" role="alert">{error}</div>}
    {cargando ? <p role="status">Cargando evaluación histórica…</p> : !reporte ? <EstadoPanel titulo="Sin evaluación" descripcion="Prepara un modelo y ejecuta su backtest para consultar esta vista." /> : <>
      <section className="card"><div className="section-heading"><div><h2>Comprobación histórica exploratoria</h2><p>Pronósticos de un día adelante con ventas anteriores a cada fecha. WAPE mide error.</p></div><label className="filter-label">Versión<select value={modeloId ?? ""} onChange={(e) => setModeloId(Number(e.target.value))}>{modelos.map((item) => <option key={item.id} value={item.id}>{item.version_modelo}</option>)}</select></label></div>
        <p className="helper-text">Entrenamiento {reporte.particion.inicio_entrenamiento}–{reporte.particion.fin_entrenamiento} · Validación {reporte.particion.inicio_validacion}–{reporte.particion.fin_validacion} · Prueba {reporte.fecha_inicio}–{reporte.fecha_fin}</p>
      </section>
      <div className="stats-grid section-space">
        <div className="card stat"><span>MAE</span><strong>{valor(reporte.metricas_globales.mae)}</strong><small>Unidades por par evaluable</small></div>
        <div className="card stat"><span>WAPE</span><strong>{valor(reporte.metricas_globales.wape_pct, "%")}</strong><small>Error sobre ventas reales conocidas</small></div>
        <div className="card stat"><span>Dentro de ±20 %</span><strong>{valor(reporte.metricas_globales.dentro_mas_menos_20_pct, "%")}</strong><small>Convención max(real, 1)</small></div>
        <div className="card stat"><span>Cobertura</span><strong>{valor(reporte.metricas_globales.cobertura_pct, "%")}</strong><small>{reporte.total_pares_evaluables} pares evaluables</small></div>
      </div>
      <section className="card"><div className="section-heading"><div><h2>Serie del tramo reservado</h2><p>Verde: previsto evaluable. Azul: real conocido de los mismos productos. Elige una fecha.</p></div></div>
        {reporte.serie_diaria.length ? <SerieHistorica dias={reporte.serie_diaria} seleccion={fecha} alSeleccionar={setFecha} /> : <EstadoPanel titulo="Sin corridas de backtest" descripcion="La evaluación automática aún no ha guardado fechas para esta versión." />}
      </section>
      {dia && <section className="card section-space"><div className="section-heading"><div><h2>{dia.fecha_local} · {dia.productos_evaluables} productos evaluables</h2><p>{dia.productos_excluidos} con pronóstico pero sin venta real conocida; {traza?.pronosticos_no_disponibles.length ?? 0} sin pronóstico disponible.</p></div>{traza && <Link href={`/pronosticos?corrida_id=${traza.corrida_id}`}>Corrida #{traza.corrida_id}</Link>}</div>
        <div className="pronostico-meta"><div><span>Previsto evaluable</span><strong>{dia.total_previsto_evaluable}</strong></div><div><span>Real conocido</span><strong>{dia.total_real_conocido}</strong></div><div><span>MAE</span><strong>{valor(dia.metricas.mae)}</strong></div><div><span>WAPE</span><strong>{valor(dia.metricas.wape_pct, "%")}</strong></div><div><span>Cobertura</span><strong>{valor(dia.metricas.cobertura_pct, "%")}</strong></div></div>
        <div className="table-wrap section-space"><table><thead><tr><th>Producto</th><th>Previsto</th><th>Real</th><th>Diferencia absoluta</th><th>Dentro ±20 %</th></tr></thead><tbody>{dia.desglose_productos.map((item) => <tr key={item.producto_id}><td>{item.producto ?? `#${item.producto_id}`}</td><td>{item.previsto}</td><td>{item.real ?? "Desconocido"}</td><td>{item.diferencia_absoluta ?? "—"}</td><td>{item.dentro_mas_menos_20 === null ? "—" : item.dentro_mas_menos_20 ? "Sí" : "No"}</td></tr>)}</tbody></table></div>
      </section>}
    </>}
  </>;
}

export default function PanelPage() {
  return <ProtectedShell titulo="Panel histórico" descripcion="Evaluación del modelo con cobertura, errores y fechas del escenario.">{({ token }) => <Suspense fallback={<p role="status">Cargando panel…</p>}><Contenido token={token} /></Suspense>}</ProtectedShell>;
}
