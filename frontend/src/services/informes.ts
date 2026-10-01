import { solicitar, solicitarArchivo } from "./http";
import type { FiltrosInforme, Informe, TipoInforme } from "@/types/informes";

function consulta(filtros: FiltrosInforme): string {
  const parametros = new URLSearchParams();
  Object.entries(filtros).forEach(([clave, valor]) => { if (valor !== undefined && valor !== "") parametros.set(clave, String(valor)); });
  return parametros.toString();
}

export function obtenerInforme(token: string, filtros: FiltrosInforme = {}, signal?: AbortSignal): Promise<Informe> {
  return solicitar<Informe>(`/informes/resumen?${consulta(filtros)}`, { token, signal });
}

export function descargarInforme(token: string, tipo: TipoInforme, filtros: FiltrosInforme, signal?: AbortSignal): Promise<Blob> {
  return solicitarArchivo(`/informes/exportar?tipo=${tipo}&${consulta(filtros)}`, { token, signal });
}
