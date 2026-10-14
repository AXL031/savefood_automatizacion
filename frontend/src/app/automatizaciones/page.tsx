"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { PanelDetalle } from "@/components/ui/PanelDetalle";
import { EstadoBadge } from "@/components/ui/EstadoBadge";
import { TablaPaginada } from "@/components/tables/TablaPaginada";
import { AsistenteFlujo } from "@/features/automatizaciones/AsistenteFlujo";
import { ejecucionesPaginadas, programacionesPaginadas } from "@/services/automatizaciones";
import { gestionarProgramacion, reprogramar } from "@/services/flujo";
import type { EjecucionAutomatizacion, ProgramacionDemo } from "@/types/automatizacion";
import { formatearFechaHora, formatearEscenario } from "@/utils/fechas";
import { etiquetaDato } from "@/utils/etiquetas";
function Contenido({ token, zona, admin }: { token: string; zona: string; admin: boolean }) {
  const [programaciones, setProgramaciones] = useState<ProgramacionDemo[]>([]), [ejecuciones, setEjecuciones] = useState<EjecucionAutomatizacion[]>([]);
  const [paginaP, setPaginaP] = useState(1), [tamanoP, setTamanoP] = useState(25), [totalP, setTotalP] = useState(0);
  const [paginaE, setPaginaE] = useState(1), [tamanoE, setTamanoE] = useState(25), [totalE, setTotalE] = useState(0);
  const [revision, setRevision] = useState(0), [error, setError] = useState(""), [cargando, setCargando] = useState(true);
  const [seleccion, setSeleccion] = useState<ProgramacionDemo | null>(null), [accion, setAccion] = useState("PAUSAR"), [motivo, setMotivo] = useState(""), [hora, setHora] = useState("");
  const [ocupado, setOcupado] = useState(false), [errorGestion, setErrorGestion] = useState("");
  useEffect(() => {
    const control = new AbortController(); let temporizador: ReturnType<typeof setTimeout>;
    async function actualizar() {
      try { const [p, e] = await Promise.all([programacionesPaginadas(token, paginaP, tamanoP, control.signal), ejecucionesPaginadas(token, paginaE, tamanoE, control.signal)]); if (!control.signal.aborted) { setProgramaciones(p.datos); setEjecuciones(e.datos); setTotalP(Number(p.metadatos?.total ?? 0)); setTotalE(Number(e.metadatos?.total ?? 0)); setError(""); } }
      catch (e) { if (!control.signal.aborted) setError(e instanceof Error ? e.message : "No se pudieron consultar las tareas."); }
      finally { if (!control.signal.aborted) { setCargando(false); temporizador = setTimeout(actualizar, 5000); } }
    }
    void actualizar(); return () => { control.abort(); clearTimeout(temporizador); };
  }, [token, revision, paginaP, tamanoP, paginaE, tamanoE]);
  async function gestionar() {
    if (!seleccion) return; setOcupado(true); setErrorGestion("");
    try {
      if (accion === "REPROGRAMAR") await reprogramar(token, seleccion.id, new Date(hora).toISOString(), motivo);
      else await gestionarProgramacion(token, seleccion.id, accion, motivo);
      setSeleccion(null); setRevision((r) => r + 1);
    } catch (e) { setErrorGestion(e instanceof Error ? e.message : "No se pudo guardar el cambio."); }
    finally { setOcupado(false); }
  }
  return <>
    <AsistenteFlujo token={token} zona={zona} admin={admin} alProgramar={() => { setPaginaP(1); setPaginaE(1); setRevision((r) => r + 1); }} />
    {error && <p className="inline-error" role="alert">{error}</p>}
    <section className="card section-space"><h2>Próximas tareas y programaciones recientes</h2><p>Actualización automática. Las horas se muestran en {zona}.</p>
      {cargando ? <p role="status">Consultando tareas…</p> : <TablaPaginada remota={{ pagina: paginaP, tamano: tamanoP, total: totalP, cargando, onCambio: (p, t) => { setPaginaP(p); setTamanoP(t); } }}><thead><tr><th>Tarea</th><th>Cuándo ejecutar</th><th>Día planificado</th><th>Estado</th><th>Resultado</th>{admin && <th>Gestionar</th>}</tr></thead><tbody>{programaciones.map((p) => <tr key={p.id}><td>{etiquetaDato(p.tipo)}</td><td>{formatearFechaHora(p.ejecutar_desde_utc, zona)}</td><td>{formatearEscenario(p.fecha_hora_simulada_local)}</td><td><span className="badge badge-neutral">{p.estado === "PAUSADA" ? "Pausada" : etiquetaDato(p.estado)}</span></td><td>{p.ejecucion_id && <Link href={`/automatizaciones/ejecuciones/${p.ejecucion_id}`}>Ver tarea #{p.ejecucion_id}</Link>}</td>{admin && <td>{p.tipo === "GENERAR_PROPUESTA" && ["PROGRAMADA", "PAUSADA"].includes(p.estado) && <button className="button-link" onClick={() => { setSeleccion(p); setAccion(p.estado === "PAUSADA" ? "REANUDAR" : "PAUSAR"); setMotivo(""); setHora(""); setErrorGestion(""); }}>Gestionar</button>}</td>}</tr>)}</tbody></TablaPaginada>}
      {!cargando && !programaciones.length && <p>Al confirmar el asistente aparecerá tu primera programación aquí.</p>}
      <p className="helper-text">Las tareas pendientes aparecen primero. Puedes recorrer todo el historial. Pausar o cancelar conserva el historial; las tareas despachadas mantienen su resultado.</p>
    </section>
    <section className="card section-space"><h2>Actividad e historial</h2><TablaPaginada remota={{ pagina: paginaE, tamano: tamanoE, total: totalE, cargando, onCambio: (p, t) => { setPaginaE(p); setTamanoE(t); } }}><thead><tr><th>Tarea</th><th>Estado</th><th>Intentos</th><th>Detalle</th></tr></thead><tbody>{ejecuciones.map((e) => <tr key={e.id}><td>{etiquetaDato(e.tipo)}</td><td><EstadoBadge estado={e.estado} /></td><td>{e.intentos.length}</td><td><Link href={`/automatizaciones/ejecuciones/${e.id}`}>Ver resultado</Link></td></tr>)}</tbody></TablaPaginada><p className="helper-text">Historial completo de ejecuciones. Las tareas pausadas esperan tu decisión.</p></section>
    {seleccion && <PanelDetalle titulo={`Gestionar programación #${seleccion.id}`} ocupado={ocupado} onCerrar={() => setSeleccion(null)}><p>Hora actual: {formatearFechaHora(seleccion.ejecutar_desde_utc, zona)}. Día planificado: {formatearEscenario(seleccion.fecha_hora_simulada_local)}.</p><form onSubmit={(e) => { e.preventDefault(); void gestionar(); }}><fieldset disabled={ocupado}><label className="field">Qué quieres hacer<select value={accion} onChange={(e) => setAccion(e.target.value)}><option value={seleccion.estado === "PAUSADA" ? "REANUDAR" : "PAUSAR"}>{seleccion.estado === "PAUSADA" ? "Reanudar" : "Pausar"}</option><option value="EJECUTAR_AHORA">Ejecutar ahora</option><option value="REPROGRAMAR">Cambiar horario</option><option value="CANCELAR">Cancelar esta tarea</option></select></label>{accion === "EJECUTAR_AHORA" && <p>Adelanta esta tarea al próximo ciclo del motor (hasta 30 segundos). Conserva la fecha planificada, el modelo y el modo de envío de los pedidos.</p>}{accion === "REPROGRAMAR" && <label className="field">Nuevo horario · hora de este equipo<input type="datetime-local" required value={hora} onChange={(e) => setHora(e.target.value)} /></label>}<label className="field">Motivo<input required minLength={3} maxLength={300} value={motivo} onChange={(e) => setMotivo(e.target.value)} /></label>{errorGestion && <p role="alert" className="inline-error">{errorGestion}</p>}<button type="submit" className="button-primary">{ocupado ? "Guardando…" : "Confirmar cambio"}</button></fieldset></form><p>Si una tarea pausada perdió su horario, cambia la hora antes de reanudarla.</p>{!!seleccion.cambios?.length && <details><summary>Historial de cambios</summary><ul>{seleccion.cambios.map((c, i) => <li key={i}>{c.accion} · {c.motivo} · {c.fecha}</li>)}</ul></details>}</PanelDetalle>}
  </>;
}
export default function AutomatizacionesPage() { return <ProtectedShell titulo="Automatización" descripcion="Programa la planificación automática y sigue sus resultados.">{({ token, negocio, perfil }) => <Contenido token={token} zona={negocio.zona_horaria} admin={perfil.rol === "ADMINISTRADOR"} />}</ProtectedShell>; }
