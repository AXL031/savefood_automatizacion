"use client";
import { TablaPaginada } from "@/components/tables/TablaPaginada";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef, useState, type FormEvent } from "react";
import { PanelDetalle } from "@/components/ui/PanelDetalle";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { CampoSelect } from "@/components/forms/CampoSelect";
import { CampoTexto } from "@/components/forms/CampoTexto";
import { BotonEnviar } from "@/components/forms/BotonEnviar";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { aprobarPedido, cancelarPropuesta, generarPedidos, listarPropuestas, rechazarPedido, verificarDestinosPropuesta } from "@/services/compras";
import { listarPlanes } from "@/services/planificacion";
import type { Pedido, PropuestaCompra } from "@/types/compras";
import type { ResumenPlan } from "@/types/planificacion";
import { etiquetaDato } from "@/utils/etiquetas";
import { cantidadVisible } from "@/utils/unidades";
import { formatearFechaHora } from "@/utils/fechas";
import { RecuperacionPedido } from "./RecuperacionPedido";

const ESTADOS: Record<string, string> = { GENERADA: "Lista para revisión", BLOQUEADA: "Bloqueada", SIN_FALTANTES: "Sin faltantes", CANCELADA: "Cancelada", BLOQUEADO: "Bloqueado", PENDIENTE_APROBACION: "Pendiente de aprobación", CANCELADO: "Cancelado", RECHAZADO: "Rechazado", PENDIENTE_ENVIO: "Autorizado · pendiente de envío", ENVIANDO: "Enviando", ENVIADO: "Envío confirmado por Telegram", FALLIDO: "Envío fallido", PENDIENTE_VERIFICACION: "Resultado incierto · verificar el chat" };
const BLOQUEOS: Record<string, string> = { DESTINO_NO_VERIFICADO: "El chat no estaba verificado al crear el pedido. Verifícalo en Proveedores y actualiza el destino de esta propuesta.", PROVEEDOR_INACTIVO: "Activa el proveedor antes de enviar.", CANAL_PENDIENTE_L03: "Este pedido fue creado antes de habilitar el envío automático. Conserva su historial; utiliza un plan nuevo.", AUTOMATICO_REQUIERE_NUEVO_PLAN: "Para enviar automáticamente después de corregir los datos, cancela esta propuesta y programa un plan nuevo.", MENSAJE_FUERA_DE_RANGO: "El pedido es demasiado largo para un mensaje. Reduce los productos de un plan nuevo.", NECESIDADES_SIN_PROVEEDOR: "Faltan ofertas para algunos ingredientes. Completa las ofertas y utiliza un plan nuevo.", PROPUESTA_BLOQUEADA: "Otro pedido de esta propuesta requiere corrección. Revisa los motivos de todos los pedidos." };
function RevisionPedido({ pedido, token, admin, ocupado, zona, alCambiar, alOcupar }: { pedido: Pedido; token: string; admin: boolean; ocupado: boolean; zona: string; alCambiar: () => void; alOcupar: (valor: boolean) => void }) {
  const [aceptado, setAceptado] = useState(false);
  const [motivo, setMotivo] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const claves = useRef<{ aprobar?: string; rechazar?: string }>({});
  const destino = pedido.destino_actual;
  useEffect(() => { setAceptado(false); }, [destino.chat_id_pruebas, destino.destino_verificado, destino.destino_verificado_en, pedido.mensaje]);
  const fecha = (valor: string) => formatearFechaHora(valor, zona);
  const deshabilitado = guardando || ocupado;
  async function decidir(accion: "aprobar" | "rechazar") {
    setGuardando(true); alOcupar(true); setError("");
    try {
      const clave = claves.current[accion] ?? (claves.current[accion] = crypto.randomUUID());
      if (accion === "aprobar") await aprobarPedido(token, pedido.id, clave, destino.chat_id_pruebas!);
      else await rechazarPedido(token, pedido.id, clave, motivo);
      alCambiar();
    } catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo registrar la decisión. Actualiza el pedido antes de volver a decidir."); }
    finally { setGuardando(false); alOcupar(false); }
  }
  return <div className="section-space">
    <h4>{pedido.envio ? "Mensaje autorizado para envío" : pedido.modo_envio === "AUTOMATICO" ? "Mensaje previsto para el envío automático" : "Revisa el mensaje antes de enviarlo"}</h4><pre className="pedido-mensaje">{pedido.mensaje}</pre>
    <p>Tu chat de pruebas: <strong>{destino.chat_id_pruebas ?? "Sin vincular"}</strong> · <span className={`badge badge-${destino.destino_verificado && destino.activo ? "ok" : "alerta"}`}>{destino.destino_verificado && destino.activo ? "Verificado" : "Falta configurar"}</span>.</p>
    {pedido.decision && <p role="status">{pedido.decision.accion === "APROBAR" ? "Aprobado" : "Rechazado"} por {pedido.decision.nombre_usuario} (usuario #{pedido.decision.usuario_id}) · {fecha(pedido.decision.fecha)}.{pedido.decision.motivo && ` Motivo: ${pedido.decision.motivo}`}</p>}
    {pedido.envio && pedido.modo_envio === "AUTOMATICO" && <p>Envío autorizado por el modo automático guardado en esta propuesta. No requiere aprobación adicional.</p>}
    {pedido.envio && <div><p>Intento #{pedido.envio.numero_intento} · chat conservado: {pedido.envio.chat_id} · {ESTADOS[pedido.envio.estado] ?? pedido.envio.estado}.</p>
      {pedido.envio.inicio_en && <p>Inicio: {fecha(pedido.envio.inicio_en)}{pedido.envio.fin_en && ` · Resultado: ${fecha(pedido.envio.fin_en)}`}.</p>}
      {pedido.envio.message_id && <p>Identificador de Telegram: <strong>{pedido.envio.message_id}</strong>{pedido.envio.fecha_telegram && ` · Fecha: ${fecha(pedido.envio.fecha_telegram)}`}. {pedido.recuperaciones?.some((r) => r.envio_id === pedido.envio!.id && r.accion === "CONFIRMAR_ENVIO") ? "Entrega registrada por el administrador con evidencia." : "Telegram confirmó el mensaje."} Esto no constituye aceptación del proveedor.</p>}
      {pedido.envio.detalle_error && pedido.envio.estado !== "ENVIADO" && <EstadoPanel tono="alerta" titulo={ESTADOS[pedido.envio.estado] ?? pedido.envio.estado} descripcion={pedido.envio.detalle_error} />}
      {["PENDIENTE_ENVIO", "ENVIANDO"].includes(pedido.envio.estado) && <EstadoPanel tono="info" titulo="Envío autorizado" descripcion="El sistema lo procesará automáticamente. Puede tardar unos 30 segundos en comenzar; esta pantalla actualiza el resultado sola." />}
    </div>}
    <RecuperacionPedido key={pedido.envio?.id ?? "sin-envio"} pedido={pedido} admin={admin} token={token} ocupado={deshabilitado} zona={zona} alOcupar={alOcupar} alCambiar={alCambiar} />
    {error && <EstadoPanel tono="alerta" titulo="Revisa la decisión" descripcion={error} />}
    {admin && ["PENDIENTE_APROBACION", "BLOQUEADO"].includes(pedido.estado) && <div>
      {pedido.estado === "PENDIENTE_APROBACION" && <div className="next-action"><strong>Siguiente paso: autorizar el mensaje</strong><label className="review-checkbox"><input type="checkbox" checked={aceptado} disabled={deshabilitado} onChange={(evento) => setAceptado(evento.target.checked)} /> Revisé el texto y confirmo que el chat {destino.chat_id_pruebas ?? "sin vincular"} es mi destino de pruebas.</label>
      <button type="button" className="button-primary" disabled={deshabilitado || !aceptado || !destino.activo || !destino.destino_verificado || !destino.chat_id_pruebas} onClick={() => void decidir("aprobar")}>{guardando ? "Registrando…" : "Aprobar y enviar a mi chat"}</button>
      {!aceptado && <p>Marca la confirmación de arriba para habilitar el envío.</p>}
      {(!destino.activo || !destino.destino_verificado) && <p><Link href="/proveedores">Activa el proveedor y verifica tu chat</Link> antes de aprobar.</p>}</div>}
      <details><summary className="danger-action">Rechazar este pedido</summary><p>Conserva el pedido y el motivo; no se enviará ningún mensaje.</p><form onSubmit={(evento) => { evento.preventDefault(); void decidir("rechazar"); }}><CampoTexto id={`rechazo-${pedido.id}`} etiqueta="Motivo para rechazar" requerido valor={motivo} deshabilitado={deshabilitado} onCambio={setMotivo} /><BotonEnviar enviando={deshabilitado} textoEnviando="Registrando…">Rechazar pedido</BotonEnviar></form></details>
    </div>}
  </div>;
}
function Contenido({ contexto: { token, perfil, negocio } }: { contexto: ContextoSesion }) {
  const parametros = useSearchParams();
  const planSolicitado = parametros.get("plan_id");
  const solicitudAplicada = useRef<string | null>(null);
  const [planes, setPlanes] = useState<ResumenPlan[]>([]);
  const [propuestas, setPropuestas] = useState<PropuestaCompra[]>([]);
  const [planId, setPlanId] = useState("");
  const [detalleAbierto, setDetalleAbierto] = useState(false);
  const [decisionEnCurso, setDecisionEnCurso] = useState(false);
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
      .then(([lista, compras]) => { if (control.signal.aborted) return; setPlanes(lista); setPropuestas(compras); if (planSolicitado && solicitudAplicada.current !== planSolicitado && lista.some((p) => String(p.id) === planSolicitado)) { solicitudAplicada.current = planSolicitado; setPlanId(planSolicitado); setDetalleAbierto(compras.some((p) => String(p.plan_id) === planSolicitado)); } else setPlanId((actual) => actual || String(lista[0]?.id ?? "")); })
      .catch((fallo: unknown) => { if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudieron consultar las compras."); })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token, revision, planSolicitado]);
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
    try { const actualizada = await verificarDestinosPropuesta(token, propuesta.id); setMensaje(actualizada.estado === "GENERADA" ? "Destino actualizado. Revisa el mensaje y marca la confirmación para aprobar el envío." : "Estado actualizado. Quedan los impedimentos que se muestran debajo; todavía no se puede enviar."); setRevision((r) => r + 1); }
    catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudieron revisar los destinos."); }
    finally { setGuardando(false); }
  }
  async function generar() {
    setGuardando(true); setError(""); setMensaje("");
    try { const nueva = await generarPedidos(token, Number(planId)); setDetalleAbierto(true); setMensaje(`Propuesta #${nueva.id}: ${ESTADOS[nueva.estado] ?? nueva.estado}.`); setRevision((r) => r + 1); }
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
    <div className="section-heading section-space"><Link href="/proveedores">Configurar proveedores y ofertas</Link><Link href="/planificacion">Ver planificación</Link><button type="button" className="button-secondary" disabled={guardando || cargando} onClick={() => setRevision((r) => r + 1)}>Actualizar</button></div>
    {error && <EstadoPanel tono="alerta" titulo="Revisa la operación" descripcion={error} />}{mensaje && <p className="inline-success" role="status">{mensaje}</p>}
    {cargando && <p role="status">Consultando planes y pedidos…</p>}
    {!cargando && planes.length === 0 && <EstadoPanel titulo="Todavía no hay planes" descripcion="Genera una propuesta de producción para conocer sus faltantes." />}
    {planes.length > 0 && <section className="card"><CampoSelect id="plan-compra" etiqueta="Elige el plan que quieres revisar" valor={planId} deshabilitado={guardando || cargando} opciones={planes.map((p) => ({ valor: String(p.id), texto: `Plan #${p.id} · ${p.fecha_objetivo} · ${etiquetaDato(p.necesidades_estado)}` }))} onCambio={(id) => { setPlanId(id); setMotivo(""); setError(""); setMensaje(""); }} />
      {admin && !propuesta && <button type="button" disabled={guardando || cargando} onClick={() => void generar()}>{guardando ? "Generando…" : "Generar pedidos desde este plan"}</button>}
      {propuesta && <button type="button" className="button-primary" onClick={() => setDetalleAbierto(true)}>Ver propuesta #{propuesta.id}</button>}
      {!propuesta && !cargando && <p>Este plan todavía no tiene propuesta de compra. Se admite una sola propuesta activa por fecha; cambiar stock u ofertas requiere un plan nuevo.</p>}
    </section>}
    {propuesta && detalleAbierto && <PanelDetalle titulo={`Propuesta #${propuesta.id} · Plan #${propuesta.plan_id}`} onCerrar={() => setDetalleAbierto(false)} ocupado={guardando || decisionEnCurso}><section className="card section-space"><div className="section-heading"><div><h2>Propuesta de compra #{propuesta.id}</h2><p>Plan #{propuesta.plan_id} · escenario histórico: {propuesta.fecha_objetivo}.</p></div><span className={`badge badge-${propuesta.estado === "BLOQUEADA" ? "alerta" : "info"}`}>{etiquetaDato(propuesta.estado)}</span></div><p>Modo de este pedido: <strong>{propuesta.modo_envio === "AUTOMATICO" ? "Automático" : "Aprobación manual"}</strong>. Se eligió al crear el pedido.</p>
      {error && <EstadoPanel tono="alerta" titulo="Revisa la operación" descripcion={error} />}{mensaje && <p role="status">{mensaje}</p>}
      {propuesta.estado === "BLOQUEADA" && <EstadoPanel tono="alerta" titulo="Este pedido necesita una corrección antes de enviarse" descripcion="Los motivos se muestran debajo. Configurar tu chat no actualiza por sí solo un pedido creado anteriormente." />}
      {propuesta.incidencias.map((i, n) => <EstadoPanel key={n} tono="alerta" titulo={i.nombre ? `Falta una oferta para ${i.nombre}` : etiquetaDato(i.codigo)} descripcion={i.detalle} accion={<Link href={i.codigo === "SIN_PROVEEDOR" ? "/proveedores" : "/planificacion"}>{i.codigo === "SIN_PROVEEDOR" ? "Configurar ofertas" : "Revisar los datos del plan"}</Link>} />)}
      {propuesta.estado === "SIN_FALTANTES" && <p>El stock disponible cubre las necesidades. No se generaron pedidos ni se reservó esta fecha.</p>}
      {propuesta.estado === "CANCELADA" && <p>Cancelada: {propuesta.motivo_cancelacion}. Para corregir el cálculo utiliza otro plan.</p>}
      {admin && propuesta.activa && propuesta.pedidos.length > 0 && propuesta.pedidos.every((p) => ["BLOQUEADO", "PENDIENTE_APROBACION"].includes(p.estado)) && <div className="action-row"><button type="button" className={propuesta.estado === "BLOQUEADA" ? "button-primary" : "button-secondary"} disabled={guardando || cargando} onClick={() => void revisarDestinos()}>{guardando ? "Actualizando…" : "Actualizar estado del destino"}</button><span className="helper-text">Úsalo después de verificar tu chat en Proveedores.</span></div>}
      {propuesta.pedidos.map((pedido) => <article key={pedido.id} className="order-card"><div className="section-heading"><h3>Pedido #{pedido.id} · {pedido.proveedor.nombre}</h3><span className={`badge badge-${pedido.estado === "ENVIADO" ? "ok" : pedido.estado === "BLOQUEADO" ? "alerta" : "info"}`}>{ESTADOS[pedido.estado] ?? etiquetaDato(pedido.estado)}</span></div>{pedido.bloqueos.map((b) => <EstadoPanel key={b} tono="alerta" titulo="Qué falta para enviar" descripcion={BLOQUEOS[b] ?? etiquetaDato(b)} />)}
        <TablaPaginada><thead><tr><th>Ingrediente</th><th>Cantidad que falta</th><th>Cantidad a comprar</th><th>Contenido total</th></tr></thead><tbody>{pedido.lineas.map((l) => <tr key={l.id}><td>{l.nombre}</td><td>{cantidadVisible(l.faltante_base, l.unidad_base)}</td><td><strong>{cantidadVisible(l.cantidad_compra, l.unidad_compra)}</strong></td><td>{cantidadVisible(l.cantidad_base_pedida, l.unidad_base)}</td></tr>)}</tbody></TablaPaginada><p className="helper-text">La compra se redondea según el mínimo y los paquetes que ofrece el proveedor.</p>
        {pedido.lineas.map((l) => <details key={l.id}><summary>Conversión de {l.nombre}</summary><p>Necesidad #{l.necesidad_ingrediente_id} · oferta #{l.oferta.oferta_id}. Factor: {l.oferta.factor_conversion} {l.unidad_base} por {l.unidad_compra}; mínimo {l.oferta.minimo}; múltiplo {l.oferta.multiplo}.</p></details>)}
        <RevisionPedido pedido={pedido} token={token} admin={admin} ocupado={guardando || cargando || decisionEnCurso} zona={negocio.zona_horaria} alOcupar={setDecisionEnCurso} alCambiar={() => setRevision((r) => r + 1)} />
      </article>)}
      {admin && propuesta.activa && propuesta.pedidos.every((p) => ["BLOQUEADO", "PENDIENTE_APROBACION", "RECHAZADO"].includes(p.estado)) && <details className="section-space"><summary className="danger-action">Cancelar propuesta para utilizar un plan corregido</summary><form onSubmit={cancelar}><p>Se cancelan los pedidos pendientes y se libera la fecha para otro plan. El historial y los rechazos se conservan.</p><CampoTexto id="cancelar-motivo" etiqueta="Motivo de cancelación" requerido valor={motivo} deshabilitado={guardando || cargando} onCambio={setMotivo} /><BotonEnviar enviando={guardando || cargando} textoEnviando="Cancelando…">Cancelar propuesta y sus pedidos</BotonEnviar></form></details>}
    </section></PanelDetalle>}
    {propuestas.length > 0 && <section className="card section-space"><h2>Historial de propuestas</h2><p className="helper-text">Últimas 50 propuestas.</p><TablaPaginada><thead><tr><th>Propuesta</th><th>Plan</th><th>Fecha</th><th>Estado</th><th>Detalle</th></tr></thead><tbody>{propuestas.map((p) => <tr key={p.id}><td>#{p.id}</td><td>#{p.plan_id}</td><td>{p.fecha_objetivo}</td><td>{ESTADOS[p.estado]}</td><td><button type="button" className="button-link" disabled={guardando} onClick={() => { setPlanId(String(p.plan_id)); setMotivo(""); setDetalleAbierto(true); }}>Ver</button></td></tr>)}</tbody></TablaPaginada></section>}
  </>;
}
export default function PaginaCompras() { return <ProtectedShell titulo="Pedidos y envíos" descripcion="Ingredientes faltantes, revisión del mensaje y confirmación de Telegram.">{(contexto) => <Suspense fallback={<p role="status">Abriendo compras…</p>}><Contenido contexto={contexto} /></Suspense>}</ProtectedShell>; }
