/** Íconos de la tienda: los SVG exportados de Figma se usan como archivo; los de interacción, en línea. */

const ARCHIVOS = {
  huella: [20, 19], "huella-grande": [28.33, 26.92], buscar: [21.5, 13.5], canasta: [13.33, 16.67], usuario: [12, 12],
  ubicacion: [10.67, 13.33], cerrar: [11.67, 11.67], google: [20, 20], candado: [10.67, 14], garantia: [20.17, 19.25],
  horno: [14.67, 9.33], copyright: [15, 15.02], flecha: [9.33, 9.33],
} as const;

export function IconoArchivo({ nombre, escala = 1 }: { nombre: keyof typeof ARCHIVOS; escala?: number }) {
  const [ancho, alto] = ARCHIVOS[nombre];
  // eslint-disable-next-line @next/next/no-img-element
  return <img src={`/tienda/iconos/${nombre}.svg`} alt="" aria-hidden="true" width={ancho * escala} height={alto * escala} className="t-icono-archivo" />;
}

type Trazo = "adelante" | "persona" | "mas" | "menos" | "check" | "copiar" | "tarjeta" | "billetera" | "atras" | "camion" | "salir" | "bolsa" | "reloj" | "estrella";

const TRAZOS: Record<Trazo, string> = {
  adelante: "M5 12h14M12 5l7 7-7 7",
  persona: "M20 21a8 8 0 0 0-16 0M12 13a4 4 0 1 0 0-8 4 4 0 0 0 0 8",
  mas: "M12 5v14M5 12h14",
  menos: "M5 12h14",
  check: "M20 6 9 17l-5-5",
  copiar: "M9 9h10v10H9zM5 15V5h10",
  tarjeta: "M3 6h18v12H3zM3 10h18",
  billetera: "M4 7h15a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a2 2 0 0 1 2-2h11M16 13h.01",
  atras: "M19 12H5M12 19l-7-7 7-7",
  camion: "M3 6h11v10H3zM14 9h4l3 3v4h-7M7 19a2 2 0 1 0 0-.01M17 19a2 2 0 1 0 0-.01",
  salir: "M15 4h4v16h-4M10 8l-4 4 4 4M6 12h11",
  bolsa: "M6 8h12l-1 12H7zM9 8V6a3 3 0 0 1 6 0v2",
  reloj: "M12 7v5l3 2M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18",
  estrella: "M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z",
};

export function Icono({ nombre, tamano = 16 }: { nombre: Trazo; tamano?: number }) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={TRAZOS[nombre]} />
    </svg>
  );
}
