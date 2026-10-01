"use client";

import { useCallback, useEffect, useState } from "react";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { ValorOpcional } from "@/components/ui/ValorOpcional";
import { TablaDatos, type Columna } from "@/components/tables/TablaDatos";
import { listarProductos } from "@/services/catalogo";
import type { Producto } from "@/types/catalogo";

const columnas: Columna<Producto>[] = [
  { clave: "nombre", encabezado: "Producto", celda: (fila) => <strong>{fila.nombre}</strong> },
  { clave: "codigo", encabezado: "Código interno", celda: (fila) => <span className="mono-corto">{fila.codigo}</span> },
  {
    clave: "sku",
    encabezado: "Código del archivo (SKU)",
    celda: (fila) => <span className="mono-corto"><ValorOpcional valor={fila.sku_externo} textoAusente="Sin mapeo" /></span>,
  },
  { clave: "origen", encabezado: "Origen", celda: (fila) => <ValorOpcional valor={fila.origen} /> },
  {
    clave: "demostrar",
    encabezado: "Participa en el plan",
    celda: (fila) => <span className={`badge badge-${fila.demostrar ? "ok" : "neutral"}`}>{fila.demostrar ? "Sí" : "No"}</span>,
  },
  {
    clave: "activo",
    encabezado: "Estado",
    celda: (fila) => <span className={`badge badge-${fila.activo ? "ok" : "alerta"}`}>{fila.activo ? "Activo" : "Inactivo"}</span>,
  },
];

function Contenido({ contexto }: { contexto: ContextoSesion }) {
  const { token } = contexto;
  const [productos, setProductos] = useState<Producto[]>([]);
  const [soloDemo, setSoloDemo] = useState(false);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargar = useCallback(
    (signal: AbortSignal) => {
      setCargando(true);
      setError("");
      listarProductos(token, { soloDemo }, signal)
        .then(setProductos)
        .catch((fallo: unknown) => {
          if (signal.aborted) return;
          setError(fallo instanceof Error ? fallo.message : "No se pudo cargar el catálogo.");
        })
        .finally(() => {
          if (!signal.aborted) setCargando(false);
        });
    },
    [token, soloDemo],
  );

  useEffect(() => {
    const control = new AbortController();
    cargar(control.signal);
    return () => control.abort();
  }, [cargar]);

  const enDemo = productos.filter((fila) => fila.demostrar).length;

  return (
    <section className="card main-card">
      <div className="section-heading">
        <div>
          <h2>Catálogo local</h2>
          <p>
            Los productos se registran en la primera carga. El Código del archivo (SKU) es el nombre del artículo del
            dataset y se resuelve al identificador interno; no se crean productos implícitos.
          </p>
        </div>
        <label className="filter-label">
          <input type="checkbox" checked={soloDemo} onChange={(evento) => setSoloDemo(evento.target.checked)} />
          Solo los de la demo
        </label>
      </div>

      {error ? <EstadoPanel tono="alerta" titulo="No se pudo cargar" descripcion={error} /> : null}

      <TablaDatos
        columnas={columnas}
        filas={productos}
        idFila={(fila) => fila.id}
        cargando={cargando}
        vacioTitulo="Todavía no hay catálogo"
        vacioDescripcion="Completa la primera carga para registrar productos y sus SKU."
        pie={
          productos.length
            ? `${productos.length} productos; ${enDemo} participan en el plan de la demostración.`
            : undefined
        }
      />
    </section>
  );
}

export default function PaginaProductos() {
  return (
    <ProtectedShell
      titulo="Productos"
      descripcion="Productos registrados y códigos usados para reconocer sus ventas importadas."
    >
      {(contexto) => <Contenido contexto={contexto} />}
    </ProtectedShell>
  );
}
