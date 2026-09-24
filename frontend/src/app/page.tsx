"use client";

import { FormEvent, useState } from "react";

const api = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Perfil = { id: number; nombre: string; correo: string; rol: string };
type Negocio = { id: number; nombre: string; zona_horaria: string; moneda: string };

export default function Inicio() {
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [negocio, setNegocio] = useState<Negocio | null>(null);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function ingresar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setError("");
    setCargando(true);
    try {
      const respuesta = await fetch(`${api}/api/v1/autenticacion/iniciar-sesion`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ correo, contrasena }),
      });
      if (!respuesta.ok) throw new Error("No se pudo iniciar sesión. Revisa tus credenciales.");
      const sesion = await respuesta.json();
      const headers = { Authorization: `Bearer ${sesion.datos.token_acceso}` };
      const [respuestaPerfil, respuestaNegocio] = await Promise.all([
        fetch(`${api}/api/v1/autenticacion/mi-perfil`, { headers }),
        fetch(`${api}/api/v1/negocios/actual`, { headers }),
      ]);
      if (!respuestaPerfil.ok || !respuestaNegocio.ok) throw new Error("La API no pudo cargar el negocio.");
      setPerfil((await respuestaPerfil.json()).datos);
      setNegocio((await respuestaNegocio.json()).datos);
      setContrasena("");
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "Error de conexión");
    } finally {
      setCargando(false);
    }
  }

  return (
    <main>
      <h1>FoodSave</h1>
      {perfil && negocio ? (
        <>
          <p>Sesión iniciada como <strong>{perfil.nombre}</strong> ({perfil.rol}).</p>
          <p>Comercio local: <strong>{negocio.nombre}</strong></p>
          <p className="meta">Zona horaria: {negocio.zona_horaria} · Moneda: {negocio.moneda}</p>
          <p>La base común está lista para integrar los módulos del equipo.</p>
          <button onClick={() => { setPerfil(null); setNegocio(null); }}>Cerrar sesión</button>
        </>
      ) : (
        <form onSubmit={ingresar}>
          <p>Ingresa con el administrador creado durante la instalación.</p>
          <label>Correo<input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required /></label>
          <label>Contraseña<input type="password" value={contrasena} onChange={(e) => setContrasena(e.target.value)} required /></label>
          {error && <p className="error" role="alert">{error}</p>}
          <button disabled={cargando}>{cargando ? "Ingresando…" : "Iniciar sesión"}</button>
        </form>
      )}
    </main>
  );
}
