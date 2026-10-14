"use client";

import React from "react";
import type { EvaluacionDia } from "@/types/pronosticos";

interface Props {
  serie: EvaluacionDia[];
  fechaSeleccionada: string;
  onSeleccionarFecha: (fecha: string) => void;
}

export function GraficoSerieHistorica({
  serie,
  fechaSeleccionada,
  onSeleccionarFecha,
}: Props) {
  if (!serie || serie.length === 0) {
    return (
      <div className="card">
        <p>No hay datos de serie temporal para mostrar.</p>
      </div>
    );
  }

  // Dimensiones del SVG
  const ancho = 780;
  const alto = 260;
  const padIzq = 50;
  const padDer = 25;
  const padSup = 30;
  const padInf = 45;

  const maxVal = Math.max(
    ...serie.map((d) => Math.max(d.total_previsto_evaluable, d.total_real_conocido)),
    10
  );
  const maxEscala = Math.ceil((maxVal * 1.15) / 10) * 10;

  const pasoX = (ancho - padIzq - padDer) / Math.max(serie.length - 1, 1);

  function coordY(valor: number): number {
    const usable = alto - padSup - padInf;
    return padSup + usable * (1 - valor / maxEscala);
  }

  function coordX(idx: number): number {
    return padIzq + idx * pasoX;
  }

  // Generar paths SVG
  const pathPrevisto = serie
    .map((d, i) => `${i === 0 ? "M" : "L"} ${coordX(i)} ${coordY(d.total_previsto_evaluable)}`)
    .join(" ");

  const pathReal = serie
    .map((d, i) => `${i === 0 ? "M" : "L"} ${coordX(i)} ${coordY(d.total_real_conocido)}`)
    .join(" ");

  return (
    <div className="card">
      <div className="section-heading">
        <div>
          <h2>Serie histórica: Previsto vs Real por fecha</h2>
          <p>
            Totales sumados exclusivamente sobre los productos evaluables con venta conocida.
            Haz clic en un punto para inspeccionar el desglose por producto.
          </p>
        </div>
        <div style={{ display: "flex", gap: "15px", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.78rem" }}>
            <span style={{ width: "12px", height: "12px", borderRadius: "3px", background: "#17604E", display: "inline-block" }} />
            <span>Previsto evaluable</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.78rem" }}>
            <span style={{ width: "12px", height: "12px", borderRadius: "3px", background: "#2F6DB5", display: "inline-block" }} />
            <span>Real conocido</span>
          </div>
        </div>
      </div>

      <div style={{ width: "100%", overflowX: "auto" }}>
        <svg
          viewBox={`0 0 ${ancho} ${alto}`}
          style={{ width: "100%", minWidth: "560px", height: "auto" }}
          role="img"
          aria-label="Gráfico de línea comparando demanda prevista y ventas reales"
        >
          {/* Líneas guía horizontales */}
          {[0, 0.25, 0.5, 0.75, 1].map((p, idx) => {
            const val = Math.round(maxEscala * p);
            const y = coordY(val);
            return (
              <g key={idx}>
                <line
                  x1={padIzq}
                  y1={y}
                  x2={ancho - padDer}
                  y2={y}
                  stroke="#DCE3DF"
                  strokeDasharray={p === 0 ? undefined : "3 3"}
                  strokeWidth="1"
                />
                <text x={padIzq - 8} y={y + 4} textAnchor="end" fontSize="10" fill="#5B6863">
                  {val}
                </text>
              </g>
            );
          })}

          {/* Línea previsto (verde azulado) */}
          <path d={pathPrevisto} fill="none" stroke="#17604E" strokeWidth="2.5" />

          {/* Línea real (azul) */}
          <path d={pathReal} fill="none" stroke="#2F6DB5" strokeWidth="2.5" />

          {/* Puntos y selectores */}
          {serie.map((d, idx) => {
            const x = coordX(idx);
            const yPrev = coordY(d.total_previsto_evaluable);
            const yReal = coordY(d.total_real_conocido);
            const esSeleccionado = d.fecha_local === fechaSeleccionada;

            return (
              <g
                key={d.fecha_local}
                onClick={() => onSeleccionarFecha(d.fecha_local)}
                style={{ cursor: "pointer" }}
              >
                {/* Indicador de columna seleccionada */}
                {esSeleccionado && (
                  <line
                    x1={x}
                    y1={padSup}
                    x2={x}
                    y2={alto - padInf}
                    stroke="#17604E"
                    strokeWidth="1.5"
                    strokeDasharray="4 2"
                    opacity="0.6"
                  />
                )}

                {/* Punto previsto */}
                <circle
                  cx={x}
                  cy={yPrev}
                  r={esSeleccionado ? "6" : "4"}
                  fill="#17604E"
                  stroke="#fff"
                  strokeWidth="2"
                />

                {/* Punto real */}
                <circle
                  cx={x}
                  cy={yReal}
                  r={esSeleccionado ? "6" : "4"}
                  fill="#2F6DB5"
                  stroke="#fff"
                  strokeWidth="2"
                />

                {/* Etiqueta fecha en eje X */}
                <text
                  x={x}
                  y={alto - padInf + 16}
                  textAnchor="middle"
                  fontSize={esSeleccionado ? "11" : "9.5"}
                  fontWeight={esSeleccionado ? "bold" : "normal"}
                  fill={esSeleccionado ? "#17604E" : "#5B6863"}
                >
                  {d.fecha_local.slice(5)}
                </text>

                {/* Sub-etiqueta si hubo productos excluidos */}
                {d.productos_excluidos > 0 && (
                  <text
                    x={x}
                    y={alto - padInf + 28}
                    textAnchor="middle"
                    fontSize="8"
                    fill="#B42318"
                  >
                    -{d.productos_excluidos} excl.
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>
      <p style={{ marginTop: "10px", fontSize: "0.75rem", color: "#5B6863" }}>
        * Las fechas con productos excluidos (en rojo) reflejan ventas no registradas en el CSV, contabilizadas como desconocidas sin imputar ceros.
      </p>
    </div>
  );
}
