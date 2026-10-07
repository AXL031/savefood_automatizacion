"use client";
import { cantidadVisible } from "@/utils/unidades";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { BotonEnviar } from "@/components/forms/BotonEnviar";
import { CampoTexto } from "@/components/forms/CampoTexto";
import { PanelDetalle } from "@/components/ui/PanelDetalle";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { TablaDatos, type Columna } from "@/components/tables/TablaDatos";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { crearVersion, listarIngredientes, listarRecetas, listarVersiones } from "@/services/recetas";
import type { Ingrediente, LineaReceta, ProductoConReceta, RecetaVersion } from "@/types/recetas";

type LineaFormulario = { clave: number; ingredienteId: string; cantidad: string };

const CANTIDAD_VALIDA = /^\d+(\.\d{1,3})?$/;
let siguienteClave = 1;

function lineasDesde(receta: RecetaVersion | null): LineaFormulario[] {
  if (!receta) return [{ clave: siguienteClave++, ingredienteId: "", cantidad: "" }];
  return receta.lineas.map((linea) => ({
    clave: siguienteClave++,
    ingredienteId: String(linea.ingrediente_id),
    cantidad: linea.cantidad_por_unidad,
  }));
}

function fechaCorta(valor: string | null): string {
  return valor ? new Date(valor).toLocaleString("es-PE", { dateStyle: "short", timeStyle: "short" }) : "Sin fecha";
}

const columnasLineas: Columna<LineaReceta>[] = [
  { clave: "ingrediente", encabezado: "Ingrediente", celda: (fila) => fila.nombre },
  { clave: "cantidad", encabezado: "Por unidad de producto", numerica: true, celda: (fila) => <strong>{cantidadVisible(fila.cantidad_por_unidad, fila.unidad_base)}</strong> },
];

function Contenido({ contexto }: { contexto: ContextoSesion }) {
  const { token, perfil } = contexto;
  const administrador = perfil.rol === "ADMINISTRADOR";
  const [productos, setProductos] = useState<ProductoConReceta[]>([]);
  const [ingredientes, setIngredientes] = useState<Ingrediente[]>([]);
  const [seleccion, setSeleccion] = useState<ProductoConReceta | null>(null);
  const [versiones, setVersiones] = useState<RecetaVersion[]>([]);
  const [lineas, setLineas] = useState<LineaFormulario[]>([]);
  const [motivo, setMotivo] = useState("");
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  const cargar = useCallback(
    (signal?: AbortSignal) => {
      setCargando(true);
      Promise.all([listarRecetas(token, signal), listarIngredientes(token, signal)])
        .then(([filas, catalogo]) => {
          setProductos(filas);
          setIngredientes(catalogo.filter((fila) => fila.activo));
          setError("");
        })
        .catch((fallo: unknown) => {
          if (signal?.aborted) return;
          setError(fallo instanceof Error ? fallo.message : "No se pudieron cargar las recetas.");
        })
        .finally(() => {
          if (!signal?.aborted) setCargando(false);
        });
    },
    [token],
  );

  useEffect(() => {
    const control = new AbortController();
    cargar(control.signal);
    return () => control.abort();
  }, [cargar]);

  useEffect(() => {
    if (!seleccion) return;
    const control = new AbortController();
    listarVersiones(token, seleccion.producto_id, control.signal)
      .then((datos) => { if (!control.signal.aborted) setVersiones(datos); })
      .catch((fallo) => { if (!control.signal.aborted) { setVersiones([]); setError(fallo instanceof Error ? fallo.message : "No se pudo cargar el historial."); } });
    return () => control.abort();
  }, [token, seleccion]);

  function elegir(producto: ProductoConReceta) {
    setSeleccion(producto);
    setLineas(lineasDesde(producto.receta));
    setMotivo("");
    setMensaje("");
    setError("");
  }

  function cambiarLinea(clave: number, cambio: Partial<LineaFormulario>) {
    setLineas((actuales) => actuales.map((linea) => (linea.clave === clave ? { ...linea, ...cambio } : linea)));
  }

  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (!seleccion) return;
    const completas = lineas.filter((linea) => linea.ingredienteId || linea.cantidad);
    if (!completas.length) return setError("La receta necesita al menos un ingrediente.");
    const ids = completas.map((linea) => linea.ingredienteId);
    if (ids.some((id) => !id)) return setError("Elige el ingrediente de cada línea.");
    if (new Set(ids).size !== ids.length) return setError("Cada ingrediente puede aparecer una sola vez.");
    const invalida = completas.find((linea) => !CANTIDAD_VALIDA.test(linea.cantidad.trim()) || Number(linea.cantidad) <= 0);
    if (invalida) return setError("Cada cantidad debe ser mayor que cero y tener hasta 3 decimales.");
    if (motivo.trim().length < 3) return setError("Indica el motivo del cambio; queda en el historial.");

    setGuardando(true);
    setError("");
    try {
      const resultado = await crearVersion(token, seleccion.producto_id, {
        motivo: motivo.trim(),
        lineas: completas.map((linea) => ({ ingrediente_id: Number(linea.ingredienteId), cantidad_por_unidad: linea.cantidad.trim() })),
      });
      setMensaje(
        resultado.creada
          ? `Se creó la versión ${resultado.version} de ${seleccion.producto_nombre}. La versión anterior se conserva para los planes que ya la usaron.`
          : "La composición es igual a la versión activa; no se creó una versión nueva.",
      );
      const actualizado = { ...seleccion, receta: resultado };
      setSeleccion(actualizado);
      setLineas(lineasDesde(resultado));
      setMotivo("");
      cargar();
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo guardar la receta.");
    } finally {
      setGuardando(false);
    }
  }

  const columnasProductos: Columna<ProductoConReceta>[] = [
    { clave: "producto", encabezado: "Producto", celda: (fila) => <strong>{fila.producto_nombre}</strong> },
    {
      clave: "demo",
      encabezado: "En la demo",
      celda: (fila) => <span className={`badge badge-${fila.demostrar ? "ok" : "neutral"}`}>{fila.demostrar ? "Sí" : "No"}</span>,
    },
    {
      clave: "receta",
      encabezado: "Receta activa",
      celda: (fila) =>
        fila.receta ? (
          <span>Versión {fila.receta.version}, {fila.receta.lineas.length} {fila.receta.lineas.length === 1 ? "ingrediente" : "ingredientes"}</span>
        ) : (
          <span className={`badge badge-${fila.demostrar ? "alerta" : "neutral"}`}>Sin receta</span>
        ),
    },
    {
      clave: "ver",
      encabezado: "Detalle",
      celda: (fila) => (
        <button type="button" className="button-link" onClick={() => elegir(fila)}>
          {seleccion?.producto_id === fila.producto_id ? "Abierto" : "Ver"}
        </button>
      ),
    },
  ];

  const opcionesIngrediente = [
    { valor: "", texto: "Elige un ingrediente" },
    ...ingredientes.map((fila) => ({ valor: String(fila.id), texto: `${fila.nombre} (${fila.unidad_base})` })),
  ];

  return (
    <>
      <section className="card main-card">
        <div className="section-heading">
          <div>
            <h2>Recetas por producto</h2>
            <p>
              Las cantidades son por una unidad de producto, en la unidad base de cada ingrediente. Cambiar una
              receta crea una versión nueva; las anteriores no se editan.
            </p>
          </div>
        </div>
        {error && !seleccion ? <EstadoPanel tono="alerta" titulo="No se pudo cargar" descripcion={error} /> : null}
        <TablaDatos
          columnas={columnasProductos}
          filas={productos}
          idFila={(fila) => fila.producto_id}
          cargando={cargando}
          vacioTitulo="Todavía no hay productos"
          vacioDescripcion="Completa la primera carga para registrar productos, ingredientes y recetas."
          pie={productos.length ? `${productos.filter((fila) => fila.receta).length} de ${productos.length} productos tienen receta.` : undefined}
        />
      </section>

      {seleccion ? (
        <PanelDetalle titulo={`Receta de ${seleccion.producto_nombre}`} onCerrar={() => setSeleccion(null)} ocupado={guardando}><section className="card main-card section-space">
          <div className="section-heading">
            <div>
              <h2>{seleccion.producto_nombre}</h2>
              <p>{seleccion.receta ? `Versión activa ${seleccion.receta.version}.` : "Este producto todavía no tiene receta."}</p>
            </div>
          </div>
          {seleccion.receta ? (
            <TablaDatos columnas={columnasLineas} filas={seleccion.receta.lineas} idFila={(fila) => fila.ingrediente_id} />
          ) : null}

          {versiones.length ? (
            <div className="rule-list section-space">
              <h3>Historial de versiones</h3>
              {versiones.map((version) => (
                <div className="rule-row" key={version.receta_id}>
                  <span>
                    <strong>Versión {version.version}:</strong> {version.motivo ?? "Sin motivo"}
                    <small className="helper-text"> {fechaCorta(version.creado_en)}</small>
                  </span>
                  <span className={`badge badge-${version.activo ? "ok" : "neutral"}`}>{version.activo ? "Activa" : "Histórica"}</span>
                </div>
              ))}
            </div>
          ) : null}

          {administrador ? (
            <form onSubmit={guardar} className="section-space">
              <h3>{seleccion.receta ? "Crear versión nueva" : "Registrar receta"}</h3>
              {error ? <EstadoPanel tono="alerta" titulo="Revisa la receta" descripcion={error} /> : null}
              {mensaje ? <p className="inline-success" role="status">{mensaje}</p> : null}
              {lineas.map((linea, indice) => {
                const unidad = ingredientes.find((fila) => String(fila.id) === linea.ingredienteId)?.unidad_base ?? "";
                return (
                  <div className="form-grid" key={linea.clave} style={{ alignItems: "start" }}>
                    <div className="field">
                      <label htmlFor={`linea-ing-${linea.clave}`}>Ingrediente {indice + 1}</label>
                      <select
                        id={`linea-ing-${linea.clave}`}
                        value={linea.ingredienteId}
                        onChange={(evento) => cambiarLinea(linea.clave, { ingredienteId: evento.target.value })}
                      >
                        {opcionesIngrediente.map((opcion) => <option key={opcion.valor} value={opcion.valor}>{opcion.texto}</option>)}
                      </select>
                    </div>
                    <div className="field">
                      <label htmlFor={`linea-cant-${linea.clave}`}>Cantidad por unidad {unidad ? `(${unidad})` : ""}</label>
                      <input
                        id={`linea-cant-${linea.clave}`}
                        inputMode="decimal"
                        value={linea.cantidad}
                        placeholder="0.000"
                        onChange={(evento) => cambiarLinea(linea.clave, { cantidad: evento.target.value })}
                      />
                      {lineas.length > 1 ? (
                        <button
                          type="button"
                          className="button-link"
                          onClick={() => setLineas((actuales) => actuales.filter((fila) => fila.clave !== linea.clave))}
                        >
                          Quitar este ingrediente
                        </button>
                      ) : null}
                    </div>
                  </div>
                );
              })}
              <button
                type="button"
                className="button-secondary"
                onClick={() => setLineas((actuales) => [...actuales, { clave: siguienteClave++, ingredienteId: "", cantidad: "" }])}
              >
                Agregar ingrediente
              </button>
              <div className="form-grid section-space">
                <CampoTexto id="motivo-receta" etiqueta="Motivo del cambio" valor={motivo} onCambio={setMotivo} ancho="completo" requerido />
              </div>
              <div className="form-actions">
                <BotonEnviar enviando={guardando} textoEnviando="Guardando versión…">
                  {seleccion.receta ? "Guardar como versión nueva" : "Registrar receta"}
                </BotonEnviar>
              </div>
            </form>
          ) : null}
        </section></PanelDetalle>
      ) : null}
    </>
  );
}

export default function PaginaRecetas() {
  return (
    <ProtectedShell titulo="Recetas" descripcion="Composición versionada de cada producto para el plan de producción.">
      {(contexto) => <Contenido contexto={contexto} />}
    </ProtectedShell>
  );
}
