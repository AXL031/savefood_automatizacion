"use client";

import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { Campo } from "@/components/forms/Campo";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { TablaPaginada } from "@/components/tables/TablaPaginada";
import type { Plan } from "@/types/planificacion";
import { cantidadVisible } from "@/utils/unidades";
import { etiquetaDato } from "@/utils/etiquetas";

type Props = Pick<Plan, "necesidades" | "elementos">;
type Filtro = "todos" | "faltantes" | "sin-stock";
const normalizar = (valor: string) => valor.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("es");

function TablaExplorable({ filas, children }: { filas: number; children: ReactNode }) {
  return <div className="plan-ingredients-table">{filas > 10
    ? <TablaPaginada>{children}</TablaPaginada>
    : <div className="table-wrap"><table>{children}</table></div>}</div>;
}

/** Explora los snapshots del plan; no consulta ni recalcula inventario. */
export function DetalleIngredientes({ necesidades, elementos }: Props) {
  const [busqueda, setBusqueda] = useState("");
  const [filtro, setFiltro] = useState<Filtro>("todos");
  const [seleccionado, setSeleccionado] = useState<number | null>(null);
  const [vista, setVista] = useState<"aportes" | "lotes">("aportes");
  const id = useId();
  const panel = useRef<HTMLElement>(null);
  const buscador = useRef<HTMLInputElement>(null);
  const origen = useRef<HTMLButtonElement | null>(null);
  const texto = normalizar(busqueda.trim());
  const filtradas = necesidades.filter(n => normalizar(`${n.stock.nombre} ${n.stock.codigo}`).includes(texto) &&
    (filtro === "todos" || (filtro === "faltantes" && n.faltante !== null && Number(n.faltante) > 0) || (filtro === "sin-stock" && n.stock_disponible === null)));
  const seleccion = filtradas.find(n => n.ingrediente_id === seleccionado);
  const conFaltantes = necesidades.filter(n => n.faltante !== null && Number(n.faltante) > 0).length;
  const sinStock = necesidades.filter(n => n.stock_disponible === null).length;

  useEffect(() => {
    if (seleccion) {
      panel.current?.focus({ preventScroll: true });
      panel.current?.scrollIntoView({ block: "nearest" });
    }
  }, [seleccion?.ingrediente_id]);

  function cerrar() {
    setSeleccionado(null);
    if (origen.current?.isConnected) origen.current.focus();
    else buscador.current?.focus();
  }

  if (!necesidades.length) return null;
  return <div className="plan-ingredients">
    <div className="plan-ingredients-summary">
      <span><strong>{necesidades.length}</strong> ingredientes</span>
      <span><strong>{conFaltantes}</strong> con faltantes</span>
      {sinStock > 0 && <span><strong>{sinStock}</strong> con stock sin confirmar</span>}
    </div>
    <div className="plan-ingredients-filters">
      <Campo htmlFor={`${id}-buscar`} etiqueta="Buscar ingrediente">
        <input ref={buscador} id={`${id}-buscar`} type="search" placeholder="Harina, azúcar, mantequilla…" value={busqueda} onChange={e => { setBusqueda(e.target.value); setSeleccionado(null); }} />
      </Campo>
      <Campo htmlFor={`${id}-filtro`} etiqueta="Mostrar">
        <select id={`${id}-filtro`} value={filtro} onChange={e => { setFiltro(e.target.value as Filtro); setSeleccionado(null); }}>
          <option value="todos">Todos los ingredientes</option>
          <option value="faltantes">Con faltantes</option>
          <option value="sin-stock">Stock sin confirmar</option>
        </select>
      </Campo>
      {(busqueda || filtro !== "todos") && <button type="button" className="button-secondary" onClick={() => { setBusqueda(""); setFiltro("todos"); setSeleccionado(null); }}>Limpiar filtros</button>}
    </div>
    <p className="helper-text plan-ingredients-hint">{filtradas.length !== necesidades.length && <span role="status">{filtradas.length} de {necesidades.length} ingredientes. </span>}Selecciona un ingrediente para ver qué productos lo necesitan y qué lotes se consideraron.</p>
    {filtradas.length ? <TablaExplorable key={`${busqueda}:${filtro}`} filas={filtradas.length}>
      <thead><tr><th scope="col">Ingrediente</th><th scope="col">Necesario</th><th scope="col">En inventario</th><th scope="col">Falta comprar</th></tr></thead>
      <tbody>{filtradas.map(n => <tr key={n.ingrediente_id} className={seleccion?.ingrediente_id === n.ingrediente_id ? "plan-ingredient-selected" : undefined}>
        <td><button type="button" className="plan-ingredient-name" aria-label={`${seleccion?.ingrediente_id === n.ingrediente_id ? "Ocultar" : "Ver"} detalle de ${n.stock.nombre}`} aria-expanded={seleccion?.ingrediente_id === n.ingrediente_id} aria-controls={`${id}-detalle`}
          onClick={e => {
            if (seleccion?.ingrediente_id === n.ingrediente_id) { cerrar(); return; }
            origen.current = e.currentTarget; setSeleccionado(n.ingrediente_id); setVista("aportes");
          }}><strong>{n.stock.nombre}</strong><span>{seleccion?.ingrediente_id === n.ingrediente_id ? "Ocultar detalle ↑" : "Ver detalle →"}</span></button></td>
        <td>{cantidadVisible(n.cantidad_necesaria, n.unidad_base)}</td>
        <td>{cantidadVisible(n.stock_disponible, n.unidad_base)}</td>
        <td><span className={n.faltante === null ? "badge badge-neutral" : Number(n.faltante) > 0 ? "badge badge-advertencia" : "badge badge-ok"}>{cantidadVisible(n.faltante, n.unidad_base)}</span></td>
      </tr>)}</tbody>
    </TablaExplorable> : <EstadoPanel titulo="No hay ingredientes con esos filtros" descripcion="Prueba otro nombre o muestra todos los ingredientes del plan." />}

    <section id={`${id}-detalle`} ref={panel} tabIndex={-1} className="plan-ingredient-detail" hidden={!seleccion} aria-labelledby={`${id}-titulo`}>
      <header className="plan-ingredient-heading"><div><span className="analytics-eyebrow">Detalle del ingrediente</span><h4 id={`${id}-titulo`}>{seleccion?.stock.nombre ?? "Ingrediente"}</h4></div>
        <button type="button" className="button-secondary" onClick={cerrar}>Cerrar detalle del ingrediente</button>
      </header>
      {seleccion && <>
        <dl className="plan-ingredient-quantities">
          <div><dt>Necesario</dt><dd>{cantidadVisible(seleccion.cantidad_necesaria, seleccion.unidad_base)}</dd></div>
          <div><dt>En inventario</dt><dd>{cantidadVisible(seleccion.stock_disponible, seleccion.unidad_base)}</dd></div>
          <div><dt>Falta comprar</dt><dd>{cantidadVisible(seleccion.faltante, seleccion.unidad_base)}</dd></div>
        </dl>
        <div className="operation-tabs" role="group" aria-label="Información del ingrediente">
          <button type="button" className={vista === "aportes" ? "button-primary" : "button-secondary"} aria-pressed={vista === "aportes"} onClick={() => setVista("aportes")}>Aportes por producto ({seleccion.aportes.length})</button>
          <button type="button" className={vista === "lotes" ? "button-primary" : "button-secondary"} aria-pressed={vista === "lotes"} onClick={() => setVista("lotes")}>Lotes consultados ({seleccion.stock.lotes.length})</button>
        </div>
        {vista === "aportes" ? seleccion.aportes.length ? <TablaExplorable key={`aportes-${seleccion.ingrediente_id}`} filas={seleccion.aportes.length}>
          <thead><tr><th scope="col">Producto y receta</th><th scope="col">Producción</th><th scope="col">Por unidad</th><th scope="col">Aporte total</th></tr></thead>
          <tbody>{seleccion.aportes.map(a => <tr key={a.producto_id}>
            <td><strong>{elementos.find(e => e.producto_id === a.producto_id)?.stock.nombre ?? `Producto #${a.producto_id}`}</strong><small>Receta #{a.receta_id} · versión {a.version_receta}</small></td>
            <td>{a.cantidad_producir} u.</td><td>{cantidadVisible(a.cantidad_por_unidad, seleccion.unidad_base)}</td><td>{cantidadVisible(a.aporte, seleccion.unidad_base)}</td>
          </tr>)}</tbody>
        </TablaExplorable> : <p className="helper-text">Este ingrediente no tiene aportes calculables guardados.</p>
          : seleccion.stock.lotes.length ? <TablaExplorable key={`lotes-${seleccion.ingrediente_id}`} filas={seleccion.stock.lotes.length}>
            <thead><tr><th scope="col">Lote</th><th scope="col">Saldo registrado</th><th scope="col">Considerado en el plan</th><th scope="col">Motivo</th></tr></thead>
            <tbody>{seleccion.stock.lotes.map(l => <tr key={l.lote_id}><td><strong>{l.codigo_lote}</strong><small>Caducidad: {l.fecha_caducidad ?? "Sin fecha"}</small></td><td>{cantidadVisible(l.saldo, seleccion.unidad_base)}</td><td><span className={`badge ${l.cuenta ? "badge-ok" : "badge-neutral"}`}>{l.cuenta ? "Incluido" : "Excluido"}</span></td><td>{etiquetaDato(l.motivo)}</td></tr>)}</tbody>
          </TablaExplorable> : <p className="helper-text">No había lotes registrados en la lectura de este plan.</p>}
        <p className="helper-text">Estos datos corresponden a la lectura guardada del plan; los movimientos posteriores no cambian este detalle.</p>
      </>}
    </section>
  </div>;
}
