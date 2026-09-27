import type { EstadoEjecucion } from "@/types/automatizacion";
import { etiquetaEstado, tonoEstado } from "@/utils/estados";

export function EstadoBadge({ estado }: { estado: EstadoEjecucion }) {
  return <span className={`badge badge-${tonoEstado(estado)}`}>{etiquetaEstado(estado)}</span>;
}
