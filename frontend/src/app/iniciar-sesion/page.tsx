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

  return <div className="login-layout"><div className="login-intro"><div className="brand brand-login"><span className="brand-mark">F</span><span>FoodSave<small>Demostración local</small></span></div><h1>Planifica. Revisa. Prueba.</h1><p>Explora tus ventas históricas, calcula qué producir y recibe los pedidos de demostración en tu propio Telegram.</p><div className="login-step">Datos → Pronóstico → Faltantes → Pedido</div></div><main className="login-card"><div className="eyebrow">Acceso al sistema</div><h2>Iniciar sesión</h2><p>Usa tu cuenta local de administrador u operador.</p><form onSubmit={ingresar}><label>Correo electrónico<input type="email" value={correo} onChange={(evento) => setCorreo(evento.target.value)} autoComplete="username" required disabled={cargando} /></label><label>Contraseña<input type="password" value={contrasena} onChange={(evento) => setContrasena(evento.target.value)} autoComplete="current-password" required disabled={cargando} /></label>{error && <div className="inline-error" role="alert">{error}</div>}<button type="submit" className="button-primary" disabled={cargando}>{cargando ? "Ingresando…" : "Entrar a FoodSave"}</button></form><p className="login-note">Si aún no tienes cuenta, solicítala al administrador de esta instalación.</p></main></div>;
}
