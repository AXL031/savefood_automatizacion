import { Campo, descripcion } from "./Campo";

type Props = {
  id: string;
  etiqueta: string;
  valor: string;
  onCambio: (valor: string) => void;
  tipo?: "text" | "email" | "password";
  ayuda?: string;
  error?: string;
  requerido?: boolean;
  deshabilitado?: boolean;
  ancho?: "normal" | "completo";
  autoComplete?: string;
};

export function CampoTexto({ id, etiqueta, valor, onCambio, tipo = "text", ayuda, error, requerido, deshabilitado, ancho, autoComplete }: Props) {
  return (
    <Campo etiqueta={etiqueta} htmlFor={id} ayuda={ayuda} error={error} ancho={ancho}>
      <input
        id={id}
        type={tipo}
        value={valor}
        onChange={(evento) => onCambio(evento.target.value)}
        required={requerido}
        disabled={deshabilitado}
        autoComplete={autoComplete}
        aria-invalid={error ? true : undefined}
        aria-describedby={descripcion(id, ayuda, error)}
      />
    </Campo>
  );
}
