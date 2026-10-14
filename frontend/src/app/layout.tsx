import type { Metadata } from "next";
import type { ReactNode } from "react";
import "@fontsource-variable/manrope";
import "@fontsource-variable/bricolage-grotesque";
import "./styles.css";
import { AppShell } from "@/components/layout/ProtectedShell";

export const metadata: Metadata = {
  title: "FoodSave",
  description: "Planificación de producción y compras para negocios de alimentos",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <html lang="es"><body><AppShell>{children}</AppShell></body></html>;
}
