type Paso = { titulo: string; detalle: string };

type Props = {
  pasos: Paso[];
  /** Índice del paso en curso, base 0. */
  actual: number;
};

/** Progreso de un asistente de varios pasos, legible sin depender solo del color. */
export function PasosAsistente({ pasos, actual }: Props) {
  return (
    <ol className="steps-list" aria-label="Progreso del asistente">
      {pasos.map((paso, indice) => {
        const estado = indice < actual ? "Completado" : indice === actual ? "En curso" : "Pendiente";
        return (
          <li key={paso.titulo} aria-current={indice === actual ? "step" : undefined}>
            <strong>{paso.titulo}</strong>
            <span className={`badge badge-${indice < actual ? "ok" : indice === actual ? "info" : "neutral"}`}>{estado}</span>
            <small>{paso.detalle}</small>
          </li>
        );
      })}
    </ol>
  );
}
