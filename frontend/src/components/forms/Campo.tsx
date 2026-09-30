import type { ReactNode } from "react";

type Props = {
  etiqueta: string;
  htmlFor: string;
  ayuda?: string;
  error?: string;
  ancho?: "normal" | "completo";
  children: ReactNode;
};

/** Envoltura común: etiqueta, ayuda y error por campo. El control se pasa como hijo. */
export function Campo({ etiqueta, htmlFor, ayuda, error, ancho = "normal", children }: Props) {
  const idAyuda = ayuda ? `${htmlFor}-ayuda` : undefined;
  const idError = error ? `${htmlFor}-error` : undefined;
  return (
    <div className={`field ${ancho === "completo" ? "field-full" : ""}`}>
      <label htmlFor={htmlFor}>{etiqueta}</label>
      {children}
      {ayuda ? <small className="helper-text" id={idAyuda}>{ayuda}</small> : null}
      {error ? <small className="inline-error" id={idError} role="alert">{error}</small> : null}
    </div>
  );
}

/** Ids de descripción para enlazar el control con su ayuda y su error. */
export function descripcion(htmlFor: string, ayuda?: string, error?: string): string | undefined {
  const partes = [ayuda ? `${htmlFor}-ayuda` : null, error ? `${htmlFor}-error` : null].filter(Boolean);
  return partes.length ? partes.join(" ") : undefined;
}
