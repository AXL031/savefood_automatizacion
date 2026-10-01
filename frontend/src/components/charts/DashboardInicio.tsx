"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { obtenerInforme } from "@/services/informes";
import type { Informe } from "@/types/informes";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { GraficosOperacion } from "./GraficosOperacion";

export function DashboardInicio({ token, revision }: { token: string; revision: number }) {
  const [informe, setInforme] = useState<Informe | null>(null);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(true);
  useEffect(() => {
    const control = new AbortController(); setCargando(true); setInforme(null); setError("");
    obtenerInforme(token, { incluir_evaluacion: false }, control.signal).then((datos) => {
      if (!control.signal.aborted) setInforme(datos);
    }).catch((e: unknown) => { if (!control.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo cargar el dashboard."); })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token, revision]);
  return <section className="section-space" aria-label="Dashboard de la operación" aria-busy={cargando}>
    <div className="section-heading"><div><h2>Tu operación en gráficos</h2><p>{informe ? `Período del escenario: ${informe.periodo.desde} al ${informe.periodo.hasta} · últimos 30 días de datos disponibles.` : "Ventas observadas y estado actual de pedidos."}</p></div><Link className="button-secondary" href="/informes">Abrir Reportes →</Link></div>
    {cargando && <p role="status">Cargando gráficos…</p>}
    {error && <EstadoPanel tono="alerta" titulo="Gráficos no disponibles" descripcion={error} />}
    {informe && <><div className="report-kpis"><div><span>Unidades vendidas</span><strong>{informe.ventas.registros ? informe.ventas.unidades.toLocaleString("es") : "Sin registros"}</strong></div><div><span>Días con ventas registradas</span><strong>{informe.ventas.dias_observados} / {informe.periodo.dias_calendario}</strong></div><div><span>Productos observados</span><strong>{informe.ventas.productos_observados}</strong></div><div><span>Pedidos en el período</span><strong>{informe.pedidos.total}</strong></div></div><GraficosOperacion informe={informe} /></>}
  </section>;
}
