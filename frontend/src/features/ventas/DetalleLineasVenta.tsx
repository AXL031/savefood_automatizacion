"use client";

import { ExploradorDetalle } from "@/components/tables/ExploradorDetalle";
import { TablaDatos } from "@/components/tables/TablaDatos";
import type { TicketCaja } from "@/types/ventas";

const soles = (v: string) => new Intl.NumberFormat("es-PE", { style: "currency", currency: "PEN" }).format(Number(v));
export function DetalleLineasVenta({ lineas }: Pick<TicketCaja, "lineas">) {
  return <ExploradorDetalle filas={lineas} idFila={l => l.id} nombre={l => l.nombre} textoBusqueda={l => `${l.nombre} ${l.codigo}`} etiquetaBusqueda="Buscar producto de la venta" etiquetaDetalle="Movimientos del producto" columnas={[
    { clave: "cantidad", encabezado: "Unidades", celda: l => `${l.cantidad} u.` },
    { clave: "precio", encabezado: "Precio base", celda: l => soles(l.precio) },
    { clave: "total", encabezado: "Total conservado", celda: l => soles(l.subtotal) },
  ]} detalle={l => <TablaDatos compacta filas={l.salidas} idFila={s => s.movimiento_id} vacioTitulo="Sin movimientos conservados para esta línea" columnas={[
    { clave: "lote", encabezado: "Lote", celda: s => `#${s.lote_id}` },
    { clave: "cantidad", encabezado: "Salida", celda: s => `${s.cantidad} u.` },
    { clave: "movimiento", encabezado: "Movimiento", celda: s => `#${s.movimiento_id}` },
    { clave: "compensacion", encabezado: "Compensación", celda: s => s.compensacion_id === null ? "Sin compensación" : `#${s.compensacion_id}` },
  ]} />} />;
}
