import { solicitar } from "./http";
import type { Notificacion } from "@/types/notificacion";

export function listarNotificaciones(token: string, signal?: AbortSignal): Promise<Notificacion[]> {
  return solicitar<Notificacion[]>("/notificaciones", { token, signal });
}
