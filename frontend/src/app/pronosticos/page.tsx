"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState, type FormEvent } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { listarCorridas, listarModelos, obtenerCorrida, prepararModelo } from "@/services/pronosticos";
import type { Corrida, Modelo } from "@/types/pronostico";

function Contenido({ token, administrador }: { token: string; administrador: boolean }) {
  const parametros = useSearchParams();
  const corridaSolicitada = Number(parametros.get("corrida_id"));
  const [modelos, setModelos] = useState<Modelo[]>([]);
  const [corridas, setCorridas] = useState<Corrida[]>([]);
  const [modeloId, setModeloId] = useState<number | undefined>();
  const [detalle, setDetalle] = useState<Corrida | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [version, setVersion] = useState("");
  const [preparando, setPreparando] = useState(false);

  useEffect(() => {
    const control = new AbortController();
    listarModelos(token, control.signal).then((datos) => {
      if (control.signal.aborted) return;
      setModelos(datos);
      setModeloId((actual) => actual ?? datos[0]?.id);
      setCargando(false);
    }).catch((fallo: unknown) => { if (!control.signal.aborted) { setError(fallo instanceof Error ? fallo.message : "No se pudo consultar el modelo."); setCargando(false); } });
    return () => control.abort();
  }, [token]);

  useEffect(() => {
    if (!modeloId) { setCorridas([]); return; }
    const control = new AbortController();
    listarCorridas(token, modeloId, control.signal).then((datos) => {
      if (!control.signal.aborted) { setCorridas(datos); setError(""); }
    }).catch((fallo: unknown) => { if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudieron consultar las corridas."); });
    return () => control.abort();
  }, [token, modeloId]);

  useEffect(() => {
    if (!Number.isSafeInteger(corridaSolicitada) || corridaSolicitada <= 0) return;
    const control = new AbortController();
    obtenerCorrida(token, corridaSolicitada, control.signal).then((corrida) => {
      if (!control.signal.aborted) { setDetalle(corrida); setModeloId(corrida.modelo_id); }
    }).catch((fallo: unknown) => {
      if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudo abrir la corrida.");
    });
    return () => control.abort();
  }, [token, corridaSolicitada]);

  async function seleccionar(corrida: Corrida) {
    setError("");
    try { setDetalle(await obtenerCorrida(token, corrida.id)); }
    catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo abrir la corrida."); }
  }

  async function entrenar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setError(""); setMensaje(""); setPreparando(true);
    try {
      const resultado = await prepararModelo(token, version, `modelo-${version}`);
      setMensaje(`Preparación encolada como ejecución #${resultado.ejecucion_id}. Consulta su estado en Automatizaciones.`);
    } catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo solicitar el entrenamiento."); }
    finally { setPreparando(false); }
  }

  const modelo = modelos.find((item) => item.id === modeloId);
  return <>
    {error && <div className="inline-error" role="alert">{error}</div>}
    {mensaje && <div className="inline-success" role="status">{mensaje}</div>}
    {cargando ? <p role="status">Cargando modelos…</p> : modelos.length === 0 ?
      <EstadoPanel titulo="Sin modelo preparado" descripcion="Carga ventas y solicita el entrenamiento para crear la primera versión demostrativa." /> : <>
      <section className="card">
        <div className="section-heading"><div><h2>Modelo y partición</h2><p>Comprobación histórica exploratoria; no acredita rendimiento comercial.</p></div>
          <label className="filter-label">Versión<select value={modeloId ?? ""} onChange={(e) => { setModeloId(Number(e.target.value)); setDetalle(null); }}>
            {modelos.map((item) => <option key={item.id} value={item.id}>{item.version_modelo}</option>)}
          </select></label></div>
        {modelo && <div className="pronostico-meta">
          <div><span>Estado</span><strong>{modelo.estado}</strong></div>
          <div><span>Corte de entrenamiento</span><strong>{modelo.fecha_corte_entrenamiento}</strong></div>
          <div><span>Entrenamiento</span><strong>{modelo.particion.inicio_entrenamiento} a {modelo.particion.fin_entrenamiento}</strong></div>
          <div><span>Validación</span><strong>{modelo.particion.inicio_validacion} a {modelo.particion.fin_validacion}</strong></div>
          <div><span>Prueba reservada</span><strong>{modelo.particion.inicio_prueba} a {modelo.particion.fin_prueba}</strong></div>
          <div><span>Huella CBM</span><strong className="mono-corto" title={modelo.sha256}>{modelo.sha256.slice(0, 16)}…</strong></div>
        </div>}
        {modelo && <p className="helper-text"><Link href={`/panel?modelo_id=${modelo.id}`}>Ver evaluación histórica de esta versión →</Link></p>}
      </section>
      <section className="card section-space">
        <h2>Corridas persistidas</h2>
        {corridas.length ? <div className="table-wrap"><table><thead><tr><th>Fecha histórica</th><th>Tipo</th><th>Estado</th><th>Versión</th><th>Ejecución</th><th></th></tr></thead><tbody>
          {corridas.map((item) => <tr key={item.id}><td>{item.fecha_objetivo}</td><td>{item.tipo}</td><td>{item.estado}</td><td>{item.version_modelo}</td><td><Link href={`/automatizaciones/ejecuciones/${item.ejecucion_id}`}>#{item.ejecucion_id}</Link></td><td><button className="button-secondary" onClick={() => void seleccionar(item)}>Ver #{item.id}</button></td></tr>)}
        </tbody></table></div> : <EstadoPanel titulo="Sin corridas" descripcion="Aún no se ha persistido una inferencia para este modelo." />}
      </section>
      {detalle && <section className="card section-space"><div className="section-heading"><div><h2>Corrida #{detalle.id} · {detalle.fecha_objetivo}</h2><p>Los valores no disponibles permanecen sin cantidad.</p></div><Link href={`/automatizaciones/ejecuciones/${detalle.ejecucion_id}`}>Ver ejecución</Link></div>
        <div className="table-wrap"><table><thead><tr><th>Producto</th><th>Pronóstico</th><th>Estado</th></tr></thead><tbody>{detalle.pronosticos?.map((item) => <tr key={item.id}><td>{item.producto}</td><td>{item.cantidad_pronosticada ?? "Desconocido"}</td><td>{item.estado}</td></tr>)}</tbody></table></div>
      </section>}
    </>}
    {administrador && <section className="card section-space"><h2>Preparar otra versión</h2><p>El worker entrena con ventas ya guardadas en PostgreSQL. La solicitud no vuelve a importar archivos.</p>
      <form className="form-grid" onSubmit={(evento) => void entrenar(evento)}><label className="field">Versión del modelo<input value={version} onChange={(e) => setVersion(e.target.value)} placeholder="demo-catboost-1" pattern="[A-Za-z0-9][A-Za-z0-9._-]*" maxLength={80} required /></label><div className="form-actions"><button className="button-primary" disabled={preparando}>{preparando ? "Solicitando…" : "Solicitar entrenamiento"}</button></div></form>
    </section>}
  </>;
}

export default function PronosticosPage() {
  return <ProtectedShell titulo="Pronósticos" descripcion="Versiones del modelo y corridas guardadas para fechas históricas.">{({ token, perfil }) => <Suspense fallback={<p role="status">Cargando pronósticos…</p>}><Contenido token={token} administrador={perfil.rol === "ADMINISTRADOR"} /></Suspense>}</ProtectedShell>;
}
