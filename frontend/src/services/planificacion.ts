import { solicitar } from "./http";
import type { Plan, ResumenPlan } from "@/types/planificacion";

export function listarPlanes(token: string, signal?: AbortSignal): Promise<ResumenPlan[]> {
  return solicitar("/planes", { token, signal });
}
export function obtenerPlan(token: string, id: number, signal?: AbortSignal): Promise<Plan> {
  return solicitar(`/planes/${id}`, { token, signal });
}
export function crearPlan(token: string, corridaId: number, clave: string): Promise<Plan> {
  return solicitar("/planes", { token, method: "POST", body: { corrida_id: corridaId, clave_ejecucion: clave } });
}
