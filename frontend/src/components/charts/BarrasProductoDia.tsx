"use client";

import React from "react";
import type { EvaluacionDia } from "@/types/pronosticos";

interface Props {
  evaluacionDia: EvaluacionDia;
}

export function BarrasProductoDia({ evaluacionDia }: Props) {
  const { fecha_local, desglose_productos, metricas, total_previsto_evaluable, total_real_conocido } =
    evaluacionDia;

  const maxVal = Math.max(
    ...desglose_productos.map((p) => Math.max(p.previsto, p.real ?? 0)),
    10
  );

  return (
    <div className="card">
      <div className="section-heading">
        <div>
          <h2>Desglose por producto — Día {fecha_local}</h2>
          <p>
            Comparación de unidades pronosticadas frente a ventas reales y diferencia absoluta (|real - previsto|).
          </p>
        </div>
        <div style={{ textAlign: "right" }}>
          <span className="badge badge-info">
            {metricas.pares_evaluables} evaluables / {metricas.productos_excluidos} excluidos
          </span>
        </div>
      </div>

      {/* Resumen numérico rápido del día */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "12px", marginBottom: "20px" }}>
        <div style={{ padding: "10px", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <span style={{ fontSize: "0.72rem", color: "#64748b" }}>Total Previsto (eval.)</span>
          <div style={{ fontSize: "1.2rem", fontWeight: "bold", color: "#0f766e" }}>
            {total_previsto_evaluable} u.
          </div>
        </div>
        <div style={{ padding: "10px", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <span style={{ fontSize: "0.72rem", color: "#64748b" }}>Total Real conocido</span>
          <div style={{ fontSize: "1.2rem", fontWeight: "bold", color: "#f59e0b" }}>
            {total_real_conocido} u.
          </div>
        </div>
        <div style={{ padding: "10px", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <span style={{ fontSize: "0.72rem", color: "#64748b" }}>MAE del día</span>
          <div style={{ fontSize: "1.2rem", fontWeight: "bold" }}>
            {metricas.mae !== null ? `${metricas.mae.toFixed(2)} u.` : "—"}
          </div>
        </div>
        <div style={{ padding: "10px", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <span style={{ fontSize: "0.72rem", color: "#64748b" }}>WAPE del día</span>
          <div style={{ fontSize: "1.2rem", fontWeight: "bold" }}>
            {metricas.wape_pct !== null ? `${metricas.wape_pct.toFixed(1)}%` : "No def."}
          </div>
        </div>
      </div>

      {/* Barras por producto */}
      <div style={{ display: "grid", gap: "16px" }}>
        {desglose_productos.map((item) => {
          const anchoPrev = (item.previsto / maxVal) * 100;
          const anchoReal = item.real !== null ? (item.real / maxVal) * 100 : 0;

          return (
            <div
              key={item.producto_id}
              style={{
                borderBottom: "1px solid #f1f5f9",
                paddingBottom: "14px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                <span style={{ fontWeight: "bold", fontSize: "0.86rem" }}>{item.producto_id}</span>
                <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                  {item.diferencia_absoluta !== null ? (
                    <>
                      <span style={{ fontSize: "0.78rem", color: "#475569" }}>
                        Dif: <strong>{item.diferencia_absoluta} u.</strong>
                      </span>
                      {item.dentro_mas_menos_20 ? (
                        <span className="badge badge-ok">±20% Ok</span>
                      ) : (
                        <span className="badge badge-alerta">&gt; 20%</span>
                      )}
                    </>
                  ) : (
                    <span className="badge badge-neutral">Venta no registrada</span>
                  )}
                </div>
              </div>

              {/* Barra de Previsto */}
              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
                <span style={{ width: "65px", fontSize: "0.72rem", color: "#0f766e", fontWeight: "bold" }}>
                  Prev: {item.previsto} u.
                </span>
                <div style={{ flex: 1, background: "#f1f5f9", borderRadius: "4px", height: "12px", overflow: "hidden" }}>
                  <div
                    style={{
                      width: `${anchoPrev}%`,
                      background: "#0f766e",
                      height: "100%",
                      borderRadius: "4px",
                    }}
                  />
                </div>
              </div>

              {/* Barra de Real */}
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span style={{ width: "65px", fontSize: "0.72rem", color: "#d97706", fontWeight: "bold" }}>
                  {item.real !== null ? `Real: ${item.real} u.` : "Real: N/D"}
                </span>
                <div style={{ flex: 1, background: "#f1f5f9", borderRadius: "4px", height: "12px", overflow: "hidden" }}>
                  {item.real !== null ? (
                    <div
                      style={{
                        width: `${anchoReal}%`,
                        background: "#f59e0b",
                        height: "100%",
                        borderRadius: "4px",
                      }}
                    />
                  ) : (
                    <div style={{ height: "100%", color: "#94a3b8", fontSize: "0.65rem", paddingLeft: "6px" }}>
                      Ausencia de venta (desconocida)
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
