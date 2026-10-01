"use client";

import { useEffect, useId, useRef, type ReactNode } from "react";
import { createPortal } from "react-dom";

/** Diálogo nativo: foco contenido, Escape y regreso al botón de la lista. */
export function PanelDetalle({ titulo, children, onCerrar, ocupado = false, abierto = true }: { titulo: string; children: ReactNode; onCerrar: () => void; ocupado?: boolean; abierto?: boolean }) {
  const dialogo = useRef<HTMLDialogElement>(null);
  const id = useId();
  useEffect(() => {
    if (!abierto) return;
    const previo = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const elemento = dialogo.current;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    if (elemento && !elemento.open) elemento.showModal();
    return () => {
      elemento?.close();
      document.body.style.overflow = overflow;
      if (previo?.isConnected) previo.focus({ preventScroll: true });
    };
  }, [abierto]);
  if (!abierto) return <>{children}</>;
  if (typeof document === "undefined") return null;
  return createPortal(<dialog ref={dialogo} className="detail-dialog" aria-labelledby={id} onCancel={(e) => { e.preventDefault(); if (!ocupado) onCerrar(); }}>
    <header className="detail-dialog-header"><h2 id={id}>{titulo}</h2><button type="button" className="button-secondary" disabled={ocupado} onClick={onCerrar}>Cerrar detalle</button></header>
    <div className="detail-dialog-body">{children}</div>
  </dialog>, document.body);
}
