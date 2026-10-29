"use client";
import { useEffect, useRef, useState } from "react";
import type { ContextoSesion } from "@/components/layout/ProtectedShell";
import { PanelDetalle } from "@/components/ui/PanelDetalle";
import { TablaDatos } from "@/components/tables/TablaDatos";
import { HttpError } from "@/services/http";
import { contextoEntradas, detalleEntrada, listarEntradas, recuperarEntrada, registrarEntrada } from "@/services/inventario";
import type { ContextoEntradas, DetalleEntrada, LineaEntrada, ResumenEntrada, SolicitudEntrada } from "@/types/inventario";
import { formatearEscenario, formatearFechaHora } from "@/utils/fechas";

type Fila = Omit<LineaEntrada, "producto_id" | "cantidad"> & { uid: string; producto_id: string; cantidad: string };
function dias(fecha: string, n: number) {
  const d = new Date(`${fecha}T12:00:00Z`);
  if (Number.isNaN(d.getTime())) return "";
  d.setUTCDate(d.getUTCDate()+n); return d.toISOString().slice(0,10);
}
function fila(fecha: string, vida: number): Fila {
  const uid = crypto.randomUUID();
  return { uid, producto_id:"", cantidad:"1", codigo_lote:`ENT-${fecha.replaceAll("-","")}-${uid.slice(0,8).toUpperCase()}`,
    fecha_elaboracion:fecha, fecha_caducidad:dias(fecha,vida-1), fecha_limite_venta:dias(fecha,vida-1) };
}

export function EntradasProductos({ contexto, onActualizar }: { contexto: ContextoSesion; onActualizar: (fecha: string, productos: boolean) => void }) {
  const { token, perfil, negocio } = contexto;
  const admin = perfil.rol === "ADMINISTRADOR", almacen = `foodsave:entrada:pendiente:${perfil.id}`;
  const [datos, setDatos] = useState<ContextoEntradas | null>(null);
  const [revision, setRevision] = useState(0), [pagina,setPagina] = useState(1), [tamano,setTamano] = useState(10);
  const [historial,setHistorial] = useState<ResumenEntrada[]>([]), [total,setTotal] = useState(0), [cargando,setCargando] = useState(true);
  const [error,setError] = useState(""), [mensaje,setMensaje] = useState(""), [ocupado,setOcupado] = useState(false);
  const [nueva,setNueva] = useState(false), [revisando,setRevisando] = useState(false), [detalle,setDetalle] = useState<DetalleEntrada | null>(null);
  const [fecha,setFecha] = useState(""), [motivo,setMotivo] = useState(""), [lineas,setLineas] = useState<Fila[]>([]);
  const [pendiente,setPendiente] = useState<SolicitudEntrada | null>(null);
  const confirmando = useRef(false);
  useEffect(() => {
    const c = new AbortController();
    contextoEntradas(token,c.signal).then(d => { if (!c.signal.aborted) { setDatos(d); onActualizar(d.fecha_actual,false); } })
      .catch(e => { if (!c.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo leer el catálogo de entradas."); });
    return () => c.abort();
  }, [token,onActualizar]);
  useEffect(() => {
    const c = new AbortController(); setCargando(true);
    listarEntradas(token,new URLSearchParams({limite:String(tamano),desplazamiento:String((pagina-1)*tamano)}),c.signal)
      .then(r => { if (!c.signal.aborted) { setHistorial(r.datos); setTotal(Number(r.metadatos?.total ?? 0)); } })
      .catch(e => { if (!c.signal.aborted) setError(e instanceof Error ? e.message : "No se pudo leer el historial de entradas."); })
      .finally(() => { if (!c.signal.aborted) setCargando(false); });
    return () => c.abort();
  }, [token,pagina,tamano,revision]);
  useEffect(() => {
    let activa = true;
    try {
      const guardada = sessionStorage.getItem(almacen);
      if (guardada) {
        const p = JSON.parse(guardada) as SolicitudEntrada; setPendiente(p);
        recuperarEntrada(token,p.clave_operacion).then(e => {
          if (!activa) return;
          sessionStorage.removeItem(almacen); setPendiente(null); setDetalle(e); setMensaje(`Entrada ${e.numero} recuperada. Las unidades ya estaban registradas.`);
          setRevision(v=>v+1); onActualizar(e.fecha_entrada,true);
        }).catch(()=> { if (activa) setMensaje("Hay una entrada pendiente de respuesta; conserva esta pestaña y recupera la misma operación."); });
      }
    } catch { setError("No se pudo leer la recuperación de entradas en este navegador."); }
    return () => { activa=false; };
  }, [token,almacen,onActualizar]);
  function abrir() {
    setError(""); setMensaje(""); setNueva(true);
    if (!pendiente && datos) { setFecha(datos.fecha_actual); setMotivo(""); setLineas([fila(datos.fecha_actual,datos.vida_maxima_dias)]); setRevisando(false); }
  }
  function cambiar(uid: string, cambio: Partial<Fila>) { setLineas(ls=>ls.map(l=>l.uid===uid ? {...l,...cambio} : l)); }
  function solicitud(): SolicitudEntrada {
    if (!fecha || motivo.trim().length<3 || !lineas.length) throw new Error("Completa fecha, motivo y al menos un lote.");
    const filas = lineas.map(l=> {
      if (!l.producto_id || !/^[1-9]\d*$/.test(l.cantidad) || Number(l.cantidad)>1000000 || !l.codigo_lote.trim()) throw new Error("Cada lote necesita producto, cantidad entera positiva y código.");
      if (!l.fecha_elaboracion || !l.fecha_limite_venta || !l.fecha_caducidad || l.fecha_elaboracion>fecha || fecha>l.fecha_limite_venta || l.fecha_limite_venta>l.fecha_caducidad || l.fecha_caducidad>dias(l.fecha_elaboracion,(datos?.vida_maxima_dias ?? 5)-1)) throw new Error("Revisa las fechas de los lotes: elaboración ≤ entrada ≤ límite de venta ≤ caducidad, con vida máxima de cinco días.");
      return {producto_id:Number(l.producto_id),cantidad:Number(l.cantidad),codigo_lote:l.codigo_lote.trim(),fecha_elaboracion:l.fecha_elaboracion,fecha_limite_venta:l.fecha_limite_venta,fecha_caducidad:l.fecha_caducidad};
    });
    if (new Set(filas.map(l=>JSON.stringify([l.producto_id,l.codigo_lote]))).size!==filas.length) throw new Error("No repitas el mismo lote de un producto.");
    return {clave_operacion:`entrada-${crypto.randomUUID()}`,fecha_entrada:fecha,motivo:motivo.trim(),lineas:filas};
  }
  async function confirmar() {
    if (confirmando.current) return;
    confirmando.current=true; setOcupado(true); setError("");
    try {
      const cuerpo = pendiente ?? solicitud();
      if (!pendiente) { sessionStorage.setItem(almacen,JSON.stringify(cuerpo)); setPendiente(cuerpo); }
      const e = await registrarEntrada(token,cuerpo);
      sessionStorage.removeItem(almacen); setPendiente(null); setNueva(false); setDetalle(e); setRevisando(false);
      setMensaje(`Entrada ${e.numero} registrada. Los lotes ya están en Inventario.`); setPagina(1); setRevision(v=>v+1); onActualizar(e.fecha_entrada,true);
    } catch(e) {
      if (e instanceof HttpError && e.status>=400 && e.status<500 && e.status!==401) { sessionStorage.removeItem(almacen); setPendiente(null); setRevisando(false); }
      setError(e instanceof Error ? e.message : "No se confirmó la respuesta. Reintenta la misma entrada.");
    } finally { confirmando.current=false; setOcupado(false); }
  }
  async function ver(id: number) {
    setOcupado(true); setError("");
    try { setDetalle(await detalleEntrada(token,id)); }
    catch(e) { setError(e instanceof Error ? e.message : "No se pudo abrir la entrada."); }
    finally { setOcupado(false); }
  }
  const aviso = error && <p role="alert" className="inline-error">{error}</p>;
  return <>
    <section className="card section-space">
      <div className="section-heading"><div><h2>Entradas de productos</h2><p>Registra existencias nuevas de varios productos o lotes en una sola entrada.</p></div><div className="form-actions"><button className="button-secondary" disabled={!datos || ocupado} onClick={()=>datos && onActualizar(datos.fecha_actual,false)}>Ver stock de hoy</button>{admin && <button className="button-primary" disabled={ocupado || (!datos && !pendiente)} onClick={abrir}>{pendiente ? "Resolver entrada pendiente" : "Registrar entrada"}</button>}</div></div>
      {!nueva && !detalle && aviso}{mensaje && <p role="status" className="inline-success">{mensaje}</p>}
      {pendiente && <p role="status" className="inline-error">Se conserva una confirmación pendiente; reintentar usa la misma solicitud y no duplica unidades.</p>}
      <details><summary>Historial de entradas · {total}</summary><TablaDatos filas={historial} idFila={e=>e.id} cargando={cargando} vacioTitulo="Todavía no hay entradas de productos" vacioDescripcion="Aquí aparecerán las nuevas entradas, con su responsable, lotes y cantidades." paginacion={{pagina,tamano,total,cargando,onCambio:(p,t)=>{setPagina(p);setTamano(t);}}} columnas={[
        {clave:"numero",encabezado:"Entrada",celda:e=><strong>{e.numero}</strong>}, {clave:"fecha",encabezado:"Fecha de entrada",celda:e=>formatearEscenario(e.fecha_entrada)},
        {clave:"lotes",encabezado:"Lotes",celda:e=>e.lotes}, {clave:"unidades",encabezado:"Unidades",celda:e=>e.unidades},
        {clave:"autor",encabezado:"Registró",celda:e=>e.nombre_usuario}, {clave:"detalle",encabezado:"Detalle",celda:e=><button className="button-link" disabled={ocupado} onClick={()=>void ver(e.id)}>Ver entrada</button>}
      ]} /></details>
    </section>
    {nueva && <PanelDetalle titulo={pendiente ? "Recuperar entrada pendiente" : "Registrar entrada de productos"} ocupado={ocupado} onCerrar={()=>setNueva(false)}>{aviso}
      {pendiente ? <><p>Confirma o recupera la misma entrada del {formatearEscenario(pendiente.fecha_entrada)}, con {pendiente.lineas.length} lote(s). No cambies de pestaña ni borres su almacenamiento mientras siga pendiente.</p><button className="button-primary" disabled={ocupado} onClick={()=>void confirmar()}>Recuperar o confirmar la misma entrada</button></> : revisando ? <>
        <h3>Revisa tu entrada</h3><p>{formatearEscenario(fecha)} · {motivo}</p><ul>{lineas.map(l=><li key={l.uid}><strong>{datos?.productos.find(p=>p.id===Number(l.producto_id))?.nombre}</strong> · {l.cantidad} u. · {l.codigo_lote}<br/><small>Elaborado {formatearEscenario(l.fecha_elaboracion)} · Venta hasta {formatearEscenario(l.fecha_limite_venta)} · Caduca {formatearEscenario(l.fecha_caducidad)}</small></li>)}</ul><p>Se registrarán todos los lotes juntos. Cada uno conservará sus fechas y movimiento de entrada.</p><div className="form-actions"><button className="button-secondary" disabled={ocupado} onClick={()=>setRevisando(false)}>Editar entrada</button><button className="button-primary" disabled={ocupado} onClick={()=>void confirmar()}>Confirmar entrada</button></div>
      </> : <form onSubmit={e=>{e.preventDefault();setError("");try {solicitud();setRevisando(true);} catch(f) {setError(f instanceof Error ? f.message : "Revisa los datos.");}}}>
        <p>Elige productos del catálogo. Puedes repetir un producto con códigos de lote distintos. Se registran productos terminados recibidos; no se consumen ingredientes.</p>
        <div className="form-grid"><label className="field">Fecha de entrada<input required type="date" max={datos?.fecha_actual} value={fecha} onChange={e=>setFecha(e.target.value)} /></label><label className="field">Motivo<input required minLength={3} maxLength={300} value={motivo} onChange={e=>setMotivo(e.target.value)} placeholder="Ej. Ingreso de productos del día" /></label></div>
        {lineas.map((l,i)=><fieldset className="entry-line" key={l.uid}><legend>Lote {i+1}</legend><div className="form-grid">
          <label className="field">Producto<select required value={l.producto_id} onChange={e=>cambiar(l.uid,{producto_id:e.target.value})}><option value="">Elige un producto</option>{datos?.productos.map(p=><option value={p.id} key={p.id}>{p.nombre} · {p.codigo}</option>)}</select></label>
          <label className="field">Cantidad (unidades)<input required type="number" min={1} max={1000000} step={1} value={l.cantidad} onChange={e=>cambiar(l.uid,{cantidad:e.target.value})}/></label>
          <label className="field">Código de lote<input required maxLength={80} value={l.codigo_lote} onChange={e=>cambiar(l.uid,{codigo_lote:e.target.value})}/></label>
          <label className="field">Fecha de elaboración<input required type="date" max={fecha} value={l.fecha_elaboracion} onChange={e=>cambiar(l.uid,{fecha_elaboracion:e.target.value})}/></label>
          <label className="field">Límite de venta<input required type="date" min={fecha} max={l.fecha_caducidad} value={l.fecha_limite_venta} onChange={e=>cambiar(l.uid,{fecha_limite_venta:e.target.value})}/></label>
          <label className="field">Caducidad<input required type="date" min={fecha} max={dias(l.fecha_elaboracion,(datos?.vida_maxima_dias ?? 5)-1)} value={l.fecha_caducidad} onChange={e=>cambiar(l.uid,{fecha_caducidad:e.target.value})}/></label>
        </div><button type="button" className="button-link" disabled={lineas.length===1} onClick={()=>setLineas(ls=>ls.filter(x=>x.uid!==l.uid))}>Quitar lote {i+1}</button></fieldset>)}
        {!datos?.productos.length && <p role="status">No hay productos activos. Revisa el catálogo antes de registrar una entrada.</p>}
        <div className="form-actions"><button type="button" className="button-secondary" disabled={lineas.length>=100 || !datos} onClick={()=>datos && setLineas(ls=>[...ls,fila(fecha,datos.vida_maxima_dias)])}>Agregar otro lote</button><button type="submit" className="button-primary" disabled={!datos?.productos.length}>Revisar entrada</button></div>
      </form>}
    </PanelDetalle>}
    {detalle && <PanelDetalle titulo={`Entrada ${detalle.numero}`} ocupado={ocupado} onCerrar={()=>{setDetalle(null);setError("");}}>{aviso}<p>Fecha de entrada: <strong>{formatearEscenario(detalle.fecha_entrada)}</strong> · Registró {detalle.nombre_usuario}</p><p>{detalle.motivo}</p><p className="helper-text">Registro: {formatearFechaHora(detalle.creado_en,negocio.zona_horaria)}</p><TablaDatos filas={detalle.lineas} idFila={l=>l.id} columnas={[
      {clave:"producto",encabezado:"Producto",celda:l=>l.nombre_producto}, {clave:"lote",encabezado:"Lote",celda:l=>l.codigo_lote}, {clave:"cantidad",encabezado:"Unidades ingresadas",celda:l=>l.cantidad},
      {clave:"elaboracion",encabezado:"Elaboración",celda:l=>formatearEscenario(l.fecha_elaboracion)}, {clave:"limite",encabezado:"Límite de venta",celda:l=>formatearEscenario(l.fecha_limite_venta)}, {clave:"caducidad",encabezado:"Caducidad",celda:l=>formatearEscenario(l.fecha_caducidad)},
      {clave:"movimiento",encabezado:"Movimiento",celda:l=>`#${l.movimiento_id}`}
    ]}/><p className="helper-text">Las cantidades de esta entrada se conservan como historial. El saldo actual se consulta en Inventario.</p></PanelDetalle>}
  </>;
}
