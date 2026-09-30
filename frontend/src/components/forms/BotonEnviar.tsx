type Props = {
  /** Texto en reposo. */
  children: string;
  /** Texto mientras la operación está en curso; evita que parezca inactivo. */
  textoEnviando: string;
  enviando: boolean;
  deshabilitado?: boolean;
  tono?: "primario" | "secundario";
  onClick?: () => void;
  type?: "submit" | "button";
};

/** Botón que impide el doble envío: mientras `enviando` está activo no acepta otro clic. */
export function BotonEnviar({ children, textoEnviando, enviando, deshabilitado, tono = "primario", onClick, type = "submit" }: Props) {
  return (
    <button
      type={type}
      className={tono === "primario" ? "button-primary" : "button-secondary"}
      disabled={enviando || deshabilitado}
      aria-busy={enviando}
      onClick={onClick}
    >
      {enviando ? textoEnviando : children}
    </button>
  );
}
