import { Campo, descripcion } from "./Campo";

type Opcion = { valor: string; texto: string };

type Props = {
  id: string;
  etiqueta: string;
  valor: string;
  opciones: Opcion[];
  onCambio: (valor: string) => void;
  ayuda?: string;
  error?: string;
  deshabilitado?: boolean;
  ancho?: "normal" | "completo";
};

export function CampoSelect({ id, etiqueta, valor, opciones, onCambio, ayuda, error, deshabilitado, ancho }: Props) {
  return (
    <Campo etiqueta={etiqueta} htmlFor={id} ayuda={ayuda} error={error} ancho={ancho}>
      <select
        id={id}
        value={valor}
        onChange={(evento) => onCambio(evento.target.value)}
        disabled={deshabilitado}
        aria-invalid={error ? true : undefined}
        aria-describedby={descripcion(id, ayuda, error)}
      >
        {opciones.map((opcion) => <option key={opcion.valor} value={opcion.valor}>{opcion.texto}</option>)}
      </select>
    </Campo>
  );
}
