import type { Metadata } from "next";
import localFont from "next/font/local";
import type { ReactNode } from "react";
import "@fontsource-variable/manrope";
import "@fontsource-variable/bricolage-grotesque";
import "@fontsource-variable/roboto";
import "./styles.css";
import { AppShell } from "@/components/layout/ProtectedShell";

// Precargamos el alfabeto habitual; los imports de Fontsource conservan los demás caracteres.
const manrope = localFont({
  src: "../../node_modules/@fontsource-variable/manrope/files/manrope-latin-wght-normal.woff2",
  variable: "--fuente-manrope",
  display: "swap",
  weight: "200 800",
});

const bricolage = localFont({
  src: "../../node_modules/@fontsource-variable/bricolage-grotesque/files/bricolage-grotesque-latin-wght-normal.woff2",
  variable: "--fuente-bricolage",
  display: "swap",
  weight: "200 800",
});

const roboto = localFont({
  src: "../../node_modules/@fontsource-variable/roboto/files/roboto-latin-wght-normal.woff2",
  variable: "--fuente-roboto",
  display: "swap",
  weight: "100 900",
});

// Aplica el tema guardado antes de pintar para evitar el destello claro en modo oscuro.
const temaInicial = `try{var t=localStorage.getItem("foodsave.tema");if(t==="oscuro"||t==="claro")document.documentElement.dataset.tema=t;}catch(e){}`;

export const metadata: Metadata = {
  title: "FoodSave",
  description: "Planificación de producción y compras para negocios de alimentos",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <html lang="es" className={`${manrope.variable} ${bricolage.variable} ${roboto.variable}`} suppressHydrationWarning><head><script dangerouslySetInnerHTML={{ __html: temaInicial }} /></head><body><AppShell>{children}</AppShell></body></html>;
}
