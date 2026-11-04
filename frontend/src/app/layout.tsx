import type { Metadata } from "next";
import localFont from "next/font/local";
import type { ReactNode } from "react";
import "@fontsource-variable/manrope";
import "@fontsource-variable/bricolage-grotesque";
import "./styles.css";
import { AppShell } from "@/components/layout/ProtectedShell";

const manrope = localFont({
  src: "../../node_modules/@fontsource-variable/manrope/files/manrope-latin-wght-normal.woff2",
  variable: "--fuente-manrope",
  display: "swap",
  weight: "200 800",
});

export const metadata: Metadata = {
  title: "FoodSave",
  description: "Planificación de producción y compras para negocios de alimentos",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <html lang="es" className={manrope.variable}><body><AppShell>{children}</AppShell></body></html>;
}
