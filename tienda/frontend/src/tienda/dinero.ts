/** Dinero en céntimos enteros para no acumular errores de coma flotante. */

export function aCentimos(valor: string): number {
  const [entero, decimales = ""] = valor.split(".");
  const signo = entero.startsWith("-") ? -1 : 1;
  return signo * (Math.abs(Number(entero)) * 100 + Number(decimales.padEnd(2, "0").slice(0, 2)));
}

export function deCentimos(centimos: number): string {
  const signo = centimos < 0 ? "-" : "";
  const absoluto = Math.abs(centimos);
  return `${signo}${Math.floor(absoluto / 100)}.${String(absoluto % 100).padStart(2, "0")}`;
}

/** Precio con descuento porcentual, redondeo ROUND_HALF_UP a céntimos. */
export function aplicarDescuento(precio: string, descuentoPct: number): string {
  return deCentimos(Math.floor((aCentimos(precio) * (100 - descuentoPct) + 50) / 100));
}

export function soles(valor: string): string {
  const [entero, decimales] = deCentimos(aCentimos(valor)).split(".");
  return `S/ ${Number(entero).toLocaleString("es-PE")}.${decimales}`;
}
