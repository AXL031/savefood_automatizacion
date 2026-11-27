import Link from "next/link";
import type { CSSProperties, ReactNode } from "react";
import { Icono, ubicar, vecinos } from "./navegacion";

type Props = {
  titulo: string;
  descripcion: string;
  ruta: string;
  esAdmin?: boolean;
  retorno?: ReactNode;
  children: ReactNode;
};

/** Inicio y Cómo funciona dibujan su propia portada: sin encabezado ni enlaces de recorrido del marco. */
const SIN_ENCABEZADO = new Set(["/", "/como-funciona"]);

/**
 * Marco común de las pantallas administrativas: encabezado compacto con la etapa del ciclo,
 * contenido y enlaces «anterior / siguiente» para seguir el recorrido sin volver al menú.
 */
export function MarcoPagina({ titulo, descripcion, ruta, esAdmin = false, retorno, children }: Props) {
  const ubicacion = ubicar(ruta);
  const { anterior, siguiente } = vecinos(ruta);
  const siguienteVisible = siguiente?.soloAdmin && !esAdmin ? null : siguiente;
  const estilo = ubicacion ? ({ "--etapa": ubicacion.etapa.color } as CSSProperties) : undefined;
  return <div className="workspace-page" style={estilo}>
    {!SIN_ENCABEZADO.has(ruta) && <header className="ma-page-header">
      <span className="ma-page-icon" aria-hidden="true"><Icono nombre={ubicacion?.pantalla.icono ?? "inicio"} tamano={24} /></span>
      <div className="ma-page-title">
        {ubicacion && <span className="ma-stage-chip">{ubicacion.etapa.numero ? `Paso ${ubicacion.etapa.numero} · ` : ""}{ubicacion.etapa.titulo}</span>}
        <h1>{titulo}</h1>
        <p>{descripcion}</p>
      </div>
    </header>}
    {retorno}
    <div className="workspace-content">{children}</div>
    {!SIN_ENCABEZADO.has(ruta) && (anterior || siguienteVisible) && <nav className="ma-pager" aria-label="Recorrido del ciclo">
      {anterior ? <Link href={anterior.href} className="ma-pager-link"><Icono nombre="flecha-izquierda" /><span><small>Anterior</small>{anterior.texto}</span></Link> : <span />}
      {siguienteVisible && <Link href={siguienteVisible.href} className="ma-pager-link ma-pager-next"><span><small>Siguiente paso</small>{siguienteVisible.texto}</span><Icono nombre="flecha-derecha" /></Link>}
    </nav>}
  </div>;
}
