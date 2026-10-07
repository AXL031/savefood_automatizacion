import { solicitar, solicitarSobre } from "@/services/http";
import type { CorreccionVenta, Producto, RevisionVenta, VentaDiaria } from "@/types/catalogo";

export function listarProductos(
  token: string,
  opciones: { soloDemo?: boolean } = {},
  signal?: AbortSignal,
): Promise<Producto[]> {
  const consulta = opciones.soloDemo ? "?solo_demo=true" : "";
  return solicitar<Producto[]>(`/productos${consulta}`, { token, signal });
}

export type FiltroVentas = {
  productoId?: number;
  desde?: string;
  hasta?: string;
  limite?: number;
  desplazamiento?: number;
};

export function listarVentas(token: string, filtro: FiltroVentas = {}, signal?: AbortSignal): Promise<VentaDiaria[]> {
  const parametros = new URLSearchParams();
  if (filtro.productoId !== undefined) parametros.set("producto_id", String(filtro.productoId));
  if (filtro.desde) parametros.set("desde", filtro.desde);
  if (filtro.hasta) parametros.set("hasta", filtro.hasta);
  if (filtro.limite !== undefined) parametros.set("limite", String(filtro.limite));
  if (filtro.desplazamiento !== undefined) parametros.set("desplazamiento", String(filtro.desplazamiento));
  const consulta = parametros.toString();
  return solicitar<VentaDiaria[]>(`/ventas${consulta ? `?${consulta}` : ""}`, { token, signal });
}

export async function listarPaginaVentas(token: string, filtro: FiltroVentas, signal?: AbortSignal): Promise<{ filas: VentaDiaria[]; total: number }> {
  const parametros = new URLSearchParams();
  if (filtro.productoId !== undefined) parametros.set("producto_id", String(filtro.productoId));
  if (filtro.desde) parametros.set("desde", filtro.desde);
  if (filtro.hasta) parametros.set("hasta", filtro.hasta);
  parametros.set("limite", String(filtro.limite ?? 10));
  parametros.set("desplazamiento", String(filtro.desplazamiento ?? 0));
  const sobre = await solicitarSobre<VentaDiaria[]>(`/ventas?${parametros}`, { token, signal });
  if (typeof sobre.metadatos?.total !== "number") throw new Error("Actualiza la API para consultar el historial paginado de ventas.");
  return { filas: sobre.datos, total: sobre.metadatos.total };
}

export function listarRevisiones(token: string, ventaId: number, signal?: AbortSignal): Promise<RevisionVenta[]> {
  return solicitar<RevisionVenta[]>(`/ventas/${ventaId}/revisiones`, { token, signal });
}

export function corregirVenta(
  token: string,
  ventaId: number,
  unidades: number,
  motivo: string,
): Promise<CorreccionVenta> {
  return solicitar<CorreccionVenta>(`/ventas/${ventaId}`, {
    method: "PATCH",
    token,
    body: { unidades_vendidas: unidades, motivo },
  });
}
