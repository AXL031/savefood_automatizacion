import { solicitar } from "./http";
import type { Plan, ResumenPlan } from "@/types/planificacion";

export function completarNecesidades(token: string, id: number): Promise<Plan> {
  return solicitar<Plan>(`/planes/${id}/necesidades`, { token, method: "POST" });
}

export function listarPlanes(token: string, signal?: AbortSignal): Promise<ResumenPlan[]> {
  return solicitar<ResumenPlan[]>("/planes", { token, signal });
}
export function obtenerPlan(token: string, id: number, signal?: AbortSignal): Promise<Plan> {
  return solicitar<Plan>(`/planes/${id}`, { token, signal });
}
export function generarPlan(token: string, corridaId: number, clave: string): Promise<Plan> {
  return solicitar<Plan>("/planes", { token, method: "POST", body: { corrida_id: corridaId, clave_ejecucion: clave } });
}
