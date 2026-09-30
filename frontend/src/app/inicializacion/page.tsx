"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { PasosAsistente } from "@/components/ui/PasosAsistente";
import { ValorOpcional } from "@/components/ui/ValorOpcional";
import { CampoArchivo } from "@/components/forms/CampoArchivo";
import { CampoFecha } from "@/components/forms/CampoFecha";
import { CampoTexto } from "@/components/forms/CampoTexto";
import { BotonEnviar } from "@/components/forms/BotonEnviar";
import { ResumenErrores } from "@/components/forms/ResumenErrores";
import { confirmarCarga, obtenerEstadoInicial, pedirVistaPrevia, reintentarPreparacion } from "@/services/inicializacion";
import type { ConfiguracionInicial, InformeCarga, VistaPrevia } from "@/types/inicializacion";
import { formatearFechaHora } from "@/utils/fechas";

const PASOS = [
  { titulo: "Elegir archivos y fechas", detalle: "Dos libros XLSX o los cinco CSV, más las fechas del escenario." },
  { titulo: "Revisar la vista previa", detalle: "Filas, productos, fechas cubiertas y errores por fila. No se guarda nada." },
  { titulo: "Aceptar la carga", detalle: "Se persiste todo en una transacción; un fallo no deja datos a medias." },
];

const ETIQUETAS: Record<ConfiguracionInicial["estado"], string> = {
  PENDIENTE: "Pendiente",
  DATOS_CARGADOS: "Datos cargados",
  ENTRENANDO: "Entrenando",
  MODELO_LISTO: "Modelo listo",
  FALLIDA: "Fallida",
};

const TONOS: Record<ConfiguracionInicial["estado"], "neutral" | "info" | "ok" | "alerta"> = {
  PENDIENTE: "neutral",
  DATOS_CARGADOS: "info",
  ENTRENANDO: "info",
  MODELO_LISTO: "ok",
  FALLIDA: "alerta",
};

/** Los cinco CSV del contrato; con XLSX son `ventas.xlsx` y `catalogo.xlsx`. */
const RANURAS = [
  { clave: "ventas", etiqueta: "Ventas", ayuda: "ventas.csv o ventas.xlsx. Acepta también el CSV de tickets del piloto." },
  { clave: "productos", etiqueta: "Productos", ayuda: "productos.csv, o la hoja del catálogo si usas XLSX." },
  { clave: "ingredientes", etiqueta: "Ingredientes", ayuda: "ingredientes.csv" },
  { clave: "recetas", etiqueta: "Recetas", ayuda: "recetas.csv" },
  { clave: "stock", etiqueta: "Stock inicial", ayuda: "stock_inicial.csv" },
] as const;

const ESTADOS_TAREA = {
  PENDIENTE: "En espera", EN_EJECUCION: "En curso", REINTENTANDO: "Reintento automático pendiente",
  COMPLETADA: "Completada", FALLIDA: "Fallida",
};

function TarjetaEstado({ estado, administrador, reintentando, alReintentar }: {
  estado: ConfiguracionInicial; administrador: boolean; reintentando: boolean; alReintentar: () => void;
}) {
  const puedeReintentar = estado.preparacion?.estado === "FALLIDA"
    || estado.evaluacion?.estado === "FALLIDA"
    || (estado.estado === "DATOS_CARGADOS" && !estado.preparacion);
  return (
    <section className="card">
      <div className="section-heading">
        <div>
          <h2>Estado de la instalación</h2>
          <p>Una sola instalación, un comercio y una sucursal.</p>
        </div>
        <span className={`badge badge-${TONOS[estado.estado]}`}>{ETIQUETAS[estado.estado]}</span>
      </div>
      <div className="pronostico-meta">
        <div>
          <span>Fecha objetivo de la demo</span>
          <strong><ValorOpcional valor={estado.fecha_objetivo_demo} textoAusente="Sin definir" /></strong>
        </div>
        <div>
          <span>Referencia de stock</span>
          <strong><ValorOpcional valor={estado.fecha_referencia_stock} textoAusente="Sin definir" /></strong>
        </div>
        <div>
          <span>Iniciada</span>
          <strong>{estado.iniciada_en ? formatearFechaHora(estado.iniciada_en) : "Sin iniciar"}</strong>
        </div>
        <div>
          <span>Huella de la solicitud</span>
          <strong className="mono-corto">
            <ValorOpcional valor={estado.huella_solicitud?.slice(0, 16)} textoAusente="Sin carga" />
          </strong>
        </div>
      </div>
      {estado.mensaje_error ? (
        <EstadoPanel tono="alerta" titulo="Preparación pendiente" descripcion={estado.mensaje_error} />
      ) : null}
      {estado.preparacion && <p role="status">Preparación del modelo: {ESTADOS_TAREA[estado.preparacion.estado]} · <Link href={`/automatizaciones/ejecuciones/${estado.preparacion.id}`}>Ver ejecución #{estado.preparacion.id}</Link></p>}
      {estado.evaluacion && <p role="status">Evaluación histórica: {ESTADOS_TAREA[estado.evaluacion.estado]} · <Link href={`/automatizaciones/ejecuciones/${estado.evaluacion.id}`}>Ver ejecución #{estado.evaluacion.id}</Link></p>}
      {estado.evaluacion?.mensaje_error && <EstadoPanel tono="alerta" titulo="La evaluación necesita revisión" descripcion={estado.evaluacion.mensaje_error} />}
      {estado.modelo_id && estado.estado === "MODELO_LISTO" && <p><Link href={`/panel?modelo_id=${estado.modelo_id}`}>Consultar el dashboard del modelo #{estado.modelo_id}</Link></p>}
      {puedeReintentar && administrador && <div className="form-actions"><BotonEnviar type="button" enviando={reintentando} textoEnviando="Solicitando…" onClick={alReintentar}>Preparar modelo sin volver a cargar</BotonEnviar></div>}
    </section>
  );
}

function ResumenVistaPrevia({ vista }: { vista: VistaPrevia }) {
  const { ventas, catalogo, adaptador_bakery: bakery } = vista;
  return (
    <>
      <div className="stats-grid">
        <div className="stat"><span>Ventas diarias</span><strong>{ventas.filas}</strong></div>
        <div className="stat"><span>SKU con ventas</span><strong>{ventas.skus}</strong></div>
        <div className="stat"><span>Productos</span><strong>{catalogo.productos}</strong></div>
        <div className="stat"><span>Líneas de receta</span><strong>{catalogo.lineas_receta}</strong></div>
        <div className="stat"><span>Filas de stock</span><strong>{catalogo.filas_stock}</strong></div>
        <div className="stat">
          <span>Fechas cubiertas</span>
          <strong>
            <ValorOpcional valor={ventas.primera_fecha} /> → <ValorOpcional valor={ventas.ultima_fecha} />
          </strong>
        </div>
      </div>

      {bakery ? (
        <EstadoPanel
          tono="info"
          titulo="Se adaptó el CSV de tickets del piloto"
          descripcion={
            `${bakery.lineas_leidas} líneas leídas de ${bakery.articulos} artículos; ` +
            `${bakery.lineas_negativas_excluidas} negativas excluidas y ${bakery.lineas_invalidas} inválidas. ` +
            `Se agregaron en ${bakery.pares_generados} ventas diarias.`
          }
        />
      ) : null}

      <h3 className="section-space">Productos de la demostración</h3>
      <p className="helper-text">Solo estos participan en el plan; el resto queda en el historial de ventas.</p>
      <ul className="rule-list">
        {catalogo.productos_demo.map((producto) => (
          <li key={producto.codigo}>
            <strong>{producto.nombre}</strong> — <span className="mono-corto">{producto.sku_externo}</span>
          </li>
        ))}
      </ul>
    </>
  );
}

function InformeFinal({ informe }: { informe: InformeCarga }) {
  if (informe.ya_estaba_cargada) {
    return (
      <EstadoPanel
        tono="info"
        titulo="Esta misma solicitud ya estaba aceptada"
        descripcion="Se recuperó el resultado anterior en lugar de cargar otra vez. No se duplicó nada."
      />
    );
  }
  return (
    <>
      <EstadoPanel
        tono={informe.pendiente_de.length ? "info" : "ok"}
        titulo={informe.pendiente_de.length ? "Carga parcial aceptada" : "Primera carga completada"}
        descripcion={
          informe.pendiente_de.length
            ? "Se guardaron catálogo y ventas. La instalación no queda inicializada hasta que lleguen los servicios que faltan."
            : "Catálogo, ventas, recetas y stock de apertura quedaron persistidos. El modelo ya puede prepararse."
        }
      />
      <div className="stats-grid">
        <div className="stat"><span>Productos</span><strong>{informe.productos}</strong></div>
        <div className="stat"><span>Ventas diarias</span><strong>{informe.ventas_diarias}</strong></div>
        <div className="stat"><span>Ingredientes</span><strong>{informe.ingredientes}</strong></div>
        <div className="stat"><span>Líneas de receta</span><strong>{informe.lineas_receta}</strong></div>
        <div className="stat"><span>Movimientos de apertura</span><strong>{informe.movimientos_apertura}</strong></div>
        <div className="stat"><span>Importación</span><strong>#{informe.importacion_id}</strong></div>
      </div>
      {informe.pendiente_de.length ? (
        <ul className="rule-list">
          {informe.pendiente_de.map((pendiente) => <li key={pendiente}>Falta: {pendiente}</li>)}
        </ul>
      ) : null}
    </>
  );
}

function Contenido({ contexto }: { contexto: ContextoSesion }) {
  const { token, perfil } = contexto;
  const administrador = perfil.rol === "ADMINISTRADOR";

  const [estado, setEstado] = useState<ConfiguracionInicial | null>(null);
  const [archivos, setArchivos] = useState<Record<string, File | null>>({});
  const [objetivo, setObjetivo] = useState("");
  const [referencia, setReferencia] = useState("");
  const [clave, setClave] = useState("");
  const [vista, setVista] = useState<VistaPrevia | null>(null);
  const [informe, setInforme] = useState<InformeCarga | null>(null);
  const [validando, setValidando] = useState(false);
  const [confirmando, setConfirmando] = useState(false);
  const [error, setError] = useState("");
  const [reintentando, setReintentando] = useState(false);

  useEffect(() => {
    const control = new AbortController();
    obtenerEstadoInicial(token, control.signal)
      .then(setEstado)
      .catch((fallo: unknown) => {
        if (control.signal.aborted) return;
        setError(fallo instanceof Error ? fallo.message : "No se pudo leer el estado.");
      });
    return () => control.abort();
  }, [token]);

  useEffect(() => {
    if (!estado?.huella_solicitud) return;
    const control = new AbortController();
    let temporizador: ReturnType<typeof setTimeout>;
    async function refrescar() {
      try {
        const actual = await obtenerEstadoInicial(token, control.signal);
        if (!control.signal.aborted) setEstado(actual);
      } catch (fallo) {
        if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudo actualizar el estado.");
      } finally {
        if (!control.signal.aborted) temporizador = setTimeout(refrescar, 3000);
      }
    }
    temporizador = setTimeout(refrescar, 3000);
    return () => { control.abort(); clearTimeout(temporizador); };
  }, [token, estado?.huella_solicitud]);

  async function reintentar() {
    setReintentando(true); setError("");
    try { setEstado(await reintentarPreparacion(token)); }
    catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo solicitar la preparación."); }
    finally { setReintentando(false); }
  }

  const cargada = Boolean(estado?.huella_solicitud && estado.estado !== "PENDIENTE");
  const elegidos = Object.values(archivos).filter((archivo): archivo is File => archivo !== null);
  const paso = informe ? 2 : vista ? 1 : 0;

  function cambiarArchivo(clave: string, archivo: File | null) {
    setArchivos((actual) => ({ ...actual, [clave]: archivo }));
    setVista(null);
    setInforme(null);
    setError("");
  }

  function validarFechas(): string {
    if (!objetivo || !referencia) return "Indica la fecha objetivo y la referencia de stock.";
    if (referencia >= objetivo) return "La referencia de stock debe ser anterior a la fecha objetivo.";
    return "";
  }

  async function pedirPrevia() {
    const fallaFechas = validarFechas();
    if (fallaFechas) {
      setError(fallaFechas);
      return;
    }
    if (!elegidos.length) {
      setError("Adjunta los archivos de la entrega.");
      return;
    }
    setValidando(true);
    setError("");
    setInforme(null);
    try {
      setVista(await pedirVistaPrevia(token, elegidos, objetivo, referencia));
    } catch (fallo) {
      setVista(null);
      setError(fallo instanceof Error ? fallo.message : "No se pudo validar la entrega.");
    } finally {
      setValidando(false);
    }
  }

  async function aceptar() {
    if (!vista?.aceptable) return;
    if (clave.trim().length < 3) {
      setError("Escribe una clave de importación estable, por ejemplo primera-carga-1.");
      return;
    }
    setConfirmando(true);
    setError("");
    try {
      const resultado = await confirmarCarga(token, elegidos, objetivo, referencia, clave.trim());
      setInforme(resultado);
      setEstado(await obtenerEstadoInicial(token));
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo aceptar la carga.");
    } finally {
      setConfirmando(false);
    }
  }

  return (
    <>
      {estado ? <TarjetaEstado estado={estado} administrador={administrador} reintentando={reintentando} alReintentar={reintentar} /> : null}
      {cargada && <EstadoPanel tono="info" titulo="La carga ya está guardada" descripcion="Ventas, recetas y lotes permanecen en la base. La preparación y evaluación continúan automáticamente; si fallan puedes reintentar sin adjuntar archivos." />}
      {cargada && error && <EstadoPanel tono="alerta" titulo="No se pudo completar la solicitud" descripcion={error} />}
      {!cargada && <>

      <section className="card main-card">
        <div className="section-heading">
          <div>
            <h2>Asistente de primera carga</h2>
            <p>
              Los archivos se piden una sola vez. Después, PostgreSQL es la fuente de ventas y stock.
            </p>
          </div>
        </div>

        <PasosAsistente pasos={PASOS} actual={paso} />

        {!administrador ? (
          <EstadoPanel
            tono="info"
            titulo="Solo un administrador puede cargar"
            descripcion="Puedes revisar el estado, pero la carga requiere rol de administrador."
          />
        ) : null}

        <h3 className="section-space">Archivos</h3>
        <div className="form-grid">
          {RANURAS.map((ranura) => (
            <CampoArchivo
              key={ranura.clave}
              id={`archivo-${ranura.clave}`}
              etiqueta={ranura.etiqueta}
              acepta=".csv,.xlsx"
              ayuda={ranura.ayuda}
              archivo={archivos[ranura.clave] ?? null}
              onCambio={(archivo) => cambiarArchivo(ranura.clave, archivo)}
              deshabilitado={!administrador}
            />
          ))}
        </div>

        <h3 className="section-space">Fechas del escenario</h3>
        <div className="form-grid">
          <CampoFecha
            id="fecha-objetivo"
            etiqueta="Fecha objetivo de la demo"
            valor={objetivo}
            onCambio={(valor) => { setObjetivo(valor); setVista(null); }}
            ayuda="Debe caer en el tramo de prueba reservado. Para el piloto se propone 2022-08-24."
            deshabilitado={!administrador}
          />
          <CampoFecha
            id="fecha-referencia"
            etiqueta="Referencia de stock"
            valor={referencia}
            onCambio={(valor) => { setReferencia(valor); setVista(null); }}
            max={objetivo || undefined}
            ayuda="Cierre simulado anterior al objetivo, por ejemplo 2022-08-23."
            deshabilitado={!administrador}
          />
        </div>

        {error ? <EstadoPanel tono="alerta" titulo="Revisa la entrega" descripcion={error} /> : null}

        <div className="form-actions">
          <BotonEnviar
            type="button"
            enviando={validando}
            textoEnviando="Validando…"
            deshabilitado={!administrador}
            onClick={pedirPrevia}
          >
            Validar y ver vista previa
          </BotonEnviar>
        </div>
      </section>

      {vista ? (
        <section className="card">
          <div className="section-heading">
            <div>
              <h2>Vista previa</h2>
              <p>Nada se ha guardado todavía.</p>
            </div>
            <span className={`badge badge-${vista.aceptable ? "ok" : "alerta"}`}>
              {vista.aceptable ? "Lista para aceptar" : `${vista.total_errores} problemas`}
            </span>
          </div>

          {vista.aceptable ? <ResumenVistaPrevia vista={vista} /> : null}
          <ResumenErrores titulo="La entrega no se puede aceptar" errores={vista.errores} />

          {vista.aceptable && !informe ? (
            <>
              <h3 className="section-space">Aceptar la carga</h3>
              <div className="form-grid">
                <CampoTexto
                  id="clave-importacion"
                  etiqueta="Clave de importación"
                  valor={clave}
                  onCambio={setClave}
                  ayuda="Estable: repetirla con los mismos archivos no vuelve a cargar."
                  ancho="completo"
                />
              </div>
              <div className="form-actions">
                <BotonEnviar
                  type="button"
                  enviando={confirmando}
                  textoEnviando="Cargando…"
                  deshabilitado={!administrador}
                  onClick={aceptar}
                >
                  Aceptar y cargar
                </BotonEnviar>
              </div>
            </>
          ) : null}
        </section>
      ) : null}

      </>}
      {informe ? (
        <section className="card">
          <div className="section-heading">
            <div>
              <h2>Resultado de la carga</h2>
              <p>Huella de la solicitud registrada para reconocer un reintento idéntico.</p>
            </div>
          </div>
          <InformeFinal informe={informe} />
        </section>
      ) : null}
    </>
  );
}

export default function PaginaInicializacion() {
  return (
    <ProtectedShell
      titulo="Primera carga"
      descripcion="Asistente de inicialización: valida los archivos, muestra la vista previa y acepta la carga."
    >
      {(contexto) => <Contenido contexto={contexto} />}
    </ProtectedShell>
  );
}
