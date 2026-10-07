import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./styles.css";
import { AppShell } from "@/components/layout/ProtectedShell";

export const metadata: Metadata = {
  title: "FoodSave",
  description: "Base local de FoodSave",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <html lang="es"><body><AppShell>{children}</AppShell></body></html>;
}
