"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { EstadoBadge } from "@/components/ui/EstadoBadge";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { listarAutomatizaciones, listarEjecuciones } from "@/services/automatizaciones";
import { HttpError } from "@/services/http";
import type { Automatizacion, EjecucionAutomatizacion, EstadoEjecucion } from "@/types/automatizacion";
import { formatearDuracion, formatearFechaHora } from "@/utils/fechas";

const pasos = ["Detectar", "Decidir", "Actuar", "Verificar", "Corregir", "Notificar"];
const reglasPrevistas = [
  { nombre: "Planificación diaria", detalle: "Ventas históricas e inventario → pronóstico y plan." },
  { nombre: "Pedido al proveedor", detalle: "Insumos faltantes → pedido y comprobación del envío." },
  { nombre: "Control de excedentes", detalle: "Producción y ventas → riesgo durante el día." },
  { nombre: "Promoción preventiva", detalle: "Riesgo alto → promoción y seguimiento del efecto." },
];

function Contenido({ token, zonaHoraria }: { token: string; zonaHoraria: string }) {
  const [reglas, setReglas] = useState<Automatizacion[]>([]);
  const [ejecuciones, setEjecuciones] = useState<EjecucionAutomatizacion[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [sinApi, setSinApi] = useState(false);
  const [filtro, setFiltro] = useState<EstadoEjecucion | "TODAS">("TODAS");

  useEffect(() => {
    const control = new AbortController();
    Promise.all([listarAutomatizaciones(token, control.signal), listarEjecuciones(token, control.signal)])
      .then(([reglasActuales, ejecucionesActuales]) => {
        setReglas(reglasActuales);
        setEjecuciones(ejecucionesActuales);
        setError("");
        setSinApi(false);
      })
      .catch((fallo: unknown) => {
        if (control.signal.aborted) return;
        if (fallo instanceof HttpError && (fallo.status === 404 || fallo.status === 501)) setSinApi(true);
        else setError(fallo instanceof Error ? fallo.message : "No se pudieron cargar las automatizaciones.");
      })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token]);

  const visibles = useMemo(() => filtro === "TODAS" ? ejecuciones : ejecuciones.filter((item) => item.estado === filtro), [ejecuciones, filtro]);
  const completadas = ejecuciones.filter((item) => item.estado === "COMPLETADO").length;
  const fallidas = ejecuciones.filter((item) => item.estado === "FALLIDO").length;
  const enControl = ejecuciones.filter((item) => ["VERIFICANDO", "REINTENTANDO"].includes(item.estado)).length;

  return <>
    {sinApi && <EstadoPanel tono="info" titulo="Automatizaciones pendientes de integración" descripcion="La pantalla está preparada, pero la API de automatizaciones y ejecuciones aún no está disponible. Los elementos que aparecen como previstos no son reglas activas." />}
    {error && <EstadoPanel tono="alerta" titulo="No se pudieron cargar los datos" descripcion={error} accion={<button className="button-secondary" onClick={() => window.location.reload()}>Volver a intentar</button>} />}
    <div className="stats-grid">
      <div className="card stat"><span>Ejecuciones recibidas</span><strong>{sinApi ? "—" : ejecuciones.length}</strong><small>En la respuesta actual</small></div>
      <div className="card stat"><span>Completadas</span><strong>{sinApi ? "—" : completadas}</strong><small>Con resultado verificado</small></div>
      <div className="card stat"><span>En control</span><strong>{sinApi ? "—" : enControl}</strong><small>Verificando o reintentando</small></div>
      <div className="card stat"><span>Fallidas</span><strong>{sinApi ? "—" : fallidas}</strong><small>Requieren revisión</small></div>
    </div>
    <div className="page-grid">
      <section className="card main-card"><div className="section-heading"><div><h2>Reglas automáticas</h2><p>Frecuencia, acción y activación de cada regla.</p></div><button className="button-secondary" disabled title="La API de creación aún no está disponible">Nueva automatización</button></div>
        {cargando ? <p role="status">Cargando reglas…</p> : reglas.length ? <div className="rule-list">{reglas.map((regla) => <div className="rule-row" key={regla.id}><div><strong>{regla.nombre}</strong><small>{regla.programacion || "Sin programación"}</small></div><span className={`badge ${regla.habilitado ? "badge-ok" : "badge-neutral"}`}>{regla.habilitado ? "Activa" : "Desactivada"}</span></div>)}</div> : <div className="planned-list">{reglasPrevistas.map((regla) => <div className="rule-row" key={regla.nombre}><div><strong>{regla.nombre}</strong><small>{regla.detalle}</small></div><span className="badge badge-neutral">Prevista</span></div>)}</div>}
      </section>
      <aside className="card aside-card"><h2>Ciclo de control</h2><p>Cada ejecución debe registrar qué decidió, qué acción realizó y cómo comprobó el resultado.</p><ol className="steps-list">{pasos.map((paso) => <li key={paso}>{paso}</li>)}</ol><p className="helper-text">Un mensaje enviado a Telegram aún requiere confirmación del proveedor.</p></aside>
    </div>
    <section className="card section-space"><div className="section-heading"><div><h2>Últimas ejecuciones</h2><p>Selecciona una para ver intentos, error y resultado.</p></div><label className="filter-label">Estado<select value={filtro} onChange={(e) => setFiltro(e.target.value as EstadoEjecucion | "TODAS")}><option value="TODAS">Todas</option><option value="PENDIENTE">Pendiente</option><option value="EN_EJECUCION">En ejecución</option><option value="VERIFICANDO">Verificando</option><option value="COMPLETADO">Completado</option><option value="REINTENTANDO">Reintentando</option><option value="FALLIDO">Fallido</option><option value="CANCELADO">Cancelado</option></select></label></div>
      {cargando ? <p role="status">Cargando ejecuciones…</p> : visibles.length ? <div className="table-wrap"><table><thead><tr><th>Automatización</th><th>Inicio</th><th>Duración</th><th>Estado</th><th></th></tr></thead><tbody>{visibles.map((item) => <tr key={item.id}><td>{item.nombre_automatizacion ?? `Regla #${item.automatizacion_id}`}</td><td>{formatearFechaHora(item.inicio_en, zonaHoraria)}</td><td>{formatearDuracion(item.inicio_en, item.fin_en)}</td><td><EstadoBadge estado={item.estado} /></td><td><Link href={`/automatizaciones/ejecuciones/${item.id}`}>Ver detalle</Link></td></tr>)}</tbody></table></div> : <EstadoPanel titulo={sinApi ? "Sin registros disponibles" : "No hay ejecuciones para este filtro"} descripcion={sinApi ? "El historial aparecerá cuando se implemente la API de ejecuciones." : "Prueba otro estado o espera la siguiente ejecución."} />}
    </section>
  </>;
}

export default function AutomatizacionesPage() {
  return <ProtectedShell titulo="Automatizaciones" descripcion="Consulta las reglas, su actividad reciente y las ejecuciones que necesitan atención.">{({ token, negocio }) => <Contenido token={token} zonaHoraria={negocio.zona_horaria} />}</ProtectedShell>;
}
