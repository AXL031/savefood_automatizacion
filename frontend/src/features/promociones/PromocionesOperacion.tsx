"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { TablaDatos } from "@/components/tables/TablaDatos";
import { PanelDetalle } from "@/components/ui/PanelDetalle";
import { formatearEscenario, formatearFechaHora } from "@/utils/fechas";

type Modo = "REQUIERE_APROBACION" | "AUTOMATICO";
export type PromocionOperativa = {
  id: number; lote_id: number; producto: string; codigo_lote: string; estado: string;
  descuento: number | null; motivo: string; fecha: string; stock_disponible: number;
  fecha_limite_venta: string | null; activa_en_tienda: boolean; modo_publicacion: Modo;
  programacion: { programacion_id: number; ejecutar_desde_utc: string; estado: string; modo_publicacion: Modo } | null;
};
type Ejecutar = (ruta: string, body: unknown, method?: "POST" | "PUT") => Promise<boolean>;

export function enDosMinutos(zona: string) {
  const partes = new Intl.DateTimeFormat("sv-SE", { timeZone: zona, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23" }).formatToParts(new Date(Date.now() + 120_000));
  const valor = (tipo: string) => partes.find(p => p.type === tipo)?.value ?? "";
  return `${valor("year")}-${valor("month")}-${valor("day")}T${valor("hour")}:${valor("minute")}:${valor("second")}`;
}

export function PromocionesOperacion({ filas, ejecutar, zona, modoPredeterminado, ocupado, bloqueado, error }: {
  filas: PromocionOperativa[]; ejecutar: Ejecutar; zona: string; modoPredeterminado: Modo;
  ocupado: boolean; bloqueado: boolean; error: string;
}) {
  const [busqueda, setBusqueda] = useState(""), [filtro, setFiltro] = useState("TODAS");
  const [seleccionada, setSeleccionada] = useState<PromocionOperativa | null>(null);
  const [fecha, setFecha] = useState(""), [modo, setModo] = useState<Modo>(modoPredeterminado);
  const [reloj, setReloj] = useState(Date.now());
  const clave = useRef("");
  const hayProgramadas = filas.some(p => p.estado === "PROGRAMADA");
  useEffect(() => { if (!hayProgramadas) return; const id = setInterval(() => setReloj(Date.now()), 1000); return () => clearInterval(id); }, [hayProgramadas]);
  const normalizar = (v: string) => v.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const visibles = filas.filter(p => normalizar(`${p.producto} ${p.codigo_lote}`).includes(normalizar(busqueda)) &&
    (filtro === "TODAS" || (filtro === "ACTIVAS" ? p.activa_en_tienda : p.estado === filtro)));
  function abrir(p: PromocionOperativa) {
    setSeleccionada(p); setFecha(enDosMinutos(zona)); setModo(modoPredeterminado); clave.current = crypto.randomUUID();
  }
  async function programar(e: FormEvent) {
    e.preventDefault(); if (!seleccionada || ocupado || bloqueado) return;
    const ok = await ejecutar(`/operaciones/promociones/${seleccionada.id}/programar`, { clave_idempotencia: clave.current, fecha_hora_local: fecha, modo_publicacion: modo });
    if (ok) setSeleccionada(null);
  }
  return <section className="card">
    <h2>Promociones y publicación programada</h2>
    <p>Programa una promoción concreta para una hora próxima. Si ya está activa, deja de ofrecerse hasta esa hora. La vigilancia general continúa cada diez minutos.</p>
    <div className="action-row"><Link href="/promociones">Configurar regla de descuento →</Link><Link href="/tienda-admin">Revisar entrega a tienda →</Link><button onClick={() => ejecutar("/operaciones/revisar", {})}>Revisar ahora</button></div>
    <div className="form-grid section-space">
      <label className="field">Buscar producto o lote<input type="search" value={busqueda} onChange={e => setBusqueda(e.target.value)} /></label>
      <label className="field">Mostrar<select value={filtro} onChange={e => setFiltro(e.target.value)}><option value="TODAS">Todas las evaluaciones</option><option value="ACTIVAS">Activas en tienda</option><option value="PROGRAMADA">Programadas</option><option value="PENDIENTE">Pendientes de aprobación</option></select></label>
    </div>
    <TablaDatos compacta filas={visibles} idFila={p => p.id} vacioTitulo="Sin promociones para este filtro" vacioDescripcion="Selecciona productos para revisión o cambia el filtro." pie="Se muestran hasta 100 evaluaciones recientes. Una aprobación solo está activa en tienda si el producto está publicado y su lote tiene disponibilidad y vigencia." columnas={[
      { clave: "producto", encabezado: "Producto y lote", celda: p => <><strong>{p.producto}</strong><small>{p.codigo_lote || `Lote #${p.lote_id}`}</small><small>Vendible: {p.stock_disponible} · límite {formatearEscenario(p.fecha_limite_venta)}</small></> },
      { clave: "estado", encabezado: "Estado", celda: p => <><span className={`badge ${p.activa_en_tienda ? "badge-ok" : "badge-neutral"}`}>{p.activa_en_tienda ? "Activa en tienda" : p.estado === "PENDIENTE" ? "Pendiente de aprobación" : p.estado === "PROGRAMADA" ? "Programada" : p.estado.replaceAll("_", " ")}</span>{p.descuento != null && <small>{p.descuento} %</small>}<small>{(p.estado === "PROGRAMADA" ? p.programacion?.modo_publicacion : p.modo_publicacion) === "AUTOMATICO" ? "Automática" : "Aprobación manual"}</small></> },
      { clave: "hora", encabezado: "Programación", celda: p => p.programacion ? <><span>{formatearFechaHora(p.programacion.ejecutar_desde_utc, zona)}</span>{p.estado === "PROGRAMADA" && <small>{Date.parse(p.programacion.ejecutar_desde_utc) > reloj ? `En ${Math.ceil((Date.parse(p.programacion.ejecutar_desde_utc) - reloj) / 1000)} s` : "Esperando al motor…"}</small>}<small>{p.programacion.estado}</small><Link href="/automatizaciones">Tarea #{p.programacion.programacion_id}</Link></> : "Sin programación puntual" },
      { clave: "motivo", encabezado: "Motivo", celda: p => p.motivo },
      { clave: "acciones", encabezado: "Acciones", celda: p => <div className="action-row">{p.estado === "PENDIENTE" && <><button onClick={() => ejecutar(`/operaciones/promociones/${p.id}/decision`, { aprobar: true })}>Aprobar ahora</button><button className="button-secondary" onClick={() => ejecutar(`/operaciones/promociones/${p.id}/decision`, { aprobar: false })}>Rechazar</button></>}{["PENDIENTE", "APROBADA"].includes(p.estado) && <button className="button-secondary" onClick={() => abrir(p)}>Programar publicación</button>}{p.estado === "PROGRAMADA" && <button className="button-secondary" onClick={() => ejecutar(`/operaciones/promociones/${p.id}/cancelar-programacion`, { programacion_id: p.programacion?.programacion_id })}>Cancelar programación</button>}</div> },
    ]} />
    {seleccionada && <PanelDetalle titulo={`Programar · ${seleccionada.producto}`} ocupado={ocupado} onCerrar={() => setSeleccionada(null)}>
      <p>Lote {seleccionada.codigo_lote} · {seleccionada.descuento} % de descuento. Se comprobarán nuevamente stock, vencimiento y la versión de regla de esta promoción al ejecutar.</p>
      {seleccionada.activa_en_tienda && <p className="inline-error">Al confirmar, esta promoción dejará de estar visible hasta la hora programada. Si existen otros lotes promocionados del producto, sus descuentos continúan vigentes.</p>}
      <form className="form-grid" onSubmit={programar}><fieldset className="form-grid field-full" disabled={ocupado || bloqueado}>
        <label className="field field-full">Fecha y hora · {zona}<input type="datetime-local" step={1} required value={fecha} onChange={e => { setFecha(e.target.value); clave.current = crypto.randomUUID(); }} /></label>
        <button type="button" className="button-secondary" onClick={() => { setFecha(enDosMinutos(zona)); clave.current = crypto.randomUUID(); }}>Dentro de dos minutos</button>
        <label className="field field-full">Al llegar la hora<select value={modo} onChange={e => { setModo(e.target.value as Modo); clave.current = crypto.randomUUID(); }}><option value="AUTOMATICO">Publicar automáticamente si cumple la regla</option><option value="REQUIERE_APROBACION">Dejar pendiente para aprobación</option></select></label>
        <p className="helper-text field-full">La tarea puede empezar hasta unos 30 segundos después de la hora elegida. La entrega a tienda tarda unos segundos adicionales. No descuenta inventario. Cancelar deja la sugerencia pendiente y oculta.</p>
        <button type="submit" className="button-primary">Confirmar programación</button>
      </fieldset>{error && <p className="inline-error field-full" role="alert">{error} Cierra este panel para consultar o recuperar la operación.</p>}</form>
    </PanelDetalle>}
  </section>;
}
