import type { EstadoEjecucion } from "@/types/automatizacion";

const etiquetas: Record<EstadoEjecucion, string> = {
  PENDIENTE: "Pendiente",
  EN_EJECUCION: "En ejecución",
  COMPLETADA: "Completada",
  REINTENTANDO: "Reintentando",
  FALLIDA: "Fallida",
  CANCELADA: "Cancelada",
};

export function etiquetaEstado(estado: EstadoEjecucion): string {
  return etiquetas[estado] ?? estado;
}

export function tonoEstado(estado: EstadoEjecucion): "neutral" | "info" | "ok" | "alerta" | "advertencia" {
  if (estado === "COMPLETADA") return "ok";
  if (estado === "FALLIDA") return "alerta";
  if (estado === "EN_EJECUCION") return "info";
  if (estado === "PENDIENTE" || estado === "REINTENTANDO") return "advertencia";
  return "neutral";
}
