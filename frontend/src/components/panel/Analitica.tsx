"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { Metricas, Particion } from "@/types/pronostico";
import { formatearEscenario } from "@/utils/fechas";

export const numeroAnalitica = (valor: number | null | undefined, sufijo = "") =>
  valor == null ? "Sin dato" : `${valor.toLocaleString("es-PE", { maximumFractionDigits: 2 })}${sufijo}`;

export function IconoAnalitica({ tipo = "grafico" }: { tipo?: "grafico" | "modelo" | "archivo" | "inicio" }) {
  const trazos = {
    grafico: <><path d="M4 4v16h16M7 14l4-5 4 3 5-7" /><path d="M16 5h4v4" /></>,
    modelo: <><path d="m12 3 9 5-9 5-9-5 9-5ZM3 12l9 5 9-5M3 16l9 5 9-5" /></>,
    archivo: <><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-6-6ZM14 3v6h6M8 13h8M8 17h5" /></>,
    inicio: <><path d="m3 10 9-7 9 7M5 9v12h14V9M9 21v-8h6v8" /></>,
  };
  return <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{trazos[tipo]}</svg>;
}

export function NavegacionAnalitica() {
  const ruta = usePathname();
  const enlaces = [
    { href: "/", texto: "Vista general", icono: "inicio" as const },
    { href: "/pronosticos", texto: "Pronósticos", icono: "modelo" as const },
    { href: "/panel", texto: "Evaluación", icono: "grafico" as const },
    { href: "/informes", texto: "Reportes", icono: "archivo" as const },
  ];
  return <nav className="analytics-nav" aria-label="Análisis del negocio">{enlaces.map((e) =>
    <Link key={e.href} href={e.href} aria-current={ruta === e.href ? "page" : undefined}>
      <IconoAnalitica tipo={e.icono} />{e.texto}
    </Link>)}</nav>;
}

export function IndicadoresEvaluacion({ metricas, pendientes = 0 }: { metricas: Metricas; pendientes?: number }) {
  const items = [
    { titulo: "Error medio", valor: numeroAnalitica(metricas.mae), unidad: "unidades · MAE", detalle: "Diferencia media por producto y día. Menor es mejor.", icono: "grafico" as const },
    { titulo: "Error relativo", valor: numeroAnalitica(metricas.wape_pct, "%"), unidad: "sobre ventas conocidas · WAPE", detalle: "No se define cuando la suma de ventas reales es cero.", icono: "archivo" as const },
    { titulo: "Dentro de ±20 %", valor: numeroAnalitica(metricas.dentro_mas_menos_20_pct, "%"), unidad: "pronósticos cercanos a la venta", detalle: "Calculado solo con pares que pueden compararse.", icono: "modelo" as const },
    { titulo: "Cobertura evaluada", valor: numeroAnalitica(metricas.cobertura_pct, "%"), unidad: `${numeroAnalitica(metricas.pares_evaluables)} pares comparables`, detalle: pendientes ? `${pendientes} ${pendientes === 1 ? "comparación espera" : "comparaciones esperan"} reevaluación.` : "Ventas ausentes conservan su condición de desconocidas.", icono: "inicio" as const },
  ];
  return <div className="analytics-kpis">{items.map((item, i) => <article key={item.titulo} className={`analytics-kpi ${i === 3 ? "analytics-kpi-accent" : ""}`}>
    <div className="analytics-kpi-label"><span>{item.titulo}</span><IconoAnalitica tipo={item.icono} /></div>
    <strong>{item.valor}</strong><span className="analytics-kpi-unit">{item.unidad}</span><p>{item.detalle}</p>
  </article>)}</div>;
}

export function ParticionModelo({ particion }: { particion: Particion }) {
  return <div className="model-partition" aria-label="Separación temporal del modelo">{[
    ["01", "Entrenamiento", particion.inicio_entrenamiento, particion.fin_entrenamiento],
    ["02", "Validación", particion.inicio_validacion, particion.fin_validacion],
    ["03", "Prueba reservada", particion.inicio_prueba, particion.fin_prueba],
  ].map(([n, titulo, inicio, fin]) => <div key={n}><span className="partition-step">{n}</span><div><strong>{titulo}</strong><span>{formatearEscenario(inicio)} — {formatearEscenario(fin)}</span></div></div>)}</div>;
}
