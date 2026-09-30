import { Campo, descripcion } from "./Campo";

type Props = {
  id: string;
  etiqueta: string;
  /** Extensiones aceptadas, por ejemplo `.xlsx` o `.csv`. */
  acepta: string;
  archivo: File | null;
  onCambio: (archivo: File | null) => void;
  ayuda?: string;
  error?: string;
  deshabilitado?: boolean;
  ancho?: "normal" | "completo";
};

function tamanoLegible(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function CampoArchivo({ id, etiqueta, acepta, archivo, onCambio, ayuda, error, deshabilitado, ancho }: Props) {
  return (
    <Campo etiqueta={etiqueta} htmlFor={id} ayuda={ayuda} error={error} ancho={ancho}>
      <input
        id={id}
        type="file"
        accept={acepta}
        disabled={deshabilitado}
        onChange={(evento) => onCambio(evento.target.files?.[0] ?? null)}
        aria-invalid={error ? true : undefined}
        aria-describedby={descripcion(id, ayuda, error)}
      />
      {archivo ? (
        <small className="helper-text">Seleccionado: <strong>{archivo.name}</strong> ({tamanoLegible(archivo.size)})</small>
      ) : null}
    </Campo>
  );
}
