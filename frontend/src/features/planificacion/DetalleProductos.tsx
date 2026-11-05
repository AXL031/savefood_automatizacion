"use client";

import { useState } from "react";
import { ExploradorDetalle } from "@/components/tables/ExploradorDetalle";
import { TablaDatos } from "@/components/tables/TablaDatos";
import type { ElementoPlan } from "@/types/planificacion";
import { cantidadVisible } from "@/utils/unidades";
import { etiquetaDato } from "@/utils/etiquetas";

const estados: Record<string, string> = { CALCULADO: "Calculado", HISTORIAL_INSUFICIENTE: "Historial insuficiente", PRODUCTO_NO_CUBIERTO: "Producto fuera del modelo", SIN_RECETA: "Sin receta", STOCK_DESCONOCIDO: "Stock desconocido", VIGENCIA_STOCK_DESCONOCIDA: "Vigencia del stock desconocida", LOTES_EXCLUIDOS: "Lotes excluidos del disponible" };
const unidades = (v: number | null) => v === null ? "No disponible" : `${v} u.`;

function TrazaProducto({ elemento: e }: { elemento: ElementoPlan }) {
  const [vista, setVista] = useState<"receta" | "lotes">("receta");
  return <>
    <p>Pronóstico #{e.pronostico_id} · {estados[e.estado] ?? etiquetaDato(e.estado)} · Receta {e.receta ? `#${e.receta.receta_id}, versión ${e.receta.version}` : "no disponible"}.</p>
    {!!e.avisos.length && <p className="inline-warning">{e.avisos.map(a => estados[a] ?? etiquetaDato(a)).join(" · ")}</p>}
    <div className="operation-tabs" role="group" aria-label="Información del producto">
      <button type="button" className={vista === "receta" ? "button-primary" : "button-secondary"} aria-pressed={vista === "receta"} onClick={() => setVista("receta")}>Receta conservada ({e.receta?.lineas.length ?? 0})</button>
      <button type="button" className={vista === "lotes" ? "button-primary" : "button-secondary"} aria-pressed={vista === "lotes"} onClick={() => setVista("lotes")}>Lotes consultados ({e.stock.lotes.length})</button>
    </div>
    {vista === "receta" ? e.receta ? <TablaDatos compacta filas={e.receta.lineas} idFila={l => l.ingrediente_id} vacioTitulo="La receta no tiene líneas conservadas" columnas={[
      { clave: "nombre", encabezado: "Ingrediente", celda: l => <><strong>{l.nombre}</strong><small>{l.codigo}</small></> },
      { clave: "cantidad", encabezado: "Cantidad por unidad", celda: l => cantidadVisible(l.cantidad_por_unidad, l.unidad_base) },
    ]} /> : <p className="helper-text">No hay una receta disponible en este plan.</p>
      : <TablaDatos compacta filas={e.stock.lotes} idFila={l => l.lote_id} vacioTitulo="No había lotes registrados" vacioDescripcion="Se conserva la lectura del plan, sin sustituir el stock desconocido por cero." columnas={[
        { clave: "lote", encabezado: "Lote", celda: l => <strong>{l.codigo_lote}</strong> },
        { clave: "saldo", encabezado: "Saldo registrado", celda: l => `${l.saldo} u.` },
        { clave: "incluido", encabezado: "Considerado en el plan", celda: l => <span className={`badge ${l.cuenta ? "badge-ok" : "badge-neutral"}`}>{l.cuenta ? "Incluido" : "Excluido"}</span> },
        { clave: "motivo", encabezado: "Motivo", celda: l => etiquetaDato(l.motivo) },
        { clave: "caducidad", encabezado: "Caducidad", celda: l => l.fecha_caducidad ?? "Desconocida" },
        { clave: "limite", encabezado: "Límite de venta", celda: l => l.fecha_limite_venta ?? "Desconocido" },
      ]} />}
    <p className="helper-text">Receta y lotes corresponden a la lectura guardada del plan; los movimientos posteriores no cambian estas trazas.</p>
  </>;
}

export function DetalleProductos({ elementos }: { elementos: ElementoPlan[] }) {
  return <section className="section-space"><h3>Productos y trazabilidad</h3><ExploradorDetalle filas={elementos} idFila={e => e.producto_id} nombre={e => e.stock.nombre} textoBusqueda={e => `${e.stock.nombre} ${e.stock.codigo}`} etiquetaBusqueda="Buscar producto del plan" etiquetaDetalle="Traza del producto" filtros={[
    { valor: "avisos", etiqueta: "Con avisos o datos incompletos", acepta: e => e.avisos.length > 0 || e.estado !== "CALCULADO" },
    { valor: "producir", etiqueta: "Con producción sugerida", acepta: e => e.cantidad_producir !== null && e.cantidad_producir > 0 },
    { valor: "stock", etiqueta: "Stock sin confirmar", acepta: e => e.stock_disponible === null },
  ]} columnas={[
    { clave: "pronostico", encabezado: "Pronóstico", celda: e => unidades(e.cantidad_pronosticada) },
    { clave: "stock", encabezado: "Stock disponible", celda: e => unidades(e.stock_disponible) },
    { clave: "producir", encabezado: "Producción sugerida", celda: e => unidades(e.cantidad_producir) },
    { clave: "estado", encabezado: "Resultado", celda: e => estados[e.estado] ?? etiquetaDato(e.estado) },
  ]} detalle={e => <TrazaProducto elemento={e} />} /></section>;
}
