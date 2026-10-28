import type { EstadoStock as Estado } from "../tipos";

const TEXTOS: Record<Estado, string> = {
  DISPONIBLE: "Disponible",
  ULTIMAS_UNIDADES: "Últimas unidades",
  AGOTADO: "Agotado",
};

/** Única forma de mostrar stock al cliente: tres estados, nunca cantidades. */
export function EstadoStock({ estado }: { estado: Estado }) {
  return <span className={`t-stock t-stock-${estado.toLowerCase()}`}><span className="t-stock-punto" aria-hidden="true" />{TEXTOS[estado]}</span>;
}

export function textoEstado(estado: Estado) {
  return TEXTOS[estado];
}
