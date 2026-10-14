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
    clave: "activo",
    encabezado: "Estado",
    celda: (fila) => <span className={`badge badge-${fila.activo ? "ok" : "alerta"}`}>{fila.activo ? "Activo" : "Inactivo"}</span>,
  },
];

function Contenido({ contexto }: { contexto: ContextoSesion }) {
  const { token } = contexto;
  const [productos, setProductos] = useState<Producto[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargar = useCallback(
    (signal: AbortSignal) => {
      setCargando(true);
      setError("");
      listarProductos(token, {}, signal)
        .then(setProductos)
        .catch((fallo: unknown) => {
          if (signal.aborted) return;
          setError(fallo instanceof Error ? fallo.message : "No se pudo cargar el catálogo.");
        })
        .finally(() => {
          if (!signal.aborted) setCargando(false);
        });
    },
    [token],
  );

  useEffect(() => {
    const control = new AbortController();
    cargar(control.signal);
    return () => control.abort();
  }, [cargar]);

  const activos = productos.filter((fila) => fila.activo).length;

  return (
    <section className="card main-card">
      <div className="section-heading">
        <div>
          <h2>Catálogo</h2>
          <p>
            Los productos se registran en la carga inicial. El SKU identifica cada producto en tus ventas.
          </p>
        </div>
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
            ? `${productos.length} productos; ${activos} activos. Puedes elegirlos en Automatización.`
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
