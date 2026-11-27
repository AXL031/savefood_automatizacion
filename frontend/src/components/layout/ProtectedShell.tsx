"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useState, type CSSProperties, type ReactNode } from "react";
import { obtenerNegocio, obtenerPerfil } from "@/services/autenticacion";
import { borrarToken, leerToken } from "@/services/sesion";
import type { Negocio, Perfil } from "@/types/autenticacion";
import { HttpError } from "@/services/http";
import { MarcaFoodSave } from "@/components/ui/MarcaFoodSave";
import { Avisos } from "@/components/ui/Avisos";
import { CampanaAvisos } from "./CampanaAvisos";
import { MarcoPagina } from "./MarcoPagina";
import { ETAPAS, ETAPAS_CICLO, GUIA, INICIO, Icono, coincide, ubicar, visibles, type NombreIcono } from "./navegacion";

export type ContextoSesion = { token: string; perfil: Perfil; negocio: Negocio; actualizarNegocioLocal: (valor: Negocio) => void; actualizarPerfilLocal: (valor: Perfil) => void };
const SesionContext = createContext<ContextoSesion | null>(null);

type Props = {
  titulo: string;
  descripcion: string;
  children: (contexto: ContextoSesion) => ReactNode;
};

const CLAVE_PLEGADO = "foodsave.menu-plegado";
const CLAVE_TEMA = "foodsave.tema";
const CLAVE_ETAPAS = "foodsave.etapas-cerradas";

function leerPreferencia(clave: string) {
  try { return window.localStorage.getItem(clave); } catch { return null; }
}
function guardarPreferencia(clave: string, valor: string) {
  try { window.localStorage.setItem(clave, valor); } catch { /* sin almacenamiento: la preferencia dura la visita */ }
}
function iniciales(nombre: string) {
  return nombre.split(/\s+/).filter(Boolean).slice(0, 2).map((parte) => parte[0]?.toUpperCase()).join("") || "FS";
}
const colorEtapa = (color: string) => ({ "--etapa": color }) as CSSProperties;

/** Montado en el layout raíz: la sesión y la navegación sobreviven a las rutas. */
export function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const ruta = usePathname();
  const [token, setToken] = useState<string | null>(null);
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [negocio, setNegocio] = useState<Negocio | null>(null);
  const [error, setError] = useState("");
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [plegado, setPlegado] = useState(false);
  const [tema, setTema] = useState<"claro" | "oscuro">("claro");
  const [cerradas, setCerradas] = useState<string[]>([]);
  const [revisionSesion, setRevisionSesion] = useState(0);
  // La tienda del cliente (ADR-009) tiene su propio layout y sesión; no usa la administrativa.
  const publica = ruta === "/iniciar-sesion" || ruta === "/tienda" || ruta.startsWith("/tienda/") || ruta.startsWith("/proveedor/");
  const ubicacion = ubicar(ruta);

  useEffect(() => {
    setPlegado(leerPreferencia(CLAVE_PLEGADO) === "1");
    setTema(document.documentElement.dataset.tema === "oscuro" ? "oscuro" : "claro");
    try { const guardadas: unknown = JSON.parse(leerPreferencia(CLAVE_ETAPAS) ?? "[]"); if (Array.isArray(guardadas)) setCerradas(guardadas.filter((id): id is string => typeof id === "string")); } catch { /* preferencia ilegible: todas abiertas */ }
  }, []);

  // La etapa de la pantalla actual siempre se abre para que el enlace activo quede visible.
  const etapaActual = ubicacion?.etapa.id;
  useEffect(() => {
    if (etapaActual) setCerradas((actuales) => actuales.includes(etapaActual) ? actuales.filter((id) => id !== etapaActual) : actuales);
  }, [etapaActual]);

  // Onda Material al pulsar botones y enlaces de navegación (decorativa, sin afectar el clic).
  useEffect(() => {
    const selector = ".button-primary, .button-secondary, button:not([class]), .ma-nav-link, .ma-cycle-step a, .ma-pager-link, .ma-tracker-step a, .ma-icon-button";
    function onda(evento: PointerEvent) {
      const destino = (evento.target as HTMLElement | null)?.closest<HTMLElement>(selector);
      if (!destino || destino.matches(":disabled") || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
      const caja = destino.getBoundingClientRect();
      const tamano = Math.max(caja.width, caja.height) * 2;
      const span = document.createElement("span");
      span.className = "ma-ripple";
      span.style.width = span.style.height = `${tamano}px`;
      span.style.left = `${evento.clientX - caja.left - tamano / 2}px`;
      span.style.top = `${evento.clientY - caja.top - tamano / 2}px`;
      destino.appendChild(span);
      span.addEventListener("animationend", () => span.remove());
    }
    document.addEventListener("pointerdown", onda);
    return () => document.removeEventListener("pointerdown", onda);
  }, []);

  // El cajón móvil se cierra al cambiar de pantalla o con Escape.
  useEffect(() => { setMenuAbierto(false); }, [ruta]);
  useEffect(() => {
    if (!menuAbierto) return;
    const cerrar = (evento: KeyboardEvent) => { if (evento.key === "Escape") setMenuAbierto(false); };
    window.addEventListener("keydown", cerrar);
    return () => window.removeEventListener("keydown", cerrar);
  }, [menuAbierto]);

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
    return <div className="access-state" role="alert"><MarcaFoodSave /><h1>No se pudo abrir FoodSave</h1><p>{error}</p><button className="button-primary" onClick={() => setRevisionSesion((r) => r + 1)}>Reintentar</button></div>;
  }
  if (!token || !perfil || !negocio) {
    return <div className="access-state" role="status"><MarcaFoodSave /><div className="ma-skeleton ma-skeleton-line" /><div className="ma-skeleton ma-skeleton-line corto" /><span className="sr-only">Cargando sesión…</span></div>;
  }

  const esAdmin = perfil.rol === "ADMINISTRADOR";

  function cerrarSesion() {
    borrarToken();
    setToken(null); setPerfil(null); setNegocio(null);
    router.replace("/iniciar-sesion");
  }
  function alternarPlegado() {
    const nuevo = !plegado;
    setPlegado(nuevo);
    guardarPreferencia(CLAVE_PLEGADO, nuevo ? "1" : "0");
  }
  function alternarEtapa(id: string) {
    const nuevas = cerradas.includes(id) ? cerradas.filter((otra) => otra !== id) : [...cerradas, id];
    setCerradas(nuevas);
    guardarPreferencia(CLAVE_ETAPAS, JSON.stringify(nuevas));
  }
  function alternarTema() {
    const nuevo = tema === "oscuro" ? "claro" : "oscuro";
    setTema(nuevo);
    document.documentElement.dataset.tema = nuevo;
    guardarPreferencia(CLAVE_TEMA, nuevo);
  }

  const enlace = (href: string, texto: string, icono: NombreIcono, ayuda: string) => {
    const activo = href === "/" ? ruta === "/" : coincide(ruta, href);
    return <Link key={href} href={href} className={`ma-nav-link ${activo ? "active" : ""}`} aria-current={activo ? "page" : undefined}
      title={plegado ? texto : ayuda}>
      <Icono nombre={icono} /><span className="ma-nav-text">{texto}</span>
    </Link>;
  };

  // Cada etapa se puede contraer; con el menú plegado a íconos se muestran todas.
  const grupoEtapa = (etapa: (typeof ETAPAS)[number], nombre: string) => {
    const abierta = plegado || !cerradas.includes(etapa.id);
    const idLista = `etapa-${etapa.id}`;
    return <section key={etapa.id} className={`ma-nav-stage ${etapa.numero === undefined ? "ma-nav-admin" : ""} ${ubicacion?.etapa.id === etapa.id ? "is-current" : ""} ${abierta ? "is-open" : ""}`}
      style={colorEtapa(etapa.color)} aria-label={nombre}>
      <button type="button" className="ma-nav-stage-title" onClick={() => alternarEtapa(etapa.id)} disabled={plegado}
        aria-expanded={abierta} aria-controls={idLista} title={plegado ? (etapa.numero ? `${etapa.numero}. ${etapa.titulo}` : etapa.titulo) : etapa.resumen}>
        {etapa.numero !== undefined && <span className="ma-stage-number">{etapa.numero}</span>}
        <span className="ma-nav-text">{etapa.titulo}</span>
        <span className="ma-nav-chevron ma-nav-text"><Icono nombre="chevron" tamano={16} /></span>
      </button>
      <div className="ma-nav-stage-links" id={idLista} inert={!abierta}>
        <div className="ma-nav-stage-inner">{visibles(etapa, esAdmin).map((p) => enlace(p.href, p.texto, p.icono, p.ayuda))}</div>
      </div>
    </section>;
  };

  return (
    <SesionContext.Provider value={{ token, perfil, negocio, actualizarNegocioLocal: setNegocio, actualizarPerfilLocal: setPerfil }}>
      <a className="skip-link" href="#contenido-principal">Saltar al contenido</a>
      <Avisos />
      <div className={`app-layout ma-shell ${plegado ? "is-collapsed" : ""} ${menuAbierto ? "drawer-open" : ""}`}>
        <aside className="ma-sidebar" id="menu-principal" aria-label="Navegación principal">
          <div className="ma-sidebar-head">
            <Link href="/" className="brand"><MarcaFoodSave /><span className="brand-name ma-nav-text">FoodSave</span></Link>
            <button type="button" className="ma-icon-button ma-collapse" onClick={alternarPlegado} aria-pressed={plegado}
              aria-label={plegado ? "Expandir menú" : "Plegar menú"} title={plegado ? "Expandir menú" : "Plegar menú"}><Icono nombre="plegar" /></button>
          </div>
          <nav className="ma-sidebar-scroll" aria-label="Pantallas de FoodSave">
            {enlace(INICIO.href, INICIO.texto, INICIO.icono, INICIO.ayuda)}
            {enlace(GUIA.href, GUIA.texto, GUIA.icono, GUIA.ayuda)}
            <p className="ma-nav-caption ma-nav-text">Ciclo del negocio</p>
            {ETAPAS_CICLO.map((etapa) => grupoEtapa(etapa, `Paso ${etapa.numero}: ${etapa.titulo}`))}
            {ETAPAS.filter((etapa) => etapa.numero === undefined).map((etapa) => grupoEtapa(etapa, etapa.titulo))}
          </nav>
          <div className="ma-sidebar-user">
            <span className="ma-avatar" aria-hidden="true">{iniciales(perfil.nombre)}</span>
            <span className="ma-nav-text ma-user-text"><strong>{perfil.nombre}</strong><small>{esAdmin ? "Administrador" : "Operador"}</small></span>
            <button type="button" className="ma-icon-button" onClick={cerrarSesion} aria-label="Cerrar sesión" title="Cerrar sesión"><Icono nombre="salir" /></button>
          </div>
        </aside>
        <button type="button" className="ma-scrim" aria-label="Cerrar menú" tabIndex={menuAbierto ? 0 : -1} onClick={() => setMenuAbierto(false)} />
        <div className="app-main">
          <header className="ma-topbar">
            <button type="button" className="ma-icon-button ma-menu-button" aria-expanded={menuAbierto} aria-controls="menu-principal"
              aria-label={menuAbierto ? "Cerrar menú" : "Abrir menú"} onClick={() => setMenuAbierto(!menuAbierto)}><Icono nombre="menu" /></button>
            <nav className="ma-breadcrumb" aria-label="Estás aquí">
              <ol>
                <li><Link href="/">Inicio</Link></li>
                {ubicacion && <li className="ma-crumb-stage">{ubicacion.etapa.numero ? `Paso ${ubicacion.etapa.numero} · ` : ""}{ubicacion.etapa.titulo}</li>}
                {ubicacion && <li aria-current="page">{ubicacion.pantalla.texto}</li>}
                {!ubicacion && ruta !== "/" && <li aria-current="page">{coincide(ruta, GUIA.href) ? GUIA.texto : "Detalle"}</li>}
              </ol>
            </nav>
            <div className="ma-topbar-actions">
              <button type="button" className="ma-icon-button" onClick={alternarTema} aria-pressed={tema === "oscuro"}
                aria-label={tema === "oscuro" ? "Usar tema claro" : "Usar tema oscuro"} title={tema === "oscuro" ? "Tema claro" : "Tema oscuro"}>
                <Icono nombre={tema === "oscuro" ? "sol" : "luna"} />
              </button>
              {esAdmin && <CampanaAvisos token={token} />}
              <span className="business-chip" title={negocio.nombre}>{negocio.nombre}</span>
            </div>
          </header>
          {ubicacion?.etapa.numero !== undefined && <BarraCiclo actual={ubicacion.etapa.id} esAdmin={esAdmin} />}
          <main className="page-content" id="contenido-principal" tabIndex={-1} key={ruta}>
            {children}
          </main>
        </div>
      </div>
    </SesionContext.Provider>
  );
}

/** Barra horizontal de las seis etapas: indica en qué parte del ciclo está la pantalla. */
function BarraCiclo({ actual, esAdmin }: { actual: string; esAdmin: boolean }) {
  const indiceActual = ETAPAS_CICLO.findIndex((etapa) => etapa.id === actual);
  return <nav className="ma-cycle" aria-label="Ciclo del negocio">
    <ol>
      {ETAPAS_CICLO.map((etapa, indice) => {
        const destino = visibles(etapa, esAdmin)[0]?.href ?? "/";
        const estado = indice < indiceActual ? "antes" : indice === indiceActual ? "actual" : "despues";
        return <li key={etapa.id} className={`ma-cycle-step is-${estado}`} style={colorEtapa(etapa.color)}>
          <Link href={destino} aria-current={estado === "actual" ? "step" : undefined} title={etapa.resumen}>
            <span className="ma-stage-number">{etapa.numero}</span>
            <span className="ma-cycle-text"><strong>{etapa.titulo}</strong><small>{etapa.resumen}</small></span>
          </Link>
        </li>;
      })}
    </ol>
  </nav>;
}

export function ProtectedShell({ titulo, descripcion, children }: Props) {
  const contexto = useContext(SesionContext);
  const ruta = usePathname();
  const [volverFlujo, setVolverFlujo] = useState(false);
  useEffect(() => { setVolverFlujo(new URLSearchParams(window.location.search).get("volver") === "automatizaciones"); }, [ruta]);
  if (!contexto) return null;
  return <MarcoPagina titulo={titulo} descripcion={descripcion} ruta={ruta} esAdmin={contexto.perfil.rol === "ADMINISTRADOR"}
    retorno={volverFlujo && <p className="return-flow"><Link href="/automatizaciones">← Continuar configurando mi automatización</Link><span>Tu selección está guardada.</span></p>}>
    {children(contexto)}
  </MarcoPagina>;
}
