"use client";

import { useId } from "react";
import type { EvaluacionDia } from "@/types/pronostico";
import { formatearEscenario } from "@/utils/fechas";
import { numeroAnalitica } from "@/components/panel/Analitica";

/** Traza solo fechas consecutivas evaluables: una ausencia corta la línea. */
export function SerieHistorica({ dias, seleccion, alSeleccionar }: {
  dias: EvaluacionDia[]; seleccion: string; alSeleccionar: (fecha: string) => void;
}) {
  const id = useId();
  if (!dias.length) return <p className="chart-empty">Todavía no hay fechas evaluadas.</p>;
  const ordenados = [...dias].sort((a, b) => a.fecha_local.localeCompare(b.fecha_local));
  const instante = (fecha: string) => Date.parse(`${fecha}T00:00:00Z`);
  const primero = instante(ordenados[0].fecha_local), ultimo = instante(ordenados.at(-1)!.fecha_local);
  const ancho = 900, alto = 285, izquierda = 62, derecha = 24, base = 235, techo = 24;
  const maximo = Math.max(1, ...ordenados.filter((d) => d.productos_evaluables > 0).flatMap((d) => [d.total_previsto_evaluable, d.total_real_conocido])) * 1.12;
  const x = (dia: EvaluacionDia) => primero === ultimo ? ancho / 2 : izquierda + (instante(dia.fecha_local) - primero) / (ultimo - primero) * (ancho - izquierda - derecha);
  const y = (valor: number) => base - valor / maximo * (base - techo);
  function trazo(campo: "total_previsto_evaluable" | "total_real_conocido") {
    return ordenados.map((dia, i) => {
      if (!dia.productos_evaluables) return "";
      const anterior = ordenados[i - 1];
      const continua = anterior?.productos_evaluables && instante(dia.fecha_local) - instante(anterior.fecha_local) === 86400000;
      return `${continua ? "L" : "M"}${x(dia)},${y(dia[campo])}`;
    }).join(" ");
  }
  const indice = Math.max(0, ordenados.findIndex((d) => d.fecha_local === seleccion));
  const actual = ordenados[indice];
  const etiquetas = [...new Set([0, Math.round((ordenados.length - 1) / 4), Math.round((ordenados.length - 1) / 2), Math.round((ordenados.length - 1) * .75), ordenados.length - 1])];
  return <div className="comparison-chart">
    <div className="chart-legend"><span><i className="legend-forecast" />Pronóstico</span><span><i className="legend-actual" />Venta real</span><small>Mismos productos comparables</small></div>
    <div className="chart-scroll" tabIndex={0} role="region" aria-label="Comparación diaria desplazable">
      <svg viewBox={`0 0 ${ancho} ${alto}`} className="comparison-svg" role="group" aria-labelledby={`${id}-title`}>
        <title id={`${id}-title`}>Pronósticos y ventas reales; una fecha sin comparación interrumpe las líneas</title>
        {[0, .25, .5, .75, 1].map((p) => <g key={p}><line x1={izquierda} x2={ancho - derecha} y1={y(p * maximo)} y2={y(p * maximo)} className="chart-gridline" /><text x={izquierda - 12} y={y(p * maximo) + 4} textAnchor="end">{numeroAnalitica(Math.round(p * maximo))}</text></g>)}
        <path d={trazo("total_previsto_evaluable")} className="forecast-line" />
        <path d={trazo("total_real_conocido")} className="actual-line" />
        {ordenados.map((dia) => <g key={dia.fecha_local} role="button" tabIndex={0} aria-pressed={seleccion === dia.fecha_local}
          aria-label={`${formatearEscenario(dia.fecha_local)}: ${dia.productos_evaluables ? `pronóstico ${dia.total_previsto_evaluable}, venta real ${dia.total_real_conocido}` : "sin pares comparables"}`}
          onClick={() => alSeleccionar(dia.fecha_local)} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); alSeleccionar(dia.fecha_local); } }} className="comparison-point">
          <title>{dia.fecha_local} · cobertura {dia.metricas.cobertura_pct}%</title>
          <rect x={x(dia) - 5} y={techo} width={10} height={base - techo} fill="transparent" />
          {seleccion === dia.fecha_local && <line x1={x(dia)} x2={x(dia)} y1={techo} y2={base} className="chart-selected-line" />}
          {dia.productos_evaluables > 0 ? <><circle cx={x(dia)} cy={y(dia.total_previsto_evaluable)} r={seleccion === dia.fecha_local ? 5 : 2.8} className="forecast-point" /><circle cx={x(dia)} cy={y(dia.total_real_conocido)} r={seleccion === dia.fecha_local ? 5 : 2.8} className="actual-point" /></> : <circle cx={x(dia)} cy={base} r={3} className="missing-point" />}
        </g>)}
        {etiquetas.map((i) => <text key={i} x={x(ordenados[i])} y={266} textAnchor="middle">{formatearEscenario(ordenados[i].fecha_local).slice(0, 5)}</text>)}
      </svg>
    </div>
    <div className="chart-inspector"><label>Explorar fecha<select value={actual.fecha_local} onChange={(e) => alSeleccionar(e.target.value)}>{ordenados.map((d) => <option key={d.fecha_local} value={d.fecha_local}>{formatearEscenario(d.fecha_local)}</option>)}</select></label>
      <div><span>Pronóstico</span><strong>{actual.productos_evaluables ? numeroAnalitica(actual.total_previsto_evaluable) : "Sin dato"}</strong></div><div><span>Venta real</span><strong>{actual.productos_evaluables ? numeroAnalitica(actual.total_real_conocido) : "Sin dato"}</strong></div>
      <div className="chart-stepper"><button type="button" className="button-secondary" aria-label="Fecha anterior" disabled={indice <= 0} onClick={() => alSeleccionar(ordenados[indice - 1].fecha_local)}>←</button><button type="button" className="button-secondary" aria-label="Fecha siguiente" disabled={indice >= ordenados.length - 1} onClick={() => alSeleccionar(ordenados[Math.max(0, indice + 1)].fecha_local)}>→</button></div>
    </div>
  </div>;
}
