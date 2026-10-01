"use client";

import { Children, cloneElement, isValidElement, useId, useState, type ReactElement, type ReactNode } from "react";

export type PaginacionRemota = {
  pagina: number; tamano: number; total: number; cargando?: boolean;
  onCambio: (pagina: number, tamano: number) => void;
};

export function Paginador({ pagina, tamano, total, cargando, onCambio }: PaginacionRemota) {
  const id = useId();
  const paginas = Math.max(1, Math.ceil(total / tamano));
  return <nav className="pagination" aria-label="Paginación de la tabla">
    <span role="status">{total ? `${(pagina - 1) * tamano + 1}–${Math.min(pagina * tamano, total)} de ${total}` : "0 registros"}</span>
    <label htmlFor={`${id}-tamano`}>Filas por página <select id={`${id}-tamano`} value={tamano} disabled={cargando} onChange={(e) => onCambio(1, Number(e.target.value))}>{[10, 25, 50, 100].map((n) => <option key={n} value={n}>{n}</option>)}</select></label>
    <div className="pagination-actions">
      <button type="button" className="button-secondary" aria-label="Primera página" disabled={cargando || pagina <= 1} onClick={() => onCambio(1, tamano)}>«</button>
      <button type="button" className="button-secondary" disabled={cargando || pagina <= 1} onClick={() => onCambio(pagina - 1, tamano)}>Anterior</button>
      <form className="pagination-jump" onSubmit={(e) => { e.preventDefault(); const valor = Number(new FormData(e.currentTarget).get("pagina")); if (Number.isSafeInteger(valor) && valor >= 1 && valor <= paginas) onCambio(valor, tamano); }}><label htmlFor={`${id}-pagina`}>Página <input key={pagina} id={`${id}-pagina`} name="pagina" type="number" min={1} max={paginas} defaultValue={pagina} disabled={cargando} required /> de {paginas}</label><button type="submit" className="button-secondary" disabled={cargando}>Ir</button></form>
      <button type="button" className="button-secondary" disabled={cargando || pagina >= paginas} onClick={() => onCambio(pagina + 1, tamano)}>Siguiente</button>
      <button type="button" className="button-secondary" aria-label="Última página" disabled={cargando || pagina >= paginas} onClick={() => onCambio(paginas, tamano)}>»</button>
    </div>
  </nav>;
}

/** Pagina filas ya cargadas; el modo remoto recibe el total real del servidor. */
export function TablaPaginada({ children, remota }: { children: ReactNode; remota?: PaginacionRemota }) {
  const partes = Children.toArray(children);
  const cuerpo = partes.find((parte): parte is ReactElement<{ children: ReactNode }> => isValidElement(parte) && parte.type === "tbody");
  const filas = Children.toArray(cuerpo?.props.children);
  const firma = filas.map((fila) => isValidElement(fila) ? fila.key : "").join("|");
  const [estado, setEstado] = useState({ pagina: 1, tamano: 10, firma });
  // Un filtro o una lista distintos vuelven a la primera página. El sondeo con
  // los mismos identificadores conserva página y tamaño.
  if (estado.firma !== firma) setEstado({ ...estado, pagina: 1, firma });
  const pagina = estado.firma === firma ? Math.min(estado.pagina, Math.max(1, Math.ceil(filas.length / estado.tamano))) : 1;
  const visibles = remota ? filas : filas.slice((pagina - 1) * estado.tamano, pagina * estado.tamano);
  const controles = remota ?? { pagina, tamano: estado.tamano, total: filas.length, onCambio: (p: number, t: number) => setEstado({ pagina: p, tamano: t, firma }) };
  return <div className="paginated-table">
    <div className="table-wrap"><table>{partes.map((parte) => parte === cuerpo ? cloneElement(cuerpo, {}, visibles) : parte)}</table></div>
    <Paginador {...controles} />
  </div>;
}
