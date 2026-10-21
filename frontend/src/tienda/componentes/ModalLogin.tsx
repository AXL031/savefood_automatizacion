"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { useTienda } from "../contexto";
import { DATOS_COMERCIO, iniciarSesionEjemplo, iniciarSesionGoogle } from "../servicios";
import { IconoArchivo } from "./Iconos";

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ?? "";

type GoogleId = {
  accounts: { id: {
    initialize: (o: { client_id: string; callback: (r: { credential: string }) => void }) => void;
    renderButton: (el: HTMLElement, o: Record<string, unknown>) => void;
  } };
};

/** Botón oficial de Google Identity Services; se usa cuando hay NEXT_PUBLIC_GOOGLE_CLIENT_ID. */
function BotonGoogleReal({ alIniciar, alFallar }: { alIniciar: (token: string) => void; alFallar: (m: string) => void }) {
  const contenedor = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const montar = () => {
      const google = (window as unknown as { google?: GoogleId }).google;
      if (!google || !contenedor.current) return;
      google.accounts.id.initialize({ client_id: GOOGLE_CLIENT_ID, callback: (r) => alIniciar(r.credential) });
      google.accounts.id.renderButton(contenedor.current, { theme: "outline", size: "large", shape: "pill", text: "continue_with", width: 380 });
    };
    if ((window as unknown as { google?: GoogleId }).google) { montar(); return; }
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.onload = montar;
    script.onerror = () => alFallar("No se pudo cargar el inicio de sesión de Google.");
    document.head.appendChild(script);
  }, [alIniciar, alFallar]);
  return <div ref={contenedor} className="t-google-real" />;
}

export function ModalLogin() {
  const { loginAbierto, cerrarLogin, guardarSesion } = useTienda();
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [correo, setCorreo] = useState("");
  const [nombre, setNombre] = useState("");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);
  const dialogo = useRef<HTMLDivElement>(null);
  const foco = useRef<Element | null>(null);

  useEffect(() => {
    if (!loginAbierto) return;
    foco.current = document.activeElement;
    setError(""); setMostrarFormulario(false);
    dialogo.current?.querySelector<HTMLElement>("button, input")?.focus();
    const escape = (e: KeyboardEvent) => { if (e.key === "Escape") cerrarLogin(); };
    document.addEventListener("keydown", escape);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", escape);
      document.body.style.overflow = "";
      (foco.current as HTMLElement | null)?.focus?.();
    };
  }, [loginAbierto, cerrarLogin]);

  if (!loginAbierto) return null;

  async function ingresarEjemplo(e: FormEvent) {
    e.preventDefault();
    setEnviando(true); setError("");
    try {
      guardarSesion(await iniciarSesionEjemplo(correo, nombre));
      cerrarLogin();
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo iniciar sesión.");
    } finally {
      setEnviando(false);
    }
  }

  async function ingresarGoogle(idToken: string) {
    setError("");
    try {
      guardarSesion(await iniciarSesionGoogle(idToken));
      cerrarLogin();
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo iniciar sesión con Google.");
    }
  }

  // Google real en cuanto exista el ID de cliente, aunque el catálogo siga en modo ejemplo.
  const googleReal = Boolean(GOOGLE_CLIENT_ID);

  return (
    <div className="t-modal-fondo" onMouseDown={(e) => { if (e.target === e.currentTarget) cerrarLogin(); }}>
      <div className="t-modal" role="dialog" aria-modal="true" aria-labelledby="t-login-titulo" ref={dialogo}>
        <div className="t-modal-acento" aria-hidden="true" />
        <button type="button" className="t-modal-cerrar" onClick={cerrarLogin} aria-label="Cerrar"><IconoArchivo nombre="cerrar" /></button>
        <div className="t-modal-cuerpo">
          <span className="t-modal-sello"><IconoArchivo nombre="huella-grande" /></span>
          <p className="t-modal-marca">{DATOS_COMERCIO.nombre}</p>
          <p className="t-modal-lema">{DATOS_COMERCIO.lema}</p>
          <h2 id="t-login-titulo">Inicia sesión para continuar</h2>
          <p className="t-modal-texto">Tu canasta está lista. Accede con tu cuenta de Google para confirmar el pedido y consultarlo después.</p>

          {googleReal ? (
            <BotonGoogleReal alIniciar={ingresarGoogle} alFallar={setError} />
          ) : !mostrarFormulario ? (
            <button type="button" className="t-boton-google" onClick={() => setMostrarFormulario(true)}>
              <IconoArchivo nombre="google" /> Continuar con Google
            </button>
          ) : (
            <form className="t-login-ejemplo" onSubmit={ingresarEjemplo}>
              <p className="t-aviso-simulado">Inicio de sesión simulado: hasta conectar Google, escribe tu correo Gmail. No se verifica la cuenta.</p>
              <label>Correo Gmail<input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} placeholder="nombre@gmail.com" autoComplete="email" required autoFocus /></label>
              <label>Tu nombre<input value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="María Rojas" autoComplete="name" required /></label>
              <button type="submit" className="t-boton-primario" disabled={enviando}>{enviando ? "Ingresando…" : "Continuar"}</button>
            </form>
          )}
          {error ? <p className="t-error" role="alert">{error}</p> : null}
          <p className="t-modal-pie"><IconoArchivo nombre="candado" /> Solo usamos tu nombre y correo para asociar tus pedidos.</p>
        </div>
      </div>
    </div>
  );
}
