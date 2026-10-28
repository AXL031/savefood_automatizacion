import type { EjecucionAutomatizacion } from "../../types/automatizacion";

export type EstadoPaso = "listo" | "actual" | "pendiente" | "error" | "cancelado";
export function describirFlujo(e: EjecucionAutomatizacion) {
  const final = e.estado === "COMPLETADA", fallo = e.estado === "FALLIDA", cancelada = e.estado === "CANCELADA";
  const procesando = e.estado === "EN_EJECUCION", reintento = e.estado === "REINTENTANDO";
  const despacho = Boolean(e.despachada_en || e.inicio_en || e.intentos.length);
  const titulos = {
    PENDIENTE: despacho ? "En cola para comenzar" : e.programacion_id === null ? "Esperando el despacho" : "Esperando el horario programado",
    EN_EJECUCION: "El motor está trabajando",
    REINTENTANDO: "Esperando el próximo intento",
    COMPLETADA: "Procesamiento completado",
    FALLIDA: "La ejecución necesita atención",
    CANCELADA: "Ejecución cancelada",
  };
  const titulosProceso = {
    GENERAR_PROPUESTA: "Pronóstico, plan y compras",
    PREPARAR_MODELO: "Preparación del modelo",
    EVALUAR_MODELO: "Evaluación histórica",
    EVALUAR_PRONOSTICO: "Comparación con ventas conocidas",
    EVALUAR_PROMOCION: "Evaluación de la promoción",
  };
  const explicacion = final ? "Ya puedes revisar los resultados guardados. Los envíos y las evaluaciones posteriores se consultan por separado."
    : fallo ? "Revisa el motivo y los intentos registrados. El motor no ha confirmado un resultado final de esta tarea."
    : cancelada ? "Esta programación no continuará. Su historial se conserva."
    : reintento ? "El intento anterior no terminó correctamente. El motor conserva la tarea y volverá a procesarla en el horario indicado."
    : procesando ? "El motor está procesando la tarea. Los resultados estarán disponibles al finalizar."
    : despacho ? "La tarea ya fue despachada y espera que el motor registre el inicio."
    : e.programacion_id === null ? "La tarea está registrada y espera el próximo ciclo del motor."
    : "La tarea está guardada. Se despachará al cumplir su horario; el inicio depende de la disponibilidad del motor.";
  const pasoProceso: EstadoPaso = final ? "listo" : fallo ? "error" : cancelada ? "cancelado" : procesando || reintento ? "actual" : "pendiente";
  const pasos: { titulo: string; detalle: string; estado: EstadoPaso }[] = [
    { titulo: "Programada", detalle: "Configuración guardada", estado: "listo" },
    { titulo: "Despacho", detalle: despacho ? "Entregada a la cola" : e.programacion_id === null ? "Esperando el despacho" : "Esperando su horario", estado: despacho || final ? "listo" : cancelada ? "cancelado" : fallo ? "error" : "actual" },
    { titulo: titulosProceso[e.tipo], detalle: reintento ? "Reintento en espera" : procesando ? "Procesando" : final ? "Resultado confirmado" : fallo ? "No completado" : cancelada ? "No se ejecutará" : "Por comenzar", estado: pasoProceso },
    { titulo: "Resultado", detalle: final ? "Disponible para revisar" : "Se confirma al finalizar", estado: final ? "listo" : cancelada ? "cancelado" : "pendiente" },
  ];
  // Las tareas por evento no tienen una programación horaria.
  if (e.programacion_id === null) pasos[0] = { titulo: "Registrada", detalle: "Disparada por un evento", estado: "listo" };
  return { titulo: titulos[e.estado], explicacion, pasos, activa: procesando || reintento || e.estado === "PENDIENTE", final };
}

export function tieneId(valor: unknown): valor is number {
  return typeof valor === "number" && Number.isSafeInteger(valor) && valor > 0;
}
