import type { Metadata } from "next";
import type { ReactNode } from "react";
import "@fontsource-variable/newsreader";
import "@fontsource-variable/plus-jakarta-sans";
import "./tienda.css";
import { ShellTienda } from "@/tienda/componentes/ShellTienda";

export const metadata: Metadata = {
  title: "Pastelería Maria Juanita · Tienda",
  description: "Pide panes, tortas y postres del día con entrega a domicilio en Lima.",
  icons: { icon: "/tienda/icono.png", apple: "/tienda/logo-192.png" },
};

/** Tienda del cliente (ADR-009): layout propio, sin la navegación ni la sesión administrativa. */
export default function LayoutTienda({ children }: { children: ReactNode }) {
  return <ShellTienda>{children}</ShellTienda>;
}
