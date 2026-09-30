import type { ReactNode } from "react";

type Props = {
  titulo: string;
  descripcion: string;
  tono?: "neutral" | "alerta" | "info" | "ok";
  accion?: ReactNode;
};

export function EstadoPanel({ titulo, descripcion, tono = "neutral", accion }: Props) {
  return <div className={`state-panel state-${tono}`} role={tono === "alerta" ? "alert" : "status"}><strong>{titulo}</strong><p>{descripcion}</p>{accion}</div>;
}
