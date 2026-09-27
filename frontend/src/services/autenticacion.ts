import { solicitar } from "./http";
import type { Negocio, Perfil, Sesion, CambioNegocio } from "@/types/autenticacion";

export function iniciarSesion(correo: string, contrasena: string): Promise<Sesion> {
  return solicitar<Sesion>("/autenticacion/iniciar-sesion", {
    method: "POST",
    body: { correo, contrasena },
  });
}

export function obtenerPerfil(token: string, signal?: AbortSignal): Promise<Perfil> {
  return solicitar<Perfil>("/autenticacion/mi-perfil", { token, signal });
}

export function obtenerNegocio(token: string, signal?: AbortSignal): Promise<Negocio> {
  return solicitar<Negocio>("/negocios/actual", { token, signal });
}

export function actualizarNegocio(token: string, datos: CambioNegocio): Promise<Negocio> {
  return solicitar<Negocio>("/negocios/actual", { method: "PATCH", token, body: datos });
}
