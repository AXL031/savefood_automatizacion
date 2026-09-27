"use client";

import Link from "next/link";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { EstadoBadge } from "@/components/ui/EstadoBadge";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { crearProgramacion, listarEjecuciones, listarProgramaciones } from "@/services/automatizaciones";
import type { EjecucionAutomatizacion, EstadoEjecucion, ProgramacionDemo } from "@/types/automatizacion";
import { formatearFechaHora } from "@/utils/fechas";

function fechaLocalParaInput(fecha: Date): string {
  return new Date(fecha.getTime() - fecha.getTimezoneOffset() * 60_000).toISOString().slice(0, 16);
}

function Contenido({ token, zonaHoraria, administrador }: { token: string; zonaHoraria: string; administrador: boolean }) {
  const [programaciones, setProgramaciones] = useState<ProgramacionDemo[]>([]);
  const [ejecuciones, setEjecuciones] = useState<EjecucionAutomatizacion[]>([]);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [errorCarga, setErrorCarga] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [filtro, setFiltro] = useState<EstadoEjecucion | "TODAS">("TODAS");
  const [horaReal, setHoraReal] = useState("");
  const [horaSimulada, setHoraSimulada] = useState("2022-08-24T10:00");
  const [productos, setProductos] = useState("");
  const [clave, setClave] = useState("");

  useEffect(() => {
    setHoraReal(fechaLocalParaInput(new Date(Date.now() + 5 * 60_000)));
    setClave(`propuesta-${crypto.randomUUID()}`);
  }, []);

  useEffect(() => {
    const control = new AbortController();
    let temporizador: ReturnType<typeof setTimeout>;
    async function actualizar() {
      try {
        const [programadas, registradas] = await Promise.all([listarProgramaciones(token, control.signal), listarEjecuciones(token, control.signal)]);
        if (control.signal.aborted) return;
        setProgramaciones(programadas);
        setEjecuciones(registradas);
        setErrorCarga("");
      } catch (fallo) {
        if (!control.signal.aborted) setErrorCarga(fallo instanceof Error ? fallo.message : "No se pudieron actualizar las automatizaciones.");
      } finally {
        if (!control.signal.aborted) {
          setCargando(false);
          temporizador = setTimeout(actualizar, 5000);
        }
      }
    }
    void actualizar();
    return () => { control.abort(); clearTimeout(temporizador); };
  }, [token]);

  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setError("");
    setMensaje("");
    const ids = productos.split(",").map((valor) => Number(valor.trim()));
    if (!horaReal || !horaSimulada || !clave || ids.length < 1 || ids.length > 5 || ids.some((id) => !Number.isInteger(id) || id <= 0)) {
      setError("Indica hora real, escenario, clave y entre 1 y 5 IDs de producto positivos separados por comas.");
      return;
    }
    setGuardando(true);
    try {
      const creada = await crearProgramacion(token, {
        tipo: "GENERAR_PROPUESTA",
        ejecutar_desde_utc: new Date(horaReal).toISOString(),
        fecha_hora_simulada_local: `${horaSimulada}:00`,
        fecha_objetivo_demo: horaSimulada.slice(0, 10),
        producto_ids: ids,
        clave_idempotencia: clave,
      });
      const [programadas, registradas] = await Promise.all([listarProgramaciones(token), listarEjecuciones(token)]);
      setProgramaciones(programadas);
      setEjecuciones(registradas);
      setMensaje(`Programación #${creada.id} guardada. El motor la recogerá al llegar la hora real; el estado se actualiza automáticamente.`);
      setClave(`propuesta-${crypto.randomUUID()}`);
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo guardar la programación.");
    } finally {
      setGuardando(false);
    }
  }

  const visibles = useMemo(
    () => filtro === "TODAS" ? ejecuciones : ejecuciones.filter((item) => item.estado === filtro),
    [ejecuciones, filtro],
  );

  return <>
    <EstadoPanel tono="info" titulo="Motor automático disponible; cálculos pendientes de integración" descripcion="Las programaciones se despachan con los servicios de automatización encendidos. Los cálculos de pronóstico y plan aún requieren conectar sus módulos; mientras tanto, una ejecución informa el servicio faltante." />
    {errorCarga && <div className="inline-error" role="alert">No se pudo actualizar: {errorCarga}</div>}
    {error && <div className="inline-error" role="alert">{error}</div>}
    {mensaje && <div className="inline-success" role="status">{mensaje}</div>}
    <div className="page-grid section-space">
      <section className="card main-card">
        <div className="section-heading"><div><h2>Programar propuesta demostrativa</h2><p>La hora real fija cuándo se despachará; la hora simulada identifica el escenario histórico.</p></div></div>
        <form className="form-grid" onSubmit={guardar}>
          <label className="field">Hora real próxima (zona de este equipo)<input type="datetime-local" value={horaReal} onChange={(e) => setHoraReal(e.target.value)} disabled={!administrador || guardando} required /></label>
          <label className="field">Hora local del escenario<input type="datetime-local" value={horaSimulada} onChange={(e) => setHoraSimulada(e.target.value)} disabled={!administrador || guardando} required /></label>
          <label className="field field-full">IDs de productos<input value={productos} onChange={(e) => setProductos(e.target.value)} placeholder="1, 2, 3" disabled={!administrador || guardando} required /><small>Usa IDs del catálogo cuando Edu lo entregue. La programación todavía no comprueba la existencia del producto.</small></label>
          <label className="field field-full">Clave de la solicitud<input value={clave} onChange={(e) => setClave(e.target.value)} maxLength={128} disabled={!administrador || guardando} required /><small>Repetir esta clave con los mismos datos recupera la programación. Cambiar sus datos produce un conflicto.</small></label>
          <div className="form-actions field-full"><button className="button-primary" type="submit" disabled={!administrador || guardando}>{guardando ? "Guardando…" : "Guardar programación"}</button></div>
        </form>
        {!administrador && <p className="helper-text">Solo un administrador puede crear programaciones.</p>}
      </section>
      <aside className="card aside-card"><h2>Seguimiento automático</h2><p>El motor revisa tareas cada 30 segundos. Un fallo interno temporal permite hasta tres intentos. Consulta el detalle para ver el resultado o el motivo del fallo.</p><p className="helper-text">La vista se actualiza cada 5 segundos y muestra hasta 50 registros recientes. Las horas reales de las tablas se muestran en {zonaHoraria}.</p><div className="fact"><span>Programaciones recientes</span><strong>{programaciones.length}</strong></div><div className="fact"><span>Ejecuciones recientes</span><strong>{ejecuciones.length}</strong></div></aside>
    </div>
    <section className="card section-space">
      <div className="section-heading"><div><h2>Programaciones guardadas</h2><p>Se muestran por separado la hora real y el reloj del escenario.</p></div></div>
      {cargando ? <p role="status">Cargando programaciones…</p> : programaciones.length ? <div className="table-wrap"><table><thead><tr><th>Tipo</th><th>Hora real</th><th>Escenario local</th><th>Estado</th><th>Ejecución</th></tr></thead><tbody>{programaciones.map((item) => <tr key={item.id}><td>{item.tipo}</td><td>{formatearFechaHora(item.ejecutar_desde_utc, zonaHoraria)}</td><td>{item.fecha_hora_simulada_local.replace("T", " ")}</td><td><span className={`badge badge-${item.estado === "CANCELADA" ? "alerta" : item.estado === "DESPACHADA" ? "info" : "neutral"}`}>{item.estado}</span></td><td>{item.ejecucion_id ? <Link href={`/automatizaciones/ejecuciones/${item.ejecucion_id}`}>Ver #{item.ejecucion_id}</Link> : "—"}</td></tr>)}</tbody></table></div> : <EstadoPanel titulo="Sin programaciones" descripcion="Aún no hay una propuesta guardada." />}
    </section>
    <section className="card section-space">
      <div className="section-heading"><div><h2>Ejecuciones e intentos</h2><p>El resultado aparecerá cuando el servicio de dominio complete la ejecución.</p></div><label className="filter-label">Estado<select value={filtro} onChange={(e) => setFiltro(e.target.value as EstadoEjecucion | "TODAS")}><option value="TODAS">Todas</option><option value="PENDIENTE">Pendiente</option><option value="EN_EJECUCION">En ejecución</option><option value="REINTENTANDO">Reintentando</option><option value="COMPLETADA">Completada</option><option value="FALLIDA">Fallida</option></select></label></div>
      {cargando ? <p role="status">Cargando ejecuciones…</p> : visibles.length ? <div className="table-wrap"><table><thead><tr><th>ID</th><th>Tipo</th><th>Inicio real</th><th>Estado</th><th>Intentos</th><th></th></tr></thead><tbody>{visibles.map((item) => <tr key={item.id}><td>#{item.id}</td><td>{item.tipo}</td><td>{formatearFechaHora(item.inicio_en, zonaHoraria)}</td><td><EstadoBadge estado={item.estado} /></td><td>{item.intentos.length}/3</td><td><Link href={`/automatizaciones/ejecuciones/${item.id}`}>Ver detalle</Link></td></tr>)}</tbody></table></div> : <EstadoPanel titulo="Sin ejecuciones para este filtro" descripcion="Cambia el filtro o crea una programación." />}
    </section>
  </>;
}

export default function AutomatizacionesPage() {
  return <ProtectedShell titulo="Automatizaciones" descripcion="Programa propuestas y consulta sus ejecuciones persistidas.">{({ token, negocio, perfil }) => <Contenido token={token} zonaHoraria={negocio.zona_horaria} administrador={perfil.rol === "ADMINISTRADOR"} />}</ProtectedShell>;
}
