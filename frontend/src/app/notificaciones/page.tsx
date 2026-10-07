"use client";
import Link from "next/link";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
export default function NotificacionesPage() {
  return <ProtectedShell titulo="Centro de avisos · función futura" descripcion="Los resultados disponibles se consultan en sus pantallas de origen.">{() => <section className="card"><span className="badge badge-neutral">Todavía no disponible</span><h2 className="section-space">Dónde consultar los avisos actuales</h2><p>El centro general de notificaciones aún no está implementado.</p><div className="home-grid section-space"><div><h3>Mensajes a tu Telegram</h3><p>Consulta el pedido, el estado del envío y el identificador confirmado por Telegram.</p><Link href="/compras">Abrir Pedidos y envíos →</Link></div><div><h3>Errores de tareas</h3><p>Consulta qué tarea falló, sus intentos y el motivo que debe corregirse.</p><Link href="/automatizaciones">Abrir tareas programadas →</Link></div></div></section>}</ProtectedShell>;
}
