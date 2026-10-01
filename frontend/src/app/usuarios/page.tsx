"use client";
import { TablaPaginada } from "@/components/tables/TablaPaginada";

import { useEffect, useState, type FormEvent } from "react";
import { ProtectedShell, type ContextoSesion } from "@/components/layout/ProtectedShell";
import { CampoTexto } from "@/components/forms/CampoTexto";
import { CampoSelect } from "@/components/forms/CampoSelect";
import { BotonEnviar } from "@/components/forms/BotonEnviar";
import { EstadoPanel } from "@/components/ui/EstadoPanel";
import { PanelDetalle } from "@/components/ui/PanelDetalle";
import { obtenerPerfil } from "@/services/autenticacion";
import { crearUsuario, editarUsuario, listarUsuarios, type UsuarioGestion, type NuevoUsuario, type RolUsuario } from "@/services/usuarios";

const ROLES = [{ valor: "OPERADOR", texto: "Operador" }, { valor: "ADMINISTRADOR", texto: "Administrador" }];
const vacio: NuevoUsuario = { nombre: "", correo: "", contrasena: "", rol: "OPERADOR" };
function Contenido({ contexto: { token, perfil, actualizarPerfilLocal } }: { contexto: ContextoSesion }) {
  const [usuarios, setUsuarios] = useState<UsuarioGestion[]>([]);
  const [nuevo, setNuevo] = useState<NuevoUsuario>(vacio);
  const [edicion, setEdicion] = useState<UsuarioGestion | null>(null);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    if (perfil.rol !== "ADMINISTRADOR") return;
    const control = new AbortController();
    setCargando(true);
    listarUsuarios(token, control.signal).then((lista) => { if (!control.signal.aborted) setUsuarios(lista); })
      .catch((fallo: unknown) => { if (!control.signal.aborted) setError(fallo instanceof Error ? fallo.message : "No se pudieron consultar los usuarios."); })
      .finally(() => { if (!control.signal.aborted) setCargando(false); });
    return () => control.abort();
  }, [token, perfil.rol, revision]);
  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault(); setGuardando(true); setError(""); setMensaje("");
    try {
      if (edicion) {
        await editarUsuario(token, edicion.id, { nombre: edicion.nombre, correo: edicion.correo, rol: edicion.rol, activo: edicion.activo });
        if (edicion.id === perfil.id) actualizarPerfilLocal(await obtenerPerfil(token));
        setEdicion(null); setMensaje("Usuario actualizado.");
      } else { await crearUsuario(token, nuevo); setNuevo(vacio); setMensaje("Usuario creado. Ya puede iniciar sesión."); }
      setRevision((r) => r + 1);
    } catch (fallo) { setError(fallo instanceof Error ? fallo.message : "No se pudo guardar el usuario."); }
    finally { setGuardando(false); }
  }
  if (perfil.rol !== "ADMINISTRADOR") return <EstadoPanel tono="alerta" titulo="Acceso restringido" descripcion="La gestión de usuarios está disponible para administradores." />;
  return <>
    {error && <EstadoPanel tono="alerta" titulo="Revisa la operación" descripcion={error} />}
    {mensaje && <p role="status" className="inline-success">{mensaje}</p>}
    <section className="card"><div className="section-heading"><h2>Usuarios registrados</h2><button type="button" className="button-secondary" disabled={guardando || cargando} onClick={() => setRevision((r) => r + 1)}>Actualizar</button></div>
      {cargando ? <p role="status">Consultando usuarios…</p> : <TablaPaginada><thead><tr><th>Nombre</th><th>Correo</th><th>Rol</th><th>Estado</th><th>Acción</th></tr></thead><tbody>{usuarios.map((u) => <tr key={u.id}><td>{u.nombre}{u.id === perfil.id ? " (tu cuenta)" : ""}</td><td>{u.correo}</td><td>{u.rol === "ADMINISTRADOR" ? "Administrador" : "Operador"}</td><td>{u.activo ? "Activo" : "Inactivo"}</td><td><button type="button" className="button-link" disabled={guardando} onClick={() => { setEdicion({ ...u }); setNuevo(vacio); setError(""); }}>Editar</button></td></tr>)}</tbody></TablaPaginada>}
    </section>
    <PanelDetalle abierto={Boolean(edicion)} titulo="Editar usuario" onCerrar={() => setEdicion(null)} ocupado={guardando}><section className="card section-space"><h2>{edicion ? "Editar usuario" : "Crear usuario"}</h2>{edicion && error && <EstadoPanel tono="alerta" titulo="Revisa el usuario" descripcion={error} />}<form onSubmit={guardar}><div className="form-grid">
      <CampoTexto id="usuario-nombre" etiqueta="Nombre" requerido valor={edicion?.nombre ?? nuevo.nombre} deshabilitado={guardando} onCambio={(nombre) => edicion ? setEdicion({ ...edicion, nombre }) : setNuevo({ ...nuevo, nombre })} />
      <CampoTexto id="usuario-correo" etiqueta="Correo" tipo="email" requerido valor={edicion?.correo ?? nuevo.correo} deshabilitado={guardando} onCambio={(correo) => edicion ? setEdicion({ ...edicion, correo }) : setNuevo({ ...nuevo, correo })} />
      {!edicion && <CampoTexto id="usuario-clave" etiqueta="Contraseña inicial" tipo="password" autoComplete="new-password" requerido ayuda="Entre 8 y 128 caracteres." valor={nuevo.contrasena} deshabilitado={guardando} onCambio={(contrasena) => setNuevo({ ...nuevo, contrasena })} />}
      <CampoSelect id="usuario-rol" etiqueta="Rol" opciones={ROLES} valor={edicion?.rol ?? nuevo.rol} deshabilitado={guardando} onCambio={(rol) => edicion ? setEdicion({ ...edicion, rol: rol as RolUsuario }) : setNuevo({ ...nuevo, rol: rol as RolUsuario })} />
      {edicion && <CampoSelect id="usuario-activo" etiqueta="Estado" opciones={[{ valor: "si", texto: "Activo" }, { valor: "no", texto: "Inactivo" }]} valor={edicion.activo ? "si" : "no"} deshabilitado={guardando} onCambio={(valor) => setEdicion({ ...edicion, activo: valor === "si" })} />}
    </div><p className="helper-text">Administrador: configura y modifica datos. Operador: consulta el sistema. Siempre debe quedar al menos un administrador activo. Desactivar una cuenta impide su acceso.</p><div className="form-actions">{edicion && <button type="button" className="button-secondary" disabled={guardando} onClick={() => setEdicion(null)}>Cancelar edición</button>}<BotonEnviar enviando={guardando} textoEnviando="Guardando…">{edicion ? "Guardar cambios" : "Crear usuario"}</BotonEnviar></div></form></section></PanelDetalle>
  </>;
}
export default function PaginaUsuarios() {
  return <ProtectedShell titulo="Usuarios" descripcion="Cuentas, roles y acceso a FoodSave.">{(contexto) => <Contenido contexto={contexto} />}</ProtectedShell>;
}
