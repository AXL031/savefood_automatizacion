"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { solicitar } from "@/services/http";
export function CampanaAvisos({ token }: { token: string }) {
  const [cantidad, setCantidad] = useState<number | null>(null);
  useEffect(() => {
    const c = new AbortController(); let consultando = false;
    async function consultar() { if (consultando) return; consultando = true; try { const datos = await solicitar<{ leido: boolean }[]>("/operaciones/avisos", { token, signal: c.signal }); if (!c.signal.aborted) setCantidad(datos.filter(a => !a.leido).length); } catch { if (!c.signal.aborted) setCantidad(null); } finally { consultando = false; } }
    consultar(); const intervalo = setInterval(consultar, 30000); return () => { c.abort(); clearInterval(intervalo); };
  }, [token]);
  // El nombre conserva «Avisos» y el contador para que también se pueda activar por voz.
  return <Link className="notification-bell" href="/notificaciones" aria-label={cantidad === null ? "Avisos: abrir notificaciones" : `Avisos ${cantidad}: notificaciones sin leer`}>Avisos {cantidad !== null && <span>{cantidad}</span>}</Link>;
}
