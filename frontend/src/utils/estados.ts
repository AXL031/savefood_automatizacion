import type { EstadoEjecucion } from "@/types/automatizacion";

const etiquetas: Record<EstadoEjecucion, string> = {
  PENDIENTE: "Pendiente",
  EN_EJECUCION: "En ejecución",
  VERIFICANDO: "Verificando",
  COMPLETADO: "Completado",
  REINTENTANDO: "Reintentando",
  FALLIDO: "Fallido",
  CANCELADO: "Cancelado",
};

export function etiquetaEstado(estado: EstadoEjecucion): string {
  return etiquetas[estado] ?? estado;
}

export function tonoEstado(estado: EstadoEjecucion): "neutral" | "info" | "ok" | "alerta" {
  if (estado === "COMPLETADO") return "ok";
  if (estado === "FALLIDO" || estado === "CANCELADO") return "alerta";
  if (estado === "EN_EJECUCION" || estado === "VERIFICANDO" || estado === "REINTENTANDO") return "info";
  return "neutral";
}
