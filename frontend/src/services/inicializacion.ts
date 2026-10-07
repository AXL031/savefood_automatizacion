import { enviarFormulario, solicitar } from "@/services/http";
import type { ConfiguracionInicial, InformeCarga, PreparacionModelo, ResultadoCargaPiloto, VistaPrevia } from "@/types/inicializacion";

export function reintentarModeloInicial(token: string, clave: string): Promise<PreparacionModelo> {
  return solicitar<PreparacionModelo>("/inicializacion/reintentar-modelo", {
    token, method: "POST", body: { clave_idempotencia: clave },
  });
}

export function obtenerEstadoInicial(token: string, signal?: AbortSignal): Promise<ConfiguracionInicial> {
  return solicitar<ConfiguracionInicial>("/inicializacion/estado", { token, signal });
}

function formulario(
  archivos: File[],
  fechaObjetivo: string,
  fechaReferenciaStock: string,
  claveImportacion?: string,
): FormData {
  const datos = new FormData();
  datos.append("fecha_objetivo_demo", fechaObjetivo);
  datos.append("fecha_referencia_stock", fechaReferenciaStock);
  if (claveImportacion !== undefined) datos.append("clave_importacion", claveImportacion);
  for (const archivo of archivos) datos.append("archivos", archivo, archivo.name);
  return datos;
}

/** Valida la entrega sin escribir nada en la base. */
export function pedirVistaPrevia(
  token: string,
  archivos: File[],
  fechaObjetivo: string,
  fechaReferenciaStock: string,
  signal?: AbortSignal,
): Promise<VistaPrevia> {
  return enviarFormulario<VistaPrevia>(
    "/inicializacion/vista-previa",
    formulario(archivos, fechaObjetivo, fechaReferenciaStock),
    { token, signal },
  );
}

/** Acepta la carga. Solo debe llamarse cuando la vista previa es aceptable. */
export function confirmarCarga(
  token: string,
  archivos: File[],
  fechaObjetivo: string,
  fechaReferenciaStock: string,
  claveImportacion: string,
  signal?: AbortSignal,
): Promise<InformeCarga> {
  return enviarFormulario<InformeCarga>(
    "/inicializacion/confirmar",
    formulario(archivos, fechaObjetivo, fechaReferenciaStock, claveImportacion),
    { token, signal },
  );
}

/** Carga rápida del CSV de tickets del piloto existente. */
export function cargarCsvPiloto(token: string, archivo: File): Promise<ResultadoCargaPiloto> {
  const datos = new FormData();
  datos.append("archivo", archivo, archivo.name);
  return enviarFormulario<ResultadoCargaPiloto>("/inicializacion/piloto-bakery", datos, { token });
}
