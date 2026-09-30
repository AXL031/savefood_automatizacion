import { solicitar } from "./http";
import type { Corrida, EvaluacionDia, EvaluacionTramo, Modelo } from "@/types/pronostico";

export function listarModelos(token: string, signal?: AbortSignal): Promise<Modelo[]> {
  return solicitar<Modelo[]>("/pronosticos/modelos", { token, signal });
}

export function listarCorridas(token: string, modeloId?: number, signal?: AbortSignal): Promise<Corrida[]> {
  const consulta = modeloId ? `?modelo_id=${modeloId}` : "";
  return solicitar<Corrida[]>(`/pronosticos/corridas${consulta}`, { token, signal });
}

export function obtenerCorrida(token: string, id: number, signal?: AbortSignal): Promise<Corrida> {
  return solicitar<Corrida>(`/pronosticos/corridas/${id}`, { token, signal });
}

export function obtenerEvaluacion(token: string, modeloId: number, signal?: AbortSignal): Promise<EvaluacionTramo> {
  return solicitar<EvaluacionTramo>(`/pronosticos/evaluacion?modelo_id=${modeloId}`, { token, signal });
}

export function obtenerEvaluacionCorrida(token: string, id: number, signal?: AbortSignal): Promise<EvaluacionDia> {
  return solicitar<EvaluacionDia>(`/pronosticos/corridas/${id}/evaluacion`, { token, signal });
}

export function prepararModelo(token: string, version: string, clave: string): Promise<{ ejecucion_id: number; estado: string }> {
  return solicitar<{ ejecucion_id: number; estado: string }>("/pronosticos/preparar-modelo", {
    token, method: "POST", body: { version_modelo: version, clave_idempotencia: clave },
  });
}
