"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { PasosAsistente } from "@/components/ui/PasosAsistente";
import { listarProductos } from "@/services/catalogo";
import { listarModelos } from "@/services/pronosticos";
import { obtenerEstadoInicial } from "@/services/inicializacion";
import { leerConfiguracionFlujo, guardarConfiguracionFlujo, comprobarFlujo, programarFlujo } from "@/services/flujo";
import type { ConfiguracionFlujo, DiagnosticoFlujo } from "@/types/flujo";
import type { Producto } from "@/types/catalogo";
import type { Modelo } from "@/types/pronostico";
import { formatearEscenario } from "@/utils/fechas";
const pasos = [{ titulo: "Productos", detalle: "Modelo y catálogo" }, { titulo: "Horario", detalle: "Cuándo y qué día" }, { titulo: "Preparación", detalle: "Recetas, stock y ofertas" }, { titulo: "Envío", detalle: "Revisión o automático" }, { titulo: "Resumen", detalle: "Guardar y programar" }];
export function horarioNegocio(fecha: Date, zona: string) {
  const partes = new Intl.DateTimeFormat("en-CA", { timeZone: zona, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(fecha);
  const parte = (tipo: string) => partes.find((p) => p.type === tipo)?.value;
  return `${parte("year")}-${parte("month")}-${parte("day")}T${parte("hour")}:${parte("minute")}`;
}
function avanzarDias(valor: string, dias: number) {
  if (!valor) return "";
  const fecha = new Date(`${valor.slice(0, 10)}T12:00:00Z`);
  fecha.setUTCDate(fecha.getUTCDate() + dias);
  return fecha.toISOString().slice(0, 10) + valor.slice(10);
}
export function AsistenteFlujo({ token, zona, admin, alProgramar }: { token: string; zona: string; admin: boolean; alProgramar: () => void }) {
  const router = useRouter();
  const [config, setConfig] = useState<ConfiguracionFlujo>({ producto_ids: [], modelo_id: null, fecha_objetivo_demo: "", hora_simulada: "10:00", primera_ejecucion_local: "", dias: 1, modo_envio_pedidos: "REQUIERE_APROBACION" });
  const [productos, setProductos] = useState<Producto[]>([]), [modelos, setModelos] = useState<Modelo[]>([]);
  const [busqueda, setBusqueda] = useState("");
  const [paso, setPaso] = useState(0), [diagnostico, setDiagnostico] = useState<DiagnosticoFlujo | null>(null);
  const [confirmado, setConfirmado] = useState(false), [ocupado, setOcupado] = useState(false), [cargando, setCargando] = useState(true);
  const [error, setError] = useState(""), [mensaje, setMensaje] = useState(""); const clave = useRef("");
  const contenidoPaso = useRef<HTMLFieldSetElement>(null);
  useEffect(() => { if (!cargando) contenidoPaso.current?.focus({ preventScroll: false }); }, [paso, cargando]);
  useEffect(() => {
    const control = new AbortController(); clave.current = `flujo-${crypto.randomUUID()}`;
    Promise.all([leerConfiguracionFlujo(token, control.signal), listarProductos(token, {}, control.signal), listarModelos(token, control.signal), obtenerEstadoInicial(token, control.signal)])
      .then(([guardada, catalogo, versiones, estado]) => {
        if (control.signal.aborted) return;
        const activos = catalogo.filter((p) => p.activo);
        setProductos(activos); setModelos(versiones);
        if (guardada) setPaso(Math.min(2, Math.max(0, Number(sessionStorage.getItem("foodsave:flujo-paso")) || 0)));
        const proxima = horarioNegocio(new Date(Date.now() + 5 * 60_000), zona);
        setConfig((c) => guardada ? { ...guardada, primera_ejecucion_local: guardada.primera_ejecucion_local > horarioNegocio(new Date(), zona) ? guardada.primera_ejecucion_local : proxima } : { ...c, producto_ids: activos.map((p) => p.id), primera_ejecucion_local: proxima, modelo_id: versiones[0]?.id ?? null, fecha_objetivo_demo: estado.fecha_objetivo_demo ?? versiones[0]?.particion.inicio_prueba ?? proxima.slice(0, 10) });
      }).catch((e: unknown) => { if (!control.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo cargar la configuración."); })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token, zona]);
  useEffect(() => { if (!cargando) sessionStorage.setItem("foodsave:flujo-paso", String(paso)); }, [paso, cargando]);
  function cambiar(cambio: Partial<ConfiguracionFlujo>) { setConfig((c) => ({ ...c, ...cambio })); setDiagnostico(null); setConfirmado(false); setMensaje(""); clave.current = `flujo-${crypto.randomUUID()}`; }
  async function comprobar() {
    setOcupado(true); setError("");
    try { const d = await comprobarFlujo(token, config); setDiagnostico(d); return d; }
    catch (e) { setError(e instanceof Error ? e.message : "No se pudo comprobar el flujo."); return null; }
    finally { setOcupado(false); }
  }
  async function continuar() {
    setError("");
    if (paso === 0 && (!config.producto_ids.length || !config.modelo_id)) { setError("Elige productos y un modelo preparado."); return; }
    if (paso === 1 && (!config.primera_ejecucion_local || !config.fecha_objetivo_demo || !config.hora_simulada || config.dias < 1 || config.dias > 31)) { setError("Completa las fechas y el número de días (1 a 31)."); return; }
    if (paso === 1) { await comprobar(); setPaso(2); return; }
    if (paso === 2 && !diagnostico?.listo) { setError("Corrige lo pendiente y pulsa Comprobar de nuevo."); return; }
    if (paso === 3 && config.modo_envio_pedidos === "AUTOMATICO" && !confirmado) { setError("Confirma el envío automático al chat verificado."); return; }
    setPaso((p) => Math.min(p + 1, 4));
  }
  async function guardar(soloConfig: boolean) {
    setOcupado(true); setError(""); setMensaje("");
    try {
      await guardarConfiguracionFlujo(token, config);
      if (soloConfig) setMensaje("Configuración guardada para continuar después. No se programó ninguna tarea.");
      else { const tareas = await programarFlujo(token, config, clave.current, confirmado); setMensaje(`${tareas.length} tarea(s) programada(s). Puedes seguirlas y gestionarlas abajo.`); alProgramar(); }
    } catch (e) { setError(e instanceof Error ? e.message : "No se pudo guardar el flujo."); } finally { setOcupado(false); }
  }
  async function corregir(enlace: string) {
    setOcupado(true); setError("");
    try { if (admin) await guardarConfiguracionFlujo(token, config); router.push(`${enlace}?volver=automatizaciones`); }
    catch (e) { setError(e instanceof Error ? e.message : "No se pudo guardar el punto de partida."); setOcupado(false); }
  }
  const modelo = modelos.find((m) => m.id === config.modelo_id);
  const nombres = config.producto_ids.map((id) => productos.find((p) => p.id === id)?.nombre ?? `#${id}`);
  const visibles = productos.filter((p) => `${p.nombre} ${p.codigo}`.toLocaleLowerCase().includes(busqueda.trim().toLocaleLowerCase()));
  return <section className="card flow-assistant"><div className="section-heading"><div><h2>Configurar mi automatización</h2><p>Configúrala una vez; FoodSave la ejecuta en el horario elegido.</p></div><Link href="/promociones">Reglas de promociones →</Link></div>
    {cargando ? <p role="status">Recuperando configuración…</p> : <>
      <PasosAsistente pasos={pasos} actual={paso} />
      {error && <p className="inline-error" role="alert">{error}</p>}{mensaje && <p className="inline-success" role="status">{mensaje}</p>}
      <fieldset ref={contenidoPaso} tabIndex={-1} disabled={ocupado || !admin} className="flow-step">
        {paso === 0 && <><h3>Qué productos quieres planificar</h3>
          <p>Puedes usar todo el catálogo activo o elegir los productos de esta programación.</p>
          <div className="form-actions"><button type="button" className="button-secondary" onClick={() => cambiar({ producto_ids: productos.map((p) => p.id) })}>Seleccionar todos</button><button type="button" className="button-link" onClick={() => cambiar({ producto_ids: [] })}>Quitar selección</button></div>
          <label className="field">Buscar producto<input type="search" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} placeholder="Nombre o código" /></label>
          <div className="product-picker">{visibles.map((p) => <label key={p.id}><input type="checkbox" checked={config.producto_ids.includes(p.id)} onChange={(e) => cambiar({ producto_ids: e.target.checked ? [...config.producto_ids, p.id] : config.producto_ids.filter((id) => id !== p.id) })} />{p.nombre}</label>)}</div>
          {!!productos.length && !visibles.length && <p>No hay productos que coincidan con la búsqueda.</p>}
          <p className="helper-text" role="status">{config.producto_ids.length} de {productos.length} productos seleccionados. Seleccionar todos incluye también los que quedan fuera de la búsqueda.</p>
          <label className="field">Modelo de pronóstico<select value={config.modelo_id ?? ""} onChange={(e) => cambiar({ modelo_id: Number(e.target.value) || null })}><option value="">Selecciona un modelo</option>{modelos.map((m) => <option key={m.id} value={m.id}>{m.version_modelo}</option>)}</select></label>{!modelos.length && <p>Prepara el modelo en <Link href="/inicializacion">Datos iniciales</Link>.</p>}</>}
        {paso === 1 && <><h3>Cuándo debe trabajar FoodSave</h3><div className="form-grid"><label className="field">Primera ejecución · {zona}<input type="datetime-local" value={config.primera_ejecucion_local.slice(0, 16)} onChange={(e) => cambiar({ primera_ejecucion_local: e.target.value })} /></label><label className="field">Repetición<select value={config.dias === 1 ? "una" : "diaria"} onChange={(e) => cambiar({ dias: e.target.value === "una" ? 1 : 2 })}><option value="una">Una sola vez</option><option value="diaria">Cada día, con fecha final</option></select></label>{config.dias > 1 && <label className="field">Número de días<input type="number" min={2} max={31} value={config.dias} onChange={(e) => cambiar({ dias: Number(e.target.value) })} /></label>}<label className="field">Primer día a planificar<input type="date" min={modelo?.particion.inicio_prueba} max={modelo?.particion.fin_prueba} value={config.fecha_objetivo_demo} onChange={(e) => cambiar({ fecha_objetivo_demo: e.target.value })} /></label><label className="field">Hora de planificación<input type="time" value={config.hora_simulada.slice(0, 5)} onChange={(e) => cambiar({ hora_simulada: e.target.value })} /></label></div><p className="helper-text">Cada ejecución avanza un día desde la fecha seleccionada hasta completar {config.dias} ejecución(es). Última ejecución: {formatearEscenario(avanzarDias(config.primera_ejecucion_local, config.dias - 1))} ({zona}). Puedes pausar las tareas pendientes.</p><button type="button" className="button-secondary" onClick={() => cambiar({ primera_ejecucion_local: horarioNegocio(new Date(Date.now() + 60_000), zona), dias: 1 })}>Probar en un minuto</button><p className="helper-text">Prepara una sola ejecución próxima. Revisa los requisitos y confirma la programación en el último paso.</p></>}
        {paso === 2 && <><h3>Qué está listo y qué falta</h3><p>Requisitos para calcular el plan y preparar posibles pedidos. La cobertura del pronóstico se conocerá al ejecutar.</p><button type="button" className="button-secondary" onClick={() => void comprobar()}>Comprobar de nuevo</button><ul className="flow-requirements">{diagnostico?.requisitos.map((r, i) => <li key={`${r.titulo}-${i}`}><div><strong>{r.titulo}</strong><p>{r.motivo}</p></div><span className={`badge badge-${r.listo ? "ok" : "advertencia"}`}>{r.listo ? "Listo" : "Pendiente"}</span>{!r.listo && <button type="button" className="button-link" onClick={() => void corregir(r.enlace)}>Configurar →</button>}</li>)}</ul></>}
        {paso === 3 && <><h3>Qué hacer con los pedidos</h3><label className="field">Modo de envío<select value={config.modo_envio_pedidos} onChange={(e) => cambiar({ modo_envio_pedidos: e.target.value as ConfiguracionFlujo["modo_envio_pedidos"] })}><option value="REQUIERE_APROBACION">Revisar y aprobar antes de enviar</option><option value="AUTOMATICO">Enviar automáticamente por Telegram</option></select></label><p>Sin faltantes no se genera un pedido. Una fecha con una compra activa conserva la protección de recompra.</p>{config.modo_envio_pedidos === "AUTOMATICO" && <label className="review-checkbox"><input type="checkbox" checked={confirmado} onChange={(e) => setConfirmado(e.target.checked)} />Autorizo el envío de estas {config.dias} ejecución(es) al chat verificado.</label>}</>}
        {paso === 4 && <><h3>Revisa tu programación</h3><dl className="flow-summary"><dt>Productos</dt><dd>{nombres.join(", ")}</dd><dt>Modelo</dt><dd>{modelo?.version_modelo}</dd><dt>Primera ejecución</dt><dd>{formatearEscenario(config.primera_ejecucion_local)} · {zona}</dd><dt>Primer día planificado</dt><dd>{formatearEscenario(config.fecha_objetivo_demo)} a las {config.hora_simulada.slice(0, 5)}</dd><dt>Calendario</dt><dd>{config.dias} día(s), una ejecución por día</dd><dt>Última ejecución</dt><dd>{formatearEscenario(avanzarDias(config.primera_ejecucion_local, config.dias - 1))} · {zona}</dd><dt>Último día planificado</dt><dd>{formatearEscenario(avanzarDias(config.fecha_objetivo_demo, config.dias - 1))}</dd><dt>Pedidos</dt><dd>{config.modo_envio_pedidos === "AUTOMATICO" ? "Envío automático autorizado" : "Esperan tu revisión y aprobación"}</dd></dl><p>Se generarán pronóstico, plan, faltantes, posibles pedidos y evaluación histórica. Promociones se evalúan al ajustar stock, según su regla.</p><button type="button" className="button-primary" onClick={() => void guardar(false)}>Confirmar y programar</button></>}
      </fieldset>
      <div className="form-actions section-space"><button type="button" className="button-secondary" disabled={ocupado || paso === 0} onClick={() => setPaso((p) => p - 1)}>Anterior</button>{paso < 4 && <button type="button" className="button-primary" disabled={ocupado || !admin} onClick={() => void continuar()}>Continuar</button>}<button type="button" className="button-link" disabled={ocupado || !admin || !config.producto_ids.length} onClick={() => void guardar(true)}>Guardar para después</button></div>
      {!admin && <p>Solo un administrador puede configurar y programar el flujo.</p>}
    </>}
  </section>;
}
