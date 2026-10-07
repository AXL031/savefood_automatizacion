"use client";
import { useId } from "react";
import type { Informe } from "@/types/informes";
import { etiquetasEstado } from "@/types/informes";

const numero = (valor: number) => valor.toLocaleString("es");
const fechaCorta = (valor: string) => `${valor.slice(8, 10)}/${valor.slice(5, 7)}`;

/** Cada barra representa un día observado; los huecos mantienen distancia temporal. */
export function GraficoVentas({ informe }: { informe: Informe }) {
  const id = useId();
  const dias = informe.ventas.serie_diaria;
  const maximo = Math.max(1, ...dias.map((d) => d.unidades));
  const inicio = Date.parse(`${informe.periodo.desde}T00:00:00Z`);
  const ancho = Math.max(600, informe.periodo.dias_calendario * 18);
  const zona = ancho - 90;
  const posicion = (fecha: string) => 60 + ((Date.parse(`${fecha}T00:00:00Z`) - inicio) / 86400000 + 0.5) / informe.periodo.dias_calendario * zona;
  return <figure className="report-figure">
    <figcaption><strong>Ventas por día</strong><span>Unidades vendidas · días sin registro conservan un espacio vacío</span></figcaption>
    {!dias.length ? <p className="chart-empty">No hay ventas registradas en este período.</p> : <div className="chart-scroll" tabIndex={0} role="region" aria-label="Gráfico de ventas diarias, desplazable horizontalmente">
      <svg className="sales-chart" viewBox={`0 0 ${ancho} 260`} style={{ minWidth: ancho }} role="img" aria-labelledby={`${id}-titulo ${id}-descripcion`}>
        <title id={`${id}-titulo`}>Ventas del {informe.periodo.desde} al {informe.periodo.hasta}</title>
        <desc id={`${id}-descripcion`}>{numero(informe.ventas.unidades)} unidades en {dias.length} días observados. Los días sin dato no son cero. El detalle de cada día está en la tabla del reporte de ventas.</desc>
        {[0, 0.5, 1].map((fraccion) => <g key={fraccion}><line x1={60} x2={ancho - 30} y1={215 - fraccion * 170} y2={215 - fraccion * 170} className="chart-gridline" /><text x={50} y={220 - fraccion * 170} textAnchor="end">{numero(Math.round(maximo * fraccion))}</text></g>)}
        {dias.map((dia) => <g key={dia.fecha}>
          <title>{dia.fecha}: {numero(dia.unidades)} unidades, {dia.productos_observados} productos observados</title>
          {dia.unidades > 0 ? <rect x={posicion(dia.fecha) - Math.min(12, zona / informe.periodo.dias_calendario * 0.7) / 2} y={215 - dia.unidades / maximo * 170} width={Math.min(12, zona / informe.periodo.dias_calendario * 0.7)} height={dia.unidades / maximo * 170} rx={2} className="chart-bar-sales" /> : <circle cx={posicion(dia.fecha)} cy={215} r={3} className="chart-bar-sales" />}
        </g>)}
        {[...new Set([informe.periodo.desde, ...dias.filter((_, i) => i % Math.max(1, Math.ceil(dias.length / 6)) === 0).map((d) => d.fecha), informe.periodo.hasta])].map((fecha) => <text key={fecha} x={posicion(fecha)} y={245} textAnchor="middle">{fechaCorta(fecha)}</text>)}
      </svg>
    </div>}
    <p className="helper-text">{dias.length} de {informe.periodo.dias_calendario} días con registros. Un punto en la base indica cero registrado. Las unidades suman solo productos observados.</p>
  </figure>;
}

export function GraficoBarras({ titulo, descripcion, filas, tono = "ventas" }: { titulo: string; descripcion: string; filas: { etiqueta: string; cantidad: number }[]; tono?: "ventas" | "pedidos" }) {
  const maximo = Math.max(1, ...filas.map((f) => f.cantidad));
  return <figure className="report-figure"><figcaption><strong>{titulo}</strong><span>{descripcion}</span></figcaption>
    {!filas.some((f) => f.cantidad > 0) ? <p className="chart-empty">No hay cantidades positivas en este período. Consulta los registros en Reportes.</p> : <ul className={`bar-list bar-list-${tono}`} aria-label={titulo}>
      {filas.map((fila) => <li key={fila.etiqueta}><div><span>{fila.etiqueta}</span><strong>{numero(fila.cantidad)}</strong></div><div className="bar-track" aria-hidden="true"><span style={{ width: `${fila.cantidad / maximo * 100}%` }} /></div></li>)}
    </ul>}
  </figure>;
}

export function GraficosOperacion({ informe }: { informe: Informe }) {
  return <div className="report-charts">
    <section className="card report-wide"><GraficoVentas informe={informe} /></section>
    <section className="card"><GraficoBarras titulo="Productos más vendidos" descripcion="Primeros 8 por unidades; ranking completo en Reportes" filas={informe.ventas.por_producto.slice(0, 8).map((p) => ({ etiqueta: `${p.producto} · #${p.producto_id}`, cantidad: p.unidades }))} /></section>
    <section className="card"><GraficoBarras titulo="Estado de pedidos" descripcion="Estado actual; seleccionados por fecha del escenario" tono="pedidos" filas={informe.pedidos.por_estado.filter((p) => p.cantidad > 0).map((p) => ({ etiqueta: etiquetasEstado[p.estado] ?? p.estado, cantidad: p.cantidad }))} />
      <p className="helper-text">{informe.pedidos.total} pedidos · {informe.pedidos.propuestas} propuestas · {informe.pedidos.propuestas_sin_pedidos} propuestas sin pedidos.</p>
    </section>
  </div>;
}
