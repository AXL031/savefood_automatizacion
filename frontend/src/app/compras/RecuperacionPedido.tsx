"use client";
import Link from "next/link";
import { useRef, useState, type FormEvent } from "react";
import { conciliarPedido, reintentarPedido } from "@/services/compras";
import type { Pedido } from "@/types/compras";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { formatearFechaHora } from "@/utils/fechas";

export function RecuperacionPedido({ pedido, admin, token, ocupado, zona, alOcupar, alCambiar }: {
  pedido: Pedido; admin: boolean; token: string; ocupado: boolean; zona: string;
  alOcupar: (valor: boolean) => void; alCambiar: () => void;
}) {
  const [resultado, setResultado] = useState<"ENVIADO" | "NO_ENVIADO">("ENVIADO");
  const [evidencia, setEvidencia] = useState("");
  const [messageId, setMessageId] = useState("");
  const [fecha, setFecha] = useState("");
  const [revisado, setRevisado] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const clave = useRef<{ huella: string; valor: string } | null>(null);
  const envio = pedido.envio;
  const incierto = envio?.estado === "PENDIENTE_VERIFICACION";
  const fallido = envio?.estado === "FALLIDO";
  const chat = incierto ? envio.chat_id : pedido.destino_actual.chat_id_pruebas;
  const deshabilitado = ocupado || guardando;
  const destinoValido = incierto || (pedido.destino_actual.activo && pedido.destino_actual.destino_verificado && chat);
  async function registrar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (!envio || !chat || !revisado || !(incierto || fallido)) return;
    setGuardando(true); alOcupar(true); setError(""); setMensaje("");
    try {
      const confirmado = incierto && resultado === "ENVIADO";
      const id = Number(messageId);
      if (confirmado && (!Number.isSafeInteger(id) || id <= 0 || !fecha)) throw new Error("Indica el identificador del mensaje y su fecha.");
      const entrada = { envio_id: envio.id, chat_id_revisado: chat, evidencia: evidencia.trim(),
        ...(incierto ? { resultado } : {}),
        ...(confirmado ? { message_id: id, fecha_telegram: new Date(fecha).toISOString() } : {}) };
      const huella = JSON.stringify(entrada);
      if (clave.current?.huella !== huella) clave.current = { huella, valor: crypto.randomUUID() };
      const cuerpo = { ...entrada, clave_idempotencia: clave.current!.valor };
      if (incierto) await conciliarPedido(token, pedido.id, { ...cuerpo, resultado });
      else await reintentarPedido(token, pedido.id, cuerpo);
      setRevisado(false); setEvidencia("");
      setMensaje(fallido ? "Nuevo intento reservado. Consulta su resultado; el intento anterior se conserva." : "Conciliación registrada. No se envió ningún mensaje al registrar la evidencia.");
      alCambiar();
    } catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo registrar la acción. Actualiza el pedido."); }
    finally { setGuardando(false); alOcupar(false); }
  }
  const acciones = { CONFIRMAR_ENVIO: "Entrega confirmada por administrador", CONFIRMAR_NO_ENVIO: "No envío registrado por administrador", REINTENTAR: "Nuevo intento solicitado" };
  return <div className="section-space">
    {!!pedido.envios?.length && <details><summary>Historial de intentos ({pedido.envios.length})</summary><ol className="timeline">{pedido.envios.map((e) => <li key={e.id}><strong>Intento #{e.numero_intento} · chat {e.chat_id}</strong><p>{e.estado === "ENVIADO" ? `Entrega registrada · mensaje ${e.message_id}` : e.estado === "FALLIDO" ? "No enviado" : e.estado === "PENDIENTE_VERIFICACION" ? "Resultado incierto" : e.estado === "ENVIANDO" ? "Enviando" : "Pendiente de envío"} · {formatearFechaHora(e.creado_en, zona)}</p>{e.detalle_error && <p>{e.detalle_error}</p>}</li>)}</ol></details>}
    {!!pedido.recuperaciones?.length && <details open><summary>Revisiones administrativas ({pedido.recuperaciones.length})</summary><ol className="timeline">{pedido.recuperaciones.map((r) => <li key={r.id}><strong>{acciones[r.accion]}</strong><p>{r.nombre_usuario} · {formatearFechaHora(r.fecha, zona)} · envío #{r.envio_id}{r.nuevo_envio_id && ` → nuevo envío #${r.nuevo_envio_id}`}</p><p>{r.evidencia}</p>{r.resultado_anterior.detalle_error && <p>Resultado anterior: {r.resultado_anterior.detalle_error}</p>}</li>)}</ol></details>}
    {mensaje && <p role="status">{mensaje}</p>}
    {error && <EstadoPanel tono="alerta" titulo="Revisa la recuperación" descripcion={error} />}
    {(incierto || fallido) && !admin && <p>Un administrador debe revisar este intento antes de cualquier nuevo envío.</p>}
    {admin && (incierto || fallido) && <section className="next-action"><h4>{incierto ? "Resolver el resultado incierto" : "Solicitar un nuevo intento"}</h4>
      <p>{incierto ? `Revisa el pedido en el chat conservado ${chat}. Registra lo que comprobaste; esta acción guarda evidencia y no envía mensajes.` : `El intento anterior consta como no enviado. El nuevo intento enviará el mismo mensaje al chat actual ${chat ?? "sin configurar"}. Conserva el plan y las cantidades.`}</p>
      {!destinoValido && <p><Link href="/proveedores">Activa el proveedor y verifica el destino actual</Link> antes de solicitar el nuevo intento.</p>}
      <form onSubmit={registrar} className="form-grid">
        {incierto && <label>Resultado comprobado<select value={resultado} disabled={deshabilitado} onChange={(e) => { setResultado(e.target.value as "ENVIADO" | "NO_ENVIADO"); setRevisado(false); }}><option value="ENVIADO">Encontré el mensaje enviado</option><option value="NO_ENVIADO">Comprobé que no se envió</option></select></label>}
        {incierto && resultado === "ENVIADO" && <><label>Identificador del mensaje en Telegram<input type="number" min={1} max={Number.MAX_SAFE_INTEGER} step={1} value={messageId} onChange={(e) => setMessageId(e.target.value)} required disabled={deshabilitado} /></label><label>Fecha y hora del mensaje (hora de este equipo)<input type="datetime-local" value={fecha} onChange={(e) => setFecha(e.target.value)} required disabled={deshabilitado} /></label></>}
        <label>Qué comprobaste y con qué evidencia<textarea minLength={10} maxLength={1500} value={evidencia} onChange={(e) => setEvidencia(e.target.value)} required disabled={deshabilitado} placeholder="Describe la revisión del pedido, el chat y el resultado." /></label>
        {incierto && resultado === "NO_ENVIADO" && <p>La ausencia de un mensaje visible puede ser insuficiente. Confirma solo con evidencia del no envío. Se guardará el resultado; solicitar otro intento será una acción separada.</p>}
        <label className="review-checkbox"><input type="checkbox" checked={revisado} onChange={(e) => setRevisado(e.target.checked)} disabled={deshabilitado} />{incierto ? `Revisé el intento #${envio.numero_intento} en el chat ${chat} y confirmo la evidencia.` : `Revisé el mensaje y autorizo un nuevo intento al chat propio ${chat ?? "sin configurar"}.`}</label>
        <button type="submit" className="button-primary" disabled={deshabilitado || !revisado || !destinoValido || evidencia.trim().length < 10}>{guardando ? "Registrando…" : incierto ? "Guardar conciliación sin enviar" : "Solicitar nuevo intento de envío"}</button>
      </form>
    </section>}
  </div>;
}
