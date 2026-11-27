"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { EVENTO_AVISO, type Aviso, type TonoAviso } from "@/services/avisos";

type AvisoVisible = Aviso & { id: number; repeticiones: number; saliendo: boolean; clave: string; version: number };

const DURACION: Record<TonoAviso, number> = { error: 9000, advertencia: 7000, exito: 4000, info: 5000 };
const MAXIMO = 4;
const ETIQUETA: Record<TonoAviso, string> = { error: "Error", advertencia: "Atención", exito: "Listo", info: "Información" };

function IconoTono({ tono }: { tono: TonoAviso }) {
  const trazos = {
    error: <><circle cx="12" cy="12" r="9" /><path d="m15 9-6 6M9 9l6 6" /></>,
    advertencia: <><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" /><path d="M12 9v4M12 17h.01" /></>,
    exito: <><circle cx="12" cy="12" r="9" /><path d="m8 12 3 3 5-6" /></>,
    info: <><circle cx="12" cy="12" r="9" /><path d="M12 11v5M12 8h.01" /></>,
  }[tono];
  return <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{trazos}</svg>;
}

/** Un aviso con cuenta regresiva visible que se detiene al pasar el cursor o al enfocarlo. */
function TarjetaAviso({ aviso, cerrar }: { aviso: AvisoVisible; cerrar: (id: number) => void }) {
  const duracion = aviso.duracion ?? DURACION[aviso.tono];
  const [pausado, setPausado] = useState(false);
  const restante = useRef(duracion);
  const inicio = useRef(Date.now());

  // Si el mismo aviso se repite, la cuenta vuelve a empezar.
  useEffect(() => { restante.current = duracion; inicio.current = Date.now(); }, [aviso.version, duracion]);
  useEffect(() => {
    if (pausado) return;
    inicio.current = Date.now();
    const temporizador = window.setTimeout(() => cerrar(aviso.id), restante.current);
    return () => { window.clearTimeout(temporizador); restante.current -= Date.now() - inicio.current; };
  }, [pausado, aviso.id, aviso.version, cerrar]);

  return <li className={`ma-toast is-${aviso.tono} ${aviso.saliendo ? "is-leaving" : ""}`} role={aviso.tono === "error" ? "alert" : "status"}
    onMouseEnter={() => setPausado(true)} onMouseLeave={() => setPausado(false)} onFocus={() => setPausado(true)} onBlur={() => setPausado(false)}>
    <span className="ma-toast-icon"><IconoTono tono={aviso.tono} /></span>
    <div className="ma-toast-body">
      <p className="ma-toast-title"><span className="sr-only">{ETIQUETA[aviso.tono]}: </span>{aviso.titulo}{aviso.repeticiones > 1 && <span className="ma-toast-count" aria-label={`${aviso.repeticiones} veces`}>×{aviso.repeticiones}</span>}</p>
      {aviso.mensaje && <p className="ma-toast-message">{aviso.mensaje}</p>}
      {aviso.ayuda && <p className="ma-toast-help"><strong>Qué hacer:</strong> {aviso.ayuda}</p>}
    </div>
    <button type="button" className="ma-toast-close" onClick={() => cerrar(aviso.id)} aria-label="Cerrar aviso" title="Cerrar">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
    </button>
    <span key={aviso.version} className={`ma-toast-progress ${pausado ? "is-paused" : ""}`} style={{ animationDuration: `${duracion}ms` }} aria-hidden="true" />
  </li>;
}

/** Contenedor de avisos arriba a la derecha. Montado una sola vez en el marco de la aplicación. */
export function Avisos() {
  const [avisos, setAvisos] = useState<AvisoVisible[]>([]);
  const siguienteId = useRef(1);

  const cerrar = useCallback((id: number) => {
    setAvisos((actuales) => actuales.map((a) => a.id === id ? { ...a, saliendo: true } : a));
    window.setTimeout(() => setAvisos((actuales) => actuales.filter((a) => a.id !== id)), 220);
  }, []);

  useEffect(() => {
    function recibir(evento: Event) {
      const aviso = (evento as CustomEvent<Aviso>).detail;
      if (!aviso?.titulo) return;
      const clave = `${aviso.tono}|${aviso.titulo}|${aviso.mensaje ?? ""}`;
      setAvisos((actuales) => {
        const repetido = actuales.find((a) => a.clave === clave && !a.saliendo);
        // Un error repetido (por ejemplo, una consulta periódica sin conexión) suma un contador en vez de apilar tarjetas.
        if (repetido) return actuales.map((a) => a === repetido ? { ...a, repeticiones: a.repeticiones + 1, version: a.version + 1 } : a);
        const nuevo: AvisoVisible = { ...aviso, id: siguienteId.current++, repeticiones: 1, saliendo: false, clave, version: 1 };
        return [...actuales, nuevo].slice(-MAXIMO);
      });
    }
    window.addEventListener(EVENTO_AVISO, recibir);
    return () => window.removeEventListener(EVENTO_AVISO, recibir);
  }, []);

  return <section className="ma-toasts" aria-label="Avisos" aria-live="polite">
    <ol>{avisos.map((aviso) => <TarjetaAviso key={aviso.id} aviso={aviso} cerrar={cerrar} />)}</ol>
  </section>;
}
