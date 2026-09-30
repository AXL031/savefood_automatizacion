"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { iniciarSesion } from "@/services/autenticacion";
import { guardarToken } from "@/services/sesion";

export default function IniciarSesion() {
  const router = useRouter();
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function ingresar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setError("");
    setCargando(true);
    try {
      const sesion = await iniciarSesion(correo.trim().toLowerCase(), contrasena);
      guardarToken(sesion.token_acceso);
      setContrasena("");
      router.replace("/");
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo iniciar sesión.");
    } finally {
      setCargando(false);
    }
  }

  return <div className="login-layout"><div className="login-intro"><div className="brand brand-login"><span className="brand-mark">F</span><span>FoodSave<small>Operación local</small></span></div><h1>Tu operación, bajo control.</h1><p>Consulta decisiones automáticas, revisa incidencias y configura cómo trabaja FoodSave en tu comercio.</p><div className="login-step">Datos → Decisión → Acción → Verificación</div></div><main className="login-card"><div className="eyebrow">Acceso al sistema</div><h2>Iniciar sesión</h2><p>Usa el administrador creado durante la instalación.</p><form onSubmit={ingresar}><label>Correo electrónico<input type="email" value={correo} onChange={(evento) => setCorreo(evento.target.value)} autoComplete="username" required /></label><label>Contraseña<input type="password" value={contrasena} onChange={(evento) => setContrasena(evento.target.value)} autoComplete="current-password" required /></label>{error && <div className="inline-error" role="alert">{error}</div>}<button type="submit" className="button-primary" disabled={cargando}>{cargando ? "Ingresando…" : "Entrar a FoodSave"}</button></form><p className="login-note">La información de este comercio se guarda en su instalación local.</p></main></div>;
}
