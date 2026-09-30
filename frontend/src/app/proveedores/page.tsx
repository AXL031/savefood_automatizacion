"use client";
import { useEffect, useState, type FormEvent } from "react";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { CampoTexto } from "@/components/forms/CampoTexto";
import { CampoSelect } from "@/components/forms/CampoSelect";
import { BotonEnviar } from "@/components/forms/BotonEnviar";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { cambiarEstadoProveedor, crearOferta, crearProveedor, desactivarOferta, listarOfertas, listarProveedores, marcarPreferida, vincularChat, consultarTelegram, guardarTelegram, comprobarTelegram, deshabilitarTelegram, verificarDestino, buscarChatsTelegram } from "@/services/compras";
import { listarIngredientes } from "@/services/recetas";
import type { Ingrediente } from "@/types/recetas";
import type { EstadoTelegram, NuevaOferta, Oferta, Proveedor } from "@/types/compras";

const ofertaVacia: NuevaOferta = { ingrediente_id: 0, descripcion: "", unidad_compra: "", factor_conversion: "", minimo: "0", multiplo: "1", preferida: true };
function Contenido({ contexto: { token, perfil } }: { contexto: ContextoSesion }) {
  const admin = perfil.rol === "ADMINISTRADOR";
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [ingredientes, setIngredientes] = useState<Ingrediente[]>([]);
  const [seleccionado, setSeleccionado] = useState("");
  const [ofertas, setOfertas] = useState<Oferta[]>([]);
  const [nuevo, setNuevo] = useState({ codigo: "", nombre: "" });
  const [oferta, setOferta] = useState<NuevaOferta>(ofertaVacia);
  const [chat, setChat] = useState("");
  const [chatPropio, setChatPropio] = useState(false);
  const [credencial, setCredencial] = useState("");
  const [telegram, setTelegram] = useState<EstadoTelegram | null>(null);
  const [chatsEncontrados, setChatsEncontrados] = useState<{ chat_id: string; tipo: string }[]>([]);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    if (!admin) return;
    const control = new AbortController();
    consultarTelegram(token, control.signal).then((estado) => { if (!control.signal.aborted) setTelegram(estado); })
      .catch((fallo: unknown) => { if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudo consultar Telegram."); });
    return () => control.abort();
  }, [token, admin]);
  useEffect(() => {
    const control = new AbortController(); setCargando(true);
    Promise.all([listarProveedores(token, control.signal), listarIngredientes(token, control.signal)])
      .then(([lista, insumos]) => { if (control.signal.aborted) return; setProveedores(lista); setIngredientes(insumos); setSeleccionado((actual) => actual || String(lista[0]?.id ?? "")); setOferta((actual) => ({ ...actual, ingrediente_id: actual.ingrediente_id || insumos.find((i) => i.activo)?.id || 0 })); })
      .catch((fallo: unknown) => { if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudo cargar el catálogo."); })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token, revision]);
  useEffect(() => {
    setOfertas([]); if (!seleccionado) return;
    const control = new AbortController();
    listarOfertas(token, Number(seleccionado), control.signal).then((lista) => { if (!control.signal.aborted) setOfertas(lista); })
      .catch((fallo: unknown) => { if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudieron consultar las ofertas."); });
    return () => control.abort();
  }, [token, seleccionado, revision]);
  const proveedor = proveedores.find((p) => p.id === Number(seleccionado));
  useEffect(() => { setChat(proveedor?.chat_id_pruebas ?? ""); setChatPropio(false); }, [proveedor?.id, proveedor?.chat_id_pruebas]);
  async function operarTelegram(accion: () => Promise<EstadoTelegram>) {
    setGuardando(true); setError(""); setMensaje(""); setChatsEncontrados([]);
    try { const estado = await accion(); setTelegram(estado);
      if (estado.bot || !estado.configurado && estado.codigo === "TOKEN_NO_CONFIGURADO") setMensaje(estado.detalle);
      else if (estado.codigo !== "SIN_COMPROBAR") setError(estado.detalle);
    } catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo configurar Telegram."); }
    finally { setCredencial(""); setGuardando(false); setRevision((r) => r + 1); }
  }
  async function verificarChat() {
    setGuardando(true); setError(""); setMensaje("");
    try { const resultado = await verificarDestino(token, Number(seleccionado));
      if (resultado.verificado) setMensaje(resultado.detalle); else setError(resultado.detalle);
    } catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo verificar el chat."); }
    finally { setGuardando(false); setRevision((r) => r + 1); }
  }
  async function buscarChats() {
    setGuardando(true); setError(""); setMensaje(""); setChatsEncontrados([]);
    try { const chats = await buscarChatsTelegram(token); setChatsEncontrados(chats);
      if (chats.length === 0) setMensaje("No se encontró /start pendiente. Escribe /start de nuevo a tu bot y vuelve a buscar.");
      else setMensaje("Selecciona tu chat propio para vincularlo al proveedor.");
    } catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo buscar tu chat."); }
    finally { setGuardando(false); }
  }
  async function operar(accion: () => Promise<unknown>, texto: string) {
    setGuardando(true); setError(""); setMensaje("");
    try { await accion(); setMensaje(texto); setRevision((r) => r + 1); }
    catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo guardar la operación."); }
    finally { setGuardando(false); }
  }
  function registrar(evento: FormEvent<HTMLFormElement>) { evento.preventDefault(); void operar(async () => { const creado = await crearProveedor(token, nuevo); setSeleccionado(String(creado.id)); setNuevo({ codigo: "", nombre: "" }); }, "Proveedor registrado."); }
  function registrarOferta(evento: FormEvent<HTMLFormElement>) { evento.preventDefault(); void operar(async () => { await crearOferta(token, Number(seleccionado), oferta); setOferta({ ...ofertaVacia, ingrediente_id: oferta.ingrediente_id }); }, "Oferta registrada. Cambiar la oferta no altera los pedidos anteriores."); }
  return <>
    {error && <EstadoPanel tono="alerta" titulo="Revisa la operación" descripcion={error} />}{mensaje && <p role="status" className="inline-success">{mensaje}</p>}
    {admin && <section className="card section-space"><h2>Configuración Telegram</h2>
      <ol><li>Crea tu bot en <a href="https://t.me/BotFather" target="_blank" rel="noreferrer">BotFather</a> con <code>/newbot</code> y copia su token.</li>
      <li>Guárdalo aquí. FoodSave comprobará la identidad del bot con Telegram.</li>
      <li>Abre el chat de tu bot y pulsa Iniciar o escribe <code>/start</code>. También puedes añadirlo a un grupo propio de pruebas.</li>
      <li>Selecciona el proveedor, pulsa Buscar mi chat, vincula el destino y verifícalo.</li></ol>
      <p role="status">{telegram ? `${telegram.configurado ? "Token configurado" : "Sin token disponible"} · ${telegram.detalle}` : "Consultando configuración…"}</p>
      {telegram?.bot && <p>Bot: {telegram.bot.nombre} · @{telegram.bot.username} · ID {telegram.bot.id}</p>}
      <form onSubmit={(e) => { e.preventDefault(); void operarTelegram(() => guardarTelegram(token, credencial)); }}>
        <CampoTexto id="telegram-token" etiqueta="Token del bot" tipo="password" autoComplete="off" valor={credencial} requerido deshabilitado={guardando}
          onCambio={setCredencial} ayuda="Se guarda cifrado en el servidor. El token guardado nunca se devuelve; este campo queda vacío después de comprobarlo." />
        <BotonEnviar enviando={guardando} textoEnviando="Comprobando…">Guardar y comprobar bot</BotonEnviar>
      </form>
      <button type="button" className="button-secondary" disabled={guardando || !telegram?.configurado} onClick={() => void operarTelegram(() => comprobarTelegram(token))}>Comprobar bot guardado</button>{" "}
      <button type="button" className="button-secondary" disabled={guardando || !telegram?.configurado} onClick={() => void operarTelegram(() => deshabilitarTelegram(token))}>Deshabilitar Telegram</button>
      <p className="helper-text">La comprobación consulta Telegram y no envía mensajes. La aprobación y el envío de pedidos se habilitarán en los siguientes pasos.</p>
    </section>}
    <section className="card"><div className="section-heading"><h2>Proveedores</h2><button type="button" className="button-secondary" disabled={guardando || cargando} onClick={() => setRevision((r) => r + 1)}>Actualizar</button></div>
      {cargando ? <p role="status">Consultando proveedores…</p> : proveedores.length === 0 ? <p>Todavía no hay proveedores. Registra uno para configurar las ofertas de los ingredientes.</p> : <CampoSelect id="proveedor" etiqueta="Proveedor" valor={seleccionado} deshabilitado={guardando} opciones={proveedores.map((p) => ({ valor: String(p.id), texto: `${p.codigo} · ${p.nombre}${p.activo ? "" : " · Inactivo"}` }))} onCambio={(id) => { setSeleccionado(id); setChat(""); }} />}
      {proveedor && <><p>{proveedor.activo ? "Activo" : "Inactivo"} · Destino {proveedor.destino_verificado ? "verificado" : "sin verificar"}</p>{admin && <button type="button" className="button-secondary" disabled={guardando} onClick={() => void operar(() => cambiarEstadoProveedor(token, proveedor.id, !proveedor.activo), "Estado actualizado.")}>{proveedor.activo ? "Desactivar proveedor" : "Activar proveedor"}</button>}
        <h3>Ofertas</h3><div className="table-wrap"><table><thead><tr><th>Ingrediente / oferta</th><th>Unidad de compra</th><th>Factor a base</th><th>Mínimo / múltiplo</th><th>Estado</th>{admin && <th>Acciones</th>}</tr></thead><tbody>{ofertas.map((o) => <tr key={o.id}><td>{ingredientes.find((i) => i.id === o.ingrediente_id)?.nombre ?? `#${o.ingrediente_id}`} · {o.descripcion}</td><td>{o.unidad_compra}</td><td>{o.factor_conversion} {ingredientes.find((i) => i.id === o.ingrediente_id)?.unidad_base}</td><td>{o.minimo} / {o.multiplo}</td><td>{o.activa ? o.preferida ? "Preferida" : "Activa" : "Inactiva"}</td>{admin && <td>{o.activa && <><button type="button" className="button-link" disabled={guardando || o.preferida} onClick={() => void operar(() => marcarPreferida(token, o.id), "Oferta preferida actualizada.")}>Usar preferida</button><button type="button" className="button-link" disabled={guardando} onClick={() => void operar(() => desactivarOferta(token, o.id), "Oferta desactivada.")}>Desactivar</button></>}</td>}</tr>)}</tbody></table></div>{ofertas.length === 0 && <p>Sin ofertas registradas.</p>}
        {admin && <div className="section-space"><h3>Chat propio de pruebas</h3>
          <p>Escribe <code>/start</code> al bot de FoodSave desde tu chat propio y busca su identificador aquí.</p>
          <button type="button" className="button-secondary" disabled={guardando || !telegram?.configurado} onClick={() => void buscarChats()}>Buscar mi chat</button>
          {chatsEncontrados.length > 0 && <ul>{chatsEncontrados.map((destino) => <li key={destino.chat_id}><button type="button" className="button-link" disabled={guardando} onClick={() => { setChat(destino.chat_id); setChatPropio(false); }}>Usar chat {destino.chat_id} ({destino.tipo === "private" ? "privado" : "grupo"})</button></li>)}</ul>}
          <form onSubmit={(e) => { e.preventDefault(); if (chatPropio) void operar(() => vincularChat(token, proveedor.id, chat), "Chat vinculado. Verifica el destino para comprobar su acceso."); }}>
            <CampoTexto id="chat" etiqueta="chat_id numérico" valor={chat} requerido deshabilitado={guardando} onCambio={(valor) => { setChat(valor); setChatPropio(false); }} ayuda={`Actual: ${proveedor.chat_id_pruebas ?? "sin vincular"}. Usa el ID numérico de tu chat privado o grupo; no el teléfono ni @usuario.`} />
            <label><input type="checkbox" checked={chatPropio} disabled={guardando} onChange={(e) => setChatPropio(e.target.checked)} /> Este chat me pertenece y lo usaré para la demostración.</label>
            <BotonEnviar enviando={guardando} textoEnviando="Guardando…" deshabilitado={!chatPropio}>Vincular chat</BotonEnviar>
          </form>
          <button type="button" className="button-secondary" disabled={guardando || !proveedor.chat_id_pruebas || chat.trim() !== proveedor.chat_id_pruebas} onClick={() => void verificarChat()}>Verificar chat vinculado</button>
          {proveedor.destino_verificado_en && <p>Verificado: {new Date(proveedor.destino_verificado_en).toLocaleString("es-CO")}</p>}
          <p className="helper-text">Verificar comprueba acceso y permisos del bot. No envía mensajes ni acredita la entrega de un pedido.</p>
        </div>}
      </>}
    </section>
    {admin && <section className="card section-space"><h2>Registrar proveedor</h2><form onSubmit={registrar}><div className="form-grid"><CampoTexto id="proveedor-codigo" etiqueta="Código" requerido valor={nuevo.codigo} deshabilitado={guardando} onCambio={(codigo) => setNuevo({ ...nuevo, codigo })} /><CampoTexto id="proveedor-nombre" etiqueta="Nombre" requerido valor={nuevo.nombre} deshabilitado={guardando} onCambio={(nombre) => setNuevo({ ...nuevo, nombre })} /></div><BotonEnviar enviando={guardando} textoEnviando="Registrando…">Registrar proveedor</BotonEnviar></form></section>}
    {admin && proveedor && ingredientes.some((i) => i.activo) && <section className="card section-space"><h2>Registrar oferta para {proveedor.nombre}</h2><form onSubmit={registrarOferta}><div className="form-grid">
      <CampoSelect id="oferta-ingrediente" etiqueta="Ingrediente" valor={String(oferta.ingrediente_id)} deshabilitado={guardando} opciones={ingredientes.filter((i) => i.activo).map((i) => ({ valor: String(i.id), texto: `${i.nombre} (${i.unidad_base})` }))} onCambio={(id) => setOferta({ ...oferta, ingrediente_id: Number(id) })} />
      {([['descripcion','Descripción'],['unidad_compra','Unidad de compra'],['factor_conversion','Unidades base por unidad de compra'],['minimo','Compra mínima'],['multiplo','Múltiplo de compra']] as const).map(([campo, etiqueta]) => <CampoTexto key={campo} id={`oferta-${campo}`} etiqueta={etiqueta} requerido valor={oferta[campo]} deshabilitado={guardando} onCambio={(valor) => setOferta({ ...oferta, [campo]: valor })} />)}
      <CampoSelect id="oferta-preferida" etiqueta="Oferta preferida" valor={oferta.preferida ? "si" : "no"} deshabilitado={guardando} opciones={[{ valor: "si", texto: "Sí" }, { valor: "no", texto: "No" }]} onCambio={(valor) => setOferta({ ...oferta, preferida: valor === "si" })} />
    </div><p className="helper-text">Ejemplo: si la base es g y compras bolsas de 1000 g, el factor es 1000. Las unidades no se convierten por su nombre.</p><BotonEnviar enviando={guardando} textoEnviando="Registrando…">Registrar oferta</BotonEnviar></form></section>}
  </>;
}
export default function PaginaProveedores() { return <ProtectedShell titulo="Proveedores" descripcion="Ofertas, conversiones y destinos de prueba para los pedidos.">{(contexto) => <Contenido contexto={contexto} />}</ProtectedShell>; }
