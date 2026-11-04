import Link from "next/link";
import type { ReactNode } from "react";

type Enlace = { href: string; texto: string };
type Props = {
  titulo: string;
  descripcion: string;
  grupo: string;
  enlaces: Enlace[];
  ruta: string;
  retorno?: ReactNode;
  children: ReactNode;
};

const PORTADAS_PROPIAS = new Set(["/", "/pronosticos", "/panel", "/informes"]);

function IconoModulo({ grupo }: { grupo: string }) {
  const trazos = grupo === "Ventas"
    ? <><path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3Z" /><path d="M9 7h6M9 11h6M9 15h3" /></>
    : grupo === "Administración"
      ? <><path d="M4 7h16M4 17h16" /><circle cx="9" cy="7" r="3" /><circle cx="15" cy="17" r="3" /></>
      : grupo === "Planificar y comprar"
        ? <><rect x="3" y="5" width="18" height="16" rx="3" /><path d="M7 3v4M17 3v4M3 11h18m-13 5 3 3 5-5" /></>
        : <><path d="m12 3 9 5-9 5-9-5 9-5ZM3 12l9 5 9-5M3 16l9 5 9-5" /></>;
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{trazos}</svg>;
}

/** El mismo lenguaje de Resultados para todos los módulos administrativos. */
export function MarcoPagina({ titulo, descripcion, grupo, enlaces, ruta, retorno, children }: Props) {
  const portadaPropia = PORTADAS_PROPIAS.has(ruta);
  return <div className={`workspace-page ${portadaPropia ? "workspace-analytics" : "workspace-standard"}`}>
    {!portadaPropia && enlaces.length > 1 && <nav className="analytics-nav workspace-nav" aria-label={`Navegación de ${grupo}`}>
      {enlaces.map(enlace => <Link key={enlace.href} href={enlace.href}
        aria-current={ruta === enlace.href || (enlace.href !== "/" && ruta.startsWith(`${enlace.href}/`)) ? "page" : undefined}>
        {enlace.texto}
      </Link>)}
    </nav>}
    {portadaPropia
      ? <header className="page-heading"><div><div className="eyebrow">{grupo}</div><h1>{titulo}</h1><p>{descripcion}</p></div></header>
      : <header className="analytics-hero analytics-hero-compact workspace-hero">
        <div><span className="analytics-eyebrow">{grupo}</span><h1>{titulo}</h1><p>{descripcion}</p></div>
        <span className="workspace-module-symbol"><IconoModulo grupo={grupo} /></span>
      </header>}
    {retorno}
    <div className="workspace-content">{children}</div>
  </div>;
}
