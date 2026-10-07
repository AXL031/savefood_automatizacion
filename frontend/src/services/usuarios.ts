import { solicitar } from "./http";
export type RolUsuario = "ADMINISTRADOR" | "OPERADOR";
export type UsuarioGestion = { id: number; nombre: string; correo: string; rol: RolUsuario; activo: boolean; creado_en: string };
export type NuevoUsuario = { nombre: string; correo: string; contrasena: string; rol: RolUsuario };
export function listarUsuarios(token: string, signal?: AbortSignal) {
  return solicitar<UsuarioGestion[]>("/usuarios", { token, signal });
}
export function crearUsuario(token: string, entrada: NuevoUsuario) {
  return solicitar<UsuarioGestion>("/usuarios", { token, method: "POST", body: entrada });
}
export function editarUsuario(token: string, id: number, cambios: Partial<Pick<UsuarioGestion, "nombre" | "correo" | "rol" | "activo">>) {
  return solicitar<UsuarioGestion>(`/usuarios/${id}`, { token, method: "PATCH", body: cambios });
}
