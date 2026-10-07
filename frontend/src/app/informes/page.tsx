"use client";
import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { PanelDetalle } from "@/components/ui/PanelDetalle";
import { TablaPaginada } from "@/components/tables/TablaPaginada";
import { GraficoVentas, GraficoBarras } from "@/components/charts/GraficosOperacion";
import { SerieHistorica } from "@/components/charts/SerieHistorica";
import { descargarInforme, obtenerInforme } from "@/services/informes";
import { listarModelos } from "@/services/pronosticos";
import type { FiltrosInforme, Informe, TipoInforme } from "@/types/informes";
import { etiquetasEstado } from "@/types/informes";
import type { Modelo } from "@/types/pronostico";

const numero = (valor: number | null, sufijo = "") => valor === null ? "Sin dato" : `${valor.toLocaleString("es", { maximumFractionDigits: 2 })}${sufijo}`;
const tipos: { tipo: TipoInforme; titulo: string }[] = [{ tipo: "ventas", titulo: "Ventas" }, { tipo: "pronosticos", titulo: "Pronósticos" }, { tipo: "pedidos", titulo: "Pedidos" }];

function Contenido({ token }: { token: string }) {
  const [tipo, setTipo] = useState<TipoInforme>("ventas");
  const [informe, setInforme] = useState<Informe | null>(null);
  const [filtros, setFiltros] = useState<FiltrosInforme>({});
  const [borrador, setBorrador] = useState({ desde: "", hasta: "", modelo: "" });
  const [modelos, setModelos] = useState<Modelo[]>([]);
  const [errorModelos, setErrorModelos] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(true);
  const [descargando, setDescargando] = useState(false);
  const [estadoDescarga, setEstadoDescarga] = useState("");
  const [diaDetalle, setDiaDetalle] = useState("");
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    const control = new AbortController();
    listarModelos(token, control.signal).then((lista) => { if (!control.signal.aborted) setModelos(lista); })
      .catch((e: unknown) => { if (!control.signal.aborted) setErrorModelos(e instanceof Error ? e.message : "No se pudieron consultar las versiones."); });
    return () => control.abort();
  }, [token]);
  useEffect(() => {
    const control = new AbortController(); setCargando(true); setError(""); setInforme(null); setDiaDetalle(""); setEstadoDescarga("");
    obtenerInforme(token, filtros, control.signal).then((datos) => {
      if (control.signal.aborted) return;
      setInforme(datos); setBorrador({ desde: datos.periodo.desde, hasta: datos.periodo.hasta, modelo: filtros.modelo_id ? String(filtros.modelo_id) : "" });
    }).catch((e: unknown) => { if (!control.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo consultar el reporte."); })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token, filtros, revision]);

  function aplicar(e: FormEvent) {
    e.preventDefault();
    const dias = (Date.parse(borrador.hasta) - Date.parse(borrador.desde)) / 86400000 + 1;
    if (!Number.isFinite(dias) || dias < 1 || dias > 366) { setError("Elige un período ordenado de hasta 366 días, inclusive."); return; }
    setFiltros({ desde: borrador.desde, hasta: borrador.hasta, ...(borrador.modelo ? { modelo_id: Number(borrador.modelo) } : {}) });
  }
  function periodoRapido(dias: number) {
    if (!informe) return;
    const hasta = informe.periodo.ventas_hasta ?? informe.periodo.pedidos_hasta ?? informe.periodo.hasta;
    const inicio = new Date(`${hasta}T00:00:00Z`); inicio.setUTCDate(inicio.getUTCDate() - dias + 1);
    setFiltros({ desde: inicio.toISOString().slice(0, 10), hasta, ...(filtros.modelo_id ? { modelo_id: filtros.modelo_id } : {}) });
  }
  async function exportar() {
    if (!informe) return;
    const seleccion = { desde: informe.periodo.desde, hasta: informe.periodo.hasta, ...(informe.evaluacion ? { modelo_id: informe.evaluacion.modelo_id } : {}) };
    setDescargando(true); setEstadoDescarga("");
    try {
      const archivo = await descargarInforme(token, tipo, seleccion);
      const url = URL.createObjectURL(archivo);
      const enlace = document.createElement("a"); enlace.href = url; enlace.download = `foodsave-${tipo}-${seleccion.desde}-${seleccion.hasta}.csv`;
      document.body.appendChild(enlace); enlace.click(); enlace.remove(); window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      setEstadoDescarga("CSV descargado con el período completo; incluye fechas y fuente de los datos.");
    } catch (e) { setEstadoDescarga(e instanceof Error ? e.message : "No se pudo descargar el CSV."); }
    finally { setDescargando(false); }
  }
  const evaluacion = informe?.evaluacion;
  const detalle = evaluacion?.serie_diaria.find((d) => d.fecha_local === diaDetalle);
  return <>
    <section className="card"><h2>Elige el período del escenario</h2><p>Los filtros se aplican al pulsar Consultar. El CSV contiene el período completo, aunque las tablas se muestren por páginas.</p>
      <form className="report-filters" onSubmit={aplicar}>
        <label>Desde<input type="date" required value={borrador.desde} disabled={cargando || descargando} onChange={(e) => setBorrador({ ...borrador, desde: e.target.value })} /></label>
        <label>Hasta, inclusive<input type="date" required value={borrador.hasta} disabled={cargando || descargando} onChange={(e) => setBorrador({ ...borrador, hasta: e.target.value })} /></label>
        <label>Modelo para pronósticos<select value={borrador.modelo} disabled={cargando || descargando} onChange={(e) => setBorrador({ ...borrador, modelo: e.target.value })}><option value="">Último modelo guardado</option>{modelos.map((m) => <option key={m.id} value={m.id}>{m.version_modelo} · #{m.id}</option>)}</select></label>
        <button type="submit" className="button-primary" disabled={cargando || descargando}>Consultar</button>
        <button type="button" className="button-secondary" disabled={cargando || descargando} onClick={() => setRevision((r) => r + 1)}>Actualizar consulta</button>
      </form>
      <div className="report-actions"><span>Últimos días disponibles:</span>{[7, 30, 90].map((dias) => <button key={dias} className="button-secondary" disabled={!informe || cargando || descargando} onClick={() => periodoRapido(dias)}>{dias} días</button>)}</div>
      {errorModelos && <p className="inline-error" role="alert">Selector de versiones: {errorModelos}</p>}
      <p className="helper-text">Hasta 366 días por consulta. El selector muestra las 50 versiones más recientes. Estos reportes muestran unidades y estados, sin calcular ingresos ni ahorro.</p>
    </section>
    {error && <EstadoPanel tono="alerta" titulo="Revisa la consulta" descripcion={error} />}
    {cargando && <p role="status">Preparando reportes…</p>}
    {informe && <>
      <section className="card section-space"><div className="section-heading"><div><h2>{informe.periodo.desde} — {informe.periodo.hasta}</h2><p>Consulta generada: {new Date(informe.generado_en).toLocaleString("es")} · {informe.periodo.dias_calendario} días calendario.</p></div><button className="button-primary" onClick={exportar} disabled={descargando}>{descargando ? "Preparando CSV…" : `Descargar CSV de ${tipos.find((t) => t.tipo === tipo)?.titulo}`}</button></div>
        <div className="report-selector" role="group" aria-label="Tipo de reporte">{tipos.map((t) => <button key={t.tipo} className={tipo === t.tipo ? "button-primary" : "button-secondary"} aria-pressed={tipo === t.tipo} disabled={descargando} onClick={() => { setTipo(t.tipo); setEstadoDescarga(""); setDiaDetalle(""); }}>{t.titulo}</button>)}</div>
        {estadoDescarga && <p role="status">{estadoDescarga}</p>}
        <p className="helper-text">Ventas disponibles: {informe.periodo.ventas_desde ?? "sin registros"} a {informe.periodo.ventas_hasta ?? "sin registros"}. Propuestas disponibles: {informe.periodo.pedidos_desde ?? "sin registros"} a {informe.periodo.pedidos_hasta ?? "sin registros"}.</p>
      </section>
      {tipo === "ventas" && <>
        <div className="report-kpis"><div><span>Unidades vendidas</span><strong>{informe.ventas.registros ? numero(informe.ventas.unidades) : "Sin registros"}</strong></div><div><span>Días observados</span><strong>{informe.ventas.dias_observados} / {informe.periodo.dias_calendario}</strong></div><div><span>Productos observados</span><strong>{informe.ventas.productos_observados}</strong></div><div><span>Registros producto/día</span><strong>{numero(informe.ventas.registros)}</strong></div></div>
        <section className="card"><GraficoVentas informe={informe} /><p className="helper-text">Fuente: {informe.fuentes.ventas}. Una ausencia no equivale a cero. Los días con menos productos observados pueden tener cobertura parcial.</p></section>
        {!informe.ventas.registros ? <EstadoPanel titulo="Sin ventas en este período" descripcion="Elige otras fechas o revisa la primera carga. No se completan los días desconocidos con ceros." /> : <>
          <section className="card section-space"><h2>Detalle por día</h2><TablaPaginada><thead><tr><th>Fecha</th><th>Unidades</th><th>Productos observados</th></tr></thead><tbody>{informe.ventas.serie_diaria.map((d) => <tr key={d.fecha}><td>{d.fecha}</td><td>{numero(d.unidades)}</td><td>{d.productos_observados}</td></tr>)}</tbody></TablaPaginada></section>
          <section className="card section-space"><h2>Ranking completo por producto</h2><TablaPaginada><thead><tr><th>Producto</th><th>Unidades vendidas</th><th>Días observados</th></tr></thead><tbody>{informe.ventas.por_producto.map((p) => <tr key={p.producto_id}><td>{p.producto} · #{p.producto_id}</td><td>{numero(p.unidades)}</td><td>{p.dias_observados}</td></tr>)}</tbody></TablaPaginada></section>
        </>}
      </>}
      {tipo === "pedidos" && <>
        <div className="report-kpis"><div><span>Pedidos</span><strong>{informe.pedidos.total}</strong></div><div><span>Propuestas</span><strong>{informe.pedidos.propuestas}</strong></div><div><span>Propuestas sin pedidos</span><strong>{informe.pedidos.propuestas_sin_pedidos}</strong></div></div>
        <section className="card"><GraficoBarras titulo="Estado de pedidos" descripcion={informe.fuentes.pedidos} tono="pedidos" filas={informe.pedidos.por_estado.filter((e) => e.cantidad > 0).map((e) => ({ etiqueta: etiquetasEstado[e.estado], cantidad: e.cantidad }))} /><p>Un pedido enviado indica confirmación del mensaje; no acredita recepción de ingredientes ni cambia stock. Los intentos repetidos no duplican el conteo.</p><Link href="/compras">Consultar pedidos y sus mensajes →</Link>
          <TablaPaginada><thead><tr><th>Estado actual</th><th>Pedidos</th></tr></thead><tbody>{informe.pedidos.por_estado.map((e) => <tr key={e.estado}><td>{etiquetasEstado[e.estado]}</td><td>{e.cantidad}</td></tr>)}</tbody></TablaPaginada>
        </section>
        <section className="card section-space"><h2>Propuestas del período</h2><p>Una propuesta puede tener varios pedidos o ninguno, por ejemplo si está bloqueada o no hay faltantes.</p><TablaPaginada><thead><tr><th>Estado</th><th>Propuestas</th></tr></thead><tbody>{informe.pedidos.propuestas_por_estado.map((e) => <tr key={e.estado}><td>{etiquetasEstado[e.estado]}</td><td>{e.cantidad}</td></tr>)}</tbody></TablaPaginada></section>
      </>}
      {tipo === "pronosticos" && <>
        {informe.aviso_evaluacion && <EstadoPanel titulo="Evaluación sin fechas disponibles" descripcion={informe.aviso_evaluacion} />}
        {evaluacion && <>
          <div className="report-kpis"><div><span>Error medio · MAE</span><strong>{numero(evaluacion.metricas_globales.mae)}</strong></div><div><span>Error relativo · WAPE</span><strong>{numero(evaluacion.metricas_globales.wape_pct, "%")}</strong></div><div><span>Cobertura</span><strong>{numero(evaluacion.metricas_globales.cobertura_pct, "%")}</strong></div><div><span>Pares comparables</span><strong>{numero(evaluacion.metricas_globales.pares_evaluables)}</strong></div></div>
          <section className="card"><h2>Pronóstico frente a ventas conocidas</h2><p>Modelo #{evaluacion.modelo_id} · {evaluacion.version_modelo}. Solo se comparan productos con pronóstico disponible y venta real evaluada en su revisión vigente.</p><p className="helper-text">MAE: diferencia media en unidades. WAPE: error relativo, sin dato si la suma real es cero. Cobertura: pares con pronóstico que tienen venta evaluable; no incluye productos sin pronóstico.</p>
            {evaluacion.serie_diaria.length > 0 && <><div className="serie-leyenda"><span><i className="previsto" /> Pronóstico evaluable</span><span><i className="real" /> Venta real conocida</span></div><SerieHistorica dias={evaluacion.serie_diaria} seleccion={diaDetalle} alSeleccionar={setDiaDetalle} /><p className="helper-text">Selecciona un día para abrir sus productos en un detalle. Un día sin pares evaluables no muestra barras.</p>
              <TablaPaginada><thead><tr><th>Fecha</th><th>Pronóstico evaluable</th><th>Venta real</th><th>Pares comparables</th><th>Excluidos</th><th>Detalle</th></tr></thead><tbody>{evaluacion.serie_diaria.map((d) => <tr key={d.fecha_local}><td>{d.fecha_local}</td><td>{d.productos_evaluables ? numero(d.total_previsto_evaluable) : "Sin dato"}</td><td>{d.productos_evaluables ? numero(d.total_real_conocido) : "Sin dato"}</td><td>{d.productos_evaluables}</td><td>{d.productos_excluidos}</td><td><button className="button-secondary" onClick={() => setDiaDetalle(d.fecha_local)}>Ver productos</button></td></tr>)}</tbody></TablaPaginada>
            </>}
            <p><Link href={`/panel?modelo_id=${evaluacion.modelo_id}`}>Ver evaluación completa y partición del modelo →</Link></p>
          </section>
        </>}
      </>}
      {detalle && <PanelDetalle titulo={`Productos del ${detalle.fecha_local}`} onCerrar={() => setDiaDetalle("")}><p>{detalle.productos_evaluables} comparables · {detalle.productos_excluidos} con pronóstico sin real evaluable · {evaluacion?.trazas.find((t) => t.fecha_local === detalle.fecha_local)?.pronosticos_no_disponibles.length ?? 0} sin pronóstico disponible.</p><TablaPaginada><thead><tr><th>Producto</th><th>Pronóstico</th><th>Venta real</th><th>Error absoluto</th><th>Exclusión</th></tr></thead><tbody>{detalle.desglose_productos.map((p) => <tr key={p.producto_id}><td>{p.producto ?? `#${p.producto_id}`}</td><td>{numero(p.previsto)}</td><td>{p.real === null ? "Desconocida" : numero(p.real)}</td><td>{numero(p.diferencia_absoluta)}</td><td>{p.motivo_exclusion ?? "—"}</td></tr>)}</tbody></TablaPaginada></PanelDetalle>}
    </>}
  </>;
}

export default function InformesPage() {
  return <ProtectedShell titulo="Reportes" descripcion="Ventas, pronósticos y pedidos con fechas, fuentes y exportación CSV.">{({ token }) => <Contenido token={token} />}</ProtectedShell>;
}
