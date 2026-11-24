"use client";
import { useEffect, useState } from "react";
import { TablaDatos } from "@/components/tables/TablaDatos";
import { cerrarDia, listarCierres } from "@/services/ventas";
import type { CierreDia as Cierre, ResultadoCierre } from "@/types/ventas";

/** Consolida las ventas de caja y tienda de un día en el historial que usa el modelo de pronóstico. */
export function CierreDia({ token, alCerrar }: { token: string; alCerrar?: () => void }) {
  const [cierres, setCierres] = useState<Cierre[]>([]), [hoy, setHoy] = useState("");
  const [fecha, setFecha] = useState(""), [terminada, setTerminada] = useState(false);
  const [ocupado, setOcupado] = useState(false), [revision, setRevision] = useState(0);
  const [error, setError] = useState(""), [resultado, setResultado] = useState<ResultadoCierre | null>(null);

  useEffect(() => {
    const c = new AbortController();
    listarCierres(token, c.signal).then(v => {
      if (c.signal.aborted) return;
      setCierres(v.datos);
      const fechaHoy = String(v.metadatos?.hoy ?? "");
      setHoy(fechaHoy); setFecha(actual => actual || fechaHoy);
    }).catch(e => { if (!c.signal.aborted) setError(e instanceof Error ? e.message : "No se pudieron leer los cierres."); });
    return () => c.abort();
  }, [token, revision]);

  async function cerrar() {
    setOcupado(true); setError(""); setResultado(null);
    try {
      const r = await cerrarDia(token, fecha, fecha === hoy && terminada);
      setResultado(r); setTerminada(false); setRevision(v => v + 1); alCerrar?.();
    } catch (e) { setError(e instanceof Error ? e.message : "No se pudo cerrar el día."); }
    finally { setOcupado(false); }
  }

  const esHoy = fecha !== "" && fecha === hoy;
  return <section className="card section-space" aria-labelledby="titulo-cierre-dia">
    <div className="section-heading"><div><h2 id="titulo-cierre-dia">Cierre del día</h2><p>Suma las ventas confirmadas de caja y tienda de un día y las agrega al historial con el que se entrena el modelo de pronóstico. El día anterior se cierra solo cada madrugada.</p></div></div>
    <div className="form-grid">
      <label className="field">Día a cerrar<input type="date" value={fecha} max={hoy || undefined} onChange={e => { setFecha(e.target.value); setResultado(null); }} /></label>
      <div className="form-actions"><button className="button-primary" disabled={ocupado || !fecha || (esHoy && !terminada)} onClick={() => void cerrar()}>{ocupado ? "Cerrando…" : "Cerrar día"}</button></div>
    </div>
    {esHoy && <label className="review-checkbox"><input type="checkbox" checked={terminada} onChange={e => setTerminada(e.target.checked)} />La jornada de hoy ya terminó y no habrá más ventas.</label>}
    {error && <p className="inline-error" role="alert">{error}</p>}
    {resultado && <p className="inline-success" role="status">{resultado.cierre_id === null
      ? `No hubo ventas confirmadas el ${resultado.fecha}; no se agregó nada al historial.`
      : resultado.repetido
        ? `El ${resultado.fecha} ya estaba cerrado con estas mismas ventas; no se cambió nada.`
        : `Día ${resultado.fecha} cerrado: ${resultado.unidades} unidades de ${resultado.productos} producto(s). ${resultado.creadas} nuevos, ${resultado.actualizadas} actualizados en el historial.`}</p>}
    {resultado && resultado.conflictos.length > 0 && <p className="inline-error" role="status">{resultado.conflictos.length} producto(s) ya tenían ese día en el historial importado o corregido y no se sobrescribieron.</p>}
    <TablaDatos filas={cierres} idFila={c => c.id} vacioTitulo="Todavía no hay cierres" vacioDescripcion="Cuando cierres un día, aparecerá aquí con las unidades que pasaron al historial." columnas={[
      { clave: "fecha", encabezado: "Día", celda: c => <strong>{c.fecha}</strong> },
      { clave: "productos", encabezado: "Productos", celda: c => c.productos },
      { clave: "unidades", encabezado: "Unidades al historial", celda: c => c.unidades },
      { clave: "id", encabezado: "Cierre", celda: c => `#${c.id}` },
    ]} />
  </section>;
}
