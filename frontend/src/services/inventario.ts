import { solicitar, solicitarSobre } from "@/services/http";
import type { ContextoEntradas, DetalleEntrada, ResumenEntrada, SolicitudEntrada } from "@/types/inventario";
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

export const contextoEntradas = (token: string, signal?: AbortSignal) => solicitar<ContextoEntradas>("/inventario/entradas-productos/contexto", { token, signal });
export const registrarEntrada = (token: string, body: SolicitudEntrada) => solicitar<DetalleEntrada>("/inventario/entradas-productos", { token, method: "POST", body });
export const recuperarEntrada = (token: string, clave: string) => solicitar<DetalleEntrada>(`/inventario/entradas-productos/por-clave/${encodeURIComponent(clave)}`, { token });
export const detalleEntrada = (token: string, id: number) => solicitar<DetalleEntrada>(`/inventario/entradas-productos/${id}`, { token });
export const listarEntradas = (token: string, parametros: URLSearchParams, signal?: AbortSignal) => solicitarSobre<ResumenEntrada[]>(`/inventario/entradas-productos?${parametros}`, { token, signal });
