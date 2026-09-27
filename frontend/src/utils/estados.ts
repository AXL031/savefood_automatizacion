import type { EstadoEjecucion } from "@/types/automatizacion";

const etiquetas: Record<EstadoEjecucion, string> = {
  PENDIENTE: "Pendiente",
  EN_EJECUCION: "En ejecución",
  COMPLETADA: "Completada",
  REINTENTANDO: "Reintentando",
  FALLIDA: "Fallida",
};

export function etiquetaEstado(estado: EstadoEjecucion): string {
  return etiquetas[estado] ?? estado;
}

export function tonoEstado(estado: EstadoEjecucion): "neutral" | "info" | "ok" | "alerta" {
  if (estado === "COMPLETADA") return "ok";
  if (estado === "FALLIDA") return "alerta";
  if (estado === "EN_EJECUCION" || estado === "REINTENTANDO") return "info";
  return "neutral";
}
