import type { ApiEnvelope, ApiErrorBody } from "@/types/api";

const baseUrl = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export class HttpError extends Error {
  constructor(
    public readonly status: number,
    mensaje: string,
    public readonly codigo?: string,
    public readonly detalles: { campo: string; mensaje: string }[] = [],
  ) {
    super(mensaje);
    this.name = "HttpError";
  }
}

type Opciones = {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  token?: string;
  body?: unknown;
  signal?: AbortSignal;
};

function mensajeError(body: ApiErrorBody | null, status: number): string {
  if (body?.error?.mensaje) return body.error.mensaje;
  if (typeof body?.detail === "string") return body.detail;
  if (Array.isArray(body?.detail)) return body.detail.map((item) => item.msg ?? "Dato inválido").join("; ");
  if (status === 401) return "Tu sesión venció. Vuelve a iniciar sesión.";
  if (status === 403) return "No tienes permiso para realizar esta acción.";
  if (status === 404) return "La ruta o el registro solicitado no existe.";
  if (status === 501) return "Este módulo aún no está conectado a la API.";
  return `No se pudo completar la solicitud (${status}).`;
}

export async function solicitar<T>(ruta: string, opciones: Opciones = {}): Promise<T> {
  let respuesta: Response;
  try {
    respuesta = await fetch(`${baseUrl}/api/v1${ruta}`, {
      method: opciones.method ?? "GET",
      headers: {
        ...(opciones.body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...(opciones.token ? { Authorization: `Bearer ${opciones.token}` } : {}),
      },
      body: opciones.body === undefined ? undefined : JSON.stringify(opciones.body),
      signal: opciones.signal,
      cache: "no-store",
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") throw error;
    throw new HttpError(0, "No se pudo conectar con la API local.");
  }

  const texto = await respuesta.text();
  let body: ApiEnvelope<T> | ApiErrorBody | null = null;
  if (texto) {
    try {
      body = JSON.parse(texto) as ApiEnvelope<T> | ApiErrorBody;
    } catch {
      throw new HttpError(respuesta.status, "La API devolvió una respuesta inválida.");
    }
  }
  if (!respuesta.ok) {
    if (respuesta.status === 401 && opciones.token && typeof window !== "undefined") {
      window.dispatchEvent(new Event("foodsave:sesion-vencida"));
    }
    const errorBody = body as ApiErrorBody | null;
    throw new HttpError(
      respuesta.status,
      mensajeError(errorBody, respuesta.status),
      errorBody?.error?.codigo,
      errorBody?.error?.detalles ?? [],
    );
  }
  if (!body || !("datos" in body)) throw new HttpError(respuesta.status, "La API no devolvió datos.");
  return body.datos;
}
