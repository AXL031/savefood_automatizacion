"use client";

import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { BotonEnviar } from "@/components/forms/BotonEnviar";
import { CampoFecha } from "@/components/forms/CampoFecha";
import { CampoSelect } from "@/components/forms/CampoSelect";
import { CampoTexto } from "@/components/forms/CampoTexto";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { TablaDatos, type Columna } from "@/components/tables/TablaDatos";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { obtenerEstadoInicial } from "@/services/inicializacion";
import { consultarDisponibilidad, listarMovimientos, registrarAjuste } from "@/services/inventario";
import type { DisponibilidadItem, EstadoLote, LoteDisponible, Movimiento, TipoItem } from "@/types/inventario";

const ETIQUETA_ESTADO: Record<EstadoLote, string> = {
  OPTIMO: "Óptimo",
  PRIORIDAD: "Vender primero",
  MERMA: "Merma",
  VIGENTE: "Vigente",
  VENCIDO: "Vencido",
  DESCONOCIDO: "Vigencia desconocida",
};

const TONO_ESTADO: Record<EstadoLote, string> = {
  OPTIMO: "ok",
  VIGENTE: "ok",
  PRIORIDAD: "prioridad",
  MERMA: "alerta",
  VENCIDO: "alerta",
  DESCONOCIDO: "neutral",
};

function BadgeLote({ lote }: { lote: LoteDisponible }) {
  const dia = lote.dia_de_vida ? `, día ${lote.dia_de_vida}` : "";
  return <span className={`badge badge-${TONO_ESTADO[lote.estado]}`} title={lote.motivo}>{ETIQUETA_ESTADO[lote.estado]}{dia}</span>;
}

/** Producto en unidades enteras (`u.`); ingrediente en su unidad base. */
function cantidad(valor: string, unidad: string): string {
  return unidad === "unidad" ? `${valor} u.` : `${valor} ${unidad}`;
}

function nuevaClave(): string {
  return `ajuste-${typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : Date.now()}`;
}

type Ajuste = { loteClave: string; delta: string; motivo: string; fecha: string; hora: string; clave: string };

function Contenido({ contexto }: { contexto: ContextoSesion }) {
  const { token, perfil } = contexto;
  const administrador = perfil.rol === "ADMINISTRADOR";
  const [fecha, setFecha] = useState("");
  const [tipo, setTipo] = useState<"" | TipoItem>("");
  const [items, setItems] = useState<DisponibilidadItem[]>([]);
  const [abierto, setAbierto] = useState<string | null>(null);
  const [movimientos, setMovimientos] = useState<Movimiento[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [ajuste, setAjuste] = useState<Ajuste>({ loteClave: "", delta: "", motivo: "", fecha: "", hora: "17:45", clave: nuevaClave() });

  // La fecha por defecto es la fecha objetivo del escenario, no el día real.
  useEffect(() => {
    const control = new AbortController();
    obtenerEstadoInicial(token, control.signal)
      .then((estado) => {
        const objetivo = estado.fecha_objetivo_demo ?? new Date().toISOString().slice(0, 10);
        setFecha((actual) => actual || objetivo);
        setAjuste((actual) => ({ ...actual, fecha: actual.fecha || objetivo }));
      })
      .catch(() => setFecha((actual) => actual || new Date().toISOString().slice(0, 10)));
    return () => control.abort();
  }, [token]);

  const cargar = useCallback(
    (signal?: AbortSignal) => {
      if (!fecha) return;
      setCargando(true);
      Promise.all([
        consultarDisponibilidad(token, fecha, tipo || undefined, signal),
        listarMovimientos(token, { tipo: tipo || undefined, limite: 50 }, signal),
      ])
        .then(([disponibilidad, historial]) => {
          setItems(disponibilidad);
          setMovimientos(historial);
          setError("");
        })
        .catch((fallo: unknown) => {
          if (signal?.aborted) return;
          setError(fallo instanceof Error ? fallo.message : "No se pudo leer el inventario.");
        })
        .finally(() => {
          if (!signal?.aborted) setCargando(false);
        });
    },
    [token, fecha, tipo],
  );

  useEffect(() => {
    const control = new AbortController();
    cargar(control.signal);
    return () => control.abort();
  }, [cargar]);

  const lotes = useMemo(
    () =>
      items.flatMap((item) =>
        item.lotes.map((lote) => ({
          clave: `${item.tipo}:${lote.lote_id}`,
          texto: `${item.nombre}, lote ${lote.lote_informado ? lote.codigo_lote : "no informado"} (${cantidad(lote.saldo, item.unidad)})`,
          item,
          lote,
        })),
      ),
    [items],
  );
  const loteElegido = lotes.find((opcion) => opcion.clave === ajuste.loteClave);

  async function enviarAjuste(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (!loteElegido) return setError("Elige el lote que vas a ajustar.");
    const delta = ajuste.delta.trim();
    const patron = loteElegido.item.tipo === "producto" ? /^-?\d+$/ : /^-?\d+(\.\d{1,3})?$/;
    if (!patron.test(delta) || Number(delta) === 0) {
      return setError(
        loteElegido.item.tipo === "producto"
          ? "El ajuste de producto es un entero distinto de cero (negativo para restar)."
          : "El ajuste de ingrediente admite hasta 3 decimales y no puede ser cero.",
      );
    }
    if (ajuste.motivo.trim().length < 3) return setError("Indica el motivo del ajuste.");
    if (!ajuste.fecha || !ajuste.hora) return setError("Indica la fecha y hora del escenario.");

    setGuardando(true);
    setError("");
    try {
      const resultado = await registrarAjuste(token, {
        tipo: loteElegido.item.tipo,
        lote_id: loteElegido.lote.lote_id,
        delta,
        motivo: ajuste.motivo.trim(),
        clave_operacion: ajuste.clave,
        efectivo_en_demo: `${ajuste.fecha}T${ajuste.hora}:00`,
      });
      setMensaje(
        resultado.repetido
          ? "Este ajuste ya estaba registrado; el saldo no cambió otra vez."
          : `Ajuste registrado. Saldo del lote: ${cantidad(resultado.saldo_resultante, loteElegido.item.unidad)}.`,
      );
      // Una clave nueva solo después de confirmar: reintentar el mismo envío no duplica.
      setAjuste({ ...ajuste, loteClave: "", delta: "", motivo: "", clave: nuevaClave() });
      cargar();
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo registrar el ajuste.");
    } finally {
      setGuardando(false);
    }
  }

  const columnas: Columna<DisponibilidadItem>[] = [
    {
      clave: "item",
      encabezado: "Ítem",
      celda: (fila) => (
        <span>
          <strong>{fila.nombre}</strong>
          <small className="helper-text"> {fila.tipo === "producto" ? "Producto" : "Ingrediente"}</small>
        </span>
      ),
    },
    {
      clave: "disponible",
      encabezado: "Disponible",
      numerica: true,
      celda: (fila) =>
        fila.cantidad_disponible === null ? (
          <span className="badge badge-alerta">Stock desconocido</span>
        ) : (
          <strong>{cantidad(fila.cantidad_disponible, fila.unidad)}</strong>
        ),
    },
    {
      clave: "prioridad",
      encabezado: "Vender primero",
      numerica: true,
      celda: (fila) => (fila.tipo === "producto" && fila.cantidad_prioridad !== "0" ? cantidad(fila.cantidad_prioridad, fila.unidad) : "—"),
    },
    {
      clave: "excluida",
      encabezado: "No cuenta",
      numerica: true,
      celda: (fila) => (fila.cantidad_excluida !== "0" && fila.cantidad_excluida !== "0.000" ? cantidad(fila.cantidad_excluida, fila.unidad) : "—"),
    },
    {
      clave: "aviso",
      encabezado: "Aviso",
      celda: (fila) => (fila.vigencia_desconocida ? <span className="badge badge-neutral">Lote sin caducidad</span> : null),
    },
    {
      clave: "lotes",
      encabezado: "Lotes",
      celda: (fila) => {
        const clave = `${fila.tipo}:${fila.item_id}`;
        return (
          <button type="button" className="button-link" onClick={() => setAbierto(abierto === clave ? null : clave)}>
            {abierto === clave ? "Ocultar" : `Ver ${fila.lotes.length}`}
          </button>
        );
      },
    },
  ];

  const itemAbierto = items.find((item) => `${item.tipo}:${item.item_id}` === abierto);
  const columnasLotes: Columna<LoteDisponible>[] = [
    { clave: "lote", encabezado: "Lote", celda: (l) => (l.lote_informado ? <span className="mono-corto">{l.codigo_lote}</span> : <span className="helper-text">Lote no informado</span>) },
    { clave: "saldo", encabezado: "Saldo", numerica: true, celda: (l) => cantidad(l.saldo, itemAbierto?.unidad ?? "") },
    { clave: "caducidad", encabezado: "Caducidad", celda: (l) => l.fecha_caducidad ?? <span className="helper-text">Sin fecha</span> },
    { clave: "limite", encabezado: "Límite de venta", celda: (l) => l.fecha_limite_venta ?? "—" },
    { clave: "estado", encabezado: `Estado al ${fecha}`, celda: (l) => <BadgeLote lote={l} /> },
    { clave: "motivo", encabezado: "Detalle", celda: (l) => <small>{l.motivo}</small> },
  ];

  const columnasMovimientos: Columna<Movimiento>[] = [
    { clave: "efectivo", encabezado: "Hora del escenario", celda: (m) => <span className="mono-corto">{m.efectivo_en_demo.replace("T", " ").slice(0, 16)}</span> },
    { clave: "item", encabezado: "Ítem y lote", celda: (m) => `${m.item_nombre}, ${m.codigo_lote}` },
    { clave: "tipo", encabezado: "Tipo", celda: (m) => <span className={`badge badge-${m.tipo_movimiento === "APERTURA" ? "info" : "neutral"}`}>{m.tipo_movimiento === "APERTURA" ? "Apertura" : "Ajuste"}</span> },
    { clave: "delta", encabezado: "Cambio", numerica: true, celda: (m) => <strong>{m.delta.startsWith("-") ? m.delta : `+${m.delta}`}</strong> },
    { clave: "saldo", encabezado: "Saldo después", numerica: true, celda: (m) => m.saldo_resultante },
    { clave: "motivo", encabezado: "Motivo", celda: (m) => m.motivo },
  ];

  return (
    <>
      <section className="card main-card">
        <div className="section-heading">
          <div>
            <h2>Stock disponible por fecha</h2>
            <p>
              Pastelería: vida máxima de 5 días. Días 1 a 3 cuentan como óptimos, 4 y 5 se venden primero y desde el
              día 6 es merma que no cuenta. Un ingrediente deja de contar al día siguiente de su caducidad.
            </p>
          </div>
        </div>
        <div className="form-grid">
          <CampoFecha id="fecha-disponibilidad" etiqueta="Fecha del escenario" valor={fecha} onCambio={setFecha} />
          <CampoSelect
            id="tipo-disponibilidad"
            etiqueta="Mostrar"
            valor={tipo}
            onCambio={(valor) => setTipo(valor as "" | TipoItem)}
            opciones={[
              { valor: "", texto: "Productos e ingredientes" },
              { valor: "producto", texto: "Solo productos" },
              { valor: "ingrediente", texto: "Solo ingredientes" },
            ]}
          />
        </div>
        {error ? <EstadoPanel tono="alerta" titulo="Revisa la operación" descripcion={error} /> : null}
        {mensaje ? <p className="inline-success" role="status">{mensaje}</p> : null}
        <TablaDatos
          columnas={columnas}
          filas={items}
          idFila={(fila) => `${fila.tipo}:${fila.item_id}`}
          cargando={cargando || !fecha}
          vacioTitulo="Todavía no hay lotes"
          vacioDescripcion="La primera carga abre los lotes con el archivo de stock inicial."
        />
        {itemAbierto ? (
          <div className="section-space">
            <h3>Lotes de {itemAbierto.nombre}</h3>
            <TablaDatos columnas={columnasLotes} filas={itemAbierto.lotes} idFila={(l) => l.lote_id} vacioTitulo="Sin lotes" />
          </div>
        ) : null}
      </section>

      {administrador ? (
        <section className="card main-card section-space">
          <h2>Registrar ajuste</h2>
          <p className="helper-text">
            Usa un número negativo para restar (merma, rotura, consumo) y positivo para sumar. El saldo nunca queda
            negativo y cada ajuste queda en el historial con su motivo.
          </p>
          <form onSubmit={enviarAjuste}>
            <div className="form-grid">
              <CampoSelect
                id="ajuste-lote"
                etiqueta="Lote"
                valor={ajuste.loteClave}
                onCambio={(valor) => setAjuste({ ...ajuste, loteClave: valor })}
                opciones={[{ valor: "", texto: "Elige un lote" }, ...lotes.map((opcion) => ({ valor: opcion.clave, texto: opcion.texto }))]}
                ancho="completo"
              />
              <CampoTexto
                id="ajuste-delta"
                etiqueta={`Cambio${loteElegido ? ` (${loteElegido.item.unidad})` : ""}`}
                valor={ajuste.delta}
                onCambio={(valor) => setAjuste({ ...ajuste, delta: valor })}
                ayuda="Ejemplo: -2 para retirar dos unidades."
              />
              <CampoFecha id="ajuste-fecha" etiqueta="Fecha del escenario" valor={ajuste.fecha} onCambio={(valor) => setAjuste({ ...ajuste, fecha: valor })} />
              <div className="field">
                <label htmlFor="ajuste-hora">Hora del escenario</label>
                <input id="ajuste-hora" type="time" value={ajuste.hora} onChange={(evento) => setAjuste({ ...ajuste, hora: evento.target.value })} />
              </div>
              <CampoTexto id="ajuste-motivo" etiqueta="Motivo" valor={ajuste.motivo} onCambio={(valor) => setAjuste({ ...ajuste, motivo: valor })} ancho="completo" requerido />
            </div>
            <div className="form-actions">
              <BotonEnviar enviando={guardando} textoEnviando="Registrando…">Registrar ajuste</BotonEnviar>
            </div>
          </form>
        </section>
      ) : null}

      <section className="card main-card section-space">
        <h2>Últimos movimientos</h2>
        <TablaDatos
          columnas={columnasMovimientos}
          filas={movimientos}
          idFila={(m) => m.id}
          vacioTitulo="Sin movimientos"
          vacioDescripcion="La apertura de la primera carga y cada ajuste aparecen aquí."
        />
      </section>
    </>
  );
}

export default function PaginaInventario() {
  return (
    <ProtectedShell titulo="Inventario" descripcion="Saldos por lote, vida útil y ajustes del escenario simulado.">
      {(contexto) => <Contenido contexto={contexto} />}
    </ProtectedShell>
  );
}
