"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { obtenerNegocio, obtenerPerfil } from "@/services/autenticacion";
import { borrarToken, leerToken } from "@/services/sesion";
import type { Negocio, Perfil } from "@/types/autenticacion";
import { HttpError } from "@/services/http";

export type ContextoSesion = { token: string; perfil: Perfil; negocio: Negocio; actualizarNegocioLocal: (valor: Negocio) => void };

type Props = {
  titulo: string;
  descripcion: string;
  children: (contexto: ContextoSesion) => ReactNode;
};

const enlaces = [
  { href: "/configuracion", texto: "Configuración" },
  { href: "/automatizaciones", texto: "Automatizaciones" },
  { href: "/notificaciones", texto: "Notificaciones" },
];

export function ProtectedShell({ titulo, descripcion, children }: Props) {
  const router = useRouter();
  const ruta = usePathname();
  const [token, setToken] = useState<string | null>(null);
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [negocio, setNegocio] = useState<Negocio | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    function sesionVencida() {
      borrarToken();
      router.replace("/iniciar-sesion");
    }
    window.addEventListener("foodsave:sesion-vencida", sesionVencida);
    return () => window.removeEventListener("foodsave:sesion-vencida", sesionVencida);
  }, [router]);

  useEffect(() => {
    const actual = leerToken();
    if (!actual) {
      router.replace("/iniciar-sesion");
      return;
    }
    const control = new AbortController();
    Promise.all([obtenerPerfil(actual, control.signal), obtenerNegocio(actual, control.signal)])
      .then(([perfilActual, negocioActual]) => {
        setToken(actual);
        setPerfil(perfilActual);
        setNegocio(negocioActual);
      })
      .catch((fallo: unknown) => {
        if (control.signal.aborted) return;
        if (fallo instanceof HttpError && fallo.status === 401) {
          borrarToken();
          router.replace("/iniciar-sesion");
          return;
        }
        setError(fallo instanceof Error ? fallo.message : "No se pudo cargar la sesión.");
      });
    return () => control.abort();
  }, [router]);

  if (error) {
    return <div className="access-state" role="alert"><h1>No se pudo abrir FoodSave</h1><p>{error}</p><button onClick={() => window.location.reload()}>Reintentar</button></div>;
  }
  if (!token || !perfil || !negocio) {
    return <div className="access-state" role="status">Cargando sesión…</div>;
  }

  function cerrarSesion() {
    borrarToken();
    router.replace("/iniciar-sesion");
  }

  return (
    <div className="app-layout">
      <aside className="sidebar" aria-label="Navegación principal">
        <Link href="/configuracion" className="brand"><span className="brand-mark">F</span><span>FoodSave<small>Operación local</small></span></Link>
        <div className="nav-group-label">Sistema</div>
        <nav>
          {enlaces.map((enlace) => (
            <Link key={enlace.href} href={enlace.href} className={`nav-link ${ruta === enlace.href || ruta.startsWith(`${enlace.href}/`) ? "active" : ""}`} aria-current={ruta === enlace.href ? "page" : undefined}>
              {enlace.texto}
            </Link>
          ))}
        </nav>
        <div className="sidebar-bottom"><span>{perfil.nombre}</span><small>{perfil.rol === "ADMINISTRADOR" ? "Administrador" : "Operador"}</small><button className="button-link" onClick={cerrarSesion}>Cerrar sesión</button></div>
      </aside>
      <div className="app-main">
        <header className="topbar"><span>FoodSave / Sistema</span><span className="business-chip">{negocio.nombre}</span></header>
        <main className="page-content">
          <div className="page-heading"><div><div className="eyebrow">Sistema</div><h1>{titulo}</h1><p>{descripcion}</p></div></div>
          {children({ token, perfil, negocio, actualizarNegocioLocal: setNegocio })}
        </main>
      </div>
    </div>
  );
}
