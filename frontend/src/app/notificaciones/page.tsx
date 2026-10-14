"use client";
import Link from "next/link";
import { ProtectedShell } from "@/components/layout/ProtectedShell";
export default function NotificacionesPage() {
  return <ProtectedShell titulo="Avisos" descripcion="Mensajes enviados a proveedores y resultados de tus tareas.">{() => <section className="card"><h2>Dónde consultar tus avisos</h2><div className="home-grid section-space"><div><h3>Mensajes por Telegram</h3><p>Consulta el pedido, el estado del envío y el identificador confirmado por Telegram.</p><Link href="/compras">Abrir Pedidos y envíos →</Link></div><div><h3>Errores de tareas</h3><p>Consulta qué tarea falló, sus intentos y el motivo que debe corregirse.</p><Link href="/automatizaciones">Abrir tareas programadas →</Link></div></div></section>}</ProtectedShell>;
}
