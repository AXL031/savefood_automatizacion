"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { BotonEnviar } from "@/components/forms/BotonEnviar";
import { CampoSelect } from "@/components/forms/CampoSelect";
import { CampoTexto } from "@/components/forms/CampoTexto";
import { PanelDetalle } from "@/components/ui/PanelDetalle";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { TablaDatos, type Columna } from "@/components/tables/TablaDatos";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { cambiarIngrediente, crearIngrediente, listarIngredientes } from "@/services/recetas";
import type { Ingrediente, UnidadBase } from "@/types/recetas";

const UNIDADES: { valor: UnidadBase; texto: string }[] = [
  { valor: "g", texto: "g (gramos)" },
  { valor: "kg", texto: "kg (kilogramos)" },
  { valor: "ml", texto: "ml (mililitros)" },
  { valor: "l", texto: "l (litros)" },
  { valor: "unidad", texto: "unidad" },
];

type Edicion = { ingrediente: Ingrediente; nombre: string; unidad: UnidadBase; activo: boolean };

function Contenido({ contexto }: { contexto: ContextoSesion }) {
  const { token, perfil } = contexto;
  const administrador = perfil.rol === "ADMINISTRADOR";
  const [ingredientes, setIngredientes] = useState<Ingrediente[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [nuevo, setNuevo] = useState({ codigo: "", nombre: "", unidad: "g" as UnidadBase });
  const [edicion, setEdicion] = useState<Edicion | null>(null);
  const [guardando, setGuardando] = useState(false);

  const cargar = useCallback(
    (signal?: AbortSignal) => {
      setCargando(true);
      listarIngredientes(token, signal)
        .then((filas) => {
          setIngredientes(filas);
          setError("");
        })
        .catch((fallo: unknown) => {
          if (signal?.aborted) return;
          setError(fallo instanceof Error ? fallo.message : "No se pudo cargar el catálogo de ingredientes.");
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

  async function crear(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (!nuevo.codigo.trim() || !nuevo.nombre.trim()) {
      setError("El código y el nombre son obligatorios.");
      return;
    }
    setGuardando(true);
    setError("");
    try {
      const creado = await crearIngrediente(token, {
        codigo: nuevo.codigo.trim(),
        nombre: nuevo.nombre.trim(),
        unidad_base: nuevo.unidad,
      });
      setMensaje(`Ingrediente ${creado.nombre} registrado en ${creado.unidad_base}.`);
      setNuevo({ codigo: "", nombre: "", unidad: "g" });
      cargar();
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo registrar el ingrediente.");
    } finally {
      setGuardando(false);
    }
  }

  async function guardarEdicion(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (!edicion) return;
    const { ingrediente } = edicion;
    const cambios: { nombre?: string; unidad_base?: UnidadBase; activo?: boolean } = {};
    if (edicion.nombre.trim() !== ingrediente.nombre) cambios.nombre = edicion.nombre.trim();
    if (edicion.unidad !== ingrediente.unidad_base) cambios.unidad_base = edicion.unidad;
    if (edicion.activo !== ingrediente.activo) cambios.activo = edicion.activo;
    if (!Object.keys(cambios).length) {
      setEdicion(null);
      return;
    }
    setGuardando(true);
    setError("");
    try {
      const actualizado = await cambiarIngrediente(token, ingrediente.id, cambios);
      setMensaje(`Se guardaron los cambios de ${actualizado.nombre}.`);
      setEdicion(null);
      cargar();
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo guardar el cambio.");
    } finally {
      setGuardando(false);
    }
  }

  const columnas: Columna<Ingrediente>[] = [
    { clave: "nombre", encabezado: "Ingrediente", celda: (fila) => <strong>{fila.nombre}</strong> },
    { clave: "codigo", encabezado: "Código", celda: (fila) => <span className="mono-corto">{fila.codigo}</span> },
    { clave: "unidad", encabezado: "Unidad base", celda: (fila) => fila.unidad_base },
    {
      clave: "uso",
      encabezado: "Uso",
      celda: (fila) =>
        fila.en_uso ? (
          <span>{fila.lineas_receta} líneas de receta, {fila.lotes} lotes</span>
        ) : (
          <span className="helper-text">Sin uso todavía</span>
        ),
    },
    {
      clave: "activo",
      encabezado: "Estado",
      celda: (fila) => <span className={`badge badge-${fila.activo ? "ok" : "alerta"}`}>{fila.activo ? "Activo" : "Inactivo"}</span>,
    },
  ];
  if (administrador) {
    columnas.push({
      clave: "editar",
      encabezado: "Editar",
      celda: (fila) => (
        <button
          type="button"
          className="button-link"
          onClick={() => {
            setMensaje("");
            setEdicion({ ingrediente: fila, nombre: fila.nombre, unidad: fila.unidad_base, activo: fila.activo });
          }}
        >
          Editar
        </button>
      ),
    });
  }

  return (
    <>
      <section className="card main-card">
        <div className="section-heading">
          <div>
            <h2>Catálogo de ingredientes</h2>
            <p>
              Cada ingrediente tiene una unidad base. Recetas, lotes y compras usan esa unidad sin conversiones
              implícitas; por eso no cambia cuando ya existe una receta o un lote que la use.
            </p>
          </div>
        </div>
        {error ? <EstadoPanel tono="alerta" titulo="Revisa la operación" descripcion={error} /> : null}
        {mensaje ? <p className="inline-success" role="status">{mensaje}</p> : null}
        <TablaDatos
          columnas={columnas}
          filas={ingredientes}
          idFila={(fila) => fila.id}
          cargando={cargando}
          vacioTitulo="Todavía no hay ingredientes"
          vacioDescripcion="Se registran en la primera carga o con el formulario de esta página."
          pie={ingredientes.length ? `${ingredientes.length} ingredientes registrados.` : undefined}
        />
      </section>

      {administrador && edicion ? (
        <PanelDetalle titulo={`Editar ${edicion.ingrediente.nombre}`} onCerrar={() => setEdicion(null)} ocupado={guardando}><section className="card main-card section-space">
          <h2>Editar {edicion.ingrediente.nombre}</h2>
          {error && <EstadoPanel tono="alerta" titulo="Revisa el ingrediente" descripcion={error} />}
          <form onSubmit={guardarEdicion}>
            <div className="form-grid">
              <CampoTexto id="editar-nombre" etiqueta="Nombre" valor={edicion.nombre} onCambio={(v) => setEdicion({ ...edicion, nombre: v })} requerido />
              <CampoSelect
                id="editar-unidad"
                etiqueta="Unidad base"
                valor={edicion.unidad}
                opciones={UNIDADES}
                onCambio={(v) => setEdicion({ ...edicion, unidad: v as UnidadBase })}
                deshabilitado={!edicion.ingrediente.unidad_editable}
                ayuda={
                  edicion.ingrediente.unidad_editable
                    ? undefined
                    : "Esta unidad se conserva porque ya se usa en recetas o lotes. En Inventario puedes introducir ajustes en kg o litros; las cantidades grandes se muestran en esas unidades."
                }
              />
              <CampoSelect
                id="editar-estado"
                etiqueta="Estado"
                valor={edicion.activo ? "si" : "no"}
                opciones={[{ valor: "si", texto: "Activo" }, { valor: "no", texto: "Inactivo" }]}
                onCambio={(v) => setEdicion({ ...edicion, activo: v === "si" })}
              />
            </div>
            <div className="form-actions">
              <button type="button" className="button-secondary" disabled={guardando} onClick={() => setEdicion(null)}>Cancelar</button>
              <BotonEnviar enviando={guardando} textoEnviando="Guardando…">Guardar cambios</BotonEnviar>
            </div>
          </form>
        </section></PanelDetalle>
      ) : null}

      {administrador ? (
        <section className="card main-card section-space">
          <h2>Registrar ingrediente</h2>
          <form onSubmit={crear}>
            <div className="form-grid">
              <CampoTexto id="nuevo-codigo" etiqueta="Código" valor={nuevo.codigo} onCambio={(v) => setNuevo({ ...nuevo, codigo: v })} ayuda="Único; no se puede cambiar después." requerido />
              <CampoTexto id="nuevo-nombre" etiqueta="Nombre" valor={nuevo.nombre} onCambio={(v) => setNuevo({ ...nuevo, nombre: v })} requerido />
              <CampoSelect id="nuevo-unidad" etiqueta="Unidad base" valor={nuevo.unidad} opciones={UNIDADES} onCambio={(v) => setNuevo({ ...nuevo, unidad: v as UnidadBase })} />
            </div>
            <div className="form-actions">
              <BotonEnviar enviando={guardando} textoEnviando="Registrando…">Registrar ingrediente</BotonEnviar>
            </div>
          </form>
        </section>
      ) : null}
    </>
  );
}

export default function PaginaIngredientes() {
  return (
    <ProtectedShell titulo="Ingredientes" descripcion="Ingredientes registrados y unidad utilizada para calcular recetas y stock.">
      {(contexto) => <Contenido contexto={contexto} />}
    </ProtectedShell>
  );
}
