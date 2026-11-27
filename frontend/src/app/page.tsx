"use client";
import Link from "next/link";
import { useEffect, useState, type CSSProperties } from "react";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { DashboardInicio } from "@/components/charts/DashboardInicio";
import { ETAPAS_CICLO, Icono, type Etapa, type NombreIcono } from "@/components/layout/navegacion";
import { obtenerEstadoInicial } from "@/services/inicializacion";
import { listarPlanes } from "@/services/planificacion";
import { listarPropuestas } from "@/services/compras";
import type { ConfiguracionInicial } from "@/types/inicializacion";
import type { ResumenPlan } from "@/types/planificacion";
import type { PropuestaCompra } from "@/types/compras";

const estados: Record<string, string> = { PENDIENTE: "Pendiente de carga", DATOS_CARGADOS: "Datos cargados", ENTRENANDO: "Entrenando modelo", MODELO_LISTO: "Modelo listo", FALLIDA: "Requiere revisión" };

type Situacion = "listo" | "atencion" | "pendiente" | "curso" | "libre";
type Paso = { etapa: Etapa; situacion: Situacion; estado: string; detalle: string; enlace: string; accion: string };
const ETIQUETA: Record<Situacion, { texto: string; icono: NombreIcono }> = {
  listo: { texto: "Listo", icono: "check" },
  atencion: { texto: "Requiere acción", icono: "alerta" },
  pendiente: { texto: "Pendiente", icono: "reloj" },
  curso: { texto: "En curso", icono: "reloj" },
  libre: { texto: "Disponible", icono: "flecha-derecha" },
};

function construirPasos(inicial: ConfiguracionInicial | null, planes: ResumenPlan[] | null, porRevisar: number, pedidos: number | null): Paso[] {
  const [preparar, pronosticar, planificar, abastecer, vender, evaluar] = ETAPAS_CICLO;
  const datosListos = inicial && inicial.estado !== "PENDIENTE";
  return [
    {
      etapa: preparar,
      situacion: !inicial ? "pendiente" : inicial.estado === "FALLIDA" ? "atencion" : inicial.estado === "PENDIENTE" ? "pendiente" : "listo",
      estado: inicial ? estados[inicial.estado] : "Sin consultar",
      detalle: datosListos ? "Ventas, catálogo y stock cargados." : "Sube ventas, catálogo y stock inicial.",
      enlace: "/inicializacion", accion: datosListos ? "Ver datos iniciales" : "Hacer la primera carga",
    },
    {
      etapa: pronosticar,
      situacion: inicial?.modelo_id ? "listo" : inicial?.estado === "ENTRENANDO" ? "curso" : "pendiente",
      estado: inicial?.modelo_id ? `Modelo #${inicial.modelo_id}` : inicial?.estado === "ENTRENANDO" ? "Entrenando" : "Sin modelo",
      detalle: inicial?.modelo_id ? "Pronósticos disponibles por producto." : "Se prepara al completar la carga.",
      enlace: "/pronosticos", accion: "Ver pronósticos",
    },
    {
      etapa: planificar,
      situacion: planes?.length ? "listo" : inicial?.modelo_id ? "atencion" : "pendiente",
      estado: planes?.length ? `${planes.length} plan${planes.length === 1 ? "" : "es"}` : "Sin planes",
      detalle: planes?.[0] ? `Último plan #${planes[0].id} para el ${planes[0].fecha_objetivo}.` : "Programa la automatización para generar planes.",
      enlace: planes?.length ? "/planificacion" : "/automatizaciones", accion: planes?.length ? "Revisar planes" : "Configurar automatización",
    },
    {
      etapa: abastecer,
      situacion: porRevisar ? "atencion" : pedidos ? "listo" : "pendiente",
      estado: porRevisar ? `${porRevisar} por aprobar` : pedidos ? "Pedidos al día" : "Sin pedidos",
      detalle: porRevisar ? "Revisa el texto y el destino antes de enviar." : "Pedidos generados por faltantes del plan.",
      enlace: "/compras", accion: porRevisar ? "Aprobar pedidos" : "Ver pedidos",
    },
    { etapa: vender, situacion: "libre", estado: "Caja abierta", detalle: "Registra tickets y aplica promociones aprobadas.", enlace: "/ventas", accion: "Abrir caja" },
    { etapa: evaluar, situacion: inicial?.modelo_id ? "libre" : "pendiente", estado: inicial?.modelo_id ? "Disponible" : "Sin modelo", detalle: "Compara pronóstico y venta real.", enlace: "/panel", accion: "Ver evaluación" },
  ];
}

function Contenido({ contexto }: { contexto: ContextoSesion }) {
  const [inicial, setInicial] = useState<ConfiguracionInicial | null>(null);
  const [planes, setPlanes] = useState<ResumenPlan[] | null>(null);
  const [propuestas, setPropuestas] = useState<PropuestaCompra[] | null>(null);
  const [errores, setErrores] = useState<string[]>([]);
  const [cargando, setCargando] = useState(true);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const control = new AbortController(); setCargando(true); setErrores([]);
    Promise.allSettled([obtenerEstadoInicial(contexto.token, control.signal), listarPlanes(contexto.token, control.signal), listarPropuestas(contexto.token, control.signal)])
      .then(([estado, lista, compras]) => {
        if (control.signal.aborted) return;
        setInicial(estado.status === "fulfilled" ? estado.value : null);
        setPlanes(lista.status === "fulfilled" ? lista.value : null);
        setPropuestas(compras.status === "fulfilled" ? compras.value : null);
        setErrores([estado, lista, compras].flatMap((resultado) => resultado.status === "rejected" ? [resultado.reason instanceof Error ? resultado.reason.message : "No se pudo consultar una sección."] : []));
        setCargando(false);
      });
    return () => control.abort();
  }, [contexto.token, revision]);
  const pedidos = propuestas?.flatMap((propuesta) => propuesta.pedidos);
  const porRevisar = pedidos?.filter((p) => p.estado === "PENDIENTE_APROBACION").length ?? 0;
  const pasos = construirPasos(inicial, planes, porRevisar, pedidos ? pedidos.length : null);
  // El siguiente paso es el primero que pide acción; si no hay, el primero pendiente.
  const foco = pasos.find((p) => p.situacion === "atencion") ?? pasos.find((p) => p.situacion === "pendiente") ?? null;
  const hora = new Date().getHours();
  const saludo = hora < 12 ? "Buenos días" : hora < 19 ? "Buenas tardes" : "Buenas noches";

  return <div className="analytics-page ma-home">
    <section className="ma-welcome">
      <div>
        <span className="ma-stage-chip">{contexto.negocio.nombre}</span>
        <h1>{saludo}, {contexto.perfil.nombre.split(" ")[0]}</h1>
        <p>Sigue el ciclo de izquierda a derecha: cada etapa alimenta a la siguiente.</p>
      </div>
      <button className="button-secondary" disabled={cargando} onClick={() => setRevision((r) => r + 1)}>{cargando ? "Actualizando…" : "Actualizar"}</button>
    </section>

    {errores.length > 0 && <EstadoPanel tono="alerta" titulo="Algunas secciones no están disponibles" descripcion={[...new Set(errores)].join(" ")} />}

    {!cargando && foco && <section className="ma-focus" aria-labelledby="siguiente-paso">
      <span className="ma-focus-icon" aria-hidden="true"><Icono nombre={foco.situacion === "atencion" ? "alerta" : "flecha-derecha"} tamano={22} /></span>
      <div>
        <span className="ma-focus-label">Tu siguiente paso · Paso {foco.etapa.numero} {foco.etapa.titulo}</span>
        <h2 id="siguiente-paso">{foco.accion}</h2>
        <p>{foco.detalle}</p>
      </div>
      <Link href={foco.enlace} className="button-primary">Continuar <Icono nombre="flecha-derecha" tamano={18} /></Link>
    </section>}

    <section aria-labelledby="titulo-ciclo">
      <div className="section-heading"><div><span className="analytics-eyebrow">Recorrido</span><h2 id="titulo-ciclo">Estado del ciclo</h2></div></div>
      <ol className="ma-tracker" aria-busy={cargando}>
        {pasos.map((paso) => {
          const etiqueta = ETIQUETA[paso.situacion];
          return <li key={paso.etapa.id} className={`ma-tracker-step is-${paso.situacion} ${foco?.etapa.id === paso.etapa.id ? "is-focus" : ""}`} style={{ "--etapa": paso.etapa.color } as CSSProperties}>
            <div className="ma-tracker-head"><span className="ma-stage-number">{paso.etapa.numero}</span><strong>{paso.etapa.titulo}</strong></div>
            {cargando ? <><div className="ma-skeleton ma-skeleton-line" /><div className="ma-skeleton ma-skeleton-line corto" /></> : <>
              <span className={`ma-status is-${paso.situacion}`}><Icono nombre={etiqueta.icono} tamano={14} />{etiqueta.texto}</span>
              <span className="ma-tracker-value">{paso.estado}</span>
              <p>{paso.detalle}</p>
              <Link href={paso.enlace}>{paso.accion} <Icono nombre="flecha-derecha" tamano={16} /></Link>
            </>}
          </li>;
        })}
      </ol>
    </section>

    <DashboardInicio token={contexto.token} revision={revision} />
  </div>;
}
export default function Inicio() { return <ProtectedShell titulo="Inicio" descripcion="Resumen de tu negocio y tareas pendientes.">{(contexto) => <Contenido contexto={contexto} />}</ProtectedShell>; }
