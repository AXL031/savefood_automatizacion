import { solicitar } from "@/services/http";
import type { DisponibilidadItem, Movimiento, ResultadoAjuste, SolicitudAjuste, TipoItem } from "@/types/inventario";

export function consultarDisponibilidad(
  token: string,
  fecha: string,
  tipo?: TipoItem,
  signal?: AbortSignal,
): Promise<DisponibilidadItem[]> {
  const parametros = new URLSearchParams({ fecha });
  if (tipo) parametros.set("tipo", tipo);
  return solicitar<DisponibilidadItem[]>(`/inventario/disponibilidad?${parametros}`, { token, signal });
}

export function listarMovimientos(
  token: string,
  filtro: { tipo?: TipoItem; loteId?: number; limite?: number } = {},
  signal?: AbortSignal,
): Promise<Movimiento[]> {
  const parametros = new URLSearchParams();
  if (filtro.tipo) parametros.set("tipo", filtro.tipo);
  if (filtro.loteId !== undefined) parametros.set("lote_id", String(filtro.loteId));
  if (filtro.limite !== undefined) parametros.set("limite", String(filtro.limite));
  const consulta = parametros.toString();
  return solicitar<Movimiento[]>(`/inventario/movimientos${consulta ? `?${consulta}` : ""}`, { token, signal });
}

export function registrarAjuste(token: string, cuerpo: SolicitudAjuste): Promise<ResultadoAjuste> {
  return solicitar<ResultadoAjuste>("/inventario/ajustes", { method: "POST", token, body: cuerpo });
}
