"use client";
import Link from "next/link";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { CampoSelect } from "@/components/forms/CampoSelect";
import { CampoTexto } from "@/components/forms/CampoTexto";
import { BotonEnviar } from "@/components/forms/BotonEnviar";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { aprobarPedido, cancelarPropuesta, generarPedidos, listarPropuestas, rechazarPedido, verificarDestinosPropuesta } from "@/services/compras";
import { listarPlanes } from "@/services/planificacion";
import type { Pedido, PropuestaCompra } from "@/types/compras";
import type { ResumenPlan } from "@/types/planificacion";

const ESTADOS: Record<string, string> = { GENERADA: "Generada", BLOQUEADA: "Bloqueada", SIN_FALTANTES: "Sin faltantes", CANCELADA: "Cancelada", BLOQUEADO: "Bloqueado", PENDIENTE_APROBACION: "Pendiente de aprobación", CANCELADO: "Cancelado", RECHAZADO: "Rechazado", PENDIENTE_ENVIO: "Aprobado · pendiente de envío", ENVIANDO: "Enviando", ENVIADO: "Envío confirmado por Telegram", FALLIDO: "Envío fallido", PENDIENTE_VERIFICACION: "Resultado incierto · verificar el chat" };
const BLOQUEOS: Record<string, string> = { DESTINO_NO_VERIFICADO: "Destino del proveedor sin verificar", PROVEEDOR_INACTIVO: "Proveedor inactivo", CANAL_PENDIENTE_L03: "Modo automático pendiente de verificación en el paso 7", NECESIDADES_SIN_PROVEEDOR: "Hay ingredientes sin proveedor", PROPUESTA_BLOQUEADA: "Otro pedido de esta propuesta tiene un impedimento" };
function fecha(valor: string) { return new Date(valor).toLocaleString("es-EC"); }
function RevisionPedido({ pedido, token, admin, alCambiar }: { pedido: Pedido; token: string; admin: boolean; alCambiar: () => void }) {
  const [aceptado, setAceptado] = useState(false);
  const [motivo, setMotivo] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const claves = useRef<{ aprobar?: string; rechazar?: string }>({});
  const destino = pedido.destino_actual;
  useEffect(() => { setAceptado(false); }, [destino.chat_id_pruebas, destino.destino_verificado]);
  async function decidir(accion: "aprobar" | "rechazar") {
    setGuardando(true); setError("");
    try {
      const clave = claves.current[accion] ?? (claves.current[accion] = crypto.randomUUID());
      if (accion === "aprobar") await aprobarPedido(token, pedido.id, clave, destino.chat_id_pruebas!);
      else await rechazarPedido(token, pedido.id, clave, motivo);
      alCambiar();
    } catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo registrar la decisión. Actualiza el pedido antes de volver a decidir."); }
    finally { setGuardando(false); }
  }
  return <div className="section-space">
    <h4>DEMOSTRACIÓN — NO SURTIR</h4><p>Texto del mensaje {pedido.envio ? "conservado al aprobar" : "para revisar"}:</p><pre className="pedido-mensaje">{pedido.mensaje}</pre>
    <p>Chat propio de pruebas actual: <strong>{destino.chat_id_pruebas ?? "Sin vincular"}</strong> · {destino.destino_verificado && destino.activo ? "Verificado" : "Requiere revisión en Proveedores"}.</p>
    {pedido.decision && <p role="status">{pedido.decision.accion === "APROBAR" ? "Aprobado" : "Rechazado"} por {pedido.decision.nombre_usuario} (usuario #{pedido.decision.usuario_id}) · {fecha(pedido.decision.fecha)}.{pedido.decision.motivo && ` Motivo: ${pedido.decision.motivo}`}</p>}
    {pedido.envio && <div><p>Intento #{pedido.envio.numero_intento} · chat conservado: {pedido.envio.chat_id} · {ESTADOS[pedido.envio.estado] ?? pedido.envio.estado}.</p>
      {pedido.envio.inicio_en && <p>Inicio: {fecha(pedido.envio.inicio_en)}{pedido.envio.fin_en && ` · Resultado: ${fecha(pedido.envio.fin_en)}`}.</p>}
      {pedido.envio.message_id && <p>Identificador de Telegram: <strong>{pedido.envio.message_id}</strong>{pedido.envio.fecha_telegram && ` · Fecha: ${fecha(pedido.envio.fecha_telegram)}`}. Telegram confirmó el mensaje; esto no constituye aceptación del proveedor.</p>}
      {pedido.envio.detalle_error && <EstadoPanel tono="alerta" titulo={ESTADOS[pedido.envio.estado] ?? pedido.envio.estado} descripcion={pedido.envio.detalle_error} />}
      {pedido.envio.estado === "PENDIENTE_VERIFICACION" && <p>Consulta el chat de pruebas. El sistema no reenvía este pedido automáticamente. La conciliación manual corresponde al paso 7.</p>}
    </div>}
    {error && <EstadoPanel tono="alerta" titulo="Revisa la decisión" descripcion={error} />}
    {admin && ["PENDIENTE_APROBACION", "BLOQUEADO"].includes(pedido.estado) && <div>
      {pedido.estado === "PENDIENTE_APROBACION" && <><label><input type="checkbox" checked={aceptado} disabled={guardando} onChange={(evento) => setAceptado(evento.target.checked)} /> Revisé el texto y confirmo que el chat {destino.chat_id_pruebas ?? "sin vincular"} es mi destino de pruebas.</label>
      <p><button type="button" disabled={guardando || !aceptado || !destino.activo || !destino.destino_verificado || !destino.chat_id_pruebas} onClick={() => void decidir("aprobar")}>{guardando ? "Registrando…" : "Aprobar y enviar a mi chat"}</button></p></>}
      <form onSubmit={(evento) => { evento.preventDefault(); void decidir("rechazar"); }}><CampoTexto id={`rechazo-${pedido.id}`} etiqueta="Motivo para rechazar" requerido valor={motivo} deshabilitado={guardando} onCambio={setMotivo} /><BotonEnviar enviando={guardando} textoEnviando="Registrando…">Rechazar pedido</BotonEnviar></form>
    </div>}
  </div>;
}
function Contenido({ contexto: { token, perfil } }: { contexto: ContextoSesion }) {
  const [planes, setPlanes] = useState<ResumenPlan[]>([]);
  const [propuestas, setPropuestas] = useState<PropuestaCompra[]>([]);
  const [planId, setPlanId] = useState("");
  const [motivo, setMotivo] = useState("");
  const [revision, setRevision] = useState(0);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const admin = perfil.rol === "ADMINISTRADOR";
  useEffect(() => {
    const control = new AbortController(); setCargando(true);
    Promise.all([listarPlanes(token, control.signal), listarPropuestas(token, control.signal)])
      .then(([lista, compras]) => { if (control.signal.aborted) return; setPlanes(lista); setPropuestas(compras); const pedido = new URLSearchParams(window.location.search).get("plan_id"); setPlanId((actual) => actual || (lista.some((p) => String(p.id) === pedido) ? pedido! : String(lista[0]?.id ?? ""))); })
      .catch((fallo: unknown) => { if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudieron consultar las compras."); })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token, revision]);
  const propuesta = propuestas.find((p) => p.plan_id === Number(planId));
  const enviosPendientes = propuestas.some((p) => p.pedidos.some((pedido) => ["PENDIENTE_ENVIO", "ENVIANDO"].includes(pedido.estado)));
  useEffect(() => {
    if (!enviosPendientes) return;
    const intervalo = window.setInterval(() => setRevision((r) => r + 1), 5000);
    return () => window.clearInterval(intervalo);
  }, [enviosPendientes]);
  async function revisarDestinos() {
    if (!propuesta) return;
    setGuardando(true); setError(""); setMensaje("");
    try { await verificarDestinosPropuesta(token, propuesta.id); setMensaje("Destinos revisados. Las cantidades y ofertas conservan su versión original."); setRevision((r) => r + 1); }
    catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudieron revisar los destinos."); }
    finally { setGuardando(false); }
  }
  async function generar() {
    setGuardando(true); setError(""); setMensaje("");
    try { const nueva = await generarPedidos(token, Number(planId)); setMensaje(`Propuesta #${nueva.id}: ${ESTADOS[nueva.estado] ?? nueva.estado}.`); setRevision((r) => r + 1); }
    catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo generar la propuesta."); }
    finally { setGuardando(false); }
  }
  async function cancelar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault(); if (!propuesta) return;
    setGuardando(true); setError(""); setMensaje("");
    try { await cancelarPropuesta(token, propuesta.id, motivo); setMotivo(""); setMensaje("Propuesta cancelada. Se conserva su historial; otro plan podrá usar esta fecha."); setRevision((r) => r + 1); }
    catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo cancelar la propuesta."); }
    finally { setGuardando(false); }
  }
  return <>
    <EstadoPanel tono="info" titulo="DEMOSTRACIÓN — NO SURTIR" descripcion="Revisa cada pedido antes de aprobar y enviar a tu chat propio de pruebas. Se guarda el responsable, la fecha y el identificador confirmado por Telegram. Los pedidos no cambian inventario." />
    <div className="section-heading section-space"><Link href="/proveedores">Configurar proveedores y ofertas</Link><Link href="/planificacion">Ver planificación</Link><button type="button" className="button-secondary" disabled={guardando || cargando} onClick={() => setRevision((r) => r + 1)}>Actualizar</button></div>
    {error && <EstadoPanel tono="alerta" titulo="Revisa la operación" descripcion={error} />}{mensaje && <p className="inline-success" role="status">{mensaje}</p>}
    {cargando && <p role="status">Consultando planes y pedidos…</p>}
    {!cargando && planes.length === 0 && <EstadoPanel titulo="Todavía no hay planes" descripcion="Genera una propuesta de producción para conocer sus faltantes." />}
    {planes.length > 0 && <section className="card"><CampoSelect id="plan-compra" etiqueta="Plan de origen" valor={planId} deshabilitado={guardando} opciones={planes.map((p) => ({ valor: String(p.id), texto: `Plan #${p.id} · ${p.fecha_objetivo} · ${p.necesidades_estado}` }))} onCambio={(id) => { setPlanId(id); setMotivo(""); setError(""); }} />
      {admin && !propuesta && <button type="button" disabled={guardando || cargando} onClick={() => void generar()}>{guardando ? "Generando…" : "Generar pedidos desde este plan"}</button>}
      {!propuesta && !cargando && <p>Este plan todavía no tiene propuesta de compra. Se admite una sola propuesta activa por fecha; cambiar stock u ofertas requiere un plan nuevo.</p>}
    </section>}
    {propuesta && <section className="card section-space"><h2>Propuesta #{propuesta.id} · {ESTADOS[propuesta.estado]}</h2><p>Plan #{propuesta.plan_id} · fecha del escenario {propuesta.fecha_objetivo} · modo conservado: {propuesta.modo_envio === "AUTOMATICO" ? "Automático" : "Requiere aprobación"}.</p>
      {propuesta.incidencias.map((i, n) => <EstadoPanel key={n} tono="alerta" titulo={i.nombre ?? i.codigo} descripcion={i.detalle} />)}
      {propuesta.estado === "SIN_FALTANTES" && <p>El stock disponible cubre las necesidades. No se generaron pedidos ni se reservó esta fecha.</p>}
      {propuesta.estado === "CANCELADA" && <p>Cancelada: {propuesta.motivo_cancelacion}. Para corregir el cálculo utiliza otro plan.</p>}
      {admin && propuesta.activa && propuesta.pedidos.length > 0 && propuesta.pedidos.every((p) => ["BLOQUEADO", "PENDIENTE_APROBACION"].includes(p.estado)) && <p><button type="button" className="button-secondary" disabled={guardando} onClick={() => void revisarDestinos()}>Revisar destinos después de configurar Telegram</button></p>}
      {propuesta.pedidos.map((pedido) => <article key={pedido.id} className="section-space"><h3>Pedido #{pedido.id} · {pedido.proveedor.nombre}</h3><p>{ESTADOS[pedido.estado] ?? pedido.estado}</p>{pedido.bloqueos.map((b) => <p key={b}>{BLOQUEOS[b] ?? b}</p>)}
        <div className="table-wrap"><table><thead><tr><th>Ingrediente</th><th>Faltante base</th><th>Compra sugerida</th><th>Equivalencia base</th></tr></thead><tbody>{pedido.lineas.map((l) => <tr key={l.id}><td>{l.nombre}</td><td>{l.faltante_base} {l.unidad_base}</td><td>{l.cantidad_compra} {l.unidad_compra}</td><td>{l.cantidad_base_pedida} {l.unidad_base}</td></tr>)}</tbody></table></div>
        {pedido.lineas.map((l) => <details key={l.id}><summary>Conversión de {l.nombre}</summary><p>Necesidad #{l.necesidad_ingrediente_id} · oferta #{l.oferta.oferta_id}. Factor: {l.oferta.factor_conversion} {l.unidad_base} por {l.unidad_compra}; mínimo {l.oferta.minimo}; múltiplo {l.oferta.multiplo}.</p></details>)}
        <RevisionPedido pedido={pedido} token={token} admin={admin} alCambiar={() => setRevision((r) => r + 1)} />
      </article>)}
      {admin && propuesta.activa && propuesta.pedidos.every((p) => ["BLOQUEADO", "PENDIENTE_APROBACION", "RECHAZADO"].includes(p.estado)) && <form onSubmit={cancelar} className="section-space"><h3>Cancelar esta propuesta</h3><p>Se cancelan los pedidos pendientes y se libera la fecha para otro plan. El historial y los rechazos se conservan.</p><CampoTexto id="cancelar-motivo" etiqueta="Motivo de cancelación" requerido valor={motivo} deshabilitado={guardando} onCambio={setMotivo} /><BotonEnviar enviando={guardando} textoEnviando="Cancelando…">Cancelar propuesta y sus pedidos</BotonEnviar></form>}
    </section>}
    {propuestas.length > 0 && <section className="card section-space"><h2>Historial de propuestas</h2><div className="table-wrap"><table><thead><tr><th>Propuesta</th><th>Plan</th><th>Fecha</th><th>Estado</th><th>Detalle</th></tr></thead><tbody>{propuestas.map((p) => <tr key={p.id}><td>#{p.id}</td><td>#{p.plan_id}</td><td>{p.fecha_objetivo}</td><td>{ESTADOS[p.estado]}</td><td><button type="button" className="button-link" disabled={guardando} onClick={() => { setPlanId(String(p.plan_id)); setMotivo(""); }}>Ver</button></td></tr>)}</tbody></table></div></section>}
  </>;
}
export default function PaginaCompras() { return <ProtectedShell titulo="Compras" descripcion="Pedidos por faltantes, ofertas conservadas y control entre planes.">{(contexto) => <Contenido contexto={contexto} />}</ProtectedShell>; }
