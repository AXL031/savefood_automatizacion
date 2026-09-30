import React from "react";
import type { MetricasEvaluacion } from "@/types/pronosticos";

interface Props {
  metricas: MetricasEvaluacion;
  titulo?: string;
  subtitulo?: string;
}

export function TarjetasMetricas({ metricas, titulo, subtitulo }: Props) {
  return (
    <div className="card">
      <div className="section-heading">
        <div>
          <h2>{titulo ?? "Métricas consolidadas del tramo histórico"}</h2>
          <p>
            {subtitulo ??
              "Cálculo conjunto sobre todos los pares producto-día evaluables (sin promediar porcentajes)."}
          </p>
        </div>
        <span className="badge badge-neutral">Demostración histórica</span>
      </div>

      <div className="stats-grid">
        {/* MAE */}
        <div className="stat">
          <span>Error Medio Absoluto (MAE)</span>
          <strong>{metricas.mae !== null ? `${metricas.mae.toFixed(2)}` : "—"}</strong>
          <small>Unidades promedio de desviación</small>
        </div>

        {/* WAPE */}
        <div className="stat">
          <span>Error Ponderado (WAPE)</span>
          <strong>
            {metricas.wape_pct !== null ? `${metricas.wape_pct.toFixed(1)}%` : "No definido"}
          </strong>
          <small>
            {metricas.wape_pct !== null
              ? "Error relativo a la venta real total (puede superar 100%)"
              : "Suma de ventas reales igual a cero"}
          </small>
        </div>

        {/* Cobertura */}
        <div className="stat">
          <span>Cobertura de ventas reales</span>
          <strong>{metricas.cobertura_pct.toFixed(1)}%</strong>
          <small>
            {metricas.pares_evaluables} de {metricas.total_pronosticados} pares con venta conocida
          </small>
        </div>

        {/* Dentro de ±20% */}
        <div className="stat">
          <span>Dentro de ±20%</span>
          <strong>
            {metricas.dentro_mas_menos_20_pct !== null
              ? `${metricas.dentro_mas_menos_20_pct.toFixed(1)}%`
              : "—"}
          </strong>
          <small>
            {metricas.dentro_mas_menos_10_pct !== null
              ? `±10%: ${metricas.dentro_mas_menos_10_pct.toFixed(1)}%`
              : "Tolerancia por producto"}
          </small>
        </div>
      </div>

      <div className="fact">
        <span>Pares evaluables computados:</span>
        <strong>{metricas.pares_evaluables}</strong>
      </div>
      <div className="fact">
        <span>Productos excluidos por ausencia de venta:</span>
        <strong>{metricas.productos_excluidos} (venta desconocida, no cero)</strong>
      </div>
      <div className="fact">
        <span>Suma total de errores absolutos:</span>
        <strong>{metricas.suma_errores_absolutos.toLocaleString("es-PE")} unidades</strong>
      </div>
      <div className="fact">
        <span>Suma total de ventas reales observadas:</span>
        <strong>{metricas.suma_reales.toLocaleString("es-PE")} unidades</strong>
      </div>
    </div>
  );
}
