"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { obtenerInforme } from "@/services/informes";
import type { Informe } from "@/types/informes";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { GraficosOperacion } from "./GraficosOperacion";
import { IconoAnalitica, numeroAnalitica as numero } from "@/components/panel/Analitica";
import { formatearEscenario } from "@/utils/fechas";

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
    <div className="section-heading"><div><span className="analytics-eyebrow">El pulso de tu negocio</span><h2>Resultados que puedes explorar</h2><p>{informe ? `${formatearEscenario(informe.periodo.desde)} — ${formatearEscenario(informe.periodo.hasta)} · últimos 30 días de datos disponibles.` : "Ventas observadas y estado actual de pedidos."}</p></div><Link className="button-secondary" href="/informes">Abrir Reportes ↗</Link></div>
    {cargando && <p role="status">Cargando gráficos…</p>}
    {error && <EstadoPanel tono="alerta" titulo="Gráficos no disponibles" descripcion={error} />}
    {informe && <><div className="analytics-kpis dashboard-kpis">{[
      ["Unidades vendidas", informe.ventas.registros ? numero(informe.ventas.unidades) : "Sin registros", "En el período seleccionado", "Suma de ventas registradas; no estima días ausentes."],
      ["Días observados", `${informe.ventas.dias_observados} / ${informe.periodo.dias_calendario}`, "Con ventas registradas", "Un cero explícito también cuenta como un día observado."],
      ["Productos observados", numero(informe.ventas.productos_observados), "Con registros en el período", "Explora el ranking para conocer su participación."],
      ["Pedidos", numero(informe.pedidos.total), "Según fecha de planificación", "El envío de un mensaje no cambia el inventario."],
    ].map(([titulo, cantidad, unidad, detalle], i) => <article key={titulo} className={`analytics-kpi ${i === 0 ? "analytics-kpi-accent" : ""}`}><div className="analytics-kpi-label"><span>{titulo}</span><IconoAnalitica tipo={i === 3 ? "archivo" : "grafico"} /></div><strong>{cantidad}</strong><span className="analytics-kpi-unit">{unidad}</span><p>{detalle}</p></article>)}</div><GraficosOperacion informe={informe} /></>}
  </section>;
}
