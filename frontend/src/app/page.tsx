"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
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
  return <>
    <section className="card"><div className="section-heading"><div><h2>Bienvenido, {contexto.perfil.nombre}</h2><p>Consulta el estado de {contexto.negocio.nombre} y continúa el recorrido de la demostración.</p></div><button className="button-secondary" disabled={cargando} onClick={() => setRevision((r) => r + 1)}>Actualizar</button></div>
      <p>Los planes y pedidos del escenario conservan su fecha histórica. Revisar o enviar un pedido no cambia el inventario.</p>
    </section>
    {errores.length > 0 && <EstadoPanel tono="alerta" titulo="Algunas secciones no están disponibles" descripcion={[...new Set(errores)].join(" ")} />}
    {cargando && <p role="status">Consultando el estado de la instalación…</p>}
    <div className="home-grid section-space">
      <section className="card"><h2>Datos y modelo</h2><strong className="home-stat">{inicial ? estados[inicial.estado] : cargando ? "Consultando…" : "Sin consulta disponible"}</strong><p>{inicial?.modelo_id ? `Modelo #${inicial.modelo_id}` : "Primera carga y preparación del modelo."}</p><Link href="/inicializacion">Abrir primera carga</Link>{inicial?.modelo_id && <p><Link href="/pronosticos">Ver pronósticos</Link></p>}</section>
      <section className="card"><h2>Planificación</h2><strong className="home-stat">{planes ? planes.length : cargando ? "…" : "—"}</strong><p>Planes en la consulta reciente{planes?.[0] ? `. Último: #${planes[0].id}, escenario ${planes[0].fecha_objetivo}.` : "."}</p><Link href="/planificacion">Revisar planes y faltantes</Link></section>
      <section className="card"><h2>Pedidos por revisar</h2><strong className="home-stat">{pedidos ? pedidos.filter((p) => p.estado === "PENDIENTE_APROBACION").length : cargando ? "…" : "—"}</strong><p>Pendientes de aprobación en las últimas 50 propuestas. Revisa el texto y el chat antes de decidir.</p><Link href="/compras">Abrir Compras</Link></section>
      <section className="card"><h2>Evaluación histórica</h2><p>Consulta la comparación entre pronósticos y ventas del escenario, métricas y cobertura disponibles.</p><Link href="/panel">Abrir panel histórico</Link></section>
    </div>
    <section className="card section-space"><h2>Recorrido de la demostración</h2><ol className="journey-grid"><li><strong>Preparar</strong><p>Carga ventas, recetas y stock; espera al modelo.</p><Link href="/inicializacion">Datos iniciales →</Link></li><li><strong>Conectar</strong><p>Asigna ofertas y verifica tu propio Telegram.</p><Link href="/proveedores">Proveedor y chat →</Link></li><li><strong>Programar</strong><p>Elige productos, horario y modo de envío.</p><Link href="/automatizaciones">Programar flujo →</Link></li><li><strong>Comprobar</strong><p>Revisa faltantes, mensajes y resultados.</p><Link href="/compras">Pedidos y envíos →</Link></li></ol></section>
  </>;
}
export default function Inicio() { return <ProtectedShell titulo="Inicio" descripcion="Estado de la instalación y acceso a tus tareas.">{(contexto) => <Contenido contexto={contexto} />}</ProtectedShell>; }
