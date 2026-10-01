/** Conversiones de presentación exactas; la API conserva su unidad base. */
function desplazarDecimal(valor: string, posiciones: number): string {
  const normalizado = valor.trim().replace(",", ".");
  if (!/^-?\d+(\.\d+)?$/.test(normalizado)) throw new Error("Escribe una cantidad numérica, por ejemplo 0,5.");
  const negativo = normalizado.startsWith("-");
  const [entero, fraccion = ""] = normalizado.replace(/^-/, "").split(".");
  const digitos = entero + fraccion;
  const corte = entero.length + posiciones;
  const parteEntera = (corte <= 0 ? "0" : digitos.slice(0, corte).padEnd(corte, "0")).replace(/^0+(?=\d)/, "");
  const parteDecimal = (corte < 0 ? "0".repeat(-corte) + digitos : digitos.slice(corte)).replace(/0+$/, "");
  const resultado = parteDecimal ? `${parteEntera}.${parteDecimal}` : parteEntera;
  return negativo && /[1-9]/.test(resultado) ? `-${resultado}` : resultado;
}
export function cantidadVisible(valor: string | number | null, unidad: string): string {
  if (valor === null) return "No disponible";
  let numero = String(valor), medida = unidad === "unidad" ? "u." : unidad;
  if (Math.abs(Number(numero)) >= 1000 && (unidad === "g" || unidad === "ml")) {
    numero = desplazarDecimal(numero, -3); medida = unidad === "g" ? "kg" : "L";
  } else if (unidad === "l") medida = "L";
  const [entero, fraccion] = numero.split(".");
  const decimal = fraccion?.replace(/0+$/, "");
  return `${entero}${decimal ? `,${decimal}` : ""} ${medida}`;
}
export function unidadesEntrada(base: string): string[] {
  if (base === "g" || base === "kg") return ["kg", "g"];
  if (base === "ml" || base === "l") return ["l", "ml"];
  return [base];
}
export function aUnidadBase(valor: string, entrada: string, base: string): string {
  if (!unidadesEntrada(base).includes(entrada)) throw new Error("La unidad elegida no corresponde al ingrediente.");
  const posiciones = entrada === base ? 0 : entrada === "kg" || entrada === "l" ? 3 : -3;
  return desplazarDecimal(valor, posiciones);
}
