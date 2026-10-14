import { solicitar, solicitarSobre } from "./http";
import type { CrearProgramacionDemo, EjecucionAutomatizacion, ProgramacionDemo } from "@/types/automatizacion";

export const programacionesPaginadas = (token: string, pagina: number, tamano: number, signal?: AbortSignal) => solicitarSobre<ProgramacionDemo[]>(`/programaciones-demo?limite=${tamano}&desplazamiento=${(pagina - 1) * tamano}`, { token, signal });
export const ejecucionesPaginadas = (token: string, pagina: number, tamano: number, signal?: AbortSignal) => solicitarSobre<EjecucionAutomatizacion[]>(`/ejecuciones-automatizacion?limite=${tamano}&desplazamiento=${(pagina - 1) * tamano}`, { token, signal });

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
