"use client";

import type { ReactNode } from "react";
import { ProveedorTienda, useTienda } from "../contexto";
import { Encabezado } from "./Encabezado";
import { ModalLogin } from "./ModalLogin";
import { Pie } from "./Pie";

function Aviso() {
  const { aviso } = useTienda();
  return <div className={`t-aviso${aviso ? " t-aviso-visible" : ""}`} role="status" aria-live="polite">{aviso}</div>;
}

export function ShellTienda({ children }: { children: ReactNode }) {
  return (
    <ProveedorTienda>
      <div className="tienda">
        <a href="#t-contenido" className="t-saltar">Saltar al contenido</a>
        <Encabezado />
        <EstadoConexion />
        <main id="t-contenido" className="t-principal">{children}</main>
        <Pie />
        <ModalLogin />
        <Aviso />
      </div>
    </ProveedorTienda>
  );
}

function EstadoConexion() {
  const { catalogo } = useTienda();
  if (!catalogo) return null;
  return <p className="t-demo-banner" role="note">{catalogo.modo === "api" ? `Catálogo de FoodSave · Payme preproducción${catalogo.disponibilidad_actualizada ? "" : " · No se pudo actualizar el stock; se comprobará antes de pagar"}` : "Catálogo de ejemplo · Payme preproducción · Sin movimientos en FoodSave"}</p>;
}
