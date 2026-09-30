import React from "react";
import type { DesgloseProducto } from "@/types/pronosticos";

interface Props {
  desglose: DesgloseProducto[];
  fecha: string;
}

export function TablaDesgloseProductos({ desglose, fecha }: Props) {
  return (
    <div className="card">
      <div className="section-heading">
        <div>
          <h2>Auditoría detallada por producto ({fecha})</h2>
          <p>
            Muestra el pronóstico frente a las ventas observadas, la diferencia absoluta y el cumplimiento de tolerancia.
          </p>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Producto / SKU</th>
              <th style={{ textAlign: "right" }}>Previsto</th>
              <th style={{ textAlign: "right" }}>Real conocido</th>
              <th style={{ textAlign: "right" }}>Diferencia absoluta</th>
              <th style={{ textAlign: "right" }}>Error relativo</th>
              <th>Estado de evaluación</th>
            </tr>
          </thead>
          <tbody>
            {desglose.map((item) => {
              const errorRelativo =
                item.real !== null && item.diferencia_absoluta !== null
                  ? (item.diferencia_absoluta / Math.max(item.real, 1)) * 100
                  : null;

              return (
                <tr key={item.producto_id}>
                  <td>
                    <strong>{item.producto_id}</strong>
                  </td>
                  <td style={{ textAlign: "right", color: "#0f766e", fontWeight: "bold" }}>
                    {item.previsto} u.
                  </td>
                  <td style={{ textAlign: "right", color: item.real !== null ? "#b45309" : "#94a3b8" }}>
                    {item.real !== null ? `${item.real} u.` : "—"}
                  </td>
                  <td style={{ textAlign: "right", fontWeight: "600" }}>
                    {item.diferencia_absoluta !== null ? `${item.diferencia_absoluta} u.` : "—"}
                  </td>
                  <td style={{ textAlign: "right" }}>
                    {errorRelativo !== null ? `${errorRelativo.toFixed(1)}%` : "—"}
                  </td>
                  <td>
                    {item.real !== null ? (
                      item.dentro_mas_menos_20 ? (
                        <span className="badge badge-ok">Dentro de ±20%</span>
                      ) : (
                        <span className="badge badge-alerta">Supera ±20%</span>
                      )
                    ) : (
                      <span className="badge badge-neutral" title="Venta desconocida; no se imputa cero">
                        Excluido (Venta no registrada)
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
