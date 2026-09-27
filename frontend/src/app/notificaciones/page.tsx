"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { HttpError } from "@/services/http";
import { listarNotificaciones } from "@/services/notificaciones";
import type { Notificacion } from "@/types/notificacion";
import { formatearFechaHora } from "@/utils/fechas";

const tiposPrevistos = [
  { titulo: "Fallo de automatización", detalle: "Causa, ejecución afectada y siguiente paso." },
  { titulo: "Pedido sin confirmar", detalle: "Aviso cuando el proveedor aún no confirma." },
  { titulo: "Riesgo alto de excedente", detalle: "Producto y acción preventiva sugerida." },
  { titulo: "Resumen diario", detalle: "Actividad y resultados del día." },
];

function Contenido({ token, zonaHoraria }: { token: string; zonaHoraria: string }) {
  const [notificaciones, setNotificaciones] = useState<Notificacion[]>([]);
  const [cargando, setCargando] = useState(true);
  const [sinApi, setSinApi] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const control = new AbortController();
    listarNotificaciones(token, control.signal)
      .then((datos) => { setNotificaciones(datos); setSinApi(false); setError(""); })
      .catch((fallo: unknown) => {
        if (control.signal.aborted) return;
        if (fallo instanceof HttpError && (fallo.status === 404 || fallo.status === 501)) setSinApi(true);
        else setError(fallo instanceof Error ? fallo.message : "No se pudieron cargar las notificaciones.");
      })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token]);

  return <>
    {sinApi && <EstadoPanel tono="info" titulo="Notificaciones pendientes de integración" descripcion="El registro de avisos se mostrará aquí cuando exista su API. No se han enviado mensajes desde esta pantalla." />}
    {error && <EstadoPanel tono="alerta" titulo="No se pudieron cargar los avisos" descripcion={error} accion={<button className="button-secondary" onClick={() => window.location.reload()}>Volver a intentar</button>} />}
    <div className="page-grid"><section className="card main-card"><div className="section-heading"><div><h2>Historial de avisos</h2><p>Estado de entrega y vínculo con la ejecución que lo originó.</p></div></div>
      {cargando ? <p role="status">Cargando avisos…</p> : notificaciones.length ? <div className="notice-list">{notificaciones.map((aviso) => <article className="notice" key={aviso.id}><div className="notice-top"><strong>{aviso.titulo}</strong><span className={`badge ${aviso.estado === "ENVIADA" ? "badge-ok" : aviso.estado === "FALLIDA" ? "badge-alerta" : "badge-neutral"}`}>{aviso.estado === "ENVIADA" ? "Enviada" : aviso.estado === "FALLIDA" ? "Fallida" : "Pendiente"}</span></div><p>{aviso.mensaje}</p><small>{formatearFechaHora(aviso.creado_en, zonaHoraria)} · {aviso.tipo}</small>{aviso.ejecucion_id && <Link href={`/automatizaciones/ejecuciones/${aviso.ejecucion_id}`}>Ver ejecución</Link>}</article>)}</div> : <EstadoPanel titulo="Sin avisos registrados" descripcion={sinApi ? "El historial aparecerá al conectar el servicio de notificaciones." : "Cuando ocurra un evento configurado, aparecerá aquí con su estado de envío."} />}
    </section><aside className="card aside-card"><h2>Cómo se genera un aviso</h2><ol className="steps-list"><li>Se detecta una incidencia o evento.</li><li>El sistema registra el aviso.</li><li>Se intenta entregar por el canal configurado.</li><li>Se conserva el resultado del envío.</li></ol><p className="helper-text">Un aviso enviado y una acción de negocio confirmada son resultados diferentes.</p></aside></div>
    <div className="section-heading section-space"><div><h2>Tipos de aviso previstos</h2><p>Las preferencias de activación se habilitarán cuando exista persistencia para ellas.</p></div></div><div className="preference-grid">{tiposPrevistos.map((tipo) => <div className="card preference" key={tipo.titulo}><div><strong>{tipo.titulo}</strong><p>{tipo.detalle}</p></div><span className="badge badge-neutral">Previsto</span></div>)}</div>
  </>;
}

export default function NotificacionesPage() {
  return <ProtectedShell titulo="Notificaciones" descripcion="Revisa avisos operativos y conoce si pudieron entregarse.">{({ token, negocio }) => <Contenido token={token} zonaHoraria={negocio.zona_horaria} />}</ProtectedShell>;
}
