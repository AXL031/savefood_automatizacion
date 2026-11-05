"use client";

import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { Campo } from "@/components/forms/Campo";
import { TablaDatos, type Columna } from "./TablaDatos";

type Filtro<T> = { valor: string; etiqueta: string; acepta: (fila: T) => boolean };
type Props<T> = {
  filas: T[]; idFila: (fila: T) => number | string; nombre: (fila: T) => string;
  textoBusqueda: (fila: T) => string; etiquetaBusqueda: string;
  columnas?: Columna<T>[]; filtros?: Filtro<T>[];
  detalle?: (fila: T) => ReactNode; etiquetaDetalle?: string;
};
const normalizar = (v: string) => v.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("es");

/** Explora registros ya recibidos, sin consultar ni modificar datos del dominio. */
export function ExploradorDetalle<T>({ filas, idFila, nombre, textoBusqueda, etiquetaBusqueda, columnas = [], filtros = [], detalle, etiquetaDetalle = "Detalle del producto" }: Props<T>) {
  const [busqueda, setBusqueda] = useState("");
  const [filtro, setFiltro] = useState("");
  const [seleccionado, setSeleccionado] = useState<number | string | null>(null);
  const id = useId(), panel = useRef<HTMLElement>(null), buscador = useRef<HTMLInputElement>(null), origen = useRef<HTMLButtonElement | null>(null);
  const criterio = filtros.find(f => f.valor === filtro);
  const visibles = filas.filter(f => normalizar(textoBusqueda(f)).includes(normalizar(busqueda.trim())) && (!criterio || criterio.acepta(f)));
  const seleccion = visibles.find(f => idFila(f) === seleccionado);
  useEffect(() => {
    if (seleccion) { panel.current?.focus({ preventScroll: true }); panel.current?.scrollIntoView({ block: "nearest" }); }
  }, [seleccionado]); // La selección no se restablece por nuevas referencias del mismo snapshot.
  function cerrar() {
    setSeleccionado(null);
    if (origen.current?.isConnected) origen.current.focus(); else buscador.current?.focus();
  }
  return <div className="record-explorer">
    <div className={`record-explorer-filters${filtros.length ? " has-filters" : ""}`}>
      <Campo etiqueta={etiquetaBusqueda} htmlFor={`${id}-buscar`}><input ref={buscador} id={`${id}-buscar`} type="search" placeholder="Nombre o código" value={busqueda} onChange={e => { setBusqueda(e.target.value); setSeleccionado(null); }} /></Campo>
      {!!filtros.length && <Campo etiqueta="Mostrar productos" htmlFor={`${id}-filtro`}><select id={`${id}-filtro`} value={filtro} onChange={e => { setFiltro(e.target.value); setSeleccionado(null); }}><option value="">Todos los productos</option>{filtros.map(f => <option key={f.valor} value={f.valor}>{f.etiqueta}</option>)}</select></Campo>}
      {(busqueda || filtro) && <button type="button" className="button-secondary" onClick={() => { setBusqueda(""); setFiltro(""); setSeleccionado(null); }}>Limpiar búsqueda y filtros</button>}
    </div>
    <p className="helper-text" role="status">{visibles.length} de {filas.length} productos{detalle ? " · Selecciona un producto para consultar su detalle." : "."}</p>
    <TablaDatos compacta key={`${busqueda}:${filtro}`} filas={visibles} idFila={idFila} vacioTitulo="No hay productos con esos filtros" vacioDescripcion="Prueba otro nombre o código, o limpia los filtros." columnas={[
      { clave: "producto", encabezado: "Producto", celda: f => detalle ? <button type="button" className="record-explorer-name" aria-label={`${idFila(f) === seleccionado ? "Ocultar" : "Ver"} detalle de ${nombre(f)}`} aria-expanded={idFila(f) === seleccionado} aria-controls={`${id}-detalle`} onClick={e => {
        if (idFila(f) === seleccionado) { cerrar(); return; }
        origen.current = e.currentTarget; setSeleccionado(idFila(f));
      }}><strong>{nombre(f)}</strong><span>{idFila(f) === seleccionado ? "Ocultar detalle ↑" : "Ver detalle →"}</span></button> : <strong>{nombre(f)}</strong> }, ...columnas,
    ]} />
    {detalle && <section ref={panel} id={`${id}-detalle`} className="record-explorer-detail" tabIndex={-1} hidden={!seleccion} aria-labelledby={`${id}-titulo`}>
      <header className="record-explorer-heading"><div><span className="analytics-eyebrow">{etiquetaDetalle}</span><h4 id={`${id}-titulo`}>{seleccion ? nombre(seleccion) : "Producto"}</h4></div><button type="button" className="button-secondary" onClick={cerrar}>Cerrar detalle del producto</button></header>
      {seleccion && <div key={idFila(seleccion)}>{detalle(seleccion)}</div>}
    </section>}
  </div>;
}
