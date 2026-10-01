"use client";
import { TablaPaginada } from "@/components/tables/TablaPaginada";


import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { BotonEnviar } from "@/components/forms/BotonEnviar";
import { CampoSelect } from "@/components/forms/CampoSelect";
import { CampoTexto } from "@/components/forms/CampoTexto";
import { PanelDetalle } from "@/components/ui/PanelDetalle";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { completarNecesidades, generarPlan, listarPlanes, obtenerPlan } from "@/services/planificacion";
import { listarCorridas } from "@/services/pronosticos";
import type { Plan, ResumenPlan } from "@/types/planificacion";
import type { Corrida } from "@/types/pronostico";
import { etiquetaDato } from "@/utils/etiquetas";
import { cantidadVisible } from "@/utils/unidades";

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
      <h2>Crear plan con un pronóstico guardado</h2><form onSubmit={generar}>
        <div className="form-grid">
          <CampoSelect id="corrida-plan" etiqueta="Cálculo de pronóstico de origen" valor={corrida} deshabilitado={guardando}
            opciones={corridas.map((c) => ({ valor: String(c.id), texto: `#${c.id} · ${c.fecha_objetivo} · ${c.version_modelo}` }))}
            onCambio={(valor) => { setCorrida(valor); setClave(nuevaClave()); }} />
          <details><summary>Identificador del cálculo (automático)</summary><CampoTexto id="clave-plan" etiqueta="Clave para evitar duplicados" valor={clave} deshabilitado={guardando} onCambio={setClave}
            ayuda="Repetir conserva el resultado. Usa Preparar nuevo cálculo si cambió stock o receta." /></details>
        </div>
        <div className="section-heading section-space"><BotonEnviar enviando={guardando} textoEnviando="Guardando…">Guardar propuesta</BotonEnviar>
          <button className="button-secondary" type="button" disabled={guardando} onClick={() => setClave(nuevaClave())}>Preparar nuevo cálculo</button></div>
      </form>
    </section>}
    {!cargando && planes.length === 0 && !error && <EstadoPanel titulo="Todavía no hay planes" descripcion="Programa una propuesta o genera un plan desde una corrida de pronóstico existente." />}
    {planes.length > 0 && <section className="card section-space"><h2>Planes guardados</h2><TablaPaginada><thead><tr><th>Plan</th><th>Fecha histórica</th><th>Pronóstico</th><th>Necesidades</th><th>Detalle</th></tr></thead><tbody>{planes.map((p) => <tr key={p.id}><td>#{p.id}</td><td>{p.fecha_objetivo}</td><td>#{p.corrida_id}</td><td>{etiquetaDato(p.necesidades_estado)}</td><td><button type="button" className="button-link" onClick={() => { setPlan(null); setSeleccionado(String(p.id)); }}>Ver plan #{p.id}</button></td></tr>)}</tbody></TablaPaginada><p className="helper-text">Últimos 50 planes guardados.</p></section>}
    {seleccionado && <PanelDetalle titulo={`Plan #${seleccionado}`} onCerrar={() => { setSeleccionado(""); setPlan(null); }} ocupado={guardando}>
    {error && <EstadoPanel tono="alerta" titulo="Revisa el plan" descripcion={error} />}
    {!plan && !error && <EstadoPanel titulo="Abriendo plan" descripcion="Leyendo el cálculo conservado…" />}
    {plan && <section className="card section-space">
      <h2>Plan #{plan.id} · escenario {plan.fecha_objetivo}</h2>
      <p>Pedidos: {etiquetaDato(plan.pedidos_estado)} · <Link href={`/compras?plan_id=${plan.id}`}>Revisar pedidos de este plan →</Link></p>
      <h3>Ingredientes necesarios · {etiquetaDato(plan.necesidades_estado)}</h3>
      {plan.necesidades_estado === "PENDIENTE_M03" && perfil.rol === "ADMINISTRADOR" && <button type="button" className="button-secondary" disabled={guardando} onClick={async () => {
        setGuardando(true); setError("");
        try { const actualizado = await completarNecesidades(token, plan.id); setPlan(actualizado); setPlanes((actual) => actual.map((p) => p.id === actualizado.id ? actualizado : p)); }
        catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudieron completar las necesidades."); }
        finally { setGuardando(false); }
      }}>Completar necesidades del plan anterior</button>}
      {plan.necesidades_estado === "INCOMPLETAS" && <EstadoPanel tono="alerta" titulo="Necesidades incompletas" descripcion="Las cantidades son subtotales de los productos calculables. Hay producción o stock desconocido; este resultado no permite generar compras automáticas." />}
      {plan.necesidades_meta && <p>Lectura de ingredientes: {new Date(plan.necesidades_meta.stock_leido_en).toLocaleString("es")} · {plan.necesidades_meta.version}{plan.necesidades_meta.vigencia_desconocida ? " · Hay lotes con vigencia desconocida" : ""}</p>}
      {plan.necesidades_meta?.productos_excluidos.map((p) => <p key={p.producto_id}>{p.nombre}: {ETIQUETA[p.estado] ?? p.estado}; sin aporte calculable.</p>)}
      {plan.necesidades.length > 0 && <TablaPaginada><thead><tr><th>Ingrediente</th><th>Necesario</th><th>En inventario</th><th>Falta comprar</th></tr></thead><tbody>{plan.necesidades.map((n) => <tr key={n.ingrediente_id}><td>{n.stock.nombre}</td><td>{cantidadVisible(n.cantidad_necesaria, n.unidad_base)}</td><td>{cantidadVisible(n.stock_disponible, n.unidad_base)}</td><td>{cantidadVisible(n.faltante, n.unidad_base)}</td></tr>)}</tbody></TablaPaginada>}
      {plan.necesidades.map((n) => <details key={n.ingrediente_id}><summary>Aportes y lotes de {n.stock.nombre}</summary><ul>{n.aportes.map((a) => <li key={a.producto_id}>Producto #{a.producto_id} · receta #{a.receta_id} versión {a.version_receta}: {a.cantidad_producir} × {a.cantidad_por_unidad} = {a.aporte} {n.unidad_base}</li>)}</ul><ul>{n.stock.lotes.map((l) => <li key={l.lote_id}>{l.codigo_lote}: {l.saldo} {n.unidad_base} · {l.cuenta ? "incluido" : "excluido"} · {l.motivo}</li>)}</ul></details>)}
      <p>Modelo {plan.origen_pronostico.version_modelo} · cálculo {plan.version_calculo} · lectura de stock {new Date(plan.stock_leido_en).toLocaleString("es")}</p>
      <p><Link href={`/automatizaciones/ejecuciones/${plan.ejecucion_id}`}>Ver ejecución de origen</Link> · <Link href="/pronosticos">Ver pronósticos</Link></p>
      <TablaPaginada><thead><tr><th scope="col">Producto</th><th scope="col">Pronóstico</th><th scope="col">Stock disponible</th><th scope="col">Producción sugerida</th><th scope="col">Resultado</th></tr></thead>
        <tbody>{plan.elementos.map((e) => <tr key={e.producto_id}><td>{e.stock.nombre}</td><td>{unidades(e.cantidad_pronosticada)}</td><td>{unidades(e.stock_disponible)}</td><td>{unidades(e.cantidad_producir)}</td><td>{ETIQUETA[e.estado]}</td></tr>)}</tbody>
      </TablaPaginada>
      {plan.elementos.map((e) => <details key={e.producto_id}><summary>Trazas de {e.stock.nombre}</summary>
        {e.avisos.length > 0 && <p>{e.avisos.map((a) => ETIQUETA[a] ?? a).join(" · ")}</p>}
        <p>Pronóstico #{e.pronostico_id} · receta {e.receta ? `#${e.receta.receta_id}, versión ${e.receta.version}` : "no disponible"}.</p>
        {e.receta && <ul>{e.receta.lineas.map((l) => <li key={l.ingrediente_id}>{l.nombre}: {l.cantidad_por_unidad} {l.unidad_base} por unidad</li>)}</ul>}
        {e.stock.lotes.length === 0 ? <p>No había lotes registrados.</p> : <ul>{e.stock.lotes.map((l) => <li key={l.lote_id}>{l.codigo_lote}: {l.saldo} u. · {l.cuenta ? "incluido" : "excluido"} · {l.motivo}. Caducidad: {l.fecha_caducidad ?? "desconocida"}; límite de venta: {l.fecha_limite_venta ?? "desconocido"}.</li>)}</ul>}
      </details>)}
    </section>}
    </PanelDetalle>}
  </>;
}

export default function PaginaPlanificacion() {
    return <ProtectedShell titulo="Planes y faltantes" descripcion="Cuánto producir y qué ingredientes hace falta comprar.">
    {(contexto) => <Contenido contexto={contexto} />}
  </ProtectedShell>;
}
