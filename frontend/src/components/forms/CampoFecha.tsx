import { Campo, descripcion } from "./Campo";

type Props = {
  id: string;
  etiqueta: string;
  /** Fecha local en formato `YYYY-MM-DD`; nunca un instante UTC. */
  valor: string;
  onCambio: (valor: string) => void;
  min?: string;
  max?: string;
  ayuda?: string;
  error?: string;
  requerido?: boolean;
  deshabilitado?: boolean;
  ancho?: "normal" | "completo";
};

export function CampoFecha({ id, etiqueta, valor, onCambio, min, max, ayuda, error, requerido, deshabilitado, ancho }: Props) {
  return (
    <Campo etiqueta={etiqueta} htmlFor={id} ayuda={ayuda} error={error} ancho={ancho}>
      <input
        id={id}
        type="date"
        value={valor}
        onInput={(evento) => onCambio(evento.currentTarget.value)}
        onChange={(evento) => onCambio(evento.target.value)}
        min={min}
        max={max}
        required={requerido}
        disabled={deshabilitado}
        aria-invalid={error ? true : undefined}
        aria-describedby={descripcion(id, ayuda, error)}
      />
    </Campo>
  );
}
