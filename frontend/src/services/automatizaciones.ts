import { solicitar } from "./http";
import type { Automatizacion, EjecucionAutomatizacion } from "@/types/automatizacion";

export function listarAutomatizaciones(token: string, signal?: AbortSignal): Promise<Automatizacion[]> {
  return solicitar<Automatizacion[]>("/automatizaciones", { token, signal });
}

export function listarEjecuciones(token: string, signal?: AbortSignal): Promise<EjecucionAutomatizacion[]> {
  return solicitar<EjecucionAutomatizacion[]>("/ejecuciones-automatizacion", { token, signal });
}

export function obtenerEjecucion(token: string, id: string, signal?: AbortSignal): Promise<EjecucionAutomatizacion> {
  return solicitar<EjecucionAutomatizacion>(`/ejecuciones-automatizacion/${encodeURIComponent(id)}`, { token, signal });
}

export function reintentarEjecucion(token: string, id: number): Promise<EjecucionAutomatizacion> {
  return solicitar<EjecucionAutomatizacion>(`/ejecuciones-automatizacion/${id}/reintentar`, { method: "POST", token });
}
