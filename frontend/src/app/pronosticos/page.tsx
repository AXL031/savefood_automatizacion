"use client";

import React, { useEffect, useState } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { TarjetasMetricas } from "@/components/panel/TarjetasMetricas";
import { GraficoSerieHistorica } from "@/components/charts/GraficoSerieHistorica";
import { BarrasProductoDia } from "@/components/charts/BarrasProductoDia";
import { TablaDesgloseProductos } from "@/components/tables/TablaDesgloseProductos";
import {
  obtenerEvaluacionHistorica,
  listarCorridasPronostico,
  ESCENARIO_DEMO_EVALUACION,
} from "@/services/pronosticos";
import type { EvaluacionTramoCompleto, CorridaPronostico } from "@/types/pronosticos";

export default function PaginaPronosticos() {
  const [evaluacion, setEvaluacion] = useState<EvaluacionTramoCompleto>(ESCENARIO_DEMO_EVALUACION);
  const [corridas, setCorridas] = useState<CorridaPronostico[]>([]);
  const [fechaSeleccionada, setFechaSeleccionada] = useState<string>("2022-08-24");
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    async function cargarDatos() {
      try {
        const [evalRes, corridasRes] = await Promise.all([
          obtenerEvaluacionHistorica("token", controller.signal),
          listarCorridasPronostico("token", controller.signal),
        ]);
        setEvaluacion(evalRes);
        setCorridas(corridasRes);
        if (evalRes.serie_diaria.length > 0) {
          // Si 2022-08-24 está en la serie, seleccionarla por defecto; si no, la última
          const tieneObj = evalRes.serie_diaria.some((d) => d.fecha_local === "2022-08-24");
          setFechaSeleccionada(
            tieneObj ? "2022-08-24" : evalRes.serie_diaria[evalRes.serie_diaria.length - 1].fecha_local
          );
        }
      } catch {
        // Fallback al escenario precalculado
        setEvaluacion(ESCENARIO_DEMO_EVALUACION);
      } finally {
        setCargando(false);
      }
    }

    cargarDatos();
    return () => controller.abort();
  }, []);

  const diaActual =
    evaluacion.serie_diaria.find((d) => d.fecha_local === fechaSeleccionada) ??
    evaluacion.serie_diaria[0];

  return (
    <ProtectedShell
      titulo="Pronósticos y Evaluación Histórica"
      descripcion="Monitoreo del desempeño del modelo CatBoost, cobertura de ventas observadas y backtest un día adelante según la política temporal."
    >
      {() => (
        <div style={{ display: "grid", gap: "24px" }}>
          {/* Ficha técnica del modelo y partición */}
          <div className="card">
            <div className="section-heading">
              <div>
                <h2>Ficha técnica del artefacto</h2>
                <p>Configuración de inferencia local y límites del escenario de prueba.</p>
              </div>
              <span className="badge badge-info">Estado: {evaluacion.estado}</span>
            </div>

            <div className="preference-grid">
              <div className="preference">
                <div>
                  <strong>Modelo CatBoost</strong>
                  <p>Versión: <code>{evaluacion.version_modelo}</code></p>
                  <small style={{ color: "#6b7280" }}>Objetivo: Quantile (alpha=0.65) | 13 variables contractuales</small>
                </div>
              </div>
              <div className="preference">
                <div>
                  <strong>Partición temporal</strong>
                  <p>
                    {evaluacion.particion
                      ? `${evaluacion.particion.inicio_prueba} a ${evaluacion.particion.fin_prueba} (Prueba reservada)`
                      : "Julio a Septiembre 2022"}
                  </p>
                  <small style={{ color: "#6b7280" }}>
                    Entrenamiento previo: {evaluacion.particion?.inicio_entrenamiento ?? "2021-01-01"} a{" "}
                    {evaluacion.particion?.fin_validacion ?? "2022-06-30"}
                  </small>
                </div>
              </div>
            </div>
          </div>

          {/* Tarjetas de Métricas Globales Consolidadas */}
          <TarjetasMetricas
            metricas={evaluacion.metricas_globales}
            titulo="Métricas acumuladas del tramo de prueba"
            subtitulo={`Evaluación sobre ${evaluacion.fechas_evaluadas} fechas y ${evaluacion.total_pares_evaluables} pares producto-día sin promediar porcentajes.`}
          />

          {/* Gráfico interactivo de serie temporal */}
          <GraficoSerieHistorica
            serie={evaluacion.serie_diaria}
            fechaSeleccionada={fechaSeleccionada}
            onSeleccionarFecha={setFechaSeleccionada}
          />

          {/* Desglose visual en barras por producto para el día seleccionado */}
          {diaActual && <BarrasProductoDia evaluacionDia={diaActual} />}

          {/* Tabla accesible de auditoría detallada */}
          {diaActual && (
            <TablaDesgloseProductos
              desglose={diaActual.desglose_productos}
              fecha={diaActual.fecha_local}
            />
          )}

          {/* Trazabilidad de corridas recientes (K02 / Celery) */}
          <div className="card">
            <div className="section-heading">
              <div>
                <h2>Trazabilidad de corridas de inferencia</h2>
                <p>Historial de corridas de pronósticos generadas por el motor o disparadores manuales.</p>
              </div>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Identificador de corrida</th>
                    <th>Fecha objetivo demo</th>
                    <th>Versión del modelo</th>
                    <th>Estado de ejecución</th>
                    <th>Productos pronosticados</th>
                  </tr>
                </thead>
                <tbody>
                  {corridas.map((c) => (
                    <tr key={c.id}>
                      <td><code>{c.id}</code></td>
                      <td><strong>{c.fecha_objetivo_demo}</strong></td>
                      <td>{c.version_modelo}</td>
                      <td>
                        <span className="badge badge-ok">{c.estado}</span>
                      </td>
                      <td>
                        {c.pronosticos.filter((p) => p.unidades_pronosticadas !== null).length} productos cubiertos
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </ProtectedShell>
  );
}
