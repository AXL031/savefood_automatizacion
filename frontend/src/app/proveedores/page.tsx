"use client";
import { TablaPaginada } from "@/components/tables/TablaPaginada";
import { TablaDatos, type Columna } from "@/components/tables/TablaDatos";
import { PanelDetalle } from "@/components/ui/PanelDetalle";

import Link from "next/link";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { CampoTexto } from "@/components/forms/CampoTexto";
import { CampoSelect } from "@/components/forms/CampoSelect";
import { BotonEnviar } from "@/components/forms/BotonEnviar";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { cambiarEstadoProveedor, crearOferta, crearProveedor, desactivarOferta, listarOfertas, listarProveedores, marcarPreferida, vincularChat, consultarTelegram, guardarTelegram, comprobarTelegram, deshabilitarTelegram, verificarDestino, buscarChatsTelegram } from "@/services/compras";
import { listarIngredientes } from "@/services/recetas";
import type { Ingrediente } from "@/types/recetas";
import type { EstadoTelegram, NuevaOferta, Oferta, Proveedor } from "@/types/compras";
import { HttpError } from "@/services/http";
import { aUnidadBase, cantidadVisible, unidadesEntrada } from "@/utils/unidades";
import { enviarPruebaProveedor, listarPruebasProveedor } from "@/services/compras";
import type { MensajePrueba } from "@/types/compras";

const ofertaVacia: NuevaOferta = { ingrediente_id: 0, descripcion: "", unidad_compra: "", factor_conversion: "", minimo: "0", multiplo: "1", preferida: true };
function Contenido({ contexto: { token, perfil, negocio } }: { contexto: ContextoSesion }) {
  const admin = perfil.rol === "ADMINISTRADOR";
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [ingredientes, setIngredientes] = useState<Ingrediente[]>([]);
  const [seleccionado, setSeleccionado] = useState("");
  const [ofertas, setOfertas] = useState<Oferta[]>([]);
  const [nuevo, setNuevo] = useState({ nombre: "" });
  const [oferta, setOferta] = useState<NuevaOferta>(ofertaVacia);
  const [unidadContenido, setUnidadContenido] = useState("");
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
  const [creando, setCreando] = useState(false);
  const [configurandoTelegram, setConfigurandoTelegram] = useState(false);
  const [agregandoInsumo, setAgregandoInsumo] = useState(false);
  const [busqueda, setBusqueda] = useState("");
  const [estado, setEstado] = useState("activos");
  const [ingredientePendiente, setIngredientePendiente] = useState("");
  const parametrosAplicados = useRef(false);
  const [pruebas, setPruebas] = useState<MensajePrueba[]>([]);
  const [cargandoPruebas, setCargandoPruebas] = useState(false);
  const [historialListo, setHistorialListo] = useState(false);
  const [errorPruebas, setErrorPruebas] = useState("");
  const [revisionChat, setRevisionChat] = useState(false);
  const solicitudPrueba = useRef<{ clave_idempotencia: string; chat_id_revisado: string; confirmar_revision_chat: boolean } | null>(null);
  const enviandoPrueba = useRef(false);
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
      .then(([lista, insumos]) => {
        if (control.signal.aborted) return;
        const parametros = new URLSearchParams(window.location.search);
        const proveedorSolicitado = lista.find((p) => p.id === Number(parametros.get("proveedor")));
        const insumoSolicitado = insumos.find((i) => i.activo && i.id === Number(parametros.get("ingrediente")));
        setProveedores(lista); setIngredientes(insumos);
        if (!parametrosAplicados.current) {
          setSeleccionado(proveedorSolicitado ? String(proveedorSolicitado.id) : "");
          setIngredientePendiente(insumoSolicitado?.nombre ?? "");
          parametrosAplicados.current = true;
        }
        setOferta((actual) => ({ ...actual, ingrediente_id: actual.ingrediente_id || insumoSolicitado?.id || insumos.find((i) => i.activo)?.id || 0 }));
      })
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
  useEffect(() => {
    setPruebas([]); setRevisionChat(false); setErrorPruebas(""); setHistorialListo(false); solicitudPrueba.current = null;
    if (!admin || !seleccionado) return;
    const control = new AbortController(); setCargandoPruebas(true);
    listarPruebasProveedor(token, Number(seleccionado), control.signal)
      .then((lista) => { if (!control.signal.aborted) { setPruebas(lista); setHistorialListo(true); } })
      .catch(() => { if (!control.signal.aborted) setErrorPruebas("No se pudo recuperar el historial de pruebas. Cierra y vuelve a abrir el proveedor antes de enviar."); })
      .finally(() => { if (!control.signal.aborted) setCargandoPruebas(false); });
    return () => control.abort();
  }, [token, admin, seleccionado]);
  async function probarMensaje() {
    if (!proveedor || enviandoPrueba.current) return;
    enviandoPrueba.current = true; setGuardando(true); setErrorPruebas("");
    const entrada = solicitudPrueba.current ?? { clave_idempotencia: `prueba-${crypto.randomUUID()}`, chat_id_revisado: proveedor.chat_id_pruebas ?? "", confirmar_revision_chat: revisionChat };
    solicitudPrueba.current = entrada;
    try {
      const resultado = await enviarPruebaProveedor(token, proveedor.id, entrada);
      setPruebas((actuales) => [resultado, ...actuales.filter((p) => p.id !== resultado.id)].slice(0, 10));
      solicitudPrueba.current = null; setRevisionChat(false);
    } catch (fallo) {
      if (fallo instanceof HttpError && fallo.status >= 400 && fallo.status < 500) {
        solicitudPrueba.current = null;
        setErrorPruebas(fallo.message);
      } else setErrorPruebas("No se pudo obtener el resultado. Consulta tu chat. Pulsa Consultar resultado para recuperar esta misma prueba sin volver a transmitirla.");
    } finally { setGuardando(false); enviandoPrueba.current = false; }
  }
  const baseOferta = ingredientes.find((i) => i.id === oferta.ingrediente_id)?.unidad_base ?? "unidad";
  const unidadFactor = unidadContenido || unidadesEntrada(baseOferta)[0];
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
      else setMensaje("Confirma el chat para vincularlo al proveedor.");
    } catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo buscar tu chat."); }
    finally { setGuardando(false); }
  }
  async function operar(accion: () => Promise<unknown>, texto: string) {
    setGuardando(true); setError(""); setMensaje("");
    try { await accion(); setMensaje(texto); setRevision((r) => r + 1); }
    catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo guardar la operación."); }
    finally { setGuardando(false); }
  }
  function registrar(evento: FormEvent<HTMLFormElement>) { evento.preventDefault(); void operar(async () => { const creado = await crearProveedor(token, nuevo); setSeleccionado(String(creado.id)); setNuevo({ nombre: "" }); setCreando(false); setAgregandoInsumo(Boolean(ingredientePendiente)); }, "Proveedor registrado con código automático."); }
  function registrarOferta(evento: FormEvent<HTMLFormElement>) { evento.preventDefault(); void operar(async () => {
    await crearOferta(token, Number(seleccionado), { ...oferta, factor_conversion: aUnidadBase(oferta.factor_conversion, unidadFactor, baseOferta) });
    const asignados = new Set([...ofertas.filter((o) => o.activa).map((o) => o.ingrediente_id), oferta.ingrediente_id]);
    const siguiente = ingredientes.find((i) => i.activo && !asignados.has(i.id));
    setOferta({ ...ofertaVacia, ingrediente_id: siguiente?.id ?? oferta.ingrediente_id }); setUnidadContenido("");
  }, "Insumo registrado para este proveedor. Puedes añadir otro sin volver a registrar al proveedor."); }
  const visibles = proveedores.filter((p) => (estado === "todos" || p.activo === (estado === "activos")) &&
    `${p.nombre} ${p.codigo} ${p.ingredientes.map((i) => i.nombre).join(" ")}`.toLocaleLowerCase().includes(busqueda.trim().toLocaleLowerCase()));
  const columnas: Columna<Proveedor>[] = [
    { clave: "nombre", encabezado: "Proveedor", celda: (p) => <><strong>{p.nombre}</strong><small className="helper-text">{p.codigo}</small></> },
    { clave: "insumos", encabezado: "Ingredientes que suministra", celda: (p) => p.ingredientes.length ? <div className="supplier-ingredients">{p.ingredientes.map((i) => <span className="badge badge-neutral" key={i.id}>{i.nombre}</span>)}</div> : <span className="helper-text">Sin ingredientes configurados</span> },
    { clave: "estado", encabezado: "Estado", celda: (p) => <span className={`badge badge-${p.activo ? "ok" : "neutral"}`}>{p.activo ? "Activo" : "Inactivo"}</span> },
    { clave: "destino", encabezado: "Telegram", celda: (p) => p.destino_verificado ? "Destino verificado" : p.chat_id_pruebas ? "Pendiente de verificar" : "Sin chat vinculado" },
    { clave: "gestion", encabezado: "Acciones", celda: (p) => <button type="button" className="button-link" aria-label={`${admin ? "Gestionar" : "Ver detalle de"} ${p.nombre}`} onClick={() => { setSeleccionado(String(p.id)); setAgregandoInsumo(Boolean(ingredientePendiente)); setError(""); setMensaje(""); }}>{admin ? "Gestionar" : "Ver detalle"}</button> },
  ];
  return <>
    {error && <EstadoPanel tono="alerta" titulo="Revisa la operación" descripcion={error} />}{mensaje && <p role="status" className="inline-success">{mensaje}</p>}
    <section className="card main-card supplier-list"><div className="section-heading"><div><h2>Proveedores registrados</h2><p>Consulta quién suministra cada ingrediente y gestiona sus datos y conexión.</p></div><div className="form-actions">{admin && <button type="button" className="button-primary" onClick={() => { setCreando(true); setNuevo({ nombre: "" }); setError(""); }}>Crear proveedor</button>}<button type="button" className="button-secondary" disabled={cargando || guardando} onClick={() => setRevision((r) => r + 1)}>Actualizar</button></div></div>
      {ingredientePendiente && <p className="helper-text">Configura quién suministra {ingredientePendiente}: abre un proveedor existente o crea uno nuevo.</p>}
      <div className="form-grid"><CampoTexto id="buscar-proveedor" etiqueta="Buscar proveedor o ingrediente" valor={busqueda} onCambio={setBusqueda} /><CampoSelect id="estado-proveedor" etiqueta="Mostrar proveedores" valor={estado} onCambio={setEstado} opciones={[{ valor: "activos", texto: "Activos" }, { valor: "inactivos", texto: "Inactivos" }, { valor: "todos", texto: "Todos" }]} /></div>
      <TablaDatos columnas={columnas} filas={visibles} idFila={(p) => p.id} cargando={cargando} vacioTitulo={proveedores.length ? "No hay proveedores que coincidan" : "Todavía no hay proveedores"} vacioDescripcion={proveedores.length ? "Prueba con otro nombre, ingrediente o estado." : "Pulsa Crear proveedor para registrar el primero y añadir los ingredientes que suministra."} pie={`${visibles.length} de ${proveedores.length} proveedores`} />
    </section>
    {admin && <section className="card section-space"><div className="section-heading"><div><h2>Conexión de Telegram</h2><p>{telegram?.configurado ? "Bot configurado. Vincula y prueba el chat desde la gestión de cada proveedor." : "Configura el bot para conectar los chats de tus proveedores."}</p></div><button type="button" className="button-secondary" onClick={() => { setConfigurandoTelegram(true); setError(""); }}>Configurar Telegram</button></div></section>}
    {admin && configurandoTelegram && <PanelDetalle titulo="Configurar Telegram" ocupado={guardando} onCerrar={() => { setConfigurandoTelegram(false); setCredencial(""); }}><section className="card section-space"><h3>Conectar el bot</h3>
      {error && <EstadoPanel tono="alerta" titulo="Revisa Telegram" descripcion={error} />}{mensaje && <p role="status">{mensaje}</p>}
      <ol><li>Crea tu bot en <a href="https://t.me/BotFather" target="_blank" rel="noreferrer">BotFather</a> con <code>/newbot</code> y copia su token.</li>
      <li>Guárdalo aquí. FoodSave comprobará la identidad del bot con Telegram.</li>
      <li>Abre el chat de tu bot y pulsa Iniciar o escribe <code>/start</code>. También puedes añadirlo a un grupo.</li>
      <li>Selecciona el proveedor, pulsa Buscar mi chat, vincula el destino y verifícalo.</li></ol>
      <p role="status">{telegram ? `${telegram.configurado ? "Token configurado" : "Sin token disponible"} · ${telegram.detalle}` : "Consultando configuración…"}</p>
      {telegram?.bot && <p>Bot: {telegram.bot.nombre} · @{telegram.bot.username} · ID {telegram.bot.id}</p>}
      <details open={telegram?.configurado === false}><summary>{telegram?.configurado ? "Cambiar el token del bot" : "Configurar token del bot"}</summary><form onSubmit={(e) => { e.preventDefault(); void operarTelegram(() => guardarTelegram(token, credencial)); }}>
        <CampoTexto id="telegram-token" etiqueta="Token del bot" tipo="password" autoComplete="off" valor={credencial} requerido deshabilitado={guardando}
          onCambio={setCredencial} ayuda="Se guarda cifrado en el servidor. El token guardado nunca se devuelve; este campo queda vacío después de comprobarlo." />
        <BotonEnviar enviando={guardando} textoEnviando="Comprobando…">Guardar y comprobar bot</BotonEnviar>
      </form></details>
      <button type="button" className="button-secondary" disabled={guardando || !telegram?.configurado} onClick={() => void operarTelegram(() => comprobarTelegram(token))}>Comprobar bot guardado</button>{" "}
      <button type="button" className="button-secondary" disabled={guardando || !telegram?.configurado} onClick={() => void operarTelegram(() => deshabilitarTelegram(token))}>Deshabilitar Telegram</button>
      <p className="helper-text">Comprobar el bot no envía mensajes. El envío de pedidos está disponible en Compras y en las tareas programadas.</p>
    </section></PanelDetalle>}
    {proveedor && <PanelDetalle titulo={proveedor.nombre} ocupado={guardando} onCerrar={() => { setSeleccionado(""); setAgregandoInsumo(false); }}><section className="card section-space">
      {error && <EstadoPanel tono="alerta" titulo="Revisa la operación" descripcion={error} />}{mensaje && <p role="status" className="inline-success">{mensaje}</p>}
      {proveedor && <><p>{proveedor.activo ? "Activo" : "Inactivo"} · Destino {proveedor.destino_verificado ? "verificado" : "sin verificar"}</p>{admin && <button type="button" className="button-secondary" disabled={guardando} onClick={() => void operar(() => cambiarEstadoProveedor(token, proveedor.id, !proveedor.activo), "Estado actualizado.")}>{proveedor.activo ? "Desactivar proveedor" : "Activar proveedor"}</button>}
        <div className="section-heading section-space"><div><h3>Ingredientes que suministra</h3><p>Añade cada ingrediente con su presentación y contenido.</p></div>{admin && <button type="button" className="button-secondary" disabled={guardando} onClick={() => setAgregandoInsumo((actual) => !actual)}>{agregandoInsumo ? "Cerrar formulario de insumo" : "Añadir ingrediente"}</button>}</div><TablaPaginada><thead><tr><th>Ingrediente / oferta</th><th>Unidad de compra</th><th>Contenido por presentación</th><th>Compra mínima / grupos</th><th>Estado</th>{admin && <th>Acciones</th>}</tr></thead><tbody>{ofertas.map((o) => <tr key={o.id}><td>{ingredientes.find((i) => i.id === o.ingrediente_id)?.nombre ?? `#${o.ingrediente_id}`} · {o.descripcion}</td><td>{o.unidad_compra}</td><td>{cantidadVisible(o.factor_conversion, ingredientes.find((i) => i.id === o.ingrediente_id)?.unidad_base ?? "")}</td><td>{o.minimo} / {o.multiplo}</td><td>{o.activa ? o.preferida ? "Preferida" : "Activa" : "Inactiva"}</td>{admin && <td>{o.activa && <><button type="button" className="button-link" disabled={guardando || o.preferida} onClick={() => void operar(() => marcarPreferida(token, o.id), "Oferta preferida actualizada.")}>Usar preferida</button><button type="button" className="button-link" disabled={guardando} onClick={() => void operar(() => desactivarOferta(token, o.id), "Oferta desactivada.")}>Desactivar</button></>}</td>}</tr>)}</tbody></TablaPaginada>{ofertas.length === 0 && <p>Este proveedor todavía no tiene insumos configurados.</p>}
    {admin && agregandoInsumo && ingredientes.some((i) => i.activo) && <section id="registrar-oferta" className="card section-space"><h3>Añadir insumo a {proveedor.nombre}</h3><p>Registra cómo te vende este insumo. Puedes repetir este paso para otros insumos del mismo proveedor.</p><form onSubmit={registrarOferta}><div className="form-grid">
      <CampoSelect id="oferta-ingrediente" etiqueta="Ingrediente" valor={String(oferta.ingrediente_id)} deshabilitado={guardando} opciones={ingredientes.filter((i) => i.activo).map((i) => ({ valor: String(i.id), texto: i.nombre }))} onCambio={(id) => { setOferta({ ...oferta, ingrediente_id: Number(id), factor_conversion: "" }); setUnidadContenido(""); }} />
      {([['descripcion','Nombre de la oferta'],['unidad_compra','Presentación que compras (kg, bolsa, caja…)'],['factor_conversion','Contenido de una presentación'],['minimo','Cantidad mínima de presentaciones'],['multiplo','Comprar en grupos de']] as const).map(([campo, etiqueta]) => <CampoTexto key={campo} id={`oferta-${campo}`} etiqueta={etiqueta} requerido valor={oferta[campo]} deshabilitado={guardando} onCambio={(valor) => setOferta({ ...oferta, [campo]: valor })} />)}
      <CampoSelect id="oferta-unidad-contenido" etiqueta="Unidad del contenido" valor={unidadFactor} deshabilitado={guardando} opciones={unidadesEntrada(baseOferta).map((u) => ({ valor: u, texto: u === "l" ? "Litros (L)" : u === "kg" ? "Kilogramos (kg)" : u === "unidad" ? "Unidades" : u }))} onCambio={setUnidadContenido} />
      <CampoSelect id="oferta-preferida" etiqueta="Oferta preferida" valor={oferta.preferida ? "si" : "no"} deshabilitado={guardando} opciones={[{ valor: "si", texto: "Sí" }, { valor: "no", texto: "No" }]} onCambio={(valor) => setOferta({ ...oferta, preferida: valor === "si" })} />
    </div><p className="helper-text">Ejemplo: bolsa de 1 kg → contenido 1, unidad kg. Mínimo 0 y grupos de 1 permiten pedir bolsas individuales. El sistema convierte el contenido a la unidad del ingrediente.</p><BotonEnviar enviando={guardando} textoEnviando="Registrando…">Guardar insumo y añadir otro</BotonEnviar></form></section>}
        {admin && <details className="section-space"><summary>Configurar o cambiar el chat</summary>
          <p>Escribe <code>/start</code> al bot de FoodSave desde el chat que recibirá los pedidos y busca su identificador aquí.</p>
          <button type="button" className="button-secondary" disabled={guardando || !telegram?.configurado} onClick={() => void buscarChats()}>Buscar mi chat</button>
          {chatsEncontrados.length > 0 && <ul>{chatsEncontrados.map((destino) => <li key={destino.chat_id}><button type="button" className="button-link" disabled={guardando} onClick={() => { setChat(destino.chat_id); setChatPropio(false); }}>Usar chat {destino.chat_id} ({destino.tipo === "private" ? "privado" : "grupo"})</button></li>)}</ul>}
          <form onSubmit={(e) => { e.preventDefault(); if (chatPropio) void operar(() => vincularChat(token, proveedor.id, chat), "Chat vinculado. Verifica el destino para comprobar su acceso."); }}>
            <CampoTexto id="chat" etiqueta="Identificador de tu chat (chat_id)" valor={chat} requerido deshabilitado={guardando} onCambio={(valor) => { setChat(valor); setChatPropio(false); }} ayuda={`Guardado: ${proveedor.chat_id_pruebas ?? "sin vincular"}. Pulsa Buscar mi chat para encontrarlo; no es tu teléfono ni @usuario.`} />
            <label><input type="checkbox" checked={chatPropio} disabled={guardando} onChange={(e) => setChatPropio(e.target.checked)} /> Confirmo que este chat es el destino correcto para los pedidos.</label>
            <BotonEnviar enviando={guardando} textoEnviando="Guardando…" deshabilitado={!chatPropio}>Vincular chat</BotonEnviar>
          </form>
          <button type="button" className="button-secondary" disabled={guardando || !proveedor.chat_id_pruebas || chat.trim() !== proveedor.chat_id_pruebas} onClick={() => void verificarChat()}>Verificar chat vinculado</button>
          {proveedor.destino_verificado_en && <p>Verificado: {new Date(proveedor.destino_verificado_en).toLocaleString("es-CO")}</p>}
          <p className="helper-text">Verificar comprueba acceso y permisos del bot. No envía mensajes ni acredita la entrega de un pedido.</p>
          {proveedor.destino_verificado && <EstadoPanel tono="ok" titulo="Tu chat está preparado" descripcion="Vuelve a Compras y pulsa Actualizar estado del destino si tenías un pedido bloqueado. Para un plan nuevo puedes programar el envío automático." accion={<Link href="/compras" className="button-primary">Continuar en Compras →</Link>} />}
        </details>}
        {admin && <section className="section-space"><h3>Probar envío de mensaje</h3><p>Destino: <strong>{proveedor.chat_id_pruebas ?? "Sin chat vinculado"}</strong> · Telegram</p><p className="helper-text">Se enviará: «{negocio.nombre} · Mensaje de prueba de FoodSave. Este mensaje comprueba la conexión de Telegram. No corresponde a un pedido.»</p>
          {!proveedor.destino_verificado && <p>Vincula y verifica el chat antes de enviar una prueba.</p>}
          {pruebas[0]?.estado === "PENDIENTE_VERIFICACION" && <label><input type="checkbox" checked={revisionChat} disabled={guardando} onChange={(e) => setRevisionChat(e.target.checked)} /> He revisado mi chat y autorizo una nueva prueba.</label>}
          {errorPruebas && <p role="alert" className="inline-error">{errorPruebas}</p>}
          <button type="button" className="button-primary" disabled={guardando || cargandoPruebas || !historialListo || (!solicitudPrueba.current && (!proveedor.activo || !proveedor.destino_verificado || (pruebas[0]?.estado === "PENDIENTE_VERIFICACION" && !revisionChat)))} onClick={() => void probarMensaje()}>{guardando ? "Consultando Telegram…" : solicitudPrueba.current ? "Consultar resultado" : pruebas.length ? "Enviar otra prueba" : "Enviar mensaje de prueba"}</button>
          {pruebas[0] && <EstadoPanel tono={pruebas[0].estado === "ENVIADO" ? "ok" : "alerta"} titulo={pruebas[0].estado === "ENVIADO" ? "Mensaje enviado" : pruebas[0].estado === "FALLIDO" ? "Envío rechazado" : "Envío sin confirmar"} descripcion={`${pruebas[0].detalle}${pruebas[0].message_id ? ` ID del mensaje: ${pruebas[0].message_id}.` : ""}`} />}
          {!!pruebas.length && <details><summary>Últimas pruebas</summary><ul>{pruebas.map((p) => <li key={p.id}>{new Date(p.creado_en).toLocaleString("es-PE")} · Chat {p.chat_id} · {p.estado === "ENVIADO" ? "Enviado" : p.estado === "FALLIDO" ? "Rechazado" : "Sin confirmar"}{p.message_id ? ` · Mensaje ${p.message_id}` : ""}</li>)}</ul></details>}
        </section>}
      </>}
    </section>

    </PanelDetalle>}
    {admin && creando && <PanelDetalle titulo="Crear proveedor" ocupado={guardando} onCerrar={() => setCreando(false)}><p>El código se asigna automáticamente al guardar. Después podrás añadir los ingredientes que suministra y probar su conexión.</p>{error && <EstadoPanel tono="alerta" titulo="Revisa el proveedor" descripcion={error} />}<form onSubmit={registrar}><CampoTexto id="proveedor-nombre" etiqueta="Nombre del proveedor" requerido valor={nuevo.nombre} deshabilitado={guardando} onCambio={(nombre) => setNuevo({ nombre })} /><div className="form-actions"><button type="button" className="button-secondary" disabled={guardando} onClick={() => setCreando(false)}>Cancelar</button><BotonEnviar enviando={guardando} textoEnviando="Registrando…">Crear proveedor</BotonEnviar></div></form></PanelDetalle>}
  </>;
}
export default function PaginaProveedores() { return <ProtectedShell titulo="Proveedores" descripcion="Ofertas, conversiones y destinos de los pedidos.">{(contexto) => <Contenido contexto={contexto} />}</ProtectedShell>; }
