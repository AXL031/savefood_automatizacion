import type { ReactNode } from "react";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { TablaPaginada, type PaginacionRemota } from "./TablaPaginada";

export type Columna<T> = {
  clave: string;
  encabezado: string;
  /** Alinea a la derecha. Solo para cifras ya formateadas como texto. */
  numerica?: boolean;
  celda: (fila: T) => ReactNode;
};

type Props<T> = {
  columnas: Columna<T>[];
  filas: T[];
  idFila: (fila: T) => string | number;
  cargando?: boolean;
  vacioTitulo?: string;
  vacioDescripcion?: string;
  /** Pie opcional para totales o para advertir que la lista está recortada. */
  pie?: ReactNode;
  paginacion?: PaginacionRemota;
  /** Omite controles cuando todas las filas locales caben en la primera página. */
  compacta?: boolean;
};

function TablaCorta({ children }: { children: ReactNode; remota?: PaginacionRemota }) {
  return <div className="table-wrap"><table>{children}</table></div>;
}

/**
 * Tabla común con encabezados, estado de carga y estado vacío.
 *
 * No ordena ni reformatea: cada dueño entrega la celda ya formateada en la unidad
 * de su dominio. Así una cantidad decimal no se ordena como texto ni pierde
 * precisión al pasar por aquí.
 */
export function TablaDatos<T>({ columnas, filas, idFila, cargando, vacioTitulo, vacioDescripcion, pie, paginacion, compacta }: Props<T>) {
  if (cargando) {
    return <EstadoPanel tono="info" titulo="Cargando datos…" descripcion="Consultando la información." />;
  }
  if (!filas.length) {
    return (
      <EstadoPanel
        tono="neutral"
        titulo={vacioTitulo ?? "Todavía no hay registros"}
        descripcion={vacioDescripcion ?? "Cuando existan datos aparecerán en esta tabla."}
      />
    );
  }
  const Tabla = compacta && !paginacion && filas.length <= 10 ? TablaCorta : TablaPaginada;
  return (
    <div>
      <Tabla remota={paginacion}>
        <thead>
          <tr>
            {columnas.map((columna) => (
              <th key={columna.clave} scope="col" style={columna.numerica ? { textAlign: "right" } : undefined}>
                {columna.encabezado}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map((fila) => (
            <tr key={idFila(fila)}>
              {columnas.map((columna) => (
                <td key={columna.clave} style={columna.numerica ? { textAlign: "right" } : undefined}>
                  {columna.celda(fila)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </Tabla>
      {pie ? <small className="helper-text">{pie}</small> : null}
    </div>
  );
}
