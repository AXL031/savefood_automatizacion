"use client";
import { useRef, useState, type FormEvent } from "react";
import { TablaPaginada } from "@/components/tables/TablaPaginada";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { registrarRecepcion } from "@/services/compras";
import type { Pedido } from "@/types/compras";
import { cantidadVisible } from "@/utils/unidades";

type DatoLinea = { cantidad: string; lote: string; caducidad: string };
export function RecepcionPedido({ pedido, admin, token, ocupado, zona, alOcupar, alCambiar }: {
  pedido: Pedido; admin: boolean; token: string; ocupado: boolean; zona: string;
  alOcupar: (valor: boolean) => void; alCambiar: () => void;
}) {
  const partes = new Intl.DateTimeFormat("en-CA", { timeZone: zona, year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date());
  const hoy = ["year", "month", "day"].map((tipo) => partes.find((p) => p.type === tipo)!.value).join("-");
  const [fecha, setFecha] = useState(hoy);
  const [motivo, setMotivo] = useState("");
  const [datos, setDatos] = useState<Record<number, DatoLinea>>({});
  const [confirmado, setConfirmado] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const clave = useRef<{ huella: string; valor: string } | null>(null);
  const deshabilitado = ocupado || guardando;
  const pendientes = pedido.lineas.filter((l) => Number(l.cantidad_pendiente) > 0);
  function cambiar(id: number, campo: keyof DatoLinea, valor: string) {
    setDatos((antes) => ({ ...antes, [id]: { ...(antes[id] ?? { cantidad: "", lote: "", caducidad: "" }), [campo]: valor } }));
    setConfirmado(false);
  }
  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault(); if (!confirmado) return;
    setError(""); setMensaje(""); setGuardando(true); alOcupar(true);
    try {
      const lineas = pendientes.filter((l) => Number(datos[l.id]?.cantidad) > 0).map((l) => ({
        linea_pedido_id: l.id, cantidad_compra: datos[l.id].cantidad,
        ...(datos[l.id].lote.trim() ? { codigo_lote: datos[l.id].lote.trim() } : {}),
        ...(datos[l.id].caducidad ? { fecha_caducidad: datos[l.id].caducidad } : {}),
      }));
      if (!lineas.length) throw new Error("Indica cuánto llegó de al menos un ingrediente.");
      const entrada = { fecha_recepcion: fecha, motivo: motivo.trim(), lineas };
      const huella = JSON.stringify(entrada);
      if (clave.current?.huella !== huella) clave.current = { huella, valor: crypto.randomUUID() };
      await registrarRecepcion(token, pedido.id, { ...entrada, clave_idempotencia: clave.current!.valor });
      setDatos({}); setConfirmado(false); setMotivo("");
      setMensaje("Recepción registrada e inventario actualizado con las cantidades recibidas."); alCambiar();
    } catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo registrar la recepción. Actualiza el pedido antes de continuar."); }
    finally { setGuardando(false); alOcupar(false); }
  }
  return <section className="section-space">
    <h4>Recepción de mercancía</h4>
    <p><strong>{pedido.recepcion_estado === "RECIBIDO" ? "Recibido completo" : pedido.recepcion_estado === "PARCIAL" ? "Recibido parcialmente" : "Pendiente de recepción"}</strong>. El inventario aumenta al confirmar lo que llegó.</p>
    {mensaje && <p role="status">{mensaje}</p>}
    {error && <EstadoPanel tono="alerta" titulo="Revisa la recepción" descripcion={error} />}
    {!!pedido.recepciones.length && <details><summary>Historial de recepciones ({pedido.recepciones.length})</summary><ol>{pedido.recepciones.map((r) => <li key={r.id}><strong>Recepción #{r.id} · {r.fecha_recepcion}</strong><p>{r.nombre_usuario}: {r.motivo}</p><ul>{r.lineas.map((l) => { const original = pedido.lineas.find((p) => p.id === l.linea_pedido_id)!; return <li key={l.linea_pedido_id}>{original.nombre}: {cantidadVisible(l.cantidad_compra, original.unidad_compra)} · lote {l.codigo_lote} · {l.fecha_caducidad ? `caduca ${l.fecha_caducidad}` : "caducidad sin informar"} · movimiento #{l.movimiento_id}</li>; })}</ul></li>)}</ol></details>}
    {pedido.estado !== "ENVIADO" && <p>La recepción se habilita cuando el envío del pedido está confirmado.</p>}
    {pedido.estado === "ENVIADO" && pendientes.length > 0 && !admin && <p>Un administrador debe confirmar las cantidades recibidas.</p>}
    {admin && pedido.estado === "ENVIADO" && pendientes.length > 0 && <details className="next-action"><summary>Confirmar llegada del pedido</summary><p>Registra solo lo que recibiste físicamente. Deja vacías las cantidades de los insumos que todavía no llegaron. Las cantidades usan la presentación de compra del pedido.</p><form onSubmit={guardar}>
      <label>Fecha de recepción<input type="date" min={pedido.fecha_objetivo} max={hoy} value={fecha} onChange={(e) => { setFecha(e.target.value); setConfirmado(false); }} required disabled={deshabilitado} /></label>
      <TablaPaginada><thead><tr><th>Ingrediente</th><th>Recibido / pendiente</th><th>Llegó ahora</th><th>Lote (opcional)</th><th>Caducidad (opcional)</th></tr></thead><tbody>{pendientes.map((l) => <tr key={l.id}><td>{l.nombre}<p className="helper-text">Presentación: {l.unidad_compra}</p></td><td>{cantidadVisible(l.cantidad_recibida, l.unidad_compra)} / {cantidadVisible(l.cantidad_pendiente, l.unidad_compra)}</td><td><input aria-label={`Cantidad recibida de ${l.nombre}`} type="number" min="0" max={l.cantidad_pendiente} step="0.0001" value={datos[l.id]?.cantidad ?? ""} onChange={(e) => cambiar(l.id, "cantidad", e.target.value)} disabled={deshabilitado} /></td><td><input aria-label={`Lote de ${l.nombre}`} maxLength={80} value={datos[l.id]?.lote ?? ""} onChange={(e) => cambiar(l.id, "lote", e.target.value)} disabled={deshabilitado} /></td><td><input aria-label={`Caducidad de ${l.nombre}`} type="date" min={fecha} value={datos[l.id]?.caducidad ?? ""} onChange={(e) => cambiar(l.id, "caducidad", e.target.value)} disabled={deshabilitado} /></td></tr>)}</tbody></TablaPaginada>
      <p className="helper-text">Si omites el lote se asignará un código interno. La caducidad sin informar se conservará como desconocida.</p>
      <label>Observaciones de la recepción<textarea minLength={3} maxLength={300} value={motivo} onChange={(e) => { setMotivo(e.target.value); setConfirmado(false); }} required disabled={deshabilitado} /></label>
      <label className="review-checkbox"><input type="checkbox" checked={confirmado} onChange={(e) => setConfirmado(e.target.checked)} disabled={deshabilitado} />Confirmo que estas cantidades llegaron y deben sumarse al inventario.</label>
      <button type="submit" className="button-primary" disabled={deshabilitado || !confirmado}>{guardando ? "Registrando…" : "Confirmar recepción y actualizar inventario"}</button>
    </form></details>}
  </section>;
}
