"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { MarcaFoodSave } from "@/components/ui/MarcaFoodSave";
import { iniciarSesion } from "@/services/autenticacion";
import { guardarToken } from "@/services/sesion";

export default function IniciarSesion() {
  const router = useRouter();
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [verClave, setVerClave] = useState(false);
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
      setError(fallo instanceof Error ? fallo.message : "No se pudo iniciar sesión. Revisa tus datos e inténtalo otra vez.");
    } finally {
      setCargando(false);
    }
  }

  return <div className="login-layout">
    <section className="login-hero" aria-label="FoodSave">
      <div className="brand"><MarcaFoodSave /><span className="brand-name">FoodSave</span></div>
      <div>
        <h1>El plan de mañana ya te está esperando.</h1>
        <ol className="login-cadena">
          <li>Pronóstico de demanda calculado</li>
          <li>Plan de producción e insumos faltantes</li>
          <li>Pedidos listos para tu aprobación</li>
        </ol>
      </div>
    </section>
    <main className="login-panel">
      <form className="login-form" onSubmit={ingresar}>
        <h2>Iniciar sesión</h2>
        <p className="login-subtitulo">Ingresa con tu correo y contraseña.</p>
        {error && <div className="login-error" role="alert" id="login-error">
          <svg width="18" height="18" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" strokeWidth="1.6" /><path d="M8 4.8v3.6M8 10.8v.1" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></svg>
          <span>{error}</span>
        </div>}
        <label>Correo electrónico
          <input type="email" value={correo} onChange={(evento) => setCorreo(evento.target.value)} autoComplete="username" placeholder="nombre@tunegocio.pe" required disabled={cargando} aria-invalid={error ? true : undefined} aria-describedby={error ? "login-error" : undefined} />
        </label>
        <label>Contraseña
          <span className="login-clave">
            <input type={verClave ? "text" : "password"} value={contrasena} onChange={(evento) => setContrasena(evento.target.value)} autoComplete="current-password" required disabled={cargando} aria-invalid={error ? true : undefined} aria-describedby={error ? "login-error" : undefined} />
            <button type="button" className="login-mostrar" onClick={() => setVerClave((valor) => !valor)} aria-pressed={verClave} aria-label={verClave ? "Ocultar contraseña" : "Mostrar contraseña"}>{verClave ? "Ocultar" : "Mostrar"}</button>
          </span>
        </label>
        <button type="submit" className="button-primary" disabled={cargando} aria-busy={cargando}>{cargando ? "Ingresando…" : "Entrar"}</button>
        <p className="login-nota">¿No tienes cuenta? Pídela al administrador de tu negocio.</p>
      </form>
    </main>
  </div>;
}
