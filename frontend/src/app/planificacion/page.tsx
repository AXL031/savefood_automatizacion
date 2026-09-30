"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { BotonEnviar } from "@/components/forms/BotonEnviar";
import { CampoSelect } from "@/components/forms/CampoSelect";
import { CampoTexto } from "@/components/forms/CampoTexto";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { completarNecesidades, generarPlan, listarPlanes, obtenerPlan } from "@/services/planificacion";
import { listarCorridas } from "@/services/pronosticos";
import type { Plan, ResumenPlan } from "@/types/planificacion";
import type { Corrida } from "@/types/pronostico";

const ETIQUETA: Record<string, string> = {
  CALCULADO: "Calculado", HISTORIAL_INSUFICIENTE: "Historial insuficiente",
  PRODUCTO_NO_CUBIERTO: "Producto fuera del modelo", SIN_RECETA: "Sin receta",
  STOCK_DESCONOCIDO: "Stock desconocido", VIGENCIA_STOCK_DESCONOCIDA: "Vigencia del stock desconocida",
  LOTES_EXCLUIDOS: "Lotes excluidos del disponible",
};
function nuevaClave() { return `plan-${crypto.randomUUID()}`; }
const unidades = (valor: number | null) => valor === null ? "No disponible" : `${valor} u.`;

function Contenido({ contexto }: { contexto: ContextoSesion }) {
  const { token, perfil } = contexto;
  const [planes, setPlanes] = useState<ResumenPlan[]>([]);
  const [corridas, setCorridas] = useState<Corrida[]>([]);
  const [corrida, setCorrida] = useState("");
  const [clave, setClave] = useState("");
  const [seleccionado, setSeleccionado] = useState("");
  const [plan, setPlan] = useState<Plan | null>(null);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    const control = new AbortController();
    setCargando(true); setError("");
    Promise.all([listarPlanes(token, control.signal), listarCorridas(token, undefined, control.signal)])
      .then(([lista, pronosticos]) => {
        if (control.signal.aborted) return;
        setPlanes(lista); setCorridas(pronosticos);
        setSeleccionado((actual) => actual || (lista[0] ? String(lista[0].id) : ""));
        setCorrida((actual) => actual || (pronosticos[0] ? String(pronosticos[0].id) : ""));
        setClave((actual) => actual || nuevaClave());
      })
      .catch((fallo: unknown) => { if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudieron consultar los planes."); })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token, revision]);

  useEffect(() => {
    if (!seleccionado) return;
    const control = new AbortController();
    setPlan(null); setError("");
    obtenerPlan(token, Number(seleccionado), control.signal).then((resultado) => {
      if (!control.signal.aborted) setPlan(resultado);
    }).catch((fallo: unknown) => { if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudo abrir el plan."); });
    return () => control.abort();
  }, [token, seleccionado, revision]);

  async function generar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault(); setGuardando(true); setError("");
    try {
      const resultado = await generarPlan(token, Number(corrida), clave);
      setPlan(resultado); setSeleccionado(String(resultado.id));
      setPlanes((actual) => [resultado, ...actual.filter((p) => p.id !== resultado.id)]);
      // Mantener clave: repetir recupera este resultado. Recalcular es explícito.
    } catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo generar el plan."); }
    finally { setGuardando(false); }
  }

  return <>
    <EstadoPanel tono="info" titulo="Propuesta de producción · margen de seguridad 0"
      descripcion="El plan conserva pronóstico, receta, necesidades de ingredientes y stock leídos. Generarlo no modifica inventario. Consulta sus pedidos en Compras." />
    <div className="section-heading section-space"><Link href="/automatizaciones">Programar propuesta automática</Link><button className="button-secondary" type="button" disabled={cargando || guardando} onClick={() => setRevision((r) => r + 1)}>Actualizar</button></div>
    {error && <EstadoPanel tono="alerta" titulo="No se pudo completar la operación" descripcion={error} />}
    {cargando && <EstadoPanel titulo="Consultando planes" descripcion="Cargando resultados persistidos…" />}
    {!cargando && perfil.rol === "ADMINISTRADOR" && corridas.length > 0 && <section className="card section-space">
      <h2>Plan desde una corrida existente</h2><form onSubmit={generar}>
        <div className="form-grid">
          <CampoSelect id="corrida-plan" etiqueta="Corrida de pronóstico" valor={corrida} deshabilitado={guardando}
            opciones={corridas.map((c) => ({ valor: String(c.id), texto: `#${c.id} · ${c.fecha_objetivo} · ${c.version_modelo}` }))}
            onCambio={(valor) => { setCorrida(valor); setClave(nuevaClave()); }} />
          <CampoTexto id="clave-plan" etiqueta="Clave de operación" valor={clave} deshabilitado={guardando} onCambio={setClave}
            ayuda="Repetir la clave conserva el resultado; si cambió stock o receta, prepara un nuevo cálculo." />
        </div>
        <div className="section-heading section-space"><BotonEnviar enviando={guardando} textoEnviando="Guardando…">Guardar propuesta</BotonEnviar>
          <button className="button-secondary" type="button" disabled={guardando} onClick={() => setClave(nuevaClave())}>Preparar nuevo cálculo</button></div>
      </form>
    </section>}
    {!cargando && planes.length === 0 && !error && <EstadoPanel titulo="Todavía no hay planes" descripcion="Programa una propuesta o genera un plan desde una corrida de pronóstico existente." />}
    {planes.length > 0 && <CampoSelect id="plan-guardado" etiqueta="Plan guardado" valor={seleccionado}
      opciones={planes.map((p) => ({ valor: String(p.id), texto: `#${p.id} · ${p.fecha_objetivo} · corrida #${p.corrida_id}` }))} onCambio={setSeleccionado} />}
    {seleccionado && !plan && !error && <EstadoPanel titulo="Abriendo plan" descripcion="Leyendo el cálculo conservado…" />}
    {plan && <section className="card section-space">
      <h2>Plan #{plan.id} · escenario {plan.fecha_objetivo}</h2>
      <p>Compras: {plan.pedidos_estado} · <Link href={`/compras?plan_id=${plan.id}`}>Ver pedidos y faltantes de este plan</Link></p>
      <h3>Necesidades de ingredientes · {plan.necesidades_estado}</h3>
      {plan.necesidades_estado === "PENDIENTE_M03" && perfil.rol === "ADMINISTRADOR" && <button type="button" className="button-secondary" disabled={guardando} onClick={async () => {
        setGuardando(true); setError("");
        try { const actualizado = await completarNecesidades(token, plan.id); setPlan(actualizado); setPlanes((actual) => actual.map((p) => p.id === actualizado.id ? actualizado : p)); }
        catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudieron completar las necesidades."); }
        finally { setGuardando(false); }
      }}>Completar necesidades del plan anterior</button>}
      {plan.necesidades_estado === "INCOMPLETAS" && <EstadoPanel tono="alerta" titulo="Necesidades incompletas" descripcion="Las cantidades son subtotales de los productos calculables. Hay producción o stock desconocido; este resultado no permite generar compras automáticas." />}
      {plan.necesidades_meta && <p>Lectura de ingredientes: {new Date(plan.necesidades_meta.stock_leido_en).toLocaleString("es")} · {plan.necesidades_meta.version}{plan.necesidades_meta.vigencia_desconocida ? " · Hay lotes con vigencia desconocida" : ""}</p>}
      {plan.necesidades_meta?.productos_excluidos.map((p) => <p key={p.producto_id}>{p.nombre}: {ETIQUETA[p.estado] ?? p.estado}; sin aporte calculable.</p>)}
      {plan.necesidades.length > 0 && <div className="table-wrap"><table><thead><tr><th>Ingrediente</th><th>Unidad</th><th>Necesidad</th><th>Disponible</th><th>Faltante</th></tr></thead><tbody>{plan.necesidades.map((n) => <tr key={n.ingrediente_id}><td>{n.stock.nombre}</td><td>{n.unidad_base}</td><td>{n.cantidad_necesaria}</td><td>{n.stock_disponible ?? "Desconocido"}</td><td>{n.faltante ?? "No calculable"}</td></tr>)}</tbody></table></div>}
      {plan.necesidades.map((n) => <details key={n.ingrediente_id}><summary>Aportes y lotes de {n.stock.nombre}</summary><ul>{n.aportes.map((a) => <li key={a.producto_id}>Producto #{a.producto_id} · receta #{a.receta_id} versión {a.version_receta}: {a.cantidad_producir} × {a.cantidad_por_unidad} = {a.aporte} {n.unidad_base}</li>)}</ul><ul>{n.stock.lotes.map((l) => <li key={l.lote_id}>{l.codigo_lote}: {l.saldo} {n.unidad_base} · {l.cuenta ? "incluido" : "excluido"} · {l.motivo}</li>)}</ul></details>)}
      <p>Modelo {plan.origen_pronostico.version_modelo} · cálculo {plan.version_calculo} · lectura de stock {new Date(plan.stock_leido_en).toLocaleString("es")}</p>
      <p><Link href={`/automatizaciones/ejecuciones/${plan.ejecucion_id}`}>Ver ejecución de origen</Link> · <Link href="/pronosticos">Ver pronósticos</Link></p>
      <div className="table-wrap"><table><thead><tr><th scope="col">Producto</th><th scope="col">Pronóstico</th><th scope="col">Stock disponible</th><th scope="col">Producción sugerida</th><th scope="col">Resultado</th></tr></thead>
        <tbody>{plan.elementos.map((e) => <tr key={e.producto_id}><td>{e.stock.nombre}</td><td>{unidades(e.cantidad_pronosticada)}</td><td>{unidades(e.stock_disponible)}</td><td>{unidades(e.cantidad_producir)}</td><td>{ETIQUETA[e.estado]}</td></tr>)}</tbody>
      </table></div>
      {plan.elementos.map((e) => <details key={e.producto_id}><summary>Trazas de {e.stock.nombre}</summary>
        {e.avisos.length > 0 && <p>{e.avisos.map((a) => ETIQUETA[a] ?? a).join(" · ")}</p>}
        <p>Pronóstico #{e.pronostico_id} · receta {e.receta ? `#${e.receta.receta_id}, versión ${e.receta.version}` : "no disponible"}.</p>
        {e.receta && <ul>{e.receta.lineas.map((l) => <li key={l.ingrediente_id}>{l.nombre}: {l.cantidad_por_unidad} {l.unidad_base} por unidad</li>)}</ul>}
        {e.stock.lotes.length === 0 ? <p>No había lotes registrados.</p> : <ul>{e.stock.lotes.map((l) => <li key={l.lote_id}>{l.codigo_lote}: {l.saldo} u. · {l.cuenta ? "incluido" : "excluido"} · {l.motivo}. Caducidad: {l.fecha_caducidad ?? "desconocida"}; límite de venta: {l.fecha_limite_venta ?? "desconocido"}.</li>)}</ul>}
      </details>)}
    </section>}
  </>;
}

export default function PaginaPlanificacion() {
  return <ProtectedShell titulo="Planificación" descripcion="Producción sugerida y trazas del escenario histórico.">
    {(contexto) => <Contenido contexto={contexto} />}
  </ProtectedShell>;
}
