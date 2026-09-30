import { solicitar } from "@/services/http";
import type {
  CambioIngrediente,
  Ingrediente,
  NuevaVersionReceta,
  NuevoIngrediente,
  ProductoConReceta,
  RecetaVersion,
} from "@/types/recetas";

export function listarIngredientes(token: string, signal?: AbortSignal): Promise<Ingrediente[]> {
  return solicitar<Ingrediente[]>("/ingredientes", { token, signal });
}

export function crearIngrediente(token: string, cuerpo: NuevoIngrediente): Promise<Ingrediente> {
  return solicitar<Ingrediente>("/ingredientes", { method: "POST", token, body: cuerpo });
}

export function cambiarIngrediente(token: string, id: number, cuerpo: CambioIngrediente): Promise<Ingrediente> {
  return solicitar<Ingrediente>(`/ingredientes/${id}`, { method: "PATCH", token, body: cuerpo });
}

export function listarRecetas(token: string, signal?: AbortSignal): Promise<ProductoConReceta[]> {
  return solicitar<ProductoConReceta[]>("/recetas", { token, signal });
}

export function listarVersiones(token: string, productoId: number, signal?: AbortSignal): Promise<RecetaVersion[]> {
  return solicitar<RecetaVersion[]>(`/recetas/productos/${productoId}/versiones`, { token, signal });
}

export function crearVersion(
  token: string,
  productoId: number,
  cuerpo: NuevaVersionReceta,
): Promise<RecetaVersion & { creada: boolean }> {
  return solicitar<RecetaVersion & { creada: boolean }>(`/recetas/productos/${productoId}/versiones`, {
    method: "POST",
    token,
    body: cuerpo,
  });
}
