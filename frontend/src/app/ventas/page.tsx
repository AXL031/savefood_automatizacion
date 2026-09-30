"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { TablaDatos, type Columna } from "@/components/tables/TablaDatos";
import { CampoFecha } from "@/components/forms/CampoFecha";
import { CampoSelect } from "@/components/forms/CampoSelect";
import { CampoTexto } from "@/components/forms/CampoTexto";
import { BotonEnviar } from "@/components/forms/BotonEnviar";
import { corregirVenta, listarProductos, listarRevisiones, listarVentas } from "@/services/catalogo";
import type { Producto, RevisionVenta, VentaDiaria } from "@/types/catalogo";
import { formatearFechaHora } from "@/utils/fechas";

const LIMITE = 200;

type Correccion = { venta: VentaDiaria; unidades: string; motivo: string };

function PanelRevisiones({ token, venta }: { token: string; venta: VentaDiaria }) {
  const [revisiones, setRevisiones] = useState<RevisionVenta[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const control = new AbortController();
    listarRevisiones(token, venta.id, control.signal)
      .then(setRevisiones)
      .catch((fallo: unknown) => {
        if (control.signal.aborted) return;
        setError(fallo instanceof Error ? fallo.message : "No se pudo leer el historial.");
      });
    return () => control.abort();
  }, [token, venta.id]);

  if (error) return <p className="error-text">{error}</p>;
  if (!revisiones) return <p className="helper-text">Cargando historial…</p>;

  return (
    <ul className="timeline">
      {revisiones.map((revision) => (
        <li key={revision.id}>
          <div>
            <strong>Revisión {revision.numero_revision}: {revision.unidades_vendidas} unidades</strong>
            <span className="badge badge-neutral">{revision.origen_cambio}</span>
          </div>
          <small>{revision.motivo} · {formatearFechaHora(revision.creado_en)}</small>
        </li>
      ))}
    </ul>
  );
}

function Contenido({ contexto }: { contexto: ContextoSesion }) {
  const { token, perfil, negocio } = contexto;
  const administrador = perfil.rol === "ADMINISTRADOR";

  const [productos, setProductos] = useState<Producto[]>([]);
  const [ventas, setVentas] = useState<VentaDiaria[]>([]);
  const [productoId, setProductoId] = useState("");
  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [correccion, setCorreccion] = useState<Correccion | null>(null);
  const [detalle, setDetalle] = useState<VentaDiaria | null>(null);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState("");

  useEffect(() => {
    const control = new AbortController();
    listarProductos(token, {}, control.signal).then(setProductos).catch(() => undefined);
    return () => control.abort();
  }, [token]);

  const cargar = useCallback(
    (signal?: AbortSignal) => {
      setCargando(true);
      setError("");
      listarVentas(
        token,
        {
          productoId: productoId ? Number(productoId) : undefined,
          desde: desde || undefined,
          hasta: hasta || undefined,
          limite: LIMITE,
        },
        signal,
      )
        .then(setVentas)
        .catch((fallo: unknown) => {
          if (signal?.aborted) return;
          setError(fallo instanceof Error ? fallo.message : "No se pudieron cargar las ventas.");
        })
        .finally(() => {
          if (!signal?.aborted) setCargando(false);
        });
    },
    [token, productoId, desde, hasta],
  );

  useEffect(() => {
    const control = new AbortController();
    cargar(control.signal);
    return () => control.abort();
  }, [cargar]);

  async function guardarCorreccion(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (!correccion) return;
    const unidades = Number(correccion.unidades);
    if (!Number.isInteger(unidades) || unidades < 0) {
      setError("Las unidades deben ser un entero no negativo.");
      return;
    }
    if (correccion.motivo.trim().length < 3) {
      setError("El motivo es obligatorio y queda registrado en la revisión.");
      return;
    }
    setGuardando(true);
    setError("");
    try {
      await corregirVenta(token, correccion.venta.id, unidades, correccion.motivo.trim());
      setMensaje(
        `Se registró una revisión nueva de ${correccion.venta.producto} del ${correccion.venta.fecha_local}. ` +
          "El valor anterior se conserva; Kevin debe reevaluar las corridas que lo usaron.",
      );
      setCorreccion(null);
      cargar();
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo guardar la corrección.");
    } finally {
      setGuardando(false);
    }
  }

  const columnas: Columna<VentaDiaria>[] = [
    { clave: "fecha", encabezado: "Fecha local", celda: (fila) => <span className="mono-corto">{fila.fecha_local}</span> },
    { clave: "producto", encabezado: "Producto", celda: (fila) => fila.producto },
    { clave: "unidades", encabezado: "Unidades", numerica: true, celda: (fila) => <strong>{fila.unidades_vendidas}</strong> },
    { clave: "revision", encabezado: "Revisión", numerica: true, celda: (fila) => fila.revision_actual },
    {
      clave: "acciones",
      encabezado: "Historial",
      celda: (fila) => (
        <button
          type="button"
          className="button-link"
          onClick={() => setDetalle(detalle?.id === fila.id ? null : fila)}
        >
          {detalle?.id === fila.id ? "Ocultar" : "Ver"}
        </button>
      ),
    },
  ];

  if (administrador) {
    columnas.push({
      clave: "corregir",
      encabezado: "Corregir",
      celda: (fila) => (
        <button
          type="button"
          className="button-link"
          onClick={() => {
            setMensaje("");
            setCorreccion({ venta: fila, unidades: String(fila.unidades_vendidas), motivo: "" });
          }}
        >
          Corregir
        </button>
      ),
    });
  }

  return (
    <>
      <section className="card main-card">
        <div className="section-heading">
          <div>
            <h2>Ventas diarias</h2>
            <p>
              Unidades agregadas por producto y día en {negocio.nombre}. Una fecha sin fila es
              <strong> desconocida</strong>, no cero; un cero explícito sí es dato.
            </p>
          </div>
        </div>

        <div className="form-grid">
          <CampoSelect
            id="filtro-producto"
            etiqueta="Producto"
            valor={productoId}
            onCambio={setProductoId}
            opciones={[
              { valor: "", texto: "Todos" },
              ...productos.map((fila) => ({ valor: String(fila.id), texto: fila.nombre })),
            ]}
          />
          <CampoFecha id="filtro-desde" etiqueta="Desde" valor={desde} onCambio={setDesde} max={hasta || undefined} />
          <CampoFecha id="filtro-hasta" etiqueta="Hasta" valor={hasta} onCambio={setHasta} min={desde || undefined} />
        </div>

        {mensaje ? <p className="inline-success">{mensaje}</p> : null}
        {error ? <EstadoPanel tono="alerta" titulo="Revisa la operación" descripcion={error} /> : null}

        <TablaDatos
          columnas={columnas}
          filas={ventas}
          idFila={(fila) => fila.id}
          cargando={cargando}
          vacioTitulo="No hay ventas para este filtro"
          vacioDescripcion="Completa la primera carga o amplía el rango de fechas."
          pie={ventas.length === LIMITE ? `Se muestran las ${LIMITE} más recientes; acota el rango para ver el resto.` : undefined}
        />
      </section>

      {detalle ? (
        <section className="card">
          <div className="section-heading">
            <div>
              <h2>Historial de {detalle.producto}</h2>
              <p>{detalle.fecha_local}. Una corrección no borra el valor anterior.</p>
            </div>
          </div>
          <PanelRevisiones token={token} venta={detalle} />
        </section>
      ) : null}

      {correccion ? (
        <section className="card">
          <div className="section-heading">
            <div>
              <h2>Corregir venta</h2>
              <p>
                {correccion.venta.producto} · {correccion.venta.fecha_local}. Se crea una revisión nueva y
                se conserva la anterior.
              </p>
            </div>
          </div>
          <form onSubmit={guardarCorreccion} className="form-grid">
            <CampoTexto
              id="correccion-unidades"
              etiqueta="Unidades vendidas"
              valor={correccion.unidades}
              onCambio={(valor) => setCorreccion({ ...correccion, unidades: valor })}
              ayuda="Entero no negativo."
            />
            <CampoTexto
              id="correccion-motivo"
              etiqueta="Motivo"
              valor={correccion.motivo}
              onCambio={(valor) => setCorreccion({ ...correccion, motivo: valor })}
              ayuda="Queda registrado en la revisión."
              ancho="completo"
            />
            <div className="form-actions">
              <BotonEnviar enviando={guardando} textoEnviando="Guardando…">Guardar corrección</BotonEnviar>
              <button type="button" className="button-secondary" onClick={() => setCorreccion(null)}>
                Cancelar
              </button>
            </div>
          </form>
        </section>
      ) : null}
    </>
  );
}

export default function PaginaVentas() {
  return (
    <ProtectedShell
      titulo="Ventas"
      descripcion="Historial diario que alimenta el pronóstico, con revisiones auditables."
    >
      {(contexto) => <Contenido contexto={contexto} />}
    </ProtectedShell>
  );
}
