"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { obtenerNegocio, obtenerPerfil } from "@/services/autenticacion";
import { borrarToken, leerToken } from "@/services/sesion";
import type { Negocio, Perfil } from "@/types/autenticacion";
import { HttpError } from "@/services/http";
import { GuiaPantalla } from "./GuiaPantalla";

export type ContextoSesion = { token: string; perfil: Perfil; negocio: Negocio; actualizarNegocioLocal: (valor: Negocio) => void; actualizarPerfilLocal: (valor: Perfil) => void };
const SesionContext = createContext<ContextoSesion | null>(null);

type Props = {
  titulo: string;
  descripcion: string;
  children: (contexto: ContextoSesion) => ReactNode;
};

const grupos = [
  { titulo: "Inicio", enlaces: [{ href: "/", texto: "Resumen y próximos pasos" }] },
  {
    titulo: "Preparar datos",
    enlaces: [
      { href: "/inicializacion", texto: "Datos iniciales" },
      { href: "/productos", texto: "Productos" },
      { href: "/ventas", texto: "Ventas" },
    ],
  },
  {
    titulo: "Catálogo e inventario",
    enlaces: [
      { href: "/ingredientes", texto: "Ingredientes" },
      { href: "/recetas", texto: "Recetas" },
      { href: "/inventario", texto: "Inventario" },
    ],
  },
  {
    titulo: "Planificar y comprar",
    enlaces: [
      { href: "/automatizaciones", texto: "Programar tareas" },
      { href: "/planificacion", texto: "Planes y faltantes" },
      { href: "/proveedores", texto: "Proveedores y Telegram" },
      { href: "/compras", texto: "Pedidos y envíos" },
    ],
  },
  { titulo: "Resultados", enlaces: [
    { href: "/pronosticos", texto: "Pronósticos y modelos" },
    { href: "/panel", texto: "Evaluación histórica" },
  ] },
  {
    titulo: "Administración",
    enlaces: [
      { href: "/configuracion", texto: "Configuración" },
      { href: "/usuarios", texto: "Usuarios" },
    ],
  },
];

/** Montado en el layout raíz: la sesión y la navegación sobreviven a las rutas. */
export function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const ruta = usePathname();
  const [token, setToken] = useState<string | null>(null);
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [negocio, setNegocio] = useState<Negocio | null>(null);
  const [error, setError] = useState("");
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [revisionSesion, setRevisionSesion] = useState(0);
  const publica = ruta === "/iniciar-sesion";
  const enlaceActual = grupos.flatMap((grupo) => grupo.enlaces).find((enlace) => ruta === enlace.href || (enlace.href !== "/" && ruta.startsWith(`${enlace.href}/`)));
  const grupoActual = grupos.find((grupo) => grupo.enlaces.some((enlace) => ruta === enlace.href || (enlace.href !== "/" && ruta.startsWith(`${enlace.href}/`))));

  useEffect(() => {
    function sesionVencida() {
      borrarToken();
      setToken(null); setPerfil(null); setNegocio(null);
      router.replace("/iniciar-sesion");
    }
    window.addEventListener("foodsave:sesion-vencida", sesionVencida);
    return () => window.removeEventListener("foodsave:sesion-vencida", sesionVencida);
  }, [router]);

  useEffect(() => {
    if (publica) { setToken(null); setPerfil(null); setNegocio(null); setError(""); return; }
    setError("");
    const actual = leerToken();
    if (!actual) {
      router.replace("/iniciar-sesion");
      return;
    }
    const control = new AbortController();
    Promise.all([obtenerPerfil(actual, control.signal), obtenerNegocio(actual, control.signal)])
      .then(([perfilActual, negocioActual]) => {
        if (control.signal.aborted) return;
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
  }, [router, publica, revisionSesion]);

  if (publica) return <>{children}</>;

  if (error) {
    return <div className="access-state" role="alert"><h1>No se pudo abrir FoodSave</h1><p>{error}</p><button onClick={() => setRevisionSesion((r) => r + 1)}>Reintentar</button></div>;
  }
  if (!token || !perfil || !negocio) {
    return <div className="access-state" role="status">Cargando sesión…</div>;
  }

  function cerrarSesion() {
    borrarToken();
    setToken(null); setPerfil(null); setNegocio(null);
    router.replace("/iniciar-sesion");
  }

  return (
    <SesionContext.Provider value={{ token, perfil, negocio, actualizarNegocioLocal: setNegocio, actualizarPerfilLocal: setPerfil }}><div className="app-layout">
      <aside className="sidebar" aria-label="Navegación principal">
        <Link href="/" className="brand"><span className="brand-mark">F</span><span>FoodSave<small>Operación local</small></span></Link>
        <button type="button" className="button-secondary mobile-menu" aria-expanded={menuAbierto} aria-controls="menu-principal" onClick={() => setMenuAbierto(!menuAbierto)}>{menuAbierto ? "Cerrar menú" : "Ver menú de pantallas"}</button>
        <div id="menu-principal" className={`sidebar-menu ${menuAbierto ? "menu-open" : ""}`} tabIndex={0} role="region" aria-label="Opciones del menú">
        {grupos.map((grupo) => (
          <div key={grupo.titulo}>
            <div className="nav-group-label">{grupo.titulo}</div>
            <nav aria-label={grupo.titulo}>
              {grupo.enlaces.filter((enlace) => enlace.href !== "/usuarios" || perfil.rol === "ADMINISTRADOR").map((enlace) => (
                <Link key={enlace.href} href={enlace.href} onClick={() => setMenuAbierto(false)} className={`nav-link ${ruta === enlace.href || (enlace.href !== "/" && ruta.startsWith(`${enlace.href}/`)) ? "active" : ""}`} aria-current={ruta === enlace.href ? "page" : undefined}>
                  {enlace.texto}
                </Link>
              ))}
            </nav>
          </div>
        ))}
        </div>
        <div className="sidebar-bottom"><span>{perfil.nombre}</span><small>{perfil.rol === "ADMINISTRADOR" ? "Administrador" : "Operador"}</small><button className="button-link" onClick={cerrarSesion}>Cerrar sesión</button></div>
      </aside>
      <div className="app-main">
        <header className="topbar"><span><Link href="/">FoodSave</Link> / {enlaceActual?.texto ?? "Detalle"}</span><span className="business-chip">{negocio.nombre}</span></header>
        <main className="page-content" id="contenido-principal">
          {children}
        </main>
      </div>
    </div></SesionContext.Provider>
  );
}

export function ProtectedShell({ titulo, descripcion, children }: Props) {
  const contexto = useContext(SesionContext);
  const ruta = usePathname();
  const grupoActual = grupos.find((grupo) => grupo.enlaces.some((enlace) => ruta === enlace.href || (enlace.href !== "/" && ruta.startsWith(`${enlace.href}/`))));
  if (!contexto) return null;
  return <>
    <div className="page-heading"><div><div className="eyebrow">{grupoActual?.titulo ?? "FoodSave"}</div><h1>{titulo}</h1><p>{descripcion}</p></div><span className="badge badge-info">Escenario de demostración</span></div>
    <GuiaPantalla ruta={ruta} />
    {children(contexto)}
  </>;
}
