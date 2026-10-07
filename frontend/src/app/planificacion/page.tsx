"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef, useState, type FormEvent } from "react";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { TablaDatos, type Columna } from "@/components/tables/TablaDatos";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { crearPlan, listarPlanes, obtenerPlan } from "@/services/planificacion";
import { listarCorridas } from "@/services/pronosticos";
import type { Corrida } from "@/types/pronostico";
import type { ElementoPlan, Necesidad, Plan, ResumenPlan } from "@/types/planificacion";

const motivos: Record<string, string> = {
  HISTORIAL_INSUFICIENTE: "Historia insuficiente para pronosticar",
  PRODUCTO_NO_CUBIERTO: "El modelo no cubre este producto",
  SIN_RECETA: "Sin receta activa", STOCK_PRODUCTO_DESCONOCIDO: "Sin stock registrado",
};
const columnasProductos: Columna<ElementoPlan>[] = [
  { clave: "nombre", encabezado: "Producto", celda: e => e.producto },
  { clave: "previsto", encabezado: "Pronóstico (un.)", numerica: true, celda: e => e.cantidad_pronosticada },
  { clave: "stock", encabezado: "Stock (un.)", numerica: true, celda: e => e.stock_disponible },
  { clave: "producir", encabezado: "Producir (un.)", numerica: true, celda: e => <strong>{e.cantidad_producir}</strong> },
  { clave: "receta", encabezado: "Receta", celda: e => `#${e.receta_id} · versión ${e.receta_version}` },
];
const columnasIngredientes: Columna<Necesidad>[] = [
  { clave: "nombre", encabezado: "Ingrediente", celda: n => n.ingrediente },
  { clave: "requerido", encabezado: "Requerido", numerica: true, celda: n => `${n.cantidad_requerida} ${n.unidad}` },
  { clave: "stock", encabezado: "Disponible", numerica: true, celda: n => n.cantidad_disponible === null ? "Desconocido" : `${n.cantidad_disponible} ${n.unidad}` },
  { clave: "faltante", encabezado: "Faltante", numerica: true, celda: n => n.cantidad_faltante === null ? "Sin calcular" : <strong>{n.cantidad_faltante} {n.unidad}</strong> },
];

function Contenido({ contexto }: { contexto: ContextoSesion }) {
  const { token, perfil } = contexto;
  const router = useRouter();
  const parametros = useSearchParams();
  const id = Number(parametros.get("plan_id"));
  const [planes, setPlanes] = useState<ResumenPlan[]>([]);
  const [corridas, setCorridas] = useState<Corrida[]>([]);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [corridaId, setCorridaId] = useState("");
  const [cargando, setCargando] = useState(true);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [errorDetalle, setErrorDetalle] = useState("");
  const clave = useRef<string | null>(null);

  useEffect(() => {
    const control = new AbortController();
    let temporizador: ReturnType<typeof setTimeout>;
    async function actualizar() {
      try {
        const [p, c] = await Promise.all([listarPlanes(token, control.signal), listarCorridas(token, undefined, control.signal)]);
        if (control.signal.aborted) return;
        setPlanes(p); setCorridas(c);
      } catch (fallo) {
        if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudieron cargar los planes.");
      } finally {
        if (!control.signal.aborted) { setCargando(false); temporizador = setTimeout(actualizar, 5000); }
      }
    }
    void actualizar();
    return () => { control.abort(); clearTimeout(temporizador); };
  }, [token]);

  useEffect(() => {
    setPlan(null); setErrorDetalle("");
    if (!id) return;
    const control = new AbortController();
    setCargandoDetalle(true);
    obtenerPlan(token, id, control.signal).then(setPlan).catch(fallo => {
      if (!control.signal.aborted) setErrorDetalle(fallo instanceof Error ? fallo.message : "No se pudo abrir el plan.");
    }).finally(() => { if (!control.signal.aborted) setCargandoDetalle(false); });
    return () => control.abort();
  }, [id, token]);

  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault(); setGuardando(true); setError("");
    clave.current ??= `plan-${crypto.randomUUID()}`;
    try {
      const resultado = await crearPlan(token, Number(corridaId), clave.current);
      clave.current = null;
      setPlanes(actuales => [resultado, ...actuales.filter(p => p.id !== resultado.id)].slice(0, 50));
      router.push(`/planificacion?plan_id=${resultado.id}`);
    } catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo crear el plan."); }
    finally { setGuardando(false); }
  }

  return <>
    <EstadoPanel tono="info" titulo="Propuesta del escenario histórico" descripcion="Producción = pronóstico menos stock, con margen de seguridad cero. Los planes conservan sus versiones y no modifican el inventario. Pedidos y envío están pendientes del siguiente paso." accion={<Link href="/automatizaciones">Programar un plan automático</Link>} />
    {error && <div className="inline-error" role="alert">{error}</div>}
    <section className="card section-space">
      <h2>Planes guardados</h2>
      <TablaDatos filas={planes} cargando={cargando} idFila={p => p.id} columnas={[
        { clave: "id", encabezado: "Plan", celda: p => <Link href={`/planificacion?plan_id=${p.id}`}>Ver plan #{p.id}</Link> },
        { clave: "fecha", encabezado: "Fecha histórica", celda: p => p.fecha_objetivo },
        { clave: "corrida", encabezado: "Pronóstico de origen", celda: p => `Corrida #${p.corrida_id}` },
      ]} vacioDescripcion="Programa una propuesta automática o calcula un plan desde una corrida existente." pie="Últimos 50 planes. Los anteriores permanecen guardados y se pueden abrir por su enlace." />
      {perfil.rol === "ADMINISTRADOR" && <form className="form-grid section-space" onSubmit={guardar}>
        <label className="field">Calcular desde un pronóstico guardado<select required value={corridaId} disabled={guardando} onChange={e => { setCorridaId(e.target.value); clave.current = null; }}>
          <option value="">Elige una corrida</option>{corridas.map(c => <option key={c.id} value={c.id}>#{c.id} · {c.fecha_objetivo} · {c.version_modelo} · {c.tipo}</option>)}
        </select></label>
        <div className="field"><span>Se conserva cada cálculo anterior.</span><button className="button button-primary" disabled={guardando || !corridaId}>{guardando ? "Calculando…" : "Crear un nuevo plan"}</button></div>
      </form>}
    </section>
    {cargandoDetalle && <EstadoPanel titulo="Cargando plan" descripcion="Consultando las cantidades guardadas." />}
    {errorDetalle && <EstadoPanel tono="alerta" titulo="No se pudo abrir el plan" descripcion={errorDetalle} />}
    {plan && <section className="card section-space">
      <h2>Plan #{plan.id} · {plan.fecha_objetivo}</h2>
      <p>Corrida #{plan.corrida_id} · Modelo #{plan.trazas.modelo_id} · Stock leído {new Date(plan.stock_leido_en).toLocaleString("es-PE")}</p>
      <p><Link href={`/automatizaciones/ejecuciones/${plan.ejecucion_id}`}>Ver ejecución de origen</Link> · <Link href="/pronosticos">Consultar pronósticos</Link> · <Link href="/recetas">Consultar recetas</Link></p>
      {plan.avisos.length > 0 && <EstadoPanel tono="alerta" titulo="Datos que requieren revisión" descripcion={plan.avisos.join(" ")} />}
      <h3>Producción sugerida</h3><TablaDatos filas={plan.elementos} columnas={columnasProductos} idFila={e => e.id} vacioDescripcion="Ningún producto tiene todos los datos necesarios para calcular producción." />
      <h3>Necesidades de insumos{plan.omisiones.length > 0 ? " (parciales)" : ""}</h3><TablaDatos filas={plan.necesidades} columnas={columnasIngredientes} idFila={n => n.id} />
      {plan.omisiones.length > 0 && <><h3>Productos sin cálculo</h3><ul>{plan.omisiones.map(o => <li key={o.producto_id}>{o.producto}: {motivos[o.motivo] ?? o.motivo}</li>)}</ul></>}
      <details className="section-space"><summary>Ver recetas y lotes usados en este cálculo</summary>
        <h3>Recetas guardadas</h3>{plan.elementos.map(e => <div key={e.id}><strong>{e.producto} · versión {e.receta_version}</strong><ul>{plan.trazas.recetas[String(e.producto_id)].lineas.map(l => <li key={l.ingrediente_id}>{l.nombre}: {l.cantidad_por_unidad} {l.unidad_base} por unidad</li>)}</ul></div>)}
        <h3>Stock del {plan.trazas.stock.fecha}</h3>{plan.trazas.stock.items.map(i => <div key={`${i.tipo}-${i.item_id}`}><strong>{i.nombre}</strong>{i.lotes.length ? <ul>{i.lotes.map(l => <li key={l.lote_id}>{l.codigo_lote}: {l.saldo} {i.unidad} · {l.cuenta ? "Incluido" : "Excluido"} · {l.motivo}</li>)}</ul> : <p>Sin lotes registrados.</p>}</div>)}
      </details>
    </section>}
  </>;
}

export default function PlanificacionPage() {
  return <ProtectedShell titulo="Planificación" descripcion="Producción sugerida y faltantes de insumos, con sus datos de origen.">{contexto => <Suspense fallback={<p>Cargando planificación…</p>}><Contenido contexto={contexto} /></Suspense>}</ProtectedShell>;
}
