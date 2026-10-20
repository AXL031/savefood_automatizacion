import { solicitar, solicitarSobre } from "./http";
import type { Corrida, EvaluacionDia, EvaluacionTramo, Modelo } from "@/types/pronostico";

export async function listarModelos(token: string, signal?: AbortSignal): Promise<Modelo[]> {
  const modelos: Modelo[] = [];
  let total = 1;
  while (modelos.length < total) {
    const sobre = await solicitarSobre<Modelo[]>(`/pronosticos/modelos?limite=100&desplazamiento=${modelos.length}`, { token, signal });
    modelos.push(...sobre.datos);
    total = typeof sobre.metadatos?.total === "number" ? sobre.metadatos.total : modelos.length;
    if (!sobre.datos.length) break;
  }
  return modelos;
}

export type FiltroCorridas = { modelo_id?: number; tipo?: string; desde?: string; hasta?: string; limite?: number; desplazamiento?: number };
export async function listarPaginaCorridas(token: string, filtro: FiltroCorridas, signal?: AbortSignal): Promise<{ filas: Corrida[]; total: number }> {
  const consulta = new URLSearchParams();
  Object.entries(filtro).forEach(([clave, valor]) => { if (valor !== undefined && valor !== "") consulta.set(clave, String(valor)); });
  const sobre = await solicitarSobre<Corrida[]>(`/pronosticos/corridas?${consulta}`, { token, signal });
  if (typeof sobre.metadatos?.total !== "number") throw new Error("Actualiza el servidor para consultar el historial completo de pronósticos.");
  return { filas: sobre.datos, total: sobre.metadatos.total };
}

export function listarCorridas(token: string, modeloId?: number, signal?: AbortSignal): Promise<Corrida[]> {
  const consulta = modeloId ? `?modelo_id=${modeloId}` : "";
  return solicitar<Corrida[]>(`/pronosticos/corridas${consulta}`, { token, signal });
}

export function obtenerCorrida(token: string, id: number, signal?: AbortSignal): Promise<Corrida> {
  return solicitar<Corrida>(`/pronosticos/corridas/${id}`, { token, signal });
}

export function obtenerEvaluacion(token: string, modeloId: number, signal?: AbortSignal, fechas: { desde?: string; hasta?: string } = {}): Promise<EvaluacionTramo> {
  const consulta = new URLSearchParams({ modelo_id: String(modeloId) });
  if (fechas.desde) consulta.set("desde", fechas.desde);
  if (fechas.hasta) consulta.set("hasta", fechas.hasta);
  return solicitar<EvaluacionTramo>(`/pronosticos/evaluacion?${consulta}`, { token, signal });
}

export function obtenerEvaluacionCorrida(token: string, id: number, signal?: AbortSignal): Promise<EvaluacionDia> {
  return solicitar<EvaluacionDia>(`/pronosticos/corridas/${id}/evaluacion`, { token, signal });
}

export function prepararModelo(token: string, version: string, clave: string): Promise<{ ejecucion_id: number; estado: string }> {
  return solicitar<{ ejecucion_id: number; estado: string }>("/pronosticos/preparar-modelo", {
    token, method: "POST", body: { version_modelo: version, clave_idempotencia: clave },
  });
}
