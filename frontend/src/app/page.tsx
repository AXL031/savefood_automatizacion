"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { DashboardInicio } from "@/components/charts/DashboardInicio";
import { NavegacionAnalitica, IconoAnalitica } from "@/components/panel/Analitica";
import { obtenerEstadoInicial } from "@/services/inicializacion";
import { listarPlanes } from "@/services/planificacion";
import { listarPropuestas } from "@/services/compras";
import type { ConfiguracionInicial } from "@/types/inicializacion";
import type { ResumenPlan } from "@/types/planificacion";
import type { PropuestaCompra } from "@/types/compras";

const estados: Record<string, string> = { PENDIENTE: "Pendiente de carga", DATOS_CARGADOS: "Datos cargados", ENTRENANDO: "Entrenando modelo", MODELO_LISTO: "Modelo listo", FALLIDA: "Requiere revisión" };
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
  const siguiente = !inicial?.modelo_id ? { titulo: "Preparar datos y modelo", detalle: "Completa la primera carga y sigue la preparación automática.", enlace: "/inicializacion" } : porRevisar ? { titulo: "Revisar pedidos pendientes", detalle: `${porRevisar} pedido(s) esperan tu revisión en la consulta reciente.`, enlace: "/compras" } : { titulo: "Configurar mi automatización", detalle: "El asistente te muestra qué está listo, qué falta y cuándo se ejecutará la planificación.", enlace: "/automatizaciones" };
  return <div className="analytics-page">
    <NavegacionAnalitica />
    <section className="analytics-hero"><div><span className="analytics-eyebrow"><IconoAnalitica tipo="inicio" /> {contexto.negocio.nombre}</span><h2>Tu negocio,<br />de un vistazo.</h2><p>Bienvenido, {contexto.perfil.nombre}. Encuentra tus últimos resultados, revisa pendientes y prepara el siguiente paso.</p></div><div className="analytics-hero-note"><span className="analytics-status-dot" /><strong>{inicial ? estados[inicial.estado] : "Resumen del negocio"}</strong><span>Información de tus datos disponibles</span><button className="button-secondary" disabled={cargando} onClick={() => setRevision((r) => r + 1)}>{cargando ? "Actualizando…" : "↻ Actualizar resumen"}</button></div></section>
    {errores.length > 0 && <EstadoPanel tono="alerta" titulo="Algunas secciones no están disponibles" descripcion={[...new Set(errores)].join(" ")} />}
    {cargando && <p role="status">Consultando el estado de tu negocio…</p>}
    {!cargando && inicial && <section className="home-next-step"><span className="model-symbol"><IconoAnalitica tipo="grafico" /></span><div><span className="analytics-eyebrow">Tu siguiente paso</span><h2>{siguiente.titulo}</h2><p>{siguiente.detalle}</p></div><Link href={siguiente.enlace} className="button-primary">Continuar →</Link></section>}
    <DashboardInicio token={contexto.token} revision={revision} />
    <div className="home-grid workflow-cards">
      <section className="card"><h2>Datos y modelo</h2><strong className="home-stat">{inicial ? estados[inicial.estado] : cargando ? "Consultando…" : "Sin consulta disponible"}</strong><p>{inicial?.modelo_id ? `Modelo #${inicial.modelo_id}` : "Primera carga y preparación del modelo."}</p><Link href="/inicializacion">Abrir primera carga</Link>{inicial?.modelo_id && <p><Link href="/pronosticos">Ver pronósticos</Link></p>}</section>
      <section className="card"><h2>Planificación</h2><strong className="home-stat">{planes ? planes.length : cargando ? "…" : "—"}</strong><p>Planes en la consulta reciente{planes?.[0] ? `. Último: #${planes[0].id}, para el ${planes[0].fecha_objetivo}.` : "."}</p><Link href="/planificacion">Revisar planes y faltantes</Link></section>
      <section className="card"><h2>Pedidos por revisar</h2><strong className="home-stat">{pedidos ? pedidos.filter((p) => p.estado === "PENDIENTE_APROBACION").length : cargando ? "…" : "—"}</strong><p>Pendientes de aprobación en las últimas 50 propuestas. Revisa el texto y el chat antes de decidir.</p><Link href="/compras">Abrir Compras</Link></section>
      <section className="card"><h2>Evaluación histórica</h2><p>Consulta la comparación entre pronósticos y ventas reales, métricas y cobertura disponibles.</p><Link href="/panel">Abrir panel histórico</Link></section>
    </div>
  </div>;
}
export default function Inicio() { return <ProtectedShell titulo="Inicio" descripcion="Resumen de tu negocio y tareas pendientes.">{(contexto) => <Contenido contexto={contexto} />}</ProtectedShell>; }
