"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import type { EjecucionAutomatizacion } from "../../types/automatizacion";
import { formatearEscenario, formatearFechaHora, formatearDuracion } from "../../utils/fechas";
import { etiquetaDato } from "../../utils/etiquetas";
import { describirFlujo, tieneId } from "./estadoFlujo";

function Marca({ estado, numero }: { estado: string; numero: number }) {
  return <span className={`execution-mark execution-mark-${estado}`} aria-hidden="true">{estado === "listo" ? "✓" : estado === "error" ? "!" : estado === "cancelado" ? "–" : numero}</span>;
}

export function FlujoEjecucion({ ejecucion: e, zona, compacto = false, actualizadoEn, desactualizado = false }: {
  ejecucion: EjecucionAutomatizacion; zona: string; compacto?: boolean; actualizadoEn?: string; desactualizado?: boolean;
}) {
  const flujo = describirFlujo(e), salida = e.datos_salida;
  const [reloj, setReloj] = useState<string | null>(null);
  useEffect(() => {
    if (compacto || !flujo.activa || !e.inicio_en) return;
    setReloj(new Date().toISOString());
    const t = setInterval(() => setReloj(new Date().toISOString()), 1000);
    return () => clearInterval(t);
  }, [compacto, flujo.activa, e.inicio_en]);
  const p = e.datos_entrada.parametros;
  const parametros = p && typeof p === "object" && !Array.isArray(p) ? p as Record<string, unknown> : {};
  const fecha = typeof parametros.fecha_objetivo_demo === "string" ? parametros.fecha_objetivo_demo
    : typeof e.datos_entrada.fecha_hora_simulada_local === "string" ? e.datos_entrada.fecha_hora_simulada_local : null;
  const productos = Array.isArray(parametros.producto_ids) ? parametros.producto_ids.length : null;
  const hora = typeof e.datos_entrada.ejecutar_desde_utc === "string" ? e.datos_entrada.ejecutar_desde_utc : null;
  return <section className={`execution-flow execution-flow-${e.estado.toLowerCase()}${compacto ? " execution-flow-compact" : ""}${desactualizado ? " execution-flow-stale" : ""}`} aria-label={`Flujo de ejecución ${e.id}`}>
    <div className="execution-heading">
      <div><span className="execution-eyebrow">{etiquetaDato(e.tipo)} · #{e.id}</span>
        <h2 aria-live="polite" aria-atomic="true">{flujo.titulo}</h2><p>{flujo.explicacion}</p></div>
      {compacto ? <Link className="execution-open" href={`/automatizaciones/ejecuciones/${e.id}`}>Seguir ejecución <span aria-hidden="true">↗</span></Link>
        : <span className={`execution-live${flujo.activa && !desactualizado ? " is-live" : ""}`}><span aria-hidden="true" />{desactualizado ? "Sin conexión · último estado" : flujo.activa ? "Actualización automática" : "Estado registrado"}</span>}
    </div>
    <ol className="execution-track" aria-label="Etapas de la ejecución">
      {flujo.pasos.map((paso, i) => <li className={`execution-step execution-step-${paso.estado}`} key={paso.titulo} aria-current={paso.estado === "actual" ? "step" : undefined}>
        <Marca estado={paso.estado} numero={i + 1} /><div><strong>{paso.titulo}</strong><span>{paso.detalle}</span></div>
      </li>)}
    </ol>
    <div className="execution-facts">
      {parametros.prueba_repetible === true && <span><small>Modalidad</small><strong>Prueba repetible</strong></span>}
      {fecha && <span><small>Día a planificar</small><strong>{formatearEscenario(fecha)}</strong></span>}
      {productos !== null && <span><small>Productos seleccionados</small><strong>{productos}</strong></span>}
      <span><small>{e.estado === "REINTENTANDO" ? "Próximo intento" : e.inicio_en ? "Tiempo transcurrido" : "Hora de ejecución"}</small>
        <strong>{e.estado === "REINTENTANDO" ? e.proximo_intento_en ? formatearFechaHora(e.proximo_intento_en, zona) : "Por confirmar"
          : e.inicio_en ? formatearDuracion(e.inicio_en, e.fin_en ?? reloj) : hora ? formatearFechaHora(hora, zona) : "Al despachar"}</strong></span>
      {!compacto && <span><small>Intentos registrados</small><strong>{e.intentos.length}</strong></span>}
    </div>
    {!compacto && <>
      {e.mensaje_error && <p className="execution-error" role="alert">{e.mensaje_error}</p>}
      {e.tipo === "GENERAR_PROPUESTA" && <div className="execution-work">
        <div className="execution-work-heading"><h3>Qué hace esta automatización</h3><span>{flujo.final ? "Resultados guardados" : "Un solo bloque de procesamiento"}</span></div>
        <div className="execution-domains">
          <article><span className="execution-domain-number">01</span><h4>Pronosticar la demanda</h4><p>Usa el modelo elegido y las ventas anteriores al día objetivo.</p>
            {tieneId(salida?.corrida_id) ? <Link href={`/pronosticos?corrida_id=${salida.corrida_id}`}>Ver corrida #{salida.corrida_id} →</Link> : <small>Resultado al finalizar</small>}</article>
          <article><span className="execution-domain-number">02</span><h4>Planificar y calcular faltantes</h4><p>Cruza la predicción con recetas, ingredientes y stock disponible.</p>
            {tieneId(salida?.plan_id) ? <Link href={`/planificacion?plan_id=${salida.plan_id}`}>Ver plan #{salida.plan_id} →</Link> : <small>Resultado al finalizar</small>}</article>
          <article><span className="execution-domain-number">03</span><h4>Preparar los pedidos</h4><p>Agrupa los faltantes por proveedor y aplica el modo de aprobación.</p>
            {tieneId(salida?.propuesta_compra_id) && tieneId(salida?.plan_id) ? <Link href={`/compras?plan_id=${salida.plan_id}`}>Revisar propuesta #{salida.propuesta_compra_id} →</Link>
              : <small>{salida?.pedidos_estado === "RECOMPRA_FECHA" ? "Compra previa para esta fecha" : "Resultado al finalizar"}</small>}</article>
        </div>
        {!flujo.final && <p className="execution-note">Pronóstico, plan y pedidos se confirman juntos al finalizar. Durante el cálculo se muestra el estado general; si un intento falla, sus cambios se revierten.</p>}
        {flujo.final && <p className="execution-note">Completar esta tarea no acredita un envío al proveedor. Revisa su aprobación y el estado de entrega en Compras.</p>}
      </div>}
      {flujo.final && salida && <div className="execution-outcomes">
        {typeof salida.pedidos_estado === "string" && <p><strong>Pedidos:</strong> {etiquetaDato(salida.pedidos_estado)} <small>· resultado al generar la propuesta</small></p>}
        {typeof salida.pedidos_motivo === "string" && <p>{salida.pedidos_motivo}</p>}
        {tieneId(salida.evaluacion_ejecucion_id) && <Link href={`/automatizaciones/ejecuciones/${salida.evaluacion_ejecucion_id}`}>Seguir evaluación posterior #{salida.evaluacion_ejecucion_id} →</Link>}
      </div>}
      {actualizadoEn && <p className="execution-updated">Última consulta: {formatearFechaHora(actualizadoEn, zona)} · {zona}{flujo.activa ? " · se consulta cada 3 segundos" : ""}</p>}
    </>}
  </section>;
}
