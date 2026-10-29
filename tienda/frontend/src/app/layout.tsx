import type { ReactNode } from "react";
import "./globales.css";
export default function Raiz({ children }: { children: ReactNode }) {
  return <html lang="es"><body>{children}</body></html>;
}
