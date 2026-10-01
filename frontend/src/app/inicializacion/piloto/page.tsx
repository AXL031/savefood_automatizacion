"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { etiquetaDato } from "@/utils/etiquetas";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { listarEjecuciones, obtenerEjecucion } from "@/services/automatizaciones";
import { cargarCsvPiloto } from "@/services/inicializacion";
import { prepararModelo } from "@/services/pronosticos";
import type { EjecucionAutomatizacion } from "@/types/automatizacion";
import type { ResultadoCargaPiloto } from "@/types/inicializacion";

const MAX_CSV_BYTES = 25 * 1024 * 1024;

function CargaPiloto({ token, administrador }: { token: string; administrador: boolean }) {
  const [archivo, setArchivo] = useState<File | null>(null);
  const [resultado, setResultado] = useState<ResultadoCargaPiloto | null>(null);
  const [ejecucionId, setEjecucionId] = useState<number | null>(null);
  const [ejecucion, setEjecucion] = useState<EjecucionAutomatizacion | null>(null);
  const [cargando, setCargando] = useState(false);
  const [reintentando, setReintentando] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const control = new AbortController();
    listarEjecuciones(token, control.signal).then((datos) => {
      if (control.signal.aborted) return;
      const ultima = datos.find((item) => item.tipo === "PREPARAR_MODELO");
      if (ultima) setEjecucionId(ultima.id);
    }).catch((fallo: unknown) => {
      if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudo consultar la preparación.");
    });
    return () => control.abort();
  }, [token]);

  useEffect(() => {
    if (!ejecucionId) return;
    let activo = true;
    const consultar = () => {
      void obtenerEjecucion(token, String(ejecucionId)).then((dato) => {
        if (activo) { setEjecucion(dato); setError(""); }
        if (dato.estado === "COMPLETADA" || dato.estado === "FALLIDA") window.clearInterval(intervalo);
      }).catch((fallo: unknown) => {
        if (activo) setError(fallo instanceof Error ? fallo.message : "No se pudo consultar el entrenamiento.");
      });
    };
    consultar();
    const intervalo = window.setInterval(consultar, 5000);
    return () => { activo = false; window.clearInterval(intervalo); };
  }, [token, ejecucionId]);

  async function subir(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (!archivo) return;
    if (archivo.size > MAX_CSV_BYTES) {
      setError("El CSV supera el límite de 25 MB.");
      return;
    }
    setCargando(true); setError(""); setResultado(null); setEjecucion(null);
    try {
      const dato = await cargarCsvPiloto(token, archivo);
      setResultado(dato);
      setEjecucionId(dato.ejecucion_id);
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo cargar el CSV.");
    } finally { setCargando(false); }
  }

  async function reintentar() {
    const version = resultado?.version_modelo ?? (typeof ejecucion?.datos_entrada.version_modelo === "string" ? ejecucion.datos_entrada.version_modelo : null);
    if (!version) return;
    setReintentando(true); setError("");
    try {
      const dato = await prepararModelo(token, version, `reintento-${version}-${crypto.randomUUID()}`);
      setEjecucion(null);
      setEjecucionId(dato.ejecucion_id);
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo reintentar el entrenamiento.");
    } finally { setReintentando(false); }
  }

  return <>
    {!administrador && <EstadoPanel titulo="Solo para administradores" descripcion="La carga de ventas requiere una cuenta de Administrador." />}
    {administrador && <section className="card">
      <div className="section-heading"><div><h2>Cargar ventas del piloto bakery</h2><p>Selecciona el CSV original con columnas date, article y Quantity. El catálogo curado se agrega automáticamente.</p></div></div>
      <form className="form-grid" onSubmit={(evento) => void subir(evento)}>
        <label className="field field-full">Archivo CSV
          <input type="file" accept=".csv,text/csv" required onChange={(evento) => { setArchivo(evento.target.files?.[0] ?? null); setError(""); }} />
          <small>Máximo 25 MB. Repetir el mismo archivo no duplica ventas.</small>
        </label>
        <div className="form-actions field-full"><button className="button-primary" disabled={!archivo || cargando}>{cargando ? "Validando y cargando…" : "Cargar CSV y preparar modelo"}</button></div>
      </form>
    </section>}
    {error && <div className="inline-error section-space" role="alert">{error}</div>}
    {resultado && <section className="card section-space" aria-live="polite">
      <h2>{resultado.repetida ? "Archivo ya cargado" : "Carga confirmada"}</h2>
      <div className="fact"><span>Productos del catálogo</span><strong>{resultado.productos}</strong></div>
      <div className="fact"><span>Líneas aceptadas</span><strong>{resultado.filas_aceptadas}</strong></div>
      <div className="fact"><span>Ventas diarias nuevas</span><strong>{resultado.ventas_diarias_creadas}</strong></div>
      <div className="fact"><span>Líneas negativas excluidas en esta carga</span><strong>{resultado.filas_negativas_excluidas}</strong></div>
      <div className="fact"><span>Versión del modelo</span><strong>{resultado.version_modelo}</strong></div>
      <div className="fact"><span>Preparación</span><strong>{etiquetaDato(ejecucion?.estado ?? resultado.estado_ejecucion)}</strong></div>
      {ejecucion?.mensaje_error && <p className="error-text">{ejecucion.mensaje_error}</p>}
      <p className="helper-text"><Link href={`/automatizaciones/ejecuciones/${ejecucionId}`}>Ver ejecución #{ejecucionId}</Link> · <Link href="/pronosticos">Ver modelos</Link> · <Link href="/panel">Ver panel histórico</Link></p>
      {ejecucion?.estado === "FALLIDA" && <button className="button-secondary" disabled={reintentando} onClick={() => void reintentar()}>{reintentando ? "Solicitando…" : "Reintentar preparación sin subir el CSV"}</button>}
    </section>}
    {!resultado && ejecucion && <section className="card section-space" aria-live="polite">
      <h2>Preparación anterior</h2>
      <p>Estado: <strong>{etiquetaDato(ejecucion.estado)}</strong>. Puedes consultar el modelo sin volver a subir el archivo.</p>
      {ejecucion.mensaje_error && <p className="error-text">{ejecucion.mensaje_error}</p>}
      <p className="helper-text"><Link href={`/automatizaciones/ejecuciones/${ejecucion.id}`}>Ver ejecución #{ejecucion.id}</Link> · <Link href="/pronosticos">Ver modelos</Link> · <Link href="/panel">Ver panel histórico</Link></p>
      {ejecucion.estado === "FALLIDA" && <button className="button-secondary" disabled={reintentando} onClick={() => void reintentar()}>{reintentando ? "Solicitando…" : "Reintentar preparación sin subir el CSV"}</button>}
    </section>}
    <section className="card section-space"><h2>Alcance de esta carga</h2><p>Este acceso carga el CSV del piloto y solicita el modelo. La carga completa con recetas y stock está disponible en Datos iniciales. Este acceso rápido prepara el piloto de ventas.</p></section>
  </>;
}

export default function InicializacionPage() {
  return <ProtectedShell titulo="Cargar CSV piloto" descripcion="Carga las ventas históricas y prepara el modelo desde FoodSave.">{({ token, perfil }) => <CargaPiloto token={token} administrador={perfil.rol === "ADMINISTRADOR"} />}</ProtectedShell>;
}
