"use client";
import Link from "next/link";
import { formatearEscenario, formatearFechaHora } from "@/utils/fechas";
import { useEffect, useState, type FormEvent } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { PanelDetalle } from "@/components/ui/PanelDetalle";
import { TablaPaginada } from "@/components/tables/TablaPaginada";
import { leerRegla, guardarRegla, listarEvaluacionesPromocion, type ReglaPromocion, type EvaluacionPromocion } from "@/services/promociones";
const inicial: ReglaPromocion = { habilitada: false, hora_revision: "17:00", hora_cierre: "20:00", stock_umbral: 5, descuento_pct: 20, descuento_maximo_pct: 30, antiguedad_maxima_stock_min: 30, demora_segundos: 5 };
function Contenido({ token, admin, zona }: { token: string; admin: boolean; zona: string }) {
  const [regla, setRegla] = useState(inicial), [version, setVersion] = useState<number | undefined>();
  const [lista, setLista] = useState<EvaluacionPromocion[]>([]), [detalle, setDetalle] = useState<EvaluacionPromocion | null>(null);
  const [pagina, setPagina] = useState(1), [tamano, setTamano] = useState(25), [total, setTotal] = useState(0);
  const [ocupado, setOcupado] = useState(false), [cargando, setCargando] = useState(true), [error, setError] = useState(""), [mensaje, setMensaje] = useState("");
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const control = new AbortController();
    leerRegla(token, control.signal).then((r) => { if (!control.signal.aborted && r) { setRegla(r); setVersion(r.version); } }).catch((e: unknown) => { if (!control.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo consultar la regla."); });
    return () => control.abort();
  }, [token]);
  useEffect(() => {
    const control = new AbortController(); let temporizador: ReturnType<typeof setTimeout>; setCargando(true);
    async function actualizar() {
      try { const sobre = await listarEvaluacionesPromocion(token, pagina, tamano, control.signal); if (!control.signal.aborted) { setLista(sobre.datos); setTotal(Number(sobre.metadatos?.total ?? 0)); } }
      catch (e) { if (!control.signal.aborted) setError(e instanceof Error ? e.message : "No se pudieron consultar las evaluaciones."); }
      finally { if (!control.signal.aborted) { setCargando(false); temporizador = setTimeout(actualizar, 5000); } }
    }
    void actualizar(); return () => { control.abort(); clearTimeout(temporizador); };
  }, [token, pagina, tamano, revision]);
  async function guardar(e: FormEvent) {
    e.preventDefault(); setOcupado(true); setError(""); setMensaje("");
    try { const r = await guardarRegla(token, regla); setRegla(r); setVersion(r.version); setMensaje(r.habilitada ? "Regla guardada. Los próximos ajustes de productos tendrán una evaluación automática." : "Promociones deshabilitadas para nuevos ajustes. Las evaluaciones anteriores se conservan."); }
    catch (e) { setError(e instanceof Error ? e.message : "No se pudo guardar la regla."); } finally { setOcupado(false); }
  }
  return <>
    {error && <EstadoPanel tono="alerta" titulo="Revisa la operación" descripcion={error} />}
    {mensaje && <p className="inline-success" role="status">{mensaje}</p>}
    <section className="card"><div className="section-heading"><div><h2>Regla de sugerencias {version ? `· versión ${version}` : ""}</h2><p>Evalúa un lote después de ajustar su stock. El descuento es una sugerencia para revisar.</p></div><span className={`badge badge-${regla.habilitada ? "ok" : "neutral"}`}>{regla.habilitada ? "Habilitada" : "Deshabilitada"}</span></div>
      <form onSubmit={guardar} className="promotion-rule"><fieldset disabled={!admin || ocupado} className="form-grid">
        <label className="review-checkbox field-full"><input type="checkbox" checked={regla.habilitada} onChange={(e) => setRegla({ ...regla, habilitada: e.target.checked })} />Evaluar promociones después de cada ajuste de producto</label>
        <label className="field">Desde qué hora del escenario<input type="time" required value={regla.hora_revision.slice(0, 5)} onChange={(e) => setRegla({ ...regla, hora_revision: e.target.value })} /></label>
        <label className="field">Hora de cierre del escenario<input type="time" required value={regla.hora_cierre.slice(0, 5)} onChange={(e) => setRegla({ ...regla, hora_cierre: e.target.value })} /></label>
        {([["stock_umbral", "Sugerir si quedan más de (unidades)", 0, 1000000], ["descuento_pct", "Descuento sugerido (%)", 1, 100], ["descuento_maximo_pct", "Descuento máximo (%)", 1, 100]] as const).map(([campo, texto, min, max]) => <label className="field" key={campo}>{texto}<input type="number" min={min} max={max} required value={regla[campo]} onChange={(e) => setRegla({ ...regla, [campo]: Number(e.target.value) })} /></label>)}
        <details className="field-full"><summary>Opciones de evaluación</summary><div className="form-grid"><label className="field">Antigüedad máxima de la lectura (minutos)<input type="number" min={1} max={1440} value={regla.antiguedad_maxima_stock_min} onChange={(e) => setRegla({ ...regla, antiguedad_maxima_stock_min: Number(e.target.value) })} /></label><label className="field">Espera real después del ajuste (segundos)<input type="number" min={5} max={3600} value={regla.demora_segundos} onChange={(e) => setRegla({ ...regla, demora_segundos: Number(e.target.value) })} /><small>El motor recoge la tarea en su siguiente ciclo.</small></label></div></details>
        {admin && <div className="form-actions field-full"><button className="button-primary" type="submit">{ocupado ? "Guardando…" : "Guardar regla"}</button></div>}
      </fieldset></form>{!admin && <p>Solo un administrador puede modificar la regla.</p>}
      <p className="helper-text">El lote debe vencer en ese día y la lectura debe seguir vigente. Cada cambio conserva una versión nueva.</p><Link href="/inventario">Registrar un ajuste en Inventario →</Link>
    </section>
    <section className="card section-space"><div className="section-heading"><h2>Sugerencias y descartes</h2><button className="button-secondary" onClick={() => setRevision((r) => r + 1)}>Actualizar</button></div>
      {cargando && <p role="status">Consultando evaluaciones…</p>}
      {!lista.length && !cargando ? <p>Sin evaluaciones. Habilita una regla y registra un ajuste de producto para iniciar el recorrido.</p> : <TablaPaginada remota={{ pagina, tamano, total, cargando, onCambio: (p, t) => { setPagina(p); setTamano(t); } }}><thead><tr><th>Producto y lote</th><th>Escenario</th><th>Resultado</th><th>Motivo</th><th>Detalle</th></tr></thead><tbody>{lista.map((e) => <tr key={e.id}><td>{e.lectura.producto_nombre} · {e.lectura.codigo_lote}</td><td>{formatearEscenario(e.fecha_hora_simulada)}</td><td><span className={`badge badge-${e.proponer ? "ok" : "neutral"}`}>{e.proponer ? `${e.descuento_pct}% sugerido` : "Descartada"}</span></td><td>{e.motivo}</td><td><button className="button-link" onClick={() => setDetalle(e)}>Ver detalle</button></td></tr>)}</tbody></TablaPaginada>}
    </section>
    {detalle && <PanelDetalle titulo={`Evaluación #${detalle.id}`} onCerrar={() => setDetalle(null)}><h3>{detalle.lectura.producto_nombre}</h3><p>{detalle.motivo}</p><p>Lote {detalle.lectura.codigo_lote}: {detalle.lectura.saldo} unidades registradas. Fecha límite: {formatearEscenario(detalle.lectura.fecha_limite_venta)}.</p><p>Evaluada: {formatearFechaHora(detalle.creado_en, zona)}. Regla versión {detalle.regla.version}; escenario {formatearEscenario(detalle.fecha_hora_simulada)}.</p><p>Movimiento #{detalle.movimiento_id}. <Link href={`/automatizaciones/ejecuciones/${detalle.ejecucion_id}`}>Ver tarea y sus intentos →</Link></p><p>Esta evaluación conserva los datos con los que se calculó.</p></PanelDetalle>}
  </>;
}
export default function PromocionesPage() { return <ProtectedShell titulo="Promociones sugeridas" descripcion="Configura la regla y revisa descuentos propuestos por lote.">{({ token, perfil, negocio }) => <Contenido token={token} zona={negocio.zona_horaria} admin={perfil.rol === "ADMINISTRADOR"} />}</ProtectedShell>; }
