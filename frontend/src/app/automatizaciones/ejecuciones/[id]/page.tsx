"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { EstadoBadge } from "@/components/ui/EstadoBadge";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { obtenerEjecucion, reintentarEjecucion } from "@/services/automatizaciones";
import { HttpError } from "@/services/http";
import type { EjecucionAutomatizacion } from "@/types/automatizacion";
import { formatearDuracion, formatearFechaHora } from "@/utils/fechas";

function Detalle({ token, id, zonaHoraria }: { token: string; id: string; zonaHoraria: string }) {
  const [ejecucion, setEjecucion] = useState<EjecucionAutomatizacion | null>(null);
  const [cargando, setCargando] = useState(true);
  const [reintentando, setReintentando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [sinApi, setSinApi] = useState(false);

  useEffect(() => {
    const control = new AbortController();
    obtenerEjecucion(token, id, control.signal)
      .then((dato) => { setEjecucion(dato); setError(""); })
      .catch((fallo: unknown) => {
        if (control.signal.aborted) return;
        if (fallo instanceof HttpError && (fallo.status === 404 || fallo.status === 501)) setSinApi(true);
        else setError(fallo instanceof Error ? fallo.message : "No se pudo cargar la ejecución.");
      })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token, id]);

  async function reintentar() {
    if (!ejecucion || reintentando) return;
    setError("");
    setMensaje("");
    setReintentando(true);
    try {
      const resultado = await reintentarEjecucion(token, ejecucion.id);
      setEjecucion(resultado);
      setMensaje("Se solicitó el reintento. Revisa el estado antes de repetir la acción.");
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo reintentar.");
    } finally {
      setReintentando(false);
    }
  }

  if (cargando) return <EstadoPanel titulo="Cargando ejecución" descripcion="Consultando estado e intentos en la API local." />;
  if (sinApi) return <EstadoPanel tono="info" titulo="Ejecución no disponible" descripcion="No se encontró esta ejecución o su ruta todavía no está implementada. Vuelve al historial para comprobar el identificador." accion={<Link href="/automatizaciones">Volver a automatizaciones</Link>} />;
  if (error && !ejecucion) return <EstadoPanel tono="alerta" titulo="No se pudo abrir la ejecución" descripcion={error} accion={<Link href="/automatizaciones">Volver</Link>} />;
  if (!ejecucion) return <EstadoPanel titulo="Ejecución no encontrada" descripcion="Comprueba el identificador o vuelve al historial." />;

  return <>
    <Link className="back-link" href="/automatizaciones">← Todas las automatizaciones</Link>
    {ejecucion.estado === "FALLIDO" && <EstadoPanel tono="alerta" titulo="Esta ejecución requiere atención" descripcion={ejecucion.mensaje_error || "Consulta los intentos y verifica la causa antes de reintentar."} />}
    {mensaje && <div className="inline-success" role="status">{mensaje}</div>}
    {error && <div className="inline-error" role="alert">{error}</div>}
    <div className="stats-grid"><div className="card stat"><span>Estado</span><div className="stat-badge"><EstadoBadge estado={ejecucion.estado} /></div></div><div className="card stat"><span>Intentos realizados</span><strong>{(ejecucion.intentos?.length ?? 0) || ejecucion.cantidad_reintentos + 1}</strong><small>Incluye el primer intento</small></div><div className="card stat"><span>Duración</span><strong className="stat-text">{formatearDuracion(ejecucion.inicio_en, ejecucion.fin_en)}</strong></div><div className="card stat"><span>Inicio</span><strong className="stat-text">{formatearFechaHora(ejecucion.inicio_en, zonaHoraria)}</strong></div></div>
    <div className="page-grid"><section className="card main-card"><div className="section-heading"><div><h2>Intentos y trazabilidad</h2><p>Los errores de cada intento se conservan para explicar el resultado.</p></div></div>{ejecucion.intentos?.length ? <ol className="timeline">{ejecucion.intentos.map((intento) => <li key={intento.id}><div><strong>Intento {intento.numero_intento}</strong><EstadoBadge estado={intento.estado} /></div><small>{formatearFechaHora(intento.inicio_en, zonaHoraria)} · {formatearDuracion(intento.inicio_en, intento.fin_en)}</small>{intento.mensaje_error && <p className="error-text">{intento.mensaje_error}</p>}</li>)}</ol> : <EstadoPanel titulo="Sin detalle de intentos" descripcion="El servicio todavía no devolvió pasos individuales para esta ejecución." />}</section><aside className="card aside-card"><h2>Recuperación</h2><p>Revisa la causa antes de enviar una nueva solicitud. Un pedido enviado a Telegram solo queda confirmado cuando responde el proveedor.</p><button className="button-primary" disabled={ejecucion.estado !== "FALLIDO" || reintentando} onClick={reintentar}>{reintentando ? "Solicitando…" : "Reintentar ahora"}</button><p className="helper-text">Cambiar proveedor y registrar un pedido manual corresponden al módulo de Compras.</p></aside></div>
  </>;
}

export default function EjecucionPage() {
  const params = useParams<{ id: string }>();
  return <ProtectedShell titulo={`Ejecución #${params.id}`} descripcion="Resultado, intentos y opciones de recuperación.">{({ token, negocio }) => <Detalle token={token} id={params.id} zonaHoraria={negocio.zona_horaria} />}</ProtectedShell>;
}
