"use client";

import { useState, type FormEvent } from "react";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { actualizarNegocio } from "@/services/autenticacion";
import type { CambioNegocio } from "@/types/autenticacion";

const preferenciasPrevistas = [
  { titulo: "Planificación nocturna", detalle: "Generar demanda y plan al finalizar el día." },
  { titulo: "Pedidos automáticos", detalle: "Preparar pedidos a partir de los insumos faltantes." },
  { titulo: "Control de excedentes", detalle: "Revisar riesgo durante la jornada." },
  { titulo: "Promociones preventivas", detalle: "Activar una acción dentro del descuento permitido." },
];

function FormularioNegocio({ contexto }: { contexto: ContextoSesion }) {
  const { token, negocio, perfil, actualizarNegocioLocal } = contexto;
  const [formulario, setFormulario] = useState<CambioNegocio>({ nombre: negocio.nombre, zona_horaria: negocio.zona_horaria, moneda: negocio.moneda });
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const administrador = perfil.rol === "ADMINISTRADOR";

  function cambiar(campo: keyof CambioNegocio, valor: string) {
    setFormulario((actual) => ({ ...actual, [campo]: valor }));
    setMensaje("");
    setError("");
  }

  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setError("");
    setMensaje("");
    if (!administrador) return;
    const datos = {
      nombre: formulario.nombre.trim(),
      zona_horaria: formulario.zona_horaria.trim(),
      moneda: formulario.moneda.trim().toUpperCase(),
    };
    if (!datos.nombre || !datos.zona_horaria || !/^[A-Z]{3}$/.test(datos.moneda)) {
      setError("Completa el nombre y la zona horaria; la moneda debe tener tres letras.");
      return;
    }
    try {
      new Intl.DateTimeFormat("es-PE", { timeZone: datos.zona_horaria });
    } catch {
      setError("La zona horaria no es válida. Usa un valor como America/Lima.");
      return;
    }
    setGuardando(true);
    try {
      const actualizado = await actualizarNegocio(token, datos);
      actualizarNegocioLocal(actualizado);
      setFormulario({ nombre: actualizado.nombre, zona_horaria: actualizado.zona_horaria, moneda: actualizado.moneda });
      setMensaje("Los datos del comercio se guardaron correctamente.");
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudieron guardar los cambios.");
    } finally {
      setGuardando(false);
    }
  }

  return <>
    <div className="page-grid">
      <section className="card main-card"><div className="section-heading"><div><h2>Datos del comercio</h2><p>Estos datos identifican a la instalación local.</p></div><span className="badge badge-ok">Activo</span></div>
        <form onSubmit={guardar} className="form-grid">
          <label className="field field-full">Nombre del comercio<input value={formulario.nombre} onChange={(e) => cambiar("nombre", e.target.value)} maxLength={160} disabled={!administrador || guardando} required /></label>
          <label className="field">Zona horaria<input value={formulario.zona_horaria} onChange={(e) => cambiar("zona_horaria", e.target.value)} placeholder="America/Lima" disabled={!administrador || guardando} required /><small>Define cómo se muestran las fechas y horas.</small></label>
          <label className="field">Moneda<input value={formulario.moneda} onChange={(e) => cambiar("moneda", e.target.value.toUpperCase())} maxLength={3} minLength={3} disabled={!administrador || guardando} required /><small>Código de tres letras; por ejemplo, PEN.</small></label>
          {error && <div className="inline-error field-full" role="alert">{error}</div>}
          {mensaje && <div className="inline-success field-full" role="status">{mensaje}</div>}
          <div className="form-actions field-full"><button type="submit" className="button-primary" disabled={!administrador || guardando}>{guardando ? "Guardando…" : "Guardar cambios"}</button></div>
        </form>
        {!administrador && <p className="helper-text">Tu rol puede consultar esta información; solo un administrador puede editarla.</p>}
      </section>
      <aside className="card aside-card"><h2>Estado de la instalación</h2><div className="fact"><span>Comercio</span><strong>{negocio.nombre}</strong></div><div className="fact"><span>Sucursales</span><strong>1 en este MVP</strong></div><div className="fact"><span>Tipo de instalación</span><strong>Local</strong></div><p className="helper-text">Cada comercio conserva su propia base de datos y configuración.</p></aside>
    </div>
    <div className="section-heading section-space"><div><h2>Preferencias operativas</h2><p>La interfaz deja visible el alcance previsto; estos ajustes se habilitarán con sus servicios.</p></div></div>
    <div className="preference-grid">{preferenciasPrevistas.map((item) => <div className="card preference" key={item.titulo}><div><strong>{item.titulo}</strong><p>{item.detalle}</p></div><span className="badge badge-neutral">Pendiente de API</span></div>)}</div>
    <EstadoPanel tono="info" titulo="Límites y avisos en preparación" descripcion="Monto máximo de pedido, margen de seguridad, descuento, reintentos y preferencias de notificación se podrán guardar cuando sus contratos y rutas estén implementados. Aún no se aplican a decisiones automáticas." />
  </>;
}

export default function ConfiguracionPage() {
  return <ProtectedShell titulo="Configuración" descripcion="Administra los datos del comercio y revisa los controles previstos para la operación.">{(contexto) => <FormularioNegocio contexto={contexto} />}</ProtectedShell>;
}
