import { solicitar } from "./http";
import type { CrearProgramacionDemo, EjecucionAutomatizacion, ProgramacionDemo } from "@/types/automatizacion";

export function listarProgramaciones(token: string, signal?: AbortSignal): Promise<ProgramacionDemo[]> {
  return solicitar<ProgramacionDemo[]>("/programaciones-demo", { token, signal });
}

export function crearProgramacion(token: string, datos: CrearProgramacionDemo): Promise<ProgramacionDemo> {
  return solicitar<ProgramacionDemo>("/programaciones-demo", { method: "POST", token, body: datos });
}

export function listarEjecuciones(token: string, signal?: AbortSignal): Promise<EjecucionAutomatizacion[]> {
  return solicitar<EjecucionAutomatizacion[]>("/ejecuciones-automatizacion", { token, signal });
}

export function obtenerEjecucion(token: string, id: string, signal?: AbortSignal): Promise<EjecucionAutomatizacion> {
  return solicitar<EjecucionAutomatizacion>(`/ejecuciones-automatizacion/${encodeURIComponent(id)}`, { token, signal });
}
