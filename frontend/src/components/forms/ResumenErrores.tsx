export type ErrorCampo = { campo: string; mensaje: string };

type Props = {
  titulo: string;
  errores: ErrorCampo[];
  /** Cuántos errores se listan antes de resumir el resto. */
  limite?: number;
};

/**
 * Lista los errores por campo/fila que devuelve la API sin perder el contexto ya
 * escrito por la persona. Un lote rechazado suele traer muchos: se acota la lista
 * y se informa cuántos quedan fuera en lugar de ocultarlos en silencio.
 */
export function ResumenErrores({ titulo, errores, limite = 20 }: Props) {
  if (!errores.length) return null;
  const visibles = errores.slice(0, limite);
  const restantes = errores.length - visibles.length;
  return (
    <div className="state-panel state-alerta" role="alert">
      <strong>{titulo}</strong>
      <p>Se encontraron {errores.length} problemas. Corrige el archivo y vuelve a intentarlo; no se guardó nada.</p>
      <ul className="rule-list">
        {visibles.map((error, indice) => (
          <li key={`${error.campo}-${indice}`}><span className="mono-corto">{error.campo}</span> — {error.mensaje}</li>
        ))}
      </ul>
      {restantes > 0 ? <small className="helper-text">Y {restantes} más no mostrados.</small> : null}
    </div>
  );
}
