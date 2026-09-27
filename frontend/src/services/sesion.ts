const clave = "foodsave.token";

export function guardarToken(token: string): void {
  window.sessionStorage.setItem(clave, token);
}

export function leerToken(): string | null {
  return typeof window === "undefined" ? null : window.sessionStorage.getItem(clave);
}

export function borrarToken(): void {
  window.sessionStorage.removeItem(clave);
}
