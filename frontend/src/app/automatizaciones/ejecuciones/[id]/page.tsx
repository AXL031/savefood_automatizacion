"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { EstadoBadge } from "@/components/ui/EstadoBadge";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { obtenerEjecucion } from "@/services/automatizaciones";
import type { EjecucionAutomatizacion } from "@/types/automatizacion";
import { formatearDuracion, formatearFechaHora } from "@/utils/fechas";

function Detalle({ token, id, zonaHoraria }: { token: string; id: string; zonaHoraria: string }) {
  const [ejecucion, setEjecucion] = useState<EjecucionAutomatizacion | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const control = new AbortController();
    obtenerEjecucion(token, id, control.signal)
      .then((dato) => { setEjecucion(dato); setError(""); })
      .catch((fallo: unknown) => {
        if (control.signal.aborted) return;
        setError(fallo instanceof Error ? fallo.message : "No se pudo cargar la ejecución.");
      })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token, id]);

  if (cargando) return <EstadoPanel titulo="Cargando ejecución" descripcion="Consultando el estado en la API local." />;
  if (error) {
    return <EstadoPanel tono="alerta" titulo="No se pudo abrir la ejecución" descripcion={error} accion={<Link href="/automatizaciones">Volver a automatizaciones</Link>} />;
  }
  if (!ejecucion) return <EstadoPanel titulo="Ejecución no encontrada" descripcion="Comprueba el identificador o vuelve al historial." />;

  return <>
    <Link className="back-link" href="/automatizaciones">← Todas las automatizaciones</Link>
    {ejecucion.estado === "FALLIDA" && <EstadoPanel tono="alerta" titulo="Esta ejecución requiere atención" descripcion={ejecucion.mensaje_error || "Consulta los intentos para identificar la causa."} />}
    {ejecucion.estado === "PENDIENTE" && <EstadoPanel tono="info" titulo="Pendiente de despacho" descripcion="La programación y esta ejecución están guardadas. El despachador automático se incorporará en el corte A03." />}
    <div className="stats-grid">
      <div className="card stat"><span>Estado</span><div className="stat-badge"><EstadoBadge estado={ejecucion.estado} /></div></div>
      <div className="card stat"><span>Intentos realizados</span><strong>{ejecucion.intentos.length}</strong></div>
      <div className="card stat"><span>Duración</span><strong className="stat-text">{ejecucion.inicio_en ? formatearDuracion(ejecucion.inicio_en, ejecucion.fin_en) : "Aún no inicia"}</strong></div>
      <div className="card stat"><span>Inicio real</span><strong className="stat-text">{ejecucion.inicio_en ? formatearFechaHora(ejecucion.inicio_en, zonaHoraria) : "Pendiente"}</strong></div>
    </div>
    <div className="page-grid">
      <section className="card main-card">
        <div className="section-heading"><div><h2>Intentos y trazabilidad</h2><p>Los intentos aparecen cuando el motor comienza a ejecutar la tarea.</p></div></div>
        {ejecucion.intentos.length ? <ol className="timeline">{ejecucion.intentos.map((intento) => <li key={intento.id}><div><strong>Intento {intento.numero_intento}</strong><EstadoBadge estado={intento.estado} /></div><small>{formatearFechaHora(intento.inicio_en, zonaHoraria)} · {intento.fin_en ? formatearDuracion(intento.inicio_en, intento.fin_en) : "En curso"}</small>{intento.mensaje_error && <p className="error-text">{intento.mensaje_error}</p>}</li>)}</ol> : <EstadoPanel titulo="Sin intentos" descripcion="Esta ejecución aún no ha comenzado." />}
      </section>
      <aside className="card aside-card">
        <h2>Datos de ejecución</h2>
        <p>Tipo: {ejecucion.tipo}</p>
        <p>Clave: {ejecucion.clave_idempotencia}</p>
        {typeof ejecucion.datos_entrada.ejecutar_desde_utc === "string" && <p>Hora real programada: {formatearFechaHora(ejecucion.datos_entrada.ejecutar_desde_utc, zonaHoraria)}</p>}
        {typeof ejecucion.datos_entrada.fecha_hora_simulada_local === "string" && <p>Escenario histórico: {ejecucion.datos_entrada.fecha_hora_simulada_local.replace("T", " ")}</p>}
        <p>Próximo intento: {ejecucion.proximo_intento_en ? formatearFechaHora(ejecucion.proximo_intento_en, zonaHoraria) : "Sin programar"}</p>
        {ejecucion.datos_salida && <><h3>Resultado</h3><pre>{JSON.stringify(ejecucion.datos_salida, null, 2)}</pre></>}
      </aside>
    </div>
  </>;
}

export default function EjecucionPage() {
  const params = useParams<{ id: string }>();
  return <ProtectedShell titulo={`Ejecución #${params.id}`} descripcion="Estado e intentos registrados.">{({ token, negocio }) => <Detalle token={token} id={params.id} zonaHoraria={negocio.zona_horaria} />}</ProtectedShell>;
}
