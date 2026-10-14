import { solicitar } from "./http";
import type { ConfiguracionFlujo, DiagnosticoFlujo } from "@/types/flujo";
import type { ProgramacionDemo } from "@/types/automatizacion";
export const leerConfiguracionFlujo = (token: string, signal?: AbortSignal) => solicitar<ConfiguracionFlujo | null>("/flujo-automatizacion/configuracion", { token, signal });
export const guardarConfiguracionFlujo = (token: string, body: ConfiguracionFlujo) => solicitar<ConfiguracionFlujo>("/flujo-automatizacion/configuracion", { token, method: "PUT", body });
export const comprobarFlujo = (token: string, body: ConfiguracionFlujo) => solicitar<DiagnosticoFlujo>("/flujo-automatizacion/comprobar", { token, method: "POST", body });
export const programarFlujo = (token: string, body: ConfiguracionFlujo, clave: string, autorizar: boolean) => solicitar<ProgramacionDemo[]>("/flujo-automatizacion/programar", { token, method: "POST", body: { ...body, clave_idempotencia: clave, autorizar_envio: autorizar } });
export const gestionarProgramacion = (token: string, id: number, accion: string, motivo: string) => solicitar<ProgramacionDemo>(`/programaciones-demo/${id}/gestionar`, { token, method: "POST", body: { accion, motivo } });
export const reprogramar = (token: string, id: number, ejecutar_desde_utc: string, motivo: string) => solicitar<ProgramacionDemo>(`/programaciones-demo/${id}`, { token, method: "PATCH", body: { ejecutar_desde_utc, motivo } });
