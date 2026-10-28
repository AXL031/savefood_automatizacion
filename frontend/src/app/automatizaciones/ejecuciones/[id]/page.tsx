"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { EstadoBadge } from "@/components/ui/EstadoBadge";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { FlujoEjecucion } from "@/components/automatizacion/FlujoEjecucion";
import { obtenerEjecucion } from "@/services/automatizaciones";
import type { EjecucionAutomatizacion } from "@/types/automatizacion";
import { etiquetaDato } from "@/utils/etiquetas";
import { formatearDuracion, formatearFechaHora } from "@/utils/fechas";
import { tieneId } from "@/components/automatizacion/estadoFlujo";

function Detalle({ token, id, zonaHoraria }: { token: string; id: string; zonaHoraria: string }) {
  const [ejecucion, setEjecucion] = useState<EjecucionAutomatizacion | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [actualizadoEn, setActualizadoEn] = useState<string>();
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    const control = new AbortController();
    let temporizador: ReturnType<typeof setTimeout>;
    setEjecucion(null);
    setCargando(true);
    async function actualizar() {
      let continuar = true;
      try {
        const dato = await obtenerEjecucion(token, id, control.signal);
        if (control.signal.aborted) return;
        setEjecucion(dato);
        setActualizadoEn(new Date().toISOString());
        setError("");
        continuar = !["COMPLETADA", "FALLIDA", "CANCELADA"].includes(dato.estado);
      } catch (fallo) {
        if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudo cargar la ejecución.");
      } finally {
        if (!control.signal.aborted) {
          setCargando(false);
          if (continuar) temporizador = setTimeout(actualizar, 3000);
        }
      }
    }
    void actualizar();
    return () => { control.abort(); clearTimeout(temporizador); };
  }, [token, id, revision]);

  if (cargando) return <EstadoPanel titulo="Cargando ejecución" descripcion="Consultando el estado de la tarea." />;
  if (error && !ejecucion) {
    return <EstadoPanel tono="alerta" titulo="No se pudo abrir la ejecución" descripcion={error} accion={<Link href="/automatizaciones">Volver a automatizaciones</Link>} />;
  }
  if (!ejecucion) return <EstadoPanel titulo="Ejecución no encontrada" descripcion="Comprueba el identificador o vuelve al historial." />;

  return <>
    <div className="execution-navigation"><Link className="back-link" href="/automatizaciones">← Todas las automatizaciones</Link><button className="button-secondary" onClick={() => setRevision(r => r + 1)}>Actualizar estado</button></div>
    {error && <div className="inline-error" role="alert">No se pudo actualizar: {error}</div>}
    <FlujoEjecucion ejecucion={ejecucion} zona={zonaHoraria} actualizadoEn={actualizadoEn} desactualizado={Boolean(error)} />
    <div className="page-grid">
      <section className="card main-card">
        <div className="section-heading"><div><h2>Intentos y trazabilidad</h2><p>Los intentos aparecen cuando el motor comienza a ejecutar la tarea.</p></div></div>
        {ejecucion.intentos.length ? <ol className="timeline">{ejecucion.intentos.map((intento) => <li key={intento.id}><div><strong>Intento {intento.numero_intento}</strong><EstadoBadge estado={intento.estado} /></div><small>{formatearFechaHora(intento.inicio_en, zonaHoraria)} · {intento.fin_en ? formatearDuracion(intento.inicio_en, intento.fin_en) : "En curso"}</small>{intento.mensaje_error && <p className="error-text">{intento.mensaje_error}</p>}</li>)}</ol> : <EstadoPanel titulo="Sin intentos" descripcion="Esta ejecución aún no ha comenzado." />}
      </section>
      <aside className="card aside-card">
        <h2>Datos de ejecución</h2>
        <p><EstadoBadge estado={ejecucion.estado} /></p>
        <p>Inicio real: {ejecucion.inicio_en ? formatearFechaHora(ejecucion.inicio_en, zonaHoraria) : "Pendiente"}</p>
        <p>Tipo: {etiquetaDato(ejecucion.tipo)}</p>
        <details><summary>Identificador técnico</summary><p>{ejecucion.clave_idempotencia}</p></details>
        <p>Primer despacho: {ejecucion.despachada_en ? formatearFechaHora(ejecucion.despachada_en, zonaHoraria) : "Pendiente"}</p>
        {typeof ejecucion.datos_entrada.ejecutar_desde_utc === "string" && <p>Hora real programada: {formatearFechaHora(ejecucion.datos_entrada.ejecutar_desde_utc, zonaHoraria)}</p>}
        {typeof ejecucion.datos_entrada.fecha_hora_simulada_local === "string" && <p>Día planificado: {ejecucion.datos_entrada.fecha_hora_simulada_local.replace("T", " ")}</p>}
        <p>Próximo intento: {ejecucion.proximo_intento_en ? formatearFechaHora(ejecucion.proximo_intento_en, zonaHoraria) : "Sin programar"}</p>
        {ejecucion.datos_salida && <><h3>Resultado de la tarea</h3>{tieneId(ejecucion.datos_salida.plan_id) && <p><Link href={`/planificacion?plan_id=${ejecucion.datos_salida.plan_id}`}>Ver plan #{ejecucion.datos_salida.plan_id} y sus faltantes →</Link></p>}{tieneId(ejecucion.datos_salida.propuesta_compra_id) && tieneId(ejecucion.datos_salida.plan_id) && <p><Link href={`/compras?plan_id=${ejecucion.datos_salida.plan_id}`}>Ver pedidos y envíos →</Link></p>}{typeof ejecucion.datos_salida.pedidos_estado === "string" && <p>Pedidos: {etiquetaDato(ejecucion.datos_salida.pedidos_estado)}</p>}{typeof ejecucion.datos_salida.pedidos_motivo === "string" && <p>{ejecucion.datos_salida.pedidos_motivo}</p>}<details><summary>Datos técnicos del resultado</summary><pre>{JSON.stringify(ejecucion.datos_salida, null, 2)}</pre></details></>}
      </aside>
    </div>
  </>;
}

export default function EjecucionPage() {
  const params = useParams<{ id: string }>();
  return <ProtectedShell titulo={`Ejecución #${params.id}`} descripcion="Sigue el flujo de la automatización y revisa sus resultados.">{({ token, negocio }) => <Detalle token={token} id={params.id} zonaHoraria={negocio.zona_horaria} />}</ProtectedShell>;
}
