"use client";

import type { EvaluacionDia } from "@/types/pronostico";

export function SerieHistorica({ dias, seleccion, alSeleccionar }: {
  dias: EvaluacionDia[]; seleccion: string; alSeleccionar: (fecha: string) => void;
}) {
  const maximo = Math.max(1, ...dias.flatMap((dia) => [dia.total_previsto_evaluable, dia.total_real_conocido]));
  return <div className="serie-historica" role="group" aria-label="Serie histórica de previsto y real evaluables">
    {dias.map((dia) => <button key={dia.fecha_local} type="button" onClick={() => alSeleccionar(dia.fecha_local)}
      className={`serie-dia ${seleccion === dia.fecha_local ? "seleccionado" : ""}`}
      aria-pressed={seleccion === dia.fecha_local} title={`${dia.fecha_local}: previsto ${dia.total_previsto_evaluable}, real ${dia.total_real_conocido}, cobertura ${dia.metricas.cobertura_pct}%`}>
      <span className="serie-barras">
        {dia.productos_evaluables > 0 && <><span className="serie-barra previsto" style={{ height: `${Math.max(2, 100 * dia.total_previsto_evaluable / maximo)}%` }} />
        <span className="serie-barra real" style={{ height: `${Math.max(2, 100 * dia.total_real_conocido / maximo)}%` }} /></>}
      </span>
      <span className="serie-fecha">{dia.fecha_local.slice(5)}</span>
    </button>)}
  </div>;
}
