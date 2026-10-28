"use client";

import { Icono } from "./Iconos";

/**
 * Campos de tarjeta del checkout. El pago es simulado (ADR-009): estos valores solo
 * existen en el estado del componente, se validan en el navegador y NUNCA se envían
 * a la API, ni se guardan en localStorage, ni se registran.
 */
export type DatosTarjeta = { numero: string; titular: string; vencimiento: string; cvv: string };
export const TARJETA_VACIA: DatosTarjeta = { numero: "", titular: "", vencimiento: "", cvv: "" };

type Marca = { nombre: string; largos: number[]; cvv: number };
const MARCAS: [RegExp, Marca][] = [
  [/^3[47]/, { nombre: "American Express", largos: [15], cvv: 4 }],
  [/^3(0[0-5]|[68])/, { nombre: "Diners Club", largos: [14], cvv: 3 }],
  [/^4/, { nombre: "Visa", largos: [13, 16, 19], cvv: 3 }],
  [/^(5[1-5]|2[2-7])/, { nombre: "Mastercard", largos: [16], cvv: 3 }],
];

export function marcaTarjeta(numero: string): Marca | null {
  const digitos = numero.replace(/\D/g, "");
  return MARCAS.find(([patron]) => patron.test(digitos))?.[1] ?? null;
}

function luhn(digitos: string): boolean {
  let suma = 0;
  for (let i = 0; i < digitos.length; i++) {
    let d = Number(digitos[digitos.length - 1 - i]);
    if (i % 2 === 1) { d *= 2; if (d > 9) d -= 9; }
    suma += d;
  }
  return suma % 10 === 0;
}

export function validarTarjeta(t: DatosTarjeta, hoy = new Date()): Record<keyof DatosTarjeta, string> {
  const digitos = t.numero.replace(/\D/g, "");
  const marca = marcaTarjeta(digitos);
  const [mes, anio] = t.vencimiento.split("/").map(Number);
  const vencida = !mes || !anio || mes < 1 || mes > 12 ||
    new Date(2000 + anio, mes, 1) <= new Date(hoy.getFullYear(), hoy.getMonth(), 1);
  return {
    numero: !marca ? "Ingresa una tarjeta Visa, Mastercard, American Express o Diners."
      : !marca.largos.includes(digitos.length) || !luhn(digitos) ? "Revisa el número de la tarjeta." : "",
    titular: t.titular.trim().length < 3 ? "Escribe el nombre como figura en la tarjeta." : "",
    vencimiento: !/^\d{2}\/\d{2}$/.test(t.vencimiento) ? "Usa el formato MM/AA." : vencida ? "La tarjeta está vencida." : "",
    cvv: t.cvv.length !== (marca?.cvv ?? 3) ? `El código tiene ${marca?.cvv ?? 3} dígitos.` : "",
  };
}

function formatoNumero(valor: string): string {
  const digitos = valor.replace(/\D/g, "").slice(0, 19);
  if (/^3[47]/.test(digitos)) return [digitos.slice(0, 4), digitos.slice(4, 10), digitos.slice(10, 15)].filter(Boolean).join(" ");
  return digitos.replace(/(\d{4})(?=\d)/g, "$1 ");
}

function formatoVencimiento(valor: string, anterior: string): string {
  const digitos = valor.replace(/\D/g, "").slice(0, 4);
  if (digitos.length <= 2) return digitos.length === 2 && valor.length > anterior.length ? `${digitos}/` : digitos;
  return `${digitos.slice(0, 2)}/${digitos.slice(2)}`;
}

export function FormularioTarjeta({ datos, alCambiar, mostrarErrores }: {
  datos: DatosTarjeta; alCambiar: (d: DatosTarjeta) => void; mostrarErrores: boolean;
}) {
  const errores = validarTarjeta(datos);
  const marca = marcaTarjeta(datos.numero);
  const error = (c: keyof DatosTarjeta) => (mostrarErrores && errores[c] ? errores[c] : "");
  const cambiar = (c: keyof DatosTarjeta, v: string) => alCambiar({ ...datos, [c]: v });

  // autoComplete="off" y nombres neutros: el navegador no debe ofrecer ni guardar tarjetas reales.
  return (
    <div className="t-tarjeta-form">
      <label className="t-campo t-campo-ancho">
        <span className="t-campo-etiqueta">Número de tarjeta</span>
        <span className="t-campo-caja"><Icono nombre="tarjeta" tamano={16} />
          <input name="t-pago-numero" value={datos.numero} onChange={(e) => cambiar("numero", formatoNumero(e.target.value))}
            placeholder="1234 5678 9012 3456" inputMode="numeric" autoComplete="off" maxLength={23} aria-invalid={Boolean(error("numero"))} />
          {marca ? <span className="t-marca-tarjeta">{marca.nombre}</span> : null}
        </span>
        {error("numero") ? <span className="t-campo-error">{error("numero")}</span> : null}
      </label>
      <label className="t-campo t-campo-ancho">
        <span className="t-campo-etiqueta">Nombre del titular</span>
        <span className="t-campo-caja"><input name="t-pago-titular" value={datos.titular} onChange={(e) => cambiar("titular", e.target.value.toUpperCase())}
          placeholder="COMO FIGURA EN LA TARJETA" autoComplete="off" maxLength={60} aria-invalid={Boolean(error("titular"))} /></span>
        {error("titular") ? <span className="t-campo-error">{error("titular")}</span> : null}
      </label>
      <label className="t-campo">
        <span className="t-campo-etiqueta">Fecha de vencimiento</span>
        <span className="t-campo-caja"><input name="t-pago-vence" value={datos.vencimiento} onChange={(e) => cambiar("vencimiento", formatoVencimiento(e.target.value, datos.vencimiento))}
          placeholder="MM/AA" inputMode="numeric" autoComplete="off" maxLength={5} aria-invalid={Boolean(error("vencimiento"))} /></span>
        {error("vencimiento") ? <span className="t-campo-error">{error("vencimiento")}</span> : null}
      </label>
      <label className="t-campo">
        <span className="t-campo-etiqueta">Código de seguridad (CVV)</span>
        <span className="t-campo-caja"><input name="t-pago-codigo" type="password" value={datos.cvv} onChange={(e) => cambiar("cvv", e.target.value.replace(/\D/g, "").slice(0, 4))}
          placeholder={marca?.cvv === 4 ? "4 dígitos" : "3 dígitos"} inputMode="numeric" autoComplete="off" maxLength={4} aria-invalid={Boolean(error("cvv"))} /></span>
        {error("cvv") ? <span className="t-campo-error">{error("cvv")}</span> : <span className="t-campo-ayuda">Los 3 o 4 dígitos al reverso de tu tarjeta.</span>}
      </label>
    </div>
  );
}
