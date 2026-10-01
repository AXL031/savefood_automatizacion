"use client";
import { TablaPaginada } from "@/components/tables/TablaPaginada";


import Link from "next/link";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
import { EstadoBadge } from "@/components/ui/EstadoBadge";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { crearProgramacion, listarEjecuciones, listarProgramaciones } from "@/services/automatizaciones";
import type { EjecucionAutomatizacion, EstadoEjecucion, ProgramacionDemo } from "@/types/automatizacion";
import { formatearFechaHora } from "@/utils/fechas";
import { etiquetaDato } from "@/utils/etiquetas";
import { listarProductos } from "@/services/catalogo";
import { obtenerEstadoInicial } from "@/services/inicializacion";
import type { Producto } from "@/types/catalogo";

function fechaLocalParaInput(fecha: Date): string {
  return new Date(fecha.getTime() - fecha.getTimezoneOffset() * 60_000).toISOString().slice(0, 16);
}

function Contenido({ token, zonaHoraria, administrador, modoInicial }: { token: string; zonaHoraria: string; administrador: boolean; modoInicial: "REQUIERE_APROBACION" | "AUTOMATICO" }) {
  const [programaciones, setProgramaciones] = useState<ProgramacionDemo[]>([]);
  const [ejecuciones, setEjecuciones] = useState<EjecucionAutomatizacion[]>([]);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [errorCarga, setErrorCarga] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [filtro, setFiltro] = useState<EstadoEjecucion | "TODAS">("TODAS");
  const [horaReal, setHoraReal] = useState("");
  const [horaSimulada, setHoraSimulada] = useState("2022-08-24T10:00");
  const [catalogo, setCatalogo] = useState<Producto[]>([]);
  const [productos, setProductos] = useState<number[]>([]);
  const [modo, setModo] = useState(modoInicial);
  const [confirmado, setConfirmado] = useState(false);
  const [errorCatalogo, setErrorCatalogo] = useState("");
  const [clave, setClave] = useState("");

  useEffect(() => {
    setHoraReal(fechaLocalParaInput(new Date(Date.now() + 5 * 60_000)));
    setClave(`propuesta-${crypto.randomUUID()}`);
  }, []);
  useEffect(() => {
    const control = new AbortController();
    listarProductos(token, { soloDemo: true }, control.signal).then((datos) => {
      if (!control.signal.aborted) setCatalogo(datos.filter((p) => p.activo));
    }).catch((fallo: unknown) => { if (!control.signal.aborted) setErrorCatalogo(fallo instanceof Error ? fallo.message : "No se pudo consultar el catálogo."); });
    obtenerEstadoInicial(token, control.signal).then((estado) => {
      if (!control.signal.aborted && estado.fecha_objetivo_demo) setHoraSimulada(`${estado.fecha_objetivo_demo}T10:00`);
    }).catch(() => { /* La fecha sigue siendo elegible manualmente. */ });
    return () => control.abort();
  }, [token]);

  useEffect(() => {
    const control = new AbortController();
    let temporizador: ReturnType<typeof setTimeout>;
    async function actualizar() {
      try {
        const [programadas, registradas] = await Promise.all([listarProgramaciones(token, control.signal), listarEjecuciones(token, control.signal)]);
        if (control.signal.aborted) return;
        setProgramaciones(programadas);
        setEjecuciones(registradas);
        setErrorCarga("");
      } catch (fallo) {
        if (!control.signal.aborted) setErrorCarga(fallo instanceof Error ? fallo.message : "No se pudieron actualizar las automatizaciones.");
      } finally {
        if (!control.signal.aborted) {
          setCargando(false);
          temporizador = setTimeout(actualizar, 5000);
        }
      }
    }
    void actualizar();
    return () => { control.abort(); clearTimeout(temporizador); };
  }, [token]);

  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setError("");
    setMensaje("");
    const ids = productos;
    if (!horaReal || !horaSimulada || !clave || ids.length < 1 || ids.length > 5 || ids.some((id) => !Number.isInteger(id) || id <= 0)) {
      setError("Elige entre uno y cinco productos e indica la hora real y la fecha del escenario.");
      return;
    }
    if (modo === "AUTOMATICO" && !confirmado) { setError("Confirma el envío automático a tu propio chat de pruebas."); return; }
    setGuardando(true);
    try {
      const creada = await crearProgramacion(token, {
        tipo: "GENERAR_PROPUESTA",
        ejecutar_desde_utc: new Date(horaReal).toISOString(),
        fecha_hora_simulada_local: `${horaSimulada}:00`,
        fecha_objetivo_demo: horaSimulada.slice(0, 10),
        producto_ids: ids,
        modo_envio_pedidos: modo,
        clave_idempotencia: clave,
      });
      const [programadas, registradas] = await Promise.all([listarProgramaciones(token), listarEjecuciones(token)]);
      setProgramaciones(programadas);
      setEjecuciones(registradas);
      setMensaje(`Programación #${creada.id} guardada. El motor la recogerá al llegar la hora real; el estado se actualiza automáticamente.`);
      setClave(`propuesta-${crypto.randomUUID()}`);
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo guardar la programación.");
    } finally {
      setGuardando(false);
    }
  }

  const visibles = useMemo(
    () => filtro === "TODAS" ? ejecuciones : ejecuciones.filter((item) => item.estado === filtro),
    [ejecuciones, filtro],
  );

  return <>
    <EstadoPanel tono="info" titulo="Pronóstico → plan → faltantes → pedido → Telegram" descripcion="Programa una ejecución para el escenario histórico. En modo automático se envía al chat verificado si todos los faltantes tienen oferta; en modo manual espera tu aprobación. Una fecha con compra activa no genera otro pedido." />
    {errorCarga && <div className="inline-error" role="alert">No se pudo actualizar: {errorCarga}</div>}
    {error && <div className="inline-error" role="alert">{error}</div>}
    {mensaje && <div className="inline-success" role="status">{mensaje}</div>}
    <div className="page-grid section-space">
      <section className="card main-card">
        <div className="section-heading"><div><h2>Programar propuesta demostrativa</h2><p>La hora real fija cuándo se despachará; la hora simulada identifica el escenario histórico.</p></div></div>
        <form className="form-grid" onSubmit={guardar}>
          <label className="field">Cuándo ejecutar (fecha y hora de este equipo)<input type="datetime-local" value={horaReal} onChange={(e) => setHoraReal(e.target.value)} disabled={!administrador || guardando} required /><small>Es una ejecución única. El motor comienza en el siguiente ciclo de 30 segundos.</small></label>
          <label className="field">Día y hora del escenario histórico<input type="datetime-local" value={horaSimulada} onChange={(e) => setHoraSimulada(e.target.value)} disabled={!administrador || guardando} required /><small>Usa una fecha del historial. Si ya se envió un pedido para esa fecha, el sistema impedirá otra compra.</small></label>
          <fieldset className="product-picker field-full" disabled={!administrador || guardando}><legend>Productos a planificar · {productos.length} de 5</legend>{catalogo.map((p) => <label key={p.id}><input type="checkbox" checked={productos.includes(p.id)} disabled={!productos.includes(p.id) && productos.length >= 5} onChange={(e) => setProductos((actual) => e.target.checked ? [...actual, p.id] : actual.filter((id) => id !== p.id))} />{p.nombre}</label>)}</fieldset>
          {errorCatalogo && <p role="alert" className="inline-error field-full">{errorCatalogo}</p>}
          {!catalogo.length && !errorCatalogo && <p className="field-full">No hay productos disponibles para elegir. <Link href="/inicializacion">Revisa la carga inicial</Link>.</p>}
          <label className="field field-full">Qué hacer con los pedidos<select value={modo} disabled={!administrador || guardando} onChange={(e) => { setModo(e.target.value as typeof modo); setConfirmado(false); }}><option value="REQUIERE_APROBACION">Revisarlos y aprobarlos antes de enviar</option><option value="AUTOMATICO">Enviar automáticamente a mi chat de pruebas</option></select><small>Este modo queda guardado en la programación y en los pedidos que produzca.</small></label>
          {modo === "AUTOMATICO" && <label className="review-checkbox field-full"><input type="checkbox" checked={confirmado} disabled={!administrador || guardando} onChange={(e) => setConfirmado(e.target.checked)} />Autorizo el envío automático de los faltantes al chat propio verificado del proveedor. El mensaje llevará DEMOSTRACIÓN — NO SURTIR.</label>}
          <details className="field-full"><summary>Identificador técnico de la solicitud</summary><label className="field">Clave para evitar duplicados<input value={clave} onChange={(e) => setClave(e.target.value)} maxLength={128} disabled={!administrador || guardando} required /><small>Se genera sola; consérvala al reintentar esta misma solicitud.</small></label></details>
          <div className="form-actions field-full"><button className="button-primary" type="submit" disabled={!administrador || guardando || !productos.length || (modo === "AUTOMATICO" && !confirmado)}>{guardando ? "Guardando…" : modo === "AUTOMATICO" ? "Programar flujo completo" : "Programar plan con revisión manual"}</button></div>
        </form>
        {!administrador && <p className="helper-text">Solo un administrador puede crear programaciones.</p>}
      </section>
      <aside className="card aside-card"><h2>Seguimiento automático</h2><p>El motor revisa tareas cada 30 segundos. Un fallo interno temporal permite hasta tres intentos. Consulta el detalle para ver el resultado o el motivo del fallo.</p><p className="helper-text">La vista se actualiza cada 5 segundos y muestra hasta 50 registros recientes. Las horas reales de las tablas se muestran en {zonaHoraria}.</p><div className="fact"><span>Programaciones recientes</span><strong>{programaciones.length}</strong></div><div className="fact"><span>Ejecuciones recientes</span><strong>{ejecuciones.length}</strong></div></aside>
    </div>
    <section className="card section-space">
      <div className="section-heading"><div><h2>Programaciones guardadas</h2><p className="helper-text">Últimas 50 programaciones.</p><p>Se muestran por separado la hora real y el reloj del escenario.</p></div></div>
      {cargando ? <p role="status">Cargando programaciones…</p> : programaciones.length ? <TablaPaginada><thead><tr><th>Tarea</th><th>Hora real</th><th>Escenario histórico</th><th>Envío de pedidos</th><th>Estado</th><th>Ejecución</th></tr></thead><tbody>{programaciones.map((item) => <tr key={item.id}><td>{etiquetaDato(item.tipo)}</td><td>{formatearFechaHora(item.ejecutar_desde_utc, zonaHoraria)}</td><td>{item.fecha_hora_simulada_local.replace("T", " ")}</td><td>{item.parametros.modo_envio_pedidos === "AUTOMATICO" ? "Automático" : item.parametros.modo_envio_pedidos === "REQUIERE_APROBACION" ? "Con aprobación" : "Configuración del negocio al ejecutar"}</td><td><span className={`badge badge-${item.estado === "CANCELADA" ? "alerta" : item.estado === "DESPACHADA" ? "info" : "neutral"}`}>{etiquetaDato(item.estado)}</span></td><td>{item.ejecucion_id ? <Link href={`/automatizaciones/ejecuciones/${item.ejecucion_id}`}>Ver #{item.ejecucion_id}</Link> : "—"}</td></tr>)}</tbody></TablaPaginada> : <EstadoPanel titulo="Sin programaciones" descripcion="Elige productos y horarios para crear tu primera tarea." />}
    </section>
    <section className="card section-space">
      <div className="section-heading"><div><h2>Ejecuciones e intentos</h2><p>El resultado aparecerá cuando el servicio de dominio complete la ejecución.</p></div><label className="filter-label">Estado<select value={filtro} onChange={(e) => setFiltro(e.target.value as EstadoEjecucion | "TODAS")}><option value="TODAS">Todas</option><option value="PENDIENTE">Pendiente</option><option value="EN_EJECUCION">En ejecución</option><option value="REINTENTANDO">Reintentando</option><option value="COMPLETADA">Completada</option><option value="FALLIDA">Fallida</option></select></label></div>
      {cargando ? <p role="status">Cargando ejecuciones…</p> : visibles.length ? <TablaPaginada><thead><tr><th>ID</th><th>Tipo</th><th>Inicio real</th><th>Estado</th><th>Intentos</th><th></th></tr></thead><tbody>{visibles.map((item) => <tr key={item.id}><td>#{item.id}</td><td>{etiquetaDato(item.tipo)}</td><td>{formatearFechaHora(item.inicio_en, zonaHoraria)}</td><td><EstadoBadge estado={item.estado} /></td><td>{item.intentos.length}/3</td><td><Link href={`/automatizaciones/ejecuciones/${item.id}`}>Ver detalle</Link></td></tr>)}</tbody></TablaPaginada> : <EstadoPanel titulo="Sin ejecuciones para este filtro" descripcion="Cambia el filtro o crea una programación." />}
    </section>
  </>;
}

export default function AutomatizacionesPage() {
  return <ProtectedShell titulo="Programar tareas" descripcion="Programa el flujo de pronóstico, faltantes y envío a Telegram.">{({ token, negocio, perfil }) => <Contenido token={token} zonaHoraria={negocio.zona_horaria} modoInicial={negocio.modo_envio_pedidos} administrador={perfil.rol === "ADMINISTRADOR"} />}</ProtectedShell>;
}
